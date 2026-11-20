package im.platform.tests.im;

import com.fasterxml.jackson.databind.JsonNode;
import im.platform.shared.authsupport.Config;
import java.net.*;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

import static im.platform.tests.im.GroupFixtures.*;

final class GroupTransactions {
    final GroupFixtures f;
    GroupTransactions(Config config,String base) {f=new GroupFixtures(config,base);}
    static String mutation(String id,List<String> targets) throws Exception {
        return JSON.writeValueAsString(Map.of("requestId",id,"memberUserIds",targets));
    }
    void concurrent(JsonNode vector)throws Exception {
        var v=JSON.readTree(f.template(vector.toString()));
        boolean create=v.get("operation").asText().equals("CREATE");
        f.prepareUsers();
        if(v.has("friendships")) for(var pair:v.get("friendships"))
            f.friendship(pair.get(0).asText(),pair.get(1).asText(),UUID.randomUUID().toString());
        else f.friendship(f.user(create?1:2),f.user(create?2:3),UUID.randomUUID().toString());
        if(!create) f.seedGroup(f.user(1),UUID.randomUUID().toString(),f.conversation(),List.of(f.user(1),f.user(2)));
        var gate=new CyclicBarrier(2);
        String path=create?"/v1/groups":"/v1/groups/"+f.conversation()+"/members";
        var futures=new ArrayList<Future<HttpResponse<String>>>();
        try(var threads=Executors.newFixedThreadPool(2)) {
            for(int i=0;i<2;i++){
                String body=mutation(v.get("requestIds").get(i).asText(),values(v.get("targets").get(i)));
                String token=f.tokens.get(v.get("actors").get(i).asText());
                futures.add(threads.submit(()->{gate.await(5,TimeUnit.SECONDS);return f.call(path,body,token);}));
            }
            var a=futures.get(0).get(15,TimeUnit.SECONDS);var b=futures.get(1).get(15,TimeUnit.SECONDS);
            require(a.statusCode()==(create?201:200)&&a.statusCode()==b.statusCode(),"concurrent HTTP");
            var ar=JSON.readTree(a.body());var br=JSON.readTree(b.body());
            var expected=v.get("expected");
            if(expected.path("resultEquality").asBoolean())require(ar.equals(br),"concurrent result mismatch");
            String conversation=ar.get("conversationId").asText();
            require(f.db.queryForObject("SELECT count(*) FROM group_operation_receipts WHERE conversation_id=?::uuid",Integer.class,conversation)==expected.get("receipts").intValue(),"concurrent receipt count");
            var users=f.db.queryForList("SELECT user_id::text FROM conversation_members WHERE conversation_id=?::uuid AND left_at IS NULL ORDER BY user_id",String.class,conversation);
            var targetUsers=new TreeSet<>(create?List.of(f.user(1)):List.of(f.user(1),f.user(2)));
            for(var targets:v.get("targets"))targetUsers.addAll(values(targets));
            require(users.equals(List.copyOf(targetUsers)),"concurrent final membership");
            int events=f.db.queryForObject("SELECT count(*) FROM user_sync_events WHERE payload->>'subjectId'=?",Integer.class,conversation);
            int outbox=f.db.queryForObject("SELECT count(*) FROM outbox_events WHERE payload->'event'->>'subjectId'=?",Integer.class,conversation);
            require(events==outbox && (events==2*users.size() || expected.has("eventsOnlyForActualChange")&&events==14),"concurrent invalidation count");
        }
    }

    void rollback(JsonNode v)throws Exception {
        f.prepareUsers();f.friendship(f.user(1),f.user(2),UUID.randomUUID().toString());
        var tables=Map.of("conversation","conversations","membership","conversation_members","receipt","group_operation_receipts",
            "user_sync","user_sync_events","outbox","outbox_events","commit-definite-failure","outbox_events");
        String body=mutation(UUID.randomUUID().toString(),List.of(f.user(2)));
        for(var point:v.get("faults")){
            String table=tables.get(point.asText()),name="im_fault_"+f.namespace;
            boolean deferred=point.asText().equals("commit-definite-failure");
            String before=f.counts();
            f.db.execute("CREATE FUNCTION "+name+"() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'controlled IM fixture failure'; END $$");
            try{
                f.db.execute("CREATE "+(deferred?"CONSTRAINT ":"")+"TRIGGER "+name+(deferred?" AFTER ":" BEFORE ")+"INSERT ON "+table+(deferred?" DEFERRABLE INITIALLY DEFERRED":"")+" FOR EACH ROW EXECUTE FUNCTION "+name+"()");
                try {
                    int code=f.call("/v1/groups",body,f.tokens.get(f.user(1))).statusCode();
                    require(code>=500 && code<600 && before.equals(f.counts()),point.asText()+" rollback");
                } finally {f.db.execute("DROP TRIGGER "+name+" ON "+table);}
            } finally {f.db.execute("DROP FUNCTION "+name+"()");}
        }
    }

    void lost(JsonNode v,boolean beforeCommit)throws Exception{
        f.prepareUsers();f.friendship(f.user(1),f.user(2),UUID.randomUUID().toString());
        var retry=JSON.readTree(f.template(v.get("retry").toString()));
        String id=retry.get("requestId").asText(),body=mutation(id,values(retry.get("targets")));
        String token=f.tokens.get(f.user(1));
        var url=URI.create(f.base);
        try(var lock=f.db.getDataSource().getConnection();var socket=new Socket(url.getHost(),url.getPort())) {
            lock.setAutoCommit(false);
            if(beforeCommit)try(var q=lock.prepareStatement("SELECT user_id FROM users WHERE user_id=?::uuid FOR UPDATE")){
                q.setString(1,f.user(1));q.executeQuery().close();
            }
            String raw="POST /v1/groups HTTP/1.1\r\nHost: "+url.getAuthority()+"\r\nAuthorization: Bearer "+token+
                "\r\nContent-Type: application/json\r\nContent-Length: "+body.getBytes(StandardCharsets.UTF_8).length+"\r\nConnection: close\r\n\r\n"+body;
            socket.getOutputStream().write(raw.getBytes(StandardCharsets.UTF_8));socket.getOutputStream().flush();
            if(beforeCommit) {
                require(receipts(id)==0,"lock must precede durable result");
                socket.close();lock.commit();
            } else {
                long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(10);
                while(receipts(id)==0 && System.nanoTime()<end) Thread.sleep(15);
                require(receipts(id)==1,"commit before losing unread response");
            }
        }
        var result=f.call("/v1/groups",body,token);
        require(result.statusCode()==201 && receipts(id)==1,"lost reply recovery");
        require(JSON.readTree(result.body()).equals(JSON.readTree(f.call("/v1/groups",body,token).body())),"retry original result");
    }
    int receipts(String id){return f.db.queryForObject("SELECT count(*) FROM group_operation_receipts WHERE actor_id=?::uuid AND request_id=?::uuid",Integer.class,f.user(1),id);}
    void snapshotInsert()throws Exception {
        f.prepareUsers();
        String group=f.conversation(), token=f.tokens.get(f.user(1));
        f.seedGroup(f.user(1),UUID.randomUUID().toString(),group,List.of(f.user(1),f.user(3),f.user(4)));
        String path="/v1/conversations?limit=2&requestId="+UUID.randomUUID();
        var first=JSON.readTree(f.call(path,null,token).body());
        require(first.get("hasMore").asBoolean(),"first page must continue");
        var next=first.get("next");
        f.friendship(f.user(1),f.user(2),UUID.randomUUID().toString());
        String body=mutation(UUID.randomUUID().toString(),List.of(f.user(2)));
        require(f.call("/v1/groups/"+group+"/members",body,token).statusCode()==200,"add member after page");
        var tail=JSON.readTree(f.call(path+"&afterConversationId="+next.get("afterConversationId").asText()+"&afterMemberUserId="+next.get("afterMemberUserId").asText(),null,token).body());
        for(var item:tail.get("items"))require(!group.equals(item.get("conversationId").asText())||!f.user(2).equals(item.at("/member/user/userId").asText()),"new tuple before cursor appeared in tail");
        var rescan=JSON.readTree(f.call("/v1/conversations?requestId="+UUID.randomUUID(),null,token).body());
        boolean seen=false;
        for(var item:rescan.get("items"))if(group.equals(item.get("conversationId").asText())&&f.user(2).equals(item.at("/member/user/userId").asText()))seen=true;
        require(seen,"periodic rescan missed earlier inserted tuple");
    }

    HttpResponse<String> addFriend(String actor,String peer)throws Exception{
        var req=java.net.http.HttpRequest.newBuilder(URI.create(f.base+"/v1/friends/"+peer)).header("Authorization","Bearer "+f.tokens.get(actor))
            .PUT(java.net.http.HttpRequest.BodyPublishers.noBody()).build();
        return f.http.send(req,HttpResponse.BodyHandlers.ofString());
    }
    void friendAndLegacy(java.nio.file.Path root)throws Exception {
        f.prepareUsers();
        var fixtures=JSON.readTree(root.resolve("contracts/fixtures/auth-user-friend/negative.json").toFile()).get("scenarios");
        var cases=new HashMap<String,JsonNode>();fixtures.forEach(c->cases.put(c.get("id").asText(),c.get("steps").get(0).get("expected")));
        String a=f.user(1),b=f.user(2);
        for(String name:List.of("friend-target-not-found","friend-self-rejected")){
            var r=addFriend(a,name.contains("self")?a:UUID.randomUUID().toString());
            require(r.statusCode()==cases.get(name).get("status").asInt()&&cases.get(name).get("errorCode").equals(JSON.readTree(r.body()).at("/error/code")),name);
        }
        HttpResponse<String> first,reverse;
        var gate=new CyclicBarrier(2);
        try(var threads=Executors.newFixedThreadPool(2)){
            var x=threads.submit(()->{gate.await();return addFriend(a,b);});
            var y=threads.submit(()->{gate.await();return addFriend(b,a);});
            first=x.get(12,TimeUnit.SECONDS);reverse=y.get(12,TimeUnit.SECONDS);
        }
        require(Set.of(first.statusCode(),reverse.statusCode()).equals(Set.of(201,200)),"reverse concurrent adds");
        String conv=JSON.readTree(first.body()).get("directConversationId").asText();
        require(conv.equals(JSON.readTree(reverse.body()).get("directConversationId").asText()),"unique DIRECT");
        var duplicate=addFriend(a,b);
        require(duplicate.statusCode()==cases.get("duplicate-friendship-divergence-rejected").get("status").intValue()
            && !JSON.readTree(duplicate.body()).get("created").booleanValue(),"friend retry diverged");
        // Existing Sync data is consumed by unmodified clients from either profile.
        String sync=JSON.writeValueAsString(Map.of("syncVersion","1.0","type","sync.user.request","requestId",UUID.randomUUID(),"cursor","0","limit",100));
        var page=JSON.readTree(f.call("/v1/sync/user",sync,f.tokens.get(a)).body());
        require(page.get("events").size()==3 && !page.get("hasMore").booleanValue(),"legacy friend sync");
        f.db.update("DELETE FROM conversation_members WHERE conversation_id=?::uuid AND user_id=?::uuid",conv,b);
        var conflict=addFriend(a,b);
        require(conflict.statusCode()==cases.get("friendship-state-conflict").get("status").intValue()
            && JSON.readTree(conflict.body()).at("/error/code").equals(cases.get("friendship-state-conflict").get("errorCode")),"inconsistent friendship");
        System.out.println("DEFERRED_BY_HUMAN friend-add-authorization-denied (ADR-0004)");
    }
}


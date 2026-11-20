package im.platform.tests.im;

import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import im.platform.shared.authsupport.Config;
import im.platform.shared.authsupport.Tokens;
import org.springframework.jdbc.core.JdbcTemplate;
import java.net.URI;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.stream.StreamSupport;

public final class GroupFixtures {
    static final ObjectMapper JSON=new ObjectMapper();
    static final String TIME="2026-10-18T06:30:00Z";
    final HttpClient http=HttpClient.newHttpClient();
    final JdbcTemplate db;
    final Tokens codec;
    final String base;
    final String namespace=UUID.randomUUID().toString().substring(0,8);
    final Map<String,String> tokens=new HashMap<>();

    GroupFixtures(Config config,String base){db=new JdbcTemplate(config.database());codec=new Tokens(config.signingKey());this.base=base;}

    String local(String raw) {
        // Preserve fixture ordering and scoped equality while isolating each scenario's rows.
        return raw.replaceAll("(?<=[0-9])-0000-([48])000-", "-"+namespace.substring(0,4)+"-$1"+namespace.substring(4,7)+"-")
            .replaceAll("(?<=8000-)00000000000","0"+namespace+"00");
    }
    String user(int index){return local("10000000-0000-4000-8000-00000000000"+index);}
    String conversation(){return local("30000000-0000-4000-8000-000000000001");}
    static void require(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
    static List<String> values(JsonNode array){return StreamSupport.stream(array.spliterator(),false).map(JsonNode::textValue).toList();}
    String template(String raw){return local(raw).replace("\"alice\"","\"alice"+namespace+"\"").replace("\"bob\"","\"bob"+namespace+"\"").replace("\"carol\"","\"carol"+namespace+"\"");}
    void prepareUsers() throws Exception {
        for(int i=1;i<=4;i++) {
            String user=user(i),sid=UUID.randomUUID().toString();
            String name=List.of("alice","bob","carol","dave").get(i-1)+namespace;
            db.update("INSERT INTO users(user_id,username,display_name,password_hash) VALUES(?::uuid,?,?,?)",user,name,i==3?"Carol 非好友":"Same name","group-fixture");
            db.update("""
                INSERT INTO sessions(user_id,client_type,session_id,session_epoch,refresh_token_hash,status,device_id,expires_at)
                VALUES(?::uuid,'WEB',?::uuid,1,?,'ACTIVE','test',now()+interval '1 hour')
                """,user,sid,UUID.randomUUID().toString());
            long now=Instant.now().getEpochSecond();
            tokens.put(user,codec.sign(new Tokens.Claims(user,sid,"WEB",1,now,now+1800)));
        }
    }
    void friendship(String a,String b,String conv) {
        String low=a.compareTo(b)<0?a:b, high=a.equals(low)?b:a;
        db.update("INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by) VALUES(?::uuid,'DIRECT',?::uuid,?::uuid,?::uuid)",conv,low,high,a);
        db.update("INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id) VALUES(?::uuid,?::uuid,?::uuid)",low,high,conv);
        for(String member:List.of(low,high)) db.update("INSERT INTO conversation_members(conversation_id,user_id,role) VALUES(?::uuid,?::uuid,'MEMBER')",conv,member);
    }
    void seedGroup(String owner,String key,String conv,List<String> members){
        db.update("INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id,created_at) VALUES(?::uuid,'GROUP',?::uuid,?::uuid,?::timestamptz)",conv,owner,key,TIME);
        for(var member:members) db.update("INSERT INTO conversation_members(conversation_id,user_id,role,joined_at) VALUES(?::uuid,?::uuid,?,?::timestamptz)",conv,member,member.equals(owner)?"OWNER":"MEMBER",TIME);
    }
    void setup(JsonNode c) throws Exception {
        prepareUsers();
        var context=c.get("context");
        String actor=context.get("actorId").textValue();
        var request=c.get("request");
        var receipt=context.path("priorReceipt");
        String group=request.path("conversationId").asText(conversation());
        if(receipt.has("response")) group=receipt.path("response").get("conversationId").textValue();
        boolean direct="DIRECT".equals(context.path("kind").asText());
        for(var f:values(context.path("friendUserIds"))) friendship(actor,f,direct && f.equals(user(1))?group:UUID.randomUUID().toString());
        boolean createReceipt=receipt.path("status").asInt()==201;
        var members=values(context.path("activeMemberIds"));
        boolean missing=context.path("originalResultUnavailable").asBoolean();
        if(!direct && (!members.isEmpty()||missing)) {
            String owner=createReceipt||missing?actor:user(1);
            String key=createReceipt?receipt.get("response").get("requestId").textValue():missing?request.get("body").get("requestId").textValue():UUID.randomUUID().toString();
            seedGroup(owner,key,group,members);
        }
        if(context.has("ownConversationIds") && !context.get("ownConversationIds").isEmpty()) {
            var ids=new ArrayList<String>();
            for(var row:context.path("activeRows")) ids.add(row.get(1).textValue());
            seedGroup(user(1),UUID.randomUUID().toString(),group,ids);
        }
        if(receipt.has("response")) {
            var original=receipt.get("response");
            db.update("""
                INSERT INTO group_operation_receipts(actor_id,operation,request_id,conversation_id,target_user_ids,added_member_user_ids,created_at)
                VALUES(?::uuid,?,?::uuid,?::uuid,?::uuid[],?::uuid[],?::timestamptz)
                """,actor,createReceipt?"CREATE":"ADD",original.get("requestId").textValue(),group,"{"+String.join(",",values(receipt.get("targets")))+"}",
                "{"+String.join(",",values(original.get("addedMemberUserIds")))+"}",original.get("createdAt").textValue());
        }
    }

    String credential(String actor,String error) throws Exception {
        String token=tokens.get(actor);
        var c=codec.parse(token);
        return switch(error) {
            case "" -> token;
            case "AUTH_REQUIRED" -> null;
            case "AUTH_TOKEN_INVALID" -> "invalid-fixture-credential";
            case "AUTH_TOKEN_EXPIRED" -> codec.sign(new Tokens.Claims(actor,c.sessionId(),"WEB",1,c.issued()-7200,c.issued()-3600));
            case "AUTH_CLIENT_TYPE_MISMATCH" -> codec.sign(new Tokens.Claims(actor,c.sessionId(),"MOBILE",1,c.issued(),c.expires()));
            case "AUTH_SESSION_EPOCH_STALE" -> {db.update("UPDATE sessions SET session_epoch=2 WHERE user_id=?::uuid",actor);yield token;}
            case "AUTH_SESSION_REVOKED" -> {db.update("UPDATE sessions SET status='REVOKED' WHERE user_id=?::uuid",actor);yield token;}
            default -> throw new AssertionError("Uncovered fixture auth setup "+error);
        };
    }
    HttpResponse<String> call(String path,String body,String token)throws Exception{
        var req=HttpRequest.newBuilder(URI.create(base+path)).timeout(Duration.ofSeconds(10));
        if(token!=null) req.header("Authorization","Bearer "+token);
        if(body!=null) req.header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(body));
        return http.send(req.build(),HttpResponse.BodyHandlers.ofString());
    }
    String counts(){
        return db.queryForObject("""
            SELECT concat_ws(',',(SELECT count(*) FROM conversations),(SELECT count(*) FROM conversation_members),
            (SELECT count(*) FROM group_operation_receipts),(SELECT count(*) FROM user_sync_events),(SELECT count(*) FROM outbox_events))
            """,String.class);
    }
    static void normalizeTimes(JsonNode node) {
        if(node.isArray()) {node.forEach(GroupFixtures::normalizeTimes);return;}
        if(!node.isObject()) return;
        node.fields().forEachRemaining(e -> {
            if(Set.of("joinedAt","createdAt").contains(e.getKey()))
                ((ObjectNode)node).put(e.getKey(),Instant.parse(e.getValue().textValue()).toString());
            else normalizeTimes(e.getValue());
        });
    }
    void exchange(JsonNode spec)throws Exception{
        var c=JSON.readTree(template(spec.toString()));
        setup(c);
        var context=c.get("context"); var request=c.get("request");
        String token=credential(context.get("actorId").textValue(),context.path("authError").asText());
        String body=null,path;
        if(request.has("query")){
            var query=new StringJoiner("&"); request.get("query").fields().forEachRemaining(e->query.add(e.getKey()+"="+e.getValue().asText()));
            path="/v1/conversations?"+query;
        } else {
            body=request.get("body").toString();
            if(request.has("bodyBytes")) body+=" ".repeat(request.get("bodyBytes").asInt()-body.getBytes(java.nio.charset.StandardCharsets.UTF_8).length);
            path=request.has("conversationId")?"/v1/groups/"+request.get("conversationId").asText()+"/members":"/v1/groups";
            if(request.path("unknownQuery").asBoolean())path+="?unknown=1";
        }
        String before=counts();
        var r=call(path,body,token);
        int expected=c.get("status").asInt();
        String id=c.get("id").textValue();
        if(expected>=500) {
            // The canonical verifier accepts the 5xx class for unknown missing receipts;
            // a Gateway may observe a Core abort before receiving response headers.
            require(r.statusCode()>=500 && r.statusCode()<600,id+" missing original result must fail");
            require(!r.body().contains("GROUP_REQUEST_CONFLICT") && !r.body().contains("addedMemberUserIds"),id+" fabricated result");
        } else require(r.statusCode()==expected,id+" HTTP expected "+expected+" got "+r.statusCode());
        if(expected>=400||request.has("query")||context.has("priorReceipt")) require(counts().equals(before),id+" unexpected database effects");
        if(expected>=500) return;
        require(r.headers().firstValue("Cache-Control").orElse("").contains("no-store"),id+" missing no-store");
        var actual=(ObjectNode)JSON.readTree(r.body());
        var want=(ObjectNode)c.get("response").deepCopy();
        if(expected>=400) {
            require(actual.path("error").path("message").isTextual()&&!actual.path("error").get("message").textValue().isEmpty(),id+" missing failure message");
            ((ObjectNode)want.get("error")).set("message",actual.get("error").get("message"));
        } else if(!request.has("query")&&!context.has("priorReceipt")) {
            String conv=actual.path("conversationId").asText();
            String stamp=actual.path("createdAt").asText();
            UUID.fromString(conv);Instant.parse(stamp);
            if(!request.has("conversationId")) want.put("conversationId",conv);
            want.put("createdAt",stamp);
            var receipt=db.queryForMap("SELECT added_member_user_ids::text,created_at FROM group_operation_receipts WHERE conversation_id=?::uuid AND request_id=?::uuid AND actor_id=?::uuid",conv,want.path("requestId").asText(),context.get("actorId").textValue());
            require(Instant.parse(stamp).equals(((java.sql.Timestamp)receipt.get("created_at")).toInstant())&&receipt.get("added_member_user_ids").equals("{"+String.join(",",values(actual.path("addedMemberUserIds")))+"}"),id+" original receipt disagrees");
            int active=db.queryForObject("SELECT count(*) FROM conversation_members WHERE conversation_id=?::uuid AND left_at IS NULL",Integer.class,conv);
            int events=actual.get("addedMemberUserIds").isEmpty()?0:active*2;
            require(db.queryForObject("SELECT count(*) FROM user_sync_events WHERE payload->>'subjectId'=?",Integer.class,conv)==events,id+" wrong sync event count");
            require(db.queryForObject("SELECT count(*) FROM outbox_events WHERE payload->'event'->>'subjectId'=?",Integer.class,conv)==events,id+" wrong outbox count");
        }
        normalizeTimes(want); normalizeTimes(actual);
        require(want.equals(actual),id+" observed body differs: "+actual);
    }
    public static void main(String[] args)throws Exception{
        var fixtures=JSON.readTree(Path.of(args[1],"contracts/fixtures/group/exchanges.json").toFile());
        var config=Config.read(args[2]);
        for(var c:fixtures.get("valid")) {
            new GroupFixtures(config,args[0]).exchange(c);
            System.out.println("PASS group "+c.get("id").textValue());
        }
        var vectors=JSON.readTree(Path.of(args[1],"contracts/fixtures/group/transaction-vectors.json").toFile());
        for(var vector:vectors.get("vectors")) {
            var run=new GroupTransactions(config,args[0]);
            String name=vector.get("id").textValue();
            switch(name) {
                case "concurrent-create-same-key","concurrent-add-same-key","overlap-different-actor-request" -> run.concurrent(vector);
                case "write-failure-rollback" -> run.rollback(vector);
                case "response-loss-before-commit","response-loss-after-commit" -> run.lost(vector,name.contains("before"));
                case "concurrent-list-insert-before-cursor" -> run.snapshotInsert();
                case "compatibility-old-client" -> run.friendAndLegacy(Path.of(args[1]));
                default -> throw new AssertionError("Uncovered group transaction vector "+name);
            }
            System.out.println("PASS group "+name);
        }
        MessageFixtures.run(config,args[0],Path.of(args[1]));
    }
}

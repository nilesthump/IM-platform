package im.platform.tests.im;

import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.ObjectNode;
import im.platform.shared.authsupport.Config;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import static im.platform.tests.im.GroupFixtures.*;

final class MessageFixtures {
    static final class Peer implements WebSocket.Listener,AutoCloseable {
        final BlockingQueue<JsonNode> frames=new LinkedBlockingQueue<>();
        final StringBuilder buffer=new StringBuilder();
        final WebSocket socket;
        Peer(String base,String token)throws Exception{
            socket=HttpClient.newHttpClient().newWebSocketBuilder().connectTimeout(Duration.ofSeconds(5))
                .buildAsync(URI.create(base.replace("http://","ws://")+"/v1/ws"),this).get(6,TimeUnit.SECONDS);
            send(frame("auth.bind",UUID.randomUUID().toString(),Map.of("accessToken",token)));
            require(next().at("/payload/status").asText().equals("bound"),"fixture peer bind");
        }
        @Override public void onOpen(WebSocket ws){ws.request(1);}
        @Override public CompletionStage<?> onText(WebSocket ws,CharSequence text,boolean last){
            buffer.append(text);
            if(last) {
                try{frames.add(JSON.readTree(buffer.toString()));}
                catch(com.fasterxml.jackson.core.JsonProcessingException failure){throw new AssertionError(failure);}
                buffer.setLength(0);
            }
            ws.request(1);
            return CompletableFuture.completedFuture(null);
        }
        void send(JsonNode event)throws Exception {socket.sendText(event.toString(),true).get(4,TimeUnit.SECONDS);}
        JsonNode next()throws Exception{
            var value=frames.poll(7,TimeUnit.SECONDS);
            require(value!=null,"expected socket frame");
            return value;
        }
        void quiet()throws Exception{require(frames.poll(500,TimeUnit.MILLISECONDS)==null,"wrong-recipient delivery");}
        @Override public void close(){socket.abort();}
    }
    static JsonNode frame(String type,String id,Object payload) {
        return JSON.valueToTree(Map.of("protocolVersion","1.0","type",type,"requestId",id,"payload",payload));
    }
    static JsonNode send(Peer sender,JsonNode fixture,String conversation,String id)throws Exception{
        var sent=(ObjectNode)fixture.deepCopy();sent.put("requestId",id);
        ((ObjectNode)sent.get("payload")).put("conversationId",conversation);
        sender.send(sent);
        var ack=sender.next();
        require(ack.path("type").asText().equals("message.ack") && ack.path("requestId").asText().equals(id) &&
            ack.at("/payload/status").asText().equals("committed")&&ack.at("/payload/conversationId").asText().equals(conversation),"durable ACK identity");
        return ack.get("payload");
    }
    static void run(Config config,String base,Path root)throws Exception{
        var f=new GroupFixtures(config,base);f.prepareUsers();
        var all=new HashMap<String,JsonNode>();
        var cases=JSON.readTree(root.resolve("contracts/fixtures/websocket/golden.json").toFile()).get("scenarios");
        cases.forEach(c->all.put(c.get("id").asText(),c));
        String group=f.conversation(),other=UUID.randomUUID().toString(),actor=f.user(1),recipient=f.user(2);
        f.seedGroup(actor,UUID.randomUUID().toString(),group,List.of(actor,recipient));
        f.seedGroup(actor,UUID.randomUUID().toString(),other,List.of(actor,f.user(3)));
        int target=all.get("group-single-message").at("/given/memberCount").intValue();
        f.db.update("""
            WITH users_added AS (
              INSERT INTO users(user_id,username,display_name,password_hash)
              SELECT gen_random_uuid(),?||i,'offline','fixture-only' FROM generate_series(1,?) n(i) RETURNING user_id
            ) INSERT INTO conversation_members(conversation_id,user_id,role) SELECT ?::uuid,user_id,'MEMBER' FROM users_added
            """,f.namespace,target-2,group);
        var socketFixture=all.get("group-single-message").at("/steps/0/in");
        try(var sender=new Peer(base,f.tokens.get(actor));
            var receiver=new Peer(base,f.tokens.get(recipient));
            var actorPeer=new Peer(base,f.tokens.get(actor));
            var outsider=new Peer(base,f.tokens.get(f.user(4)))) {
            String id=UUID.randomUUID().toString();
            var first=send(sender,socketFixture,group,id);
            var event=receiver.next();
            require(first.path("seq").intValue()==1 && first.get("messageId").equals(event.at("/payload/messageId")) &&
                event.at("/payload/content").equals(socketFixture.at("/payload/content"))&&actorPeer.next().equals(event),"all recipient sessions");
            require(f.db.queryForObject("SELECT count(*) FROM messages WHERE conversation_id=?::uuid",Integer.class,group)==1 &&
                f.db.queryForObject("SELECT count(*) FROM outbox_events WHERE conversation_id=?::uuid AND event_type='message.created'",Integer.class,group)==1,
                "group creates exactly one message and Outbox");
            sender.quiet();outsider.quiet();
            JsonNode second=send(sender,all.get("same-request-different-conversation").at("/steps/1/in"),other,id);
            require(second.get("seq").asInt()==1 && !first.get("messageId").equals(second.get("messageId")),"conversation-scoped identity");
            require(actorPeer.next().at("/payload/conversationId").asText().equals(other),"other sender session");
            receiver.quiet();outsider.quiet();
            String id2=UUID.randomUUID().toString();
            var next=send(sender,socketFixture,group,id2);
            var secondEvent=receiver.next();
            require(next.get("messageId").equals(secondEvent.at("/payload/messageId")),"second durable message");
            actorPeer.next();
            try(var late=new Peer(base,f.tokens.get(recipient));var nats=io.nats.client.Nats.connect(config.natsUrl)){
                require(all.get("out-of-order-fanout").at("/steps/0/in/payload/seq").asInt()==2 &&
                    all.get("duplicate-fanout").at("/expect/clientMaterializations").asInt()==1,"fixture availability");
                for(var delivery:List.of(secondEvent,secondEvent,event)) nats.publish("message.created."+recipient,delivery.toString().getBytes(StandardCharsets.UTF_8));
                nats.flush(Duration.ofSeconds(2));
                var two=late.next();var repeated=late.next();
                require(two.equals(secondEvent)&&two.equals(repeated)&&late.next().equals(event),"out-of-order and repeated delivery");
                String sync=JSON.writeValueAsString(Map.of("syncVersion","1.0","type","sync.conversation.request","requestId",UUID.randomUUID(),"conversationId",group,"afterSeq",0,"limit",100));
                var page=JSON.readTree(f.call("/v1/sync/conversation",sync,f.tokens.get(recipient)).body());
                var records=page.get("messages");
                require(records.size()==2 && records.get(0).path("messageId").equals(first.get("messageId")) && records.get(1).path("messageId").equals(next.get("messageId")) &&
                    records.get(0).path("seq").asInt()==1 && records.get(1).path("seq").asInt()==2 && !page.path("hasMore").booleanValue(),"durable history convergence");
            }
        }
        System.out.println("PASS group-single-message / same-request-different-conversation / wrong-conversation-fanout / duplicate-fanout / out-of-order-fanout");
    }
}


package im.platform.tests.im;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.sun.net.httpserver.HttpServer;
import im.platform.gateway.auth.Gateway;
import im.platform.core.auth.CoreAuth;
import jakarta.servlet.ServletInputStream;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.TransactionSystemException;
import org.springframework.transaction.support.DefaultTransactionStatus;
import org.springframework.transaction.support.TransactionTemplate;
import im.platform.shared.authsupport.Config;
import org.springframework.web.socket.*;
import java.lang.reflect.Proxy;
import java.net.*;
import java.net.http.*;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
import static im.platform.tests.im.GroupFixtures.*;

/** Drop or damage the private confirmation only after the real Java Core has committed. */
public final class MessageOutcomeProbe {
    public static void main(String[] args)throws Exception {
        var config=Config.read(args[0]);
        var f=new GroupFixtures(config,args[1]);
        f.prepareUsers();
        var actor=f.user(1);
        var conv=f.conversation();
        f.seedGroup(actor,UUID.randomUUID().toString(),conv,List.of(actor,f.user(2)));
        var original=new AtomicReference<JsonNode>();
        var fault=new AtomicReference<String>();
        URI upstream=URI.create(config.coreUrl+"/__core/message");
        var relay=HttpServer.create(new InetSocketAddress("127.0.0.1",0),0);
        relay.createContext("/__core/message",exchange->{
            try(exchange) {
                var request=HttpRequest.newBuilder(upstream).header("Content-Type","application/json")
                    .header("Authorization",exchange.getRequestHeaders().getFirst("Authorization"))
                    .POST(HttpRequest.BodyPublishers.ofByteArray(exchange.getRequestBody().readAllBytes())).build();
                HttpResponse<byte[]> response;
                try {response=f.http.send(request,HttpResponse.BodyHandlers.ofByteArray());}
                catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new java.io.IOException(interrupted);}
                require(response.statusCode()==200,"Core response");
                var ack=(ObjectNode)JSON.readTree(response.body());
                require("committed".equals(ack.at("/payload/status").asText()),"real committed result");
                original.compareAndSet(null,ack.deepCopy());
                require(original.get().equals(ack),"Core replay identity");
                String damage=fault.get();
                if("lost".equals(damage)) return;
                if("protocolVersion".equals(damage)) ack.remove(damage);
                else if("conversationId".equals(damage)) ((ObjectNode)ack.get("payload")).put(damage,UUID.randomUUID().toString());
                else if(damage!=null) ((ObjectNode)ack.get("payload")).remove(damage);
                byte[] body=JSON.writeValueAsBytes(ack);
                exchange.sendResponseHeaders(200,body.length);
                exchange.getResponseBody().write(body);
            }
        });
        relay.start();
        try {
            config.coreUrl="http://127.0.0.1:"+relay.getAddress().getPort();
            var gateway=new Gateway(config);
            try(AutoCloseable shutdown=gateway::destroy) {
                var ctor=Class.forName(Gateway.class.getName()+"$Socket").getDeclaredConstructor(Gateway.class);
                ctor.setAccessible(true);
                var handler=(WebSocketHandler)ctor.newInstance(gateway);
                var attributes=new HashMap<String,Object>();
                var sent=new ArrayList<JsonNode>();
                var socket=(WebSocketSession)Proxy.newProxyInstance(WebSocketSession.class.getClassLoader(),
                    new Class<?>[]{WebSocketSession.class},(peer,method,values)->switch(method.getName()){
                        case "hashCode" -> System.identityHashCode(peer);
                        case "equals" -> peer==values[0];
                        case "getAttributes" -> attributes;
                        case "isOpen" -> true;
                        case "sendMessage" -> {sent.add(JSON.readTree(((TextMessage)values[0]).getPayload()));yield null;}
                        case "close" -> null;
                        default -> throw new AssertionError(method.getName());
                    });
                var bind=MessageFixtures.frame("auth.bind",UUID.randomUUID().toString(),Map.of("accessToken",f.tokens.get(actor)));
                handler.handleMessage(socket,new TextMessage(bind.toString()));
                require(sent.removeFirst().at("/payload/status").asText().equals("bound"),"bind");
                String id=UUID.randomUUID().toString();
                var frame=MessageFixtures.frame("message.send",id,Map.of("conversationId",conv,"content",Map.of("kind","TEXT","text","test")));
                var send=new TextMessage(frame.toString());
                for(var damage:List.of("lost","protocolVersion","conversationId","messageId","seq","createdAt")) {
                    fault.set(damage);
                    try {handler.handleMessage(socket,send);throw new AssertionError("Confirmed "+damage);}
                    catch(java.io.IOException lost){if(!damage.equals("lost")) throw lost;}
                    catch(IllegalStateException invalid){
                        if(damage.equals("lost") || !(invalid.getMessage().equals("Invalid Core message acknowledgement envelope") ||
                            invalid.getMessage().equals("Incomplete or unrelated Core commit confirmation"))) throw invalid;
                    }
                    require(sent.isEmpty(),"unconfirmed outcome");
                }
                fault.set(null);
                handler.handleMessage(socket,send);
                require(sent.size()==1 && sent.getFirst().equals(original.get()),"retry returns original committed ACK");
                JSON.writeValue(Path.of(args[2]).toFile(),sent.getFirst());
                require(f.db.queryForObject("SELECT count(*) FROM messages WHERE conversation_id=?::uuid AND request_id=?::uuid",
                    Integer.class,conv,id)==1 && f.db.queryForObject("SELECT count(*) FROM outbox_events WHERE conversation_id=?::uuid AND event_type='message.created'",
                    Integer.class,conv)==1,"one durable message and event");
            }
        } finally {relay.stop(0);}
        unknownDatabaseCommit(config,f,actor,conv);
        overlap(new GroupFixtures(config,args[1]));
        sameSlotLogin(f,actor,conv);
        // Persist the authoritative retirement with no live notification.
        var idle=f.user(4);
        try(var receiver=new MessageFixtures.Peer(f.base,f.tokens.get(idle));
            var db=config.database().getConnection()) {
            var claims=f.codec.parse(f.tokens.get(idle));
            db.setAutoCommit(false);
            try(var retire=db.prepareStatement("UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL WHERE session_id=?::uuid");
                var history=db.prepareStatement("INSERT INTO user_sync_events(user_id,event_type,payload) VALUES(?::uuid,'session.revoked',?::jsonb)")) {
                retire.setString(1,claims.sessionId());
                require(retire.executeUpdate()==1,"fixture session");
                history.setString(1,idle);
                history.setString(2,JSON.writeValueAsString(Map.of("sessionId",claims.sessionId(),"reason","LOGOUT")));
                history.executeUpdate();
                db.commit();
            }
            var frame=receiver.next();
            require("session.revoked".equals(frame.path("type").asText()) &&
                claims.sessionId().equals(frame.at("/payload/sessionId").asText()) &&
                "LOGOUT".equals(frame.at("/payload/reason").asText()),"periodic Session retirement with durable reason");
        }
        System.out.println("JAVA lost/incomplete confirmations, retry identity and overlapping member add/send PASS");
    }

    // A real commit succeeds, but the transaction manager observes SQLSTATE 08007.
    // Drive the same Core handler twice and compare the retry with persisted identity.
    private static void unknownDatabaseCommit(Config config,GroupFixtures f,String actor,String conv)throws Exception {
        var core=new CoreAuth(config);
        var transaction=CoreAuth.class.getDeclaredField("tx");
        transaction.setAccessible(true);
        var template=(TransactionTemplate)transaction.get(core);
        var manager=template.getTransactionManager();
        var unknown=new TransactionSystemException("commit outcome unknown",new java.sql.SQLException("unknown","08007"));
        template.setTransactionManager(new DataSourceTransactionManager(config.database()){
            @Override protected void doCommit(DefaultTransactionStatus status){
                super.doCommit(status);
                throw unknown;
            }
        });
        String id=UUID.randomUUID().toString();
        byte[] body=JSON.writeValueAsBytes(MessageFixtures.frame("message.send",id,
            Map.of("conversationId",conv,"content",Map.of("kind","TEXT","text","unknown database outcome"))));
        var request=(HttpServletRequest)Proxy.newProxyInstance(HttpServletRequest.class.getClassLoader(),
            new Class<?>[]{HttpServletRequest.class},(proxy,method,args)->switch(method.getName()){
                case "getHeader" -> "Bearer "+f.tokens.get(actor);
                case "getInputStream" -> new ServletInputStream(){
                    final java.io.ByteArrayInputStream input=new java.io.ByteArrayInputStream(body);
                    public int read(){return input.read();}
                    public boolean isFinished(){return input.available()==0;}
                    public boolean isReady(){return true;}
                    public void setReadListener(jakarta.servlet.ReadListener unused){throw new AssertionError();}
                };
                default -> throw new AssertionError(method.getName());
            });
        try {core.message(request);throw new AssertionError("Unknown database commit produced an ACK");}
        catch(TransactionSystemException failure){if(failure!=unknown) throw failure;}
        finally {template.setTransactionManager(manager);}
        var persisted=f.db.queryForMap("SELECT server_message_id,seq,created_at FROM messages WHERE conversation_id=?::uuid AND request_id=?::uuid",conv,id);
        JsonNode ack=JSON.valueToTree(core.message(request));
        require("committed".equals(ack.at("/payload/status").asText()) && id.equals(ack.get("requestId").asText()) &&
            persisted.get("server_message_id").toString().equals(ack.at("/payload/messageId").asText()) &&
            persisted.get("seq").equals(ack.at("/payload/seq").longValue()) &&
            ((java.sql.Timestamp)persisted.get("created_at")).toInstant().equals(java.time.Instant.parse(ack.at("/payload/createdAt").asText())),
            "unknown database outcome replays persisted identity");
    }

    private static void overlap(GroupFixtures f)throws Exception {
        f.prepareUsers();
        String owner=f.user(1),member=f.user(2),conv=f.conversation();
        f.seedGroup(owner,UUID.randomUUID().toString(),conv,List.of(owner,member));
        f.friendship(owner,member,UUID.randomUUID().toString());
        try(var peer=new MessageFixtures.Peer(f.base,f.tokens.get(member));
            var fence=f.db.getDataSource().getConnection();var pool=Executors.newSingleThreadExecutor()) {
            int pid=lockConversation(fence,conv);
            var add=pool.submit(()->f.call("/v1/groups/"+conv+"/members",
                GroupTransactions.mutation(UUID.randomUUID().toString(),List.of(member)),f.tokens.get(owner)));
            try {
                awaitWaiters(f,pid,1);
                peer.send(MessageFixtures.frame("message.send",UUID.randomUUID().toString(),Map.of("conversationId",conv,
                    "content",Map.of("kind","TEXT","text","overlap"))));
                awaitWaiters(f,pid,2);
            } finally {fence.rollback();}
            var response=add.get(10,TimeUnit.SECONDS);
            require(response.statusCode()==200 && JSON.readTree(response.body()).get("addedMemberUserIds").isEmpty(),"no-op add");
            require("committed".equals(peer.next().at("/payload/status").asText()),"overlapping send");
        }
    }

    private static int lockConversation(java.sql.Connection fence,String conv)throws Exception {
        fence.setAutoCommit(false);
        try(var q=fence.prepareStatement("SELECT pg_backend_pid() FROM conversations WHERE conversation_id=?::uuid FOR UPDATE")) {
            q.setString(1,conv);
            try(var row=q.executeQuery()){require(row.next(),"fixture group");return row.getInt(1);}
        }
    }

    private static void sameSlotLogin(GroupFixtures f,String actor,String conv)throws Exception {
        String password=UUID.randomUUID().toString();
        String username=f.db.queryForObject("UPDATE users SET password_hash=? WHERE user_id=?::uuid RETURNING username",
            String.class,im.platform.shared.authsupport.PasswordHash.create(password),actor);
        String credentials=JSON.writeValueAsString(Map.of("username",username,"password",password,"clientType","WEB",
            "deviceId","replacement","clientVersion","1","protocolVersion","1"));
        String id=UUID.randomUUID().toString();
        try(var sender=new MessageFixtures.Peer(f.base,f.tokens.get(actor));
            var fence=f.db.getDataSource().getConnection();var pool=Executors.newSingleThreadExecutor()) {
            int pid=lockConversation(fence,conv);
            Future<HttpResponse<String>> login;
            try {
                sender.send(MessageFixtures.frame("message.send",id,Map.of("conversationId",conv,
                    "content",Map.of("kind","TEXT","text","before same-slot replacement"))));
                awaitWaiters(f,pid,1);
                login=pool.submit(()->f.call("/v1/auth/login",credentials,null));
                awaitWaiters(f,pid,2);
            } finally {fence.rollback();}
            var response=login.get(10,TimeUnit.SECONDS);
            require(response.statusCode()==200 && JSON.readTree(response.body()).path("replacedExistingSession").asBoolean(),
                "same-slot login must replace the sending session");
            require(f.db.queryForObject("""
                SELECT count(*) FROM messages m JOIN outbox_events e ON e.message_id=m.server_message_id
                WHERE m.conversation_id=?::uuid AND m.request_id=?::uuid AND e.event_type='message.created'
                """,Integer.class,conv,id)==1,"overlapping send must commit before replacement");
        }
    }

    private static void awaitWaiters(GroupFixtures f,int pid,int target)throws Exception {
        long limit=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
        do {
            int count=f.db.queryForObject("""
                WITH RECURSIVE waiting(pid) AS (
                  SELECT ?::integer UNION
                  SELECT a.pid FROM pg_stat_activity a JOIN waiting w ON w.pid=ANY(pg_blocking_pids(a.pid))
                ) SELECT count(*)-1 FROM waiting
                """,Integer.class,pid);
            if(count>=target) return;
            Thread.sleep(20);
        } while(System.nanoTime()<limit);
        throw new AssertionError("Concurrent operations did not reach conversation lock");
    }
}

package im.platform.gateway.auth;
import im.platform.shared.authsupport.*;
import com.fasterxml.jackson.databind.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.socket.*;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import org.springframework.web.socket.config.annotation.*;
import org.springframework.web.socket.server.HandshakeInterceptor;
import org.springframework.http.server.*;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.DisposableBean;
import io.nats.client.Nats;
import io.nats.client.Connection;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.time.Instant;
import java.time.Duration;
import java.sql.Timestamp;
import java.io.IOException;
import java.io.UncheckedIOException;

@SpringBootConfiguration
@EnableAutoConfiguration(exclude=DataSourceAutoConfiguration.class)
@EnableWebSocket
@RestController
public class Gateway implements WebSocketConfigurer,DisposableBean {
    private static final ObjectMapper JSON=new ObjectMapper().enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);
    private final Config config;
    private final JdbcTemplate db;
    private final Tokens tokens;
    private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    private final Map<WebSocketSession,Tokens.Claims> bound=new ConcurrentHashMap<>();
    private final Connection nats;
    private final Thread events;
    private final Thread messages;
    private volatile boolean stopping;
    public Gateway(Config config)throws IOException,InterruptedException {
        this.config=config;db=new JdbcTemplate(config.database());tokens=new Tokens(config.signingKey());
        nats=Nats.connect(config.natsUrl);var subscription=nats.subscribe("session.revoked");
        events=Thread.ofPlatform().name("session-notifications").unstarted(()->{
            try{while(!stopping){var message=subscription.nextMessage(Duration.ofSeconds(1));
                if(message!=null){JsonNode b=JSON.readTree(message.getData());
                    if(b==null||!b.path("sessionId").isTextual()||!b.path("reason").isTextual()||!Set.of("REPLACED","LOGOUT","REVOKED").contains(b.path("reason").textValue()))throw new IllegalStateException("Invalid committed session event");
                    revoke(b.get("sessionId").textValue(),b.get("reason").textValue());
                }
            }}catch(InterruptedException interrupted){if(!stopping){Thread.currentThread().interrupt();throw new IllegalStateException(interrupted);}}
            catch(IOException failure){throw new UncheckedIOException(failure);}
        });
        var deliveries=nats.subscribe("message.created.*");
        messages=Thread.ofPlatform().name("message-notifications").unstarted(()->{
            try {
                long lastCheck=System.nanoTime();
                while(!stopping) {
                    var message=deliveries.nextMessage(Duration.ofSeconds(1));
                    if(System.nanoTime()-lastCheck>=Duration.ofSeconds(1).toNanos()) {
                        reconcileSessions();
                        lastCheck=System.nanoTime();
                    }
                    if(message!=null) deliver(message.getSubject().substring("message.created.".length()),JSON.readTree(message.getData()));
                }
            } catch(InterruptedException interrupted) {
                if(!stopping){Thread.currentThread().interrupt();throw new IllegalStateException(interrupted);}
            } catch(IOException failure){throw new UncheckedIOException(failure);}
        });
        messages.start();
        events.start();
    }
    @Override public void destroy()throws Exception{
        stopping=true;
        events.interrupt(); messages.interrupt();
        try(nats; AutoCloseable peers=this::closeBoundPeers){
            events.join(); messages.join();
        }
    }
    private void closeBoundPeers()throws IOException{
        Throwable first=null;
        for(var socket:bound.keySet()){
            try{socket.close();}
            catch(IOException|RuntimeException|Error failure){
                if(first==null)first=failure;
                else if(first!=failure)first.addSuppressed(failure);
            }
        }
        if(first instanceof IOException io)throw io;
        if(first instanceof RuntimeException runtime)throw runtime;
        if(first instanceof Error error)throw error;
    }
    @RequestMapping("/__infra/health") public String health(){return "profile=java role=gateway";}
    @RequestMapping({"/v1/auth/**","/v1/users/**","/v1/friends","/v1/friends/*","/v1/groups","/v1/groups/*/members","/v1/conversations","/v1/sync/user","/v1/sync/conversation"})
    public ResponseEntity<byte[]> proxy(HttpServletRequest r)throws IOException,InterruptedException {
        URI target=URI.create(config.coreUrl+r.getRequestURI()+(r.getQueryString()==null?"":"?"+r.getQueryString()));
        var stream=r.getInputStream();
        var body=HttpRequest.BodyPublishers.ofInputStream(()->stream);
        HttpRequest.Builder request=HttpRequest.newBuilder(target).timeout(Duration.ofSeconds(10)).method(r.getMethod(),body);
        for(String h:List.of("Authorization","Cookie","Content-Type"))if(r.getHeader(h)!=null)request.header(h,r.getHeader(h));
        var result=client.send(request.build(),HttpResponse.BodyHandlers.ofByteArray());
        var response=ResponseEntity.status(result.statusCode());
        for(String h:List.of("Content-Type","Cache-Control","Set-Cookie"))for(String value:result.headers().allValues(h))response.header(h,value);
        return response.body(result.body());
    }
    @Override public void registerWebSocketHandlers(WebSocketHandlerRegistry registry){
        registry.addHandler(new Socket(),"/v1/ws").setAllowedOrigins(config.publicOrigin==null?new String[]{"http://tauri.localhost"}:new String[]{"http://tauri.localhost",config.publicOrigin}).addInterceptors(new HandshakeInterceptor(){
            public boolean beforeHandshake(ServerHttpRequest r,ServerHttpResponse response,WebSocketHandler h,Map<String,Object> attributes){if(r.getURI().getRawQuery()!=null){response.setStatusCode(org.springframework.http.HttpStatus.BAD_REQUEST);return false;}return true;}
            public void afterHandshake(ServerHttpRequest r,ServerHttpResponse response,WebSocketHandler h,Exception error){}
        });
    }
    private static Map<String,Object> frame(String type,String request,Object payload){return Map.of("protocolVersion","1.0","type",type,"requestId",request,"payload",payload);}
    private static void send(WebSocketSession socket,Object value)throws IOException {
        String json=JSON.writeValueAsString(value);
        synchronized(socket){socket.sendMessage(new TextMessage(json));}
    }
    @SuppressWarnings("unchecked")
    private static Set<String> origins(WebSocketSession socket) {
        return (Set<String>)socket.getAttributes().get("im.origins");
    }
    private static String originKey(JsonNode payload,String request) {
        return payload.path("conversationId").asText("").toLowerCase(Locale.ROOT)+":"+request.toLowerCase(Locale.ROOT);
    }
    private static final java.util.regex.Pattern WIRE_TIMESTAMP = java.util.regex.Pattern.compile(
        "(?!0000)[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt](?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]" +
        "(?:[.][0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])");

    private static void checkCommittedTimestamp(JsonNode value) {
        String timestamp=value.textValue();
        if(timestamp==null || !WIRE_TIMESTAMP.matcher(timestamp).matches())
            throw new IllegalStateException("Invalid committed message timestamp");
        java.time.LocalDate.parse(timestamp.substring(0,10));
    }

    private static boolean canonicalId(JsonNode id) {
        return id.isTextual() && id.textValue().matches("[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}");
    }
    private static void checkCommittedMessage(JsonNode event) {
        if(event==null || !event.isObject() || event.size()!=4 || !canonicalId(event.path("requestId")) ||
            !"message.created".equals(event.path("type").textValue()) || !"1.0".equals(event.path("protocolVersion").textValue()))
            throw new IllegalStateException("Invalid committed message envelope");
        var payload=event.path("payload");
        var content=payload.path("content");
        String text=content.path("text").textValue();
        if(!payload.isObject() || payload.size()!=6 || !canonicalId(payload.path("conversationId")) ||
            !canonicalId(payload.path("messageId")) || !canonicalId(payload.path("senderId")) ||
            !payload.path("seq").isIntegralNumber() || payload.get("seq").bigIntegerValue().signum()<=0 ||
            !content.isObject() || content.size()!=2 ||
            !"TEXT".equals(content.path("kind").textValue()) || text==null || text.isEmpty() ||
            text.codePointCount(0,text.length())>4096)
            throw new IllegalStateException("Invalid committed message payload");
        checkCommittedTimestamp(payload.path("createdAt"));
    }
    private void deliver(String recipient,JsonNode event)throws IOException {
        checkCommittedMessage(event);
        var message=new TextMessage(JSON.writeValueAsString(event));
        var payload=event.get("payload");
        String key=originKey(payload,event.get("requestId").textValue());
        for(var entry:bound.entrySet()) {
            var socket=entry.getKey();
            var claims=entry.getValue();
            if(!recipient.equals(claims.userId())) continue;
            synchronized(socket) {
                if(!claims.equals(bound.get(socket)) || claims.expires()<=Instant.now().getEpochSecond() || !socket.isOpen()) continue;
                if(recipient.equals(payload.get("senderId").textValue()) && origins(socket).contains(key)) continue;
                try {socket.sendMessage(message);}
                catch(IOException disconnected) {
                    bound.remove(socket,claims);
                    closeRevoked(socket);
                } catch(IllegalStateException closed) {
                    if(socket.isOpen()) throw closed;
                    bound.remove(socket,claims);
                }
            }
        }
    }
    private void reconcileSessions()throws IOException {
        for(var claims:new HashSet<>(bound.values())) {
            try {
                validateSession(claims);
            } catch(ApiFailure retired) {
                var rows=db.queryForList("""
                    SELECT payload->>'reason' FROM user_sync_events
                    WHERE user_id=? AND event_type='session.revoked' AND payload->>'sessionId'=?
                    ORDER BY cursor_id DESC LIMIT 1
                    """,String.class,UUID.fromString(claims.userId()),claims.sessionId());
                String reason=rows.isEmpty()?"REVOKED":rows.getFirst();
                if(!Set.of("REPLACED","LOGOUT","REVOKED").contains(reason))
                    throw new IllegalStateException("Invalid persisted session revocation reason");
                revoke(claims.sessionId(),reason);
            }
        }
    }
    private void revoke(String sid,String reason)throws IOException {
        for(var entry:bound.entrySet())if(entry.getValue().sessionId().equals(sid)){
            WebSocketSession socket=entry.getKey();
            synchronized(socket){
                if(!bound.remove(socket,entry.getValue()))continue;
                try(java.io.Closeable retirement=()->closeRevoked(socket)){
                    if(!socket.isOpen())continue;
                    var message=new TextMessage(JSON.writeValueAsString(frame("session.revoked",UUID.randomUUID().toString(),Map.of("sessionId",sid,"reason",reason))));
                    try{
                        socket.sendMessage(message);
                    }catch(IOException disconnected){
                        // Delivery failed on this transport. Retirement closes it before the next peer.
                        continue;
                    }catch(IllegalStateException state){
                        if(socket.isOpen())throw state;
                        // The container observed a peer close between isOpen and sendMessage.
                    }
                }
            }
        }
    }
    private static void closeRevoked(WebSocketSession socket){
        try{
            socket.close();
        }catch(IOException disconnected){
            // The registry entry is retired and this transport cannot complete its closing handshake.
            return;
        }catch(IllegalStateException state){
            if(socket.isOpen())throw state;
        }
    }
    private Map<String,Object> one(String sql,Object...args){var rows=db.queryForList(sql,args);if(rows.isEmpty())return null;if(rows.size()!=1)throw new IllegalStateException("Session uniqueness violated");return rows.getFirst();}
    private void validateSession(Tokens.Claims c){
        UUID user=UUID.fromString(c.userId()),session=UUID.fromString(c.sessionId());
        var row=one("SELECT session_id,client_type,session_epoch,status,expires_at FROM sessions WHERE user_id=? AND client_type=?",user,c.clientType());
        if(row==null){var actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",user,session);if(actual!=null&&!c.clientType().equals(actual.get("client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");}
        if(!"ACTIVE".equals(row.get("status"))||!((Timestamp)row.get("expires_at")).toInstant().isAfter(Instant.now()))throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
        if(((Number)row.get("session_epoch")).longValue()!=c.epoch())throw new ApiFailure(401,"AUTH_SESSION_EPOCH_STALE","Access token carries a stale session epoch.");
        if(!c.sessionId().equals(row.get("session_id").toString())){var actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",user,session);if(actual!=null&&!c.clientType().equals(actual.get("client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");throw new ApiFailure(401,"AUTH_TOKEN_INVALID","Access token and session binding disagree.");}
    }
    private static void checkMessageAck(JsonNode ack,String id,JsonNode sent) {
        if(ack==null || !ack.isObject() || ack.size()!=4 || !"1.0".equals(ack.path("protocolVersion").textValue()) ||
            !"message.ack".equals(ack.path("type").textValue()) || !canonicalId(ack.path("requestId")) || !id.equals(ack.path("requestId").textValue()))
            throw new IllegalStateException("Invalid Core message acknowledgement envelope");
        var body=ack.path("payload");
        if("committed".equals(body.path("status").textValue())) {
            if(body.size()!=5 || !canonicalId(body.path("conversationId")) ||
                !body.get("conversationId").textValue().equals(sent.path("conversationId").textValue()) ||
                !canonicalId(body.path("messageId")) || !body.path("seq").isIntegralNumber() ||
                body.get("seq").bigIntegerValue().signum()<=0)
                throw new IllegalStateException("Incomplete or unrelated Core commit confirmation");
            checkCommittedTimestamp(body.path("createdAt"));
            return;
        }
        var error=body.path("error");
        if(!"rejected".equals(body.path("status").textValue()) || body.size()!=2 || error.size()!=2 ||
            !Set.of("VALIDATION_FAILED","AUTH_REQUIRED","AUTH_SESSION_REVOKED","AUTHORIZATION_DENIED",
                "MESSAGE_REQUEST_CONFLICT","MESSAGE_COMMIT_FAILED").contains(error.path("code").asText("")) ||
            error.path("message").asText("").isEmpty() || !error.path("message").isTextual())
            throw new IllegalStateException("Invalid Core message rejection");
    }
    private final class Socket extends TextWebSocketHandler {
        private void closeBinding(WebSocketSession socket,Tokens.Claims claims)throws IOException {
            if(bound.remove(socket,claims))socket.close();
        }
        @Override public void afterConnectionEstablished(WebSocketSession socket){socket.setTextMessageSizeLimit(65536);}
        @Override public void afterConnectionClosed(WebSocketSession socket,CloseStatus status){bound.remove(socket);}
        private void reject(WebSocketSession socket,String ack,String request,String code)throws IOException {
            try(socket){
                send(socket,frame(ack,request,Map.of("status","rejected","error",Map.of("code",code,"message","Request rejected"))));
            }
        }
        @Override protected void handleTextMessage(WebSocketSession socket,TextMessage message)throws Exception {
            JsonNode e;try{e=JSON.readTree(message.getPayload());}catch(com.fasterxml.jackson.core.JsonProcessingException malformed){socket.close(CloseStatus.BAD_DATA);return;}
            if(e==null||!e.isObject()||e.size()!=4||!e.path("protocolVersion").isTextual()||!e.path("protocolVersion").textValue().equals("1.0")||!e.path("requestId").isTextual()||!e.path("requestId").textValue().matches("[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")||!e.path("type").isTextual()||!e.path("payload").isObject()){socket.close(CloseStatus.BAD_DATA);return;}
            String type=e.get("type").textValue(),id=e.get("requestId").textValue();JsonNode payload=e.get("payload");
            if(type.equals("message.send") && !canonicalId(e.get("requestId"))){socket.close(CloseStatus.BAD_DATA);return;}
            if(type.equals("ping")||type.equals("pong")){if(payload.size()!=0){socket.close(CloseStatus.BAD_DATA);return;}if(type.equals("ping"))send(socket,frame("pong",id,Map.of()));return;}
            Tokens.Claims current=bound.get(socket);
            if(current==null){
                if(!type.equals("auth.bind")){
                    if(type.equals("message.send"))reject(socket,"message.ack",id,"AUTH_REQUIRED");
                    else socket.close();
                    return;
                }
                if(payload.size()!=1||!payload.path("accessToken").isTextual()||payload.path("accessToken").textValue().isEmpty()){reject(socket,"auth.ack",id,"VALIDATION_FAILED");return;}
                // Register before reading the Session so a committed revoke is either
                // visible to the read or delivered after the successful bind ACK.
                synchronized (socket) {
                    Tokens.Claims claims;
                    try {
                        claims = tokens.parse(payload.get("accessToken").textValue());
                    } catch (ApiFailure rejected) {
                        reject(socket, "auth.ack", id, rejected.code);
                        return;
                    }
                    bound.put(socket, claims);
                    boolean acknowledged = false;
                    try {
                        try {
                            validateSession(claims);
                        } catch (ApiFailure rejected) {
                            reject(socket, "auth.ack", id, rejected.code);
                            return;
                        }
                        send(socket, frame("auth.ack", id, Map.of("status", "bound", "userId", claims.userId(),
                            "sessionId", claims.sessionId(), "clientType", claims.clientType(), "sessionEpoch", claims.epoch())));
                        socket.getAttributes().put("im.token",payload.get("accessToken").textValue());
                        socket.getAttributes().put("im.origins",ConcurrentHashMap.<String>newKeySet());
                        acknowledged = true;
                    } finally {
                        if (!acknowledged) bound.remove(socket, claims);
                    }
                }
                return;
            }
            if(current.expires()<=Instant.now().getEpochSecond()){closeBinding(socket,current);return;}
            if(type.equals("auth.bind")){reject(socket,"auth.ack",id,"VALIDATION_FAILED");return;}
            if(!type.equals("message.send")) {socket.close();return;}
            String key=originKey(payload,id);
            boolean newOrigin=origins(socket).add(key);
            var forward=HttpRequest.newBuilder(URI.create(config.coreUrl+"/__core/message"))
                .timeout(Duration.ofSeconds(10)).header("Content-Type","application/json")
                .header("Authorization","Bearer "+socket.getAttributes().get("im.token"))
                .POST(HttpRequest.BodyPublishers.ofString(message.getPayload())).build();
            var response=client.send(forward,HttpResponse.BodyHandlers.ofByteArray());
            if(response.statusCode()!=200) throw new IOException("Core did not confirm message outcome: "+response.statusCode());
            var ack=JSON.readTree(response.body());
            checkMessageAck(ack,id,payload);
            if(ack.get("payload").get("status").textValue().equals("rejected") && newOrigin) origins(socket).remove(key);
            synchronized(socket){if(current.equals(bound.get(socket)) && socket.isOpen()) send(socket,ack);}
        }
    }
}

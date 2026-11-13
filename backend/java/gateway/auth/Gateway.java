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
    private static final ObjectMapper JSON=new ObjectMapper();
    private final Config config;
    private final JdbcTemplate db;
    private final Tokens tokens;
    private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    private final Map<WebSocketSession,Tokens.Claims> bound=new ConcurrentHashMap<>();
    private final Connection nats;
    private final Thread events;
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
        });events.start();
    }
    @Override public void destroy()throws Exception{stopping=true;events.interrupt();events.join();for(var socket:bound.keySet())socket.close();nats.close();}
    @RequestMapping("/__infra/health") public String health(){return "profile=java role=gateway";}
    @RequestMapping({"/v1/auth/**","/v1/users/**","/v1/friends"})
    public ResponseEntity<byte[]> proxy(HttpServletRequest r)throws IOException,InterruptedException {
        URI target=URI.create(config.coreUrl+r.getRequestURI()+(r.getQueryString()==null?"":"?"+r.getQueryString()));
        byte[] body=r.getInputStream().readNBytes(65537);
        HttpRequest.Builder request=HttpRequest.newBuilder(target).timeout(Duration.ofSeconds(10)).method(r.getMethod(),HttpRequest.BodyPublishers.ofByteArray(body));
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
    private void revoke(String sid,String reason)throws IOException {
        for(var entry:bound.entrySet())if(entry.getValue().sessionId().equals(sid)){
            WebSocketSession socket=entry.getKey();bound.remove(socket);
            try{send(socket,frame("session.revoked",UUID.randomUUID().toString(),Map.of("sessionId",sid,"reason",reason)));}finally{socket.close();}
        }
    }
    private Map<String,Object> one(String sql,Object...args){var rows=db.queryForList(sql,args);if(rows.isEmpty())return null;if(rows.size()!=1)throw new IllegalStateException("Session uniqueness violated");return rows.getFirst();}
    private Tokens.Claims validate(String token){
        Tokens.Claims c=tokens.parse(token);UUID user=UUID.fromString(c.userId()),session=UUID.fromString(c.sessionId());
        var row=one("SELECT session_id,client_type,session_epoch,status,expires_at FROM sessions WHERE user_id=? AND client_type=?",user,c.clientType());
        if(row==null){var actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",user,session);if(actual!=null&&!c.clientType().equals(actual.get("client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");}
        if(!"ACTIVE".equals(row.get("status"))||!((Timestamp)row.get("expires_at")).toInstant().isAfter(Instant.now()))throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
        if(((Number)row.get("session_epoch")).longValue()!=c.epoch())throw new ApiFailure(401,"AUTH_SESSION_EPOCH_STALE","Access token carries a stale session epoch.");
        if(!c.sessionId().equals(row.get("session_id").toString())){var actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",user,session);if(actual!=null&&!c.clientType().equals(actual.get("client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");throw new ApiFailure(401,"AUTH_TOKEN_INVALID","Access token and session binding disagree.");}
        return c;
    }
    private final class Socket extends TextWebSocketHandler {
        @Override public void afterConnectionEstablished(WebSocketSession socket){socket.setTextMessageSizeLimit(65536);}
        @Override public void afterConnectionClosed(WebSocketSession socket,CloseStatus status){bound.remove(socket);}
        private void reject(WebSocketSession socket,String request,String code)throws IOException {try{send(socket,frame("auth.ack",request,Map.of("status","rejected","error",Map.of("code",code,"message","Request rejected"))));}finally{socket.close();}}
        @Override protected void handleTextMessage(WebSocketSession socket,TextMessage message)throws Exception {
            JsonNode e;try{e=JSON.readTree(message.getPayload());}catch(com.fasterxml.jackson.core.JsonProcessingException malformed){socket.close(CloseStatus.BAD_DATA);return;}
            if(e==null||!e.isObject()||e.size()!=4||!e.path("protocolVersion").isTextual()||!e.path("protocolVersion").textValue().equals("1.0")||!e.path("requestId").isTextual()||!e.path("requestId").textValue().matches("[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")||!e.path("type").isTextual()||!e.path("payload").isObject()){socket.close(CloseStatus.BAD_DATA);return;}
            String type=e.get("type").textValue(),id=e.get("requestId").textValue();JsonNode payload=e.get("payload");
            if(type.equals("ping")||type.equals("pong")){if(payload.size()!=0){socket.close(CloseStatus.BAD_DATA);return;}if(type.equals("ping"))send(socket,frame("pong",id,Map.of()));return;}
            Tokens.Claims current=bound.get(socket);
            if(current==null){
                if(!type.equals("auth.bind")){try{if(type.equals("message.send"))send(socket,frame("message.ack",id,Map.of("status","rejected","error",Map.of("code","AUTH_REQUIRED","message","Request rejected"))));}finally{socket.close();}return;}
                if(payload.size()!=1||!payload.path("accessToken").isTextual()||payload.path("accessToken").textValue().isEmpty()){reject(socket,id,"VALIDATION_FAILED");return;}
                Tokens.Claims c;try{c=validate(payload.get("accessToken").textValue());}catch(ApiFailure rejected){reject(socket,id,rejected.code);return;}
                bound.put(socket,c);
                send(socket,frame("auth.ack",id,Map.of("status","bound","userId",c.userId(),"sessionId",c.sessionId(),"clientType",c.clientType(),"sessionEpoch",c.epoch())));
                // Recheck after registry insertion so a concurrent committed revoke cannot be lost during bind.
                try{validate(payload.get("accessToken").textValue());}catch(ApiFailure revoked){revoke(c.sessionId(),"REVOKED");}
                return;
            }
            if(current.expires()<=Instant.now().getEpochSecond()){revoke(current.sessionId(),"REVOKED");return;}
            if(type.equals("auth.bind")){reject(socket,id,"VALIDATION_FAILED");return;}
            socket.close(); // Message business belongs to the next task; no fabricated ACK.
        }
    }
}

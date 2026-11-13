package im.platform.core.auth;

import im.platform.shared.authsupport.*;
import com.fasterxml.jackson.databind.*;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;
import java.util.*;
import java.time.Instant;
import java.sql.Timestamp;
import java.nio.charset.StandardCharsets;

@SpringBootConfiguration
@EnableAutoConfiguration(exclude=DataSourceAutoConfiguration.class)
@RestController
public class CoreAuth {
    private static final ObjectMapper JSON=new ObjectMapper().enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS);
    private final JdbcTemplate db;
    private final TransactionTemplate tx;
    private final Tokens tokens;
    private final Config config;
    public CoreAuth(Config config){this.config=config;db=new JdbcTemplate(config.database());tx=new TransactionTemplate(new DataSourceTransactionManager(config.database()));tokens=new Tokens(config.signingKey());}
    @ExceptionHandler(ApiFailure.class)
    public ResponseEntity<?> rejection(ApiFailure error){return ResponseEntity.status(error.status).header("Cache-Control","no-store").body(Map.of("error",Map.of("code",error.code,"message",error.publicMessage),"requestId",UUID.randomUUID().toString()));}
    private static ApiFailure invalid(String message){return new ApiFailure(400,"VALIDATION_FAILED",message);}
    private static String field(JsonNode b,String f){JsonNode n=b.get(f);if(n==null||!n.isTextual())throw invalid("Request body is invalid.");return n.textValue();}
    private static void fields(JsonNode b,String...allowed){Set<String> names=Set.of(allowed);b.fieldNames().forEachRemaining(n->{if(!names.contains(n))throw invalid("Request body is invalid.");});}
    private static boolean length(String s,int min,int max){int n=s.codePointCount(0,s.length());return n>=min&&n<=max;}
    private static boolean username(String name){return length(name,3,64)&&name.matches("[A-Za-z0-9][A-Za-z0-9._-]*");}
    private static String bearer(HttpServletRequest r){String h=r.getHeader("Authorization");if(h==null||!h.startsWith("Bearer ")||h.length()==7)throw new ApiFailure(401,"AUTH_REQUIRED","Authentication is required.");return h.substring(7);}
    private static JsonNode body(HttpServletRequest r)throws java.io.IOException {
        byte[] raw=r.getInputStream().readNBytes(65537);if(raw.length>65536)throw invalid("Request body is invalid.");
        JsonNode b;try{b=JSON.readTree(raw);}catch(com.fasterxml.jackson.core.JsonProcessingException malformed){throw invalid("Request body is invalid.");}
        if(b==null||!b.isObject())throw invalid("Request body is invalid.");return b;
    }
    private static void client(JsonNode b){
        if(!Tokens.validClient(field(b,"clientType")))throw invalid("clientType is invalid.");
        if(!length(field(b,"deviceId"),1,256)||!length(field(b,"clientVersion"),1,64))throw invalid("Login fields are invalid.");
        if(!"1".equals(field(b,"protocolVersion")))throw new ApiFailure(426,"PROTOCOL_VERSION_UNSUPPORTED","Protocol version is unsupported.");
    }
    private Map<String,Object> one(String sql,Object...args){List<Map<String,Object>> rows=db.queryForList(sql,args);if(rows.isEmpty())return null;if(rows.size()!=1)throw new IllegalStateException("Expected unique database row");return rows.getFirst();}
    private static String string(Map<String,Object> row,String key){Object value=row.get(key);if(value==null)throw new IllegalStateException("Missing database field "+key);return value.toString();}
    private static long number(Map<String,Object> row,String key){return ((Number)row.get(key)).longValue();}
    private static UUID uuid(String value){return UUID.fromString(value);}
    private Tokens.Claims authenticate(String token){
        Tokens.Claims c=tokens.parse(token);
        Map<String,Object> row=one("SELECT session_id,client_type,session_epoch,status,expires_at FROM sessions WHERE user_id=? AND client_type=?",uuid(c.userId()),c.clientType());
        if(row==null){
            Map<String,Object> actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",uuid(c.userId()),uuid(c.sessionId()));
            if(actual!=null&&!c.clientType().equals(string(actual,"client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");
            throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
        }
        if(!"ACTIVE".equals(string(row,"status"))||!((Timestamp)row.get("expires_at")).toInstant().isAfter(Instant.now()))throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
        if(number(row,"session_epoch")!=c.epoch())throw new ApiFailure(401,"AUTH_SESSION_EPOCH_STALE","Access token carries a stale session epoch.");
        if(!string(row,"session_id").equals(c.sessionId())){
            Map<String,Object> actual=one("SELECT client_type FROM sessions WHERE user_id=? AND session_id=?",uuid(c.userId()),uuid(c.sessionId()));
            if(actual!=null&&!c.clientType().equals(string(actual,"client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Access token does not match the active client session.");
            throw new ApiFailure(401,"AUTH_TOKEN_INVALID","Access token and session binding disagree.");
        }
        return c;
    }
    private void revoke(UUID user,UUID session,String reason){
        String payload="{\"sessionId\":\""+session+"\",\"reason\":\""+reason+"\"}";
        db.update("INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload) VALUES(?,'session',?,'session.revoked',?::jsonb)",UUID.randomUUID(),session,payload);
        db.update("INSERT INTO user_sync_events(user_id,event_type,payload) VALUES(?,'session.revoked',?::jsonb)",user,payload);
    }
    private record Session(UUID user,UUID id,String type,long epoch,boolean replaced,String refresh){}
    private ResponseEntity<?> sessionResponse(Session s)throws java.io.IOException {
        long now=Instant.now().getEpochSecond();Map<String,Object> result=new LinkedHashMap<>();
        result.put("accessToken",tokens.sign(new Tokens.Claims(s.user.toString(),s.id.toString(),s.type,s.epoch,now,now+config.accessTokenSeconds)));result.put("accessTokenExpiresInSeconds",config.accessTokenSeconds);
        ResponseEntity.BodyBuilder response=ResponseEntity.ok().header("Cache-Control","no-store");
        if(s.type.equals("WEB")){response.header("Set-Cookie","__Host-im_refresh="+s.refresh+"; Path=/; Max-Age="+config.refreshTokenSeconds+"; HttpOnly; Secure; SameSite=Strict");result.put("refreshTokenDelivery","HTTP_ONLY_SECURE_COOKIE");}
        else{result.put("refreshToken",s.refresh);result.put("refreshTokenExpiresInSeconds",config.refreshTokenSeconds);result.put("refreshTokenDelivery","RESPONSE_BODY_FOR_OS_SECURE_STORAGE");}
        return response.body(Map.of("session",Map.of("sessionId",s.id.toString(),"userId",s.user.toString(),"clientType",s.type,"sessionEpoch",s.epoch,"status","ACTIVE"),"tokens",result,"replacedExistingSession",s.replaced));
    }
    @RequestMapping("/__infra/health") public String health(){return "profile=java role=core";}
    @RequestMapping("/v1/**")
    public ResponseEntity<?> request(HttpServletRequest request)throws java.io.IOException {
        for(String key:request.getParameterMap().keySet())if(key.toLowerCase(Locale.ROOT).matches(".*(token|password|secret).*|authorization|cookie"))throw invalid("Authentication material is forbidden in query parameters.");
        String route=request.getMethod()+" "+request.getRequestURI();
        return switch(route){
            case "POST /v1/auth/register" -> register(body(request));
            case "POST /v1/auth/login" -> login(body(request));
            case "POST /v1/auth/refresh/web" -> refresh(body(request),request,true);
            case "POST /v1/auth/refresh/native" -> refresh(body(request),request,false);
            case "POST /v1/auth/logout" -> logout(request);
            case "GET /v1/users/me" -> me(request);
            case "GET /v1/users/search" -> search(request);
            case "GET /v1/friends" -> {authenticate(bearer(request));yield ResponseEntity.notFound().build();}
            default -> ResponseEntity.notFound().build();
        };
    }
    private ResponseEntity<?> register(JsonNode b){
        fields(b,"username","password","displayName");String name=field(b,"username"),password=field(b,"password"),display=field(b,"displayName");
        if(!username(name)||!length(password,12,256)||!length(display,1,128))throw invalid("Registration fields are invalid.");
        UUID id=UUID.randomUUID();String canonical=name.toLowerCase(Locale.ROOT),hash=PasswordHash.create(password);
        int inserted=db.update("INSERT INTO users(user_id,username,display_name,password_hash) VALUES(?,?,?,?) ON CONFLICT(username) DO NOTHING",id,canonical,display,hash);
        if(inserted==0)throw new ApiFailure(409,"USERNAME_ALREADY_EXISTS","Username already exists.");
        if(inserted!=1)throw new IllegalStateException("Registration row count invariant violated");
        return ResponseEntity.status(201).header("Cache-Control","no-store").body(Map.of("user",Map.of("userId",id.toString(),"username",canonical,"displayName",display)));
    }
    private ResponseEntity<?> login(JsonNode b)throws java.io.IOException {
        fields(b,"username","password","clientType","deviceId","clientVersion","protocolVersion");client(b);
        String name=field(b,"username"),password=field(b,"password");if(!username(name)||!length(password,12,256))throw invalid("Login fields are invalid.");
        Map<String,Object> user=one("SELECT user_id,password_hash FROM users WHERE username=?",name.toLowerCase(Locale.ROOT));
        if(user==null||!PasswordHash.matches(password,string(user,"password_hash")))throw new ApiFailure(401,"AUTH_INVALID_CREDENTIALS","Credentials are invalid.");
        UUID uid=uuid(string(user,"user_id"));String type=field(b,"clientType");
        Session session=tx.execute(status->{
            Objects.requireNonNull(one("SELECT user_id FROM users WHERE user_id=? FOR UPDATE",uid));
            Map<String,Object> old=one("SELECT session_id,session_epoch,status FROM sessions WHERE user_id=? AND client_type=?",uid,type);
            long epoch=old==null?1:Math.addExact(number(old,"session_epoch"),1);boolean replaced=old!=null&&"ACTIVE".equals(string(old,"status"));
            UUID sid=UUID.randomUUID();String refresh=Tokens.random();
            db.update("INSERT INTO sessions(user_id,client_type,session_id,session_epoch,refresh_token_hash,status,device_id,expires_at) VALUES(?,?,?,?,?,'ACTIVE',?,?) ON CONFLICT(user_id,client_type) DO UPDATE SET session_id=EXCLUDED.session_id,session_epoch=EXCLUDED.session_epoch,refresh_token_hash=EXCLUDED.refresh_token_hash,status='ACTIVE',device_id=EXCLUDED.device_id,expires_at=EXCLUDED.expires_at,updated_at=now()",uid,type,sid,epoch,Tokens.hash(refresh),field(b,"deviceId"),Timestamp.from(Instant.now().plusSeconds(config.refreshTokenSeconds)));
            if(replaced)revoke(uid,uuid(string(old,"session_id")),"REPLACED");
            return new Session(uid,sid,type,epoch,replaced,refresh);
        });
        return sessionResponse(Objects.requireNonNull(session));
    }
    private ResponseEntity<?> refresh(JsonNode b,HttpServletRequest request,boolean web)throws java.io.IOException {
        fields(b,web?new String[]{"clientType","deviceId","clientVersion","protocolVersion"}:new String[]{"clientType","deviceId","clientVersion","protocolVersion","refreshToken"});
        String supplied;
        if(web){client(b);if(!"WEB".equals(field(b,"clientType")))throw invalid("WEB refresh fields are invalid.");supplied=null;
            if(request.getCookies()!=null)for(var cookie:request.getCookies())if(cookie.getName().equals("__Host-im_refresh")){supplied=cookie.getValue();break;}
            if(supplied==null||supplied.isEmpty())throw new ApiFailure(401,"AUTH_REQUIRED","WEB refresh cookie is required.");
        }else{if(!b.has("refreshToken")||!b.get("refreshToken").isTextual()||b.get("refreshToken").textValue().isEmpty())throw invalid("refreshToken is required.");supplied=field(b,"refreshToken");client(b);if("WEB".equals(field(b,"clientType")))throw invalid("Native refresh fields are invalid.");}
        String credential=supplied;
        Session session=tx.execute(status->{
            Map<String,Object> row=one("SELECT * FROM sessions WHERE refresh_token_hash=? FOR UPDATE",Tokens.hash(credential));
            if(row==null)throw new ApiFailure(401,"AUTH_REFRESH_REVOKED","Refresh token has been revoked.");
            String type=field(b,"clientType");
            if(!type.equals(string(row,"client_type")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Refresh credential does not belong to the declared client type.");
            if(!"ACTIVE".equals(string(row,"status"))||!((Timestamp)row.get("expires_at")).toInstant().isAfter(Instant.now()))throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
            if(!field(b,"deviceId").equals(string(row,"device_id")))throw new ApiFailure(401,"AUTH_CLIENT_TYPE_MISMATCH","Refresh token does not match the active client session.");
            String next=Tokens.random();UUID uid=uuid(string(row,"user_id"));db.update("UPDATE sessions SET refresh_token_hash=?,expires_at=?,updated_at=now() WHERE user_id=? AND client_type=?",Tokens.hash(next),Timestamp.from(Instant.now().plusSeconds(config.refreshTokenSeconds)),uid,type);
            return new Session(uid,uuid(string(row,"session_id")),type,number(row,"session_epoch"),false,next);
        });return sessionResponse(Objects.requireNonNull(session));
    }
    private ResponseEntity<?> logout(HttpServletRequest request){
        Tokens.Claims c=authenticate(bearer(request));
        tx.executeWithoutResult(status->{
            Map<String,Object> row=Objects.requireNonNull(one("SELECT session_id,status,session_epoch FROM sessions WHERE user_id=? AND client_type=? FOR UPDATE",uuid(c.userId()),c.clientType()));
            if(!c.sessionId().equals(string(row,"session_id"))||c.epoch()!=number(row,"session_epoch")||!"ACTIVE".equals(string(row,"status")))throw new ApiFailure(401,"AUTH_SESSION_REVOKED","Session has been revoked.");
            db.update("UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL,updated_at=now() WHERE user_id=? AND client_type=?",uuid(c.userId()),c.clientType());revoke(uuid(c.userId()),uuid(c.sessionId()),"LOGOUT");
        });return ResponseEntity.noContent().build();
    }
    private static Map<String,Object> user(Map<String,Object> row){return Map.of("userId",string(row,"user_id"),"username",string(row,"username"),"displayName",string(row,"display_name"));}
    private ResponseEntity<?> me(HttpServletRequest request){Tokens.Claims c=authenticate(bearer(request));return ResponseEntity.ok().body(Map.of("user",user(Objects.requireNonNull(one("SELECT user_id,username,display_name FROM users WHERE user_id=?",uuid(c.userId()))))));}
    private ResponseEntity<?> search(HttpServletRequest request){
        authenticate(bearer(request));String name=request.getParameter("username");
        if(request.getParameterMap().size()!=1||name==null||request.getParameterValues("username").length!=1||!username(name))throw invalid("username is invalid.");
        Map<String,Object> row=one("SELECT user_id,username,display_name FROM users WHERE username=?",name.toLowerCase(Locale.ROOT));return ResponseEntity.ok().body(Map.of("users",row==null?List.of():List.of(user(row))));
    }
}

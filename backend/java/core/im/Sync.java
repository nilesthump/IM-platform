package im.platform.core.im;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.http.ResponseEntity;
import im.platform.shared.authsupport.ApiFailure;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class Sync {
    private static final ObjectMapper JSON=new ObjectMapper();
    private final JdbcTemplate db;
    private final TransactionTemplate tx;
    private final byte[] key;
    public Sync(JdbcTemplate db,TransactionTemplate tx,byte[] key) {this.db=db;this.tx=tx;this.key=key;}
    private static ApiFailure invalid(){return new ApiFailure(400,"VALIDATION_FAILED","Sync request is invalid.");}

    public static ObjectNode read(InputStream stream)throws IOException {
        byte[] bytes=new SyncInput(stream).normalized();
        JsonNode body;
        try {body=JSON.reader().with(DeserializationFeature.FAIL_ON_TRAILING_TOKENS).readTree(bytes);}
        catch(JsonProcessingException malformed){throw invalid();}
        if(!(body instanceof ObjectNode object)) throw invalid();
        return object;
    }
    public ResponseEntity<?> page(UUID user,String request,JsonNode body,boolean conversation,Runnable checkSession) {
        if(!body.path("syncVersion").isTextual()) throw invalid();
        if(!"1.0".equals(body.get("syncVersion").textValue())) throw new ApiFailure(426,"PROTOCOL_VERSION_UNSUPPORTED","Sync version is unsupported.");
        if(!(conversation?"sync.conversation.request":"sync.user.request").equals(body.path("type").textValue()) ||
            body.size()!=(conversation?6:5)||!body.path("limit").isIntegralNumber()||body.path("limit").longValue()<1) throw invalid();
        int limit=(int)Math.min(100,body.get("limit").longValue());
        var result=tx.execute(s -> {
            if(!conversation) db.queryForObject("SELECT user_id FROM users WHERE user_id=? FOR SHARE",UUID.class,user);
            checkSession.run();
            if(conversation) return history(user,request,body,limit,checkSession);
            return userPage(user,request,body,limit);
        });
        return ResponseEntity.ok().header("Cache-Control","no-store").body(result);
    }

    private String cursor(UUID user,long pos) {
        byte[] bytes=ByteBuffer.allocate(8).putLong(pos).array();
        try {
            var mac=Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(key,"HmacSHA256"));
            mac.update(("im-sync-user-cursor-v1\0"+user+"\0").getBytes(StandardCharsets.UTF_8));
            return Base64.getUrlEncoder().withoutPadding().encodeToString(ByteBuffer.allocate(40).put(bytes).put(mac.doFinal(bytes)).array());
        } catch(java.security.GeneralSecurityException failure) {throw new IllegalStateException(failure);}
    }
    private long position(UUID user,String value) {
        if("0".equals(value)) return 0;
        if(value==null||value.length()!=54) throw invalid();
        byte[] bytes;
        try {bytes=Base64.getUrlDecoder().decode(value);}
        catch(IllegalArgumentException malformed){throw invalid();}
        long p=ByteBuffer.wrap(bytes).getLong();
        if(p<=0||!MessageDigest.isEqual(value.getBytes(StandardCharsets.US_ASCII),cursor(user,p).getBytes(StandardCharsets.US_ASCII))) throw invalid();
        return p;
    }
    private Map<String,Object> userPage(UUID user,String request,JsonNode body,int limit) {
        String start=body.path("cursor").textValue();
        long pos=position(user,start);
        String eligible="event_type IN ('friend.changed','conversation.changed','membership.changed','plugin.changed')";
        if(pos>0 && !db.queryForObject("SELECT EXISTS(SELECT 1 FROM user_sync_events WHERE user_id=? AND cursor_id=? AND "+eligible+")",Boolean.class,user,pos)) throw invalid();
        var events=db.query("SELECT cursor_id,event_type,payload::text FROM user_sync_events WHERE user_id=? AND cursor_id>? AND "+eligible+" ORDER BY cursor_id LIMIT ?",(r,i)->{
            JsonNode payload;
            try {payload=JSON.readTree(r.getString(3));}
            catch(JsonProcessingException malformed){throw new IllegalStateException("Invalid durable Sync event",malformed);}
            String kind=r.getString(2);
            if(!kind.equals(payload.path("kind").textValue()) || !Groups.validId(payload.path("subjectId").textValue()) ||
                !Groups.validId(payload.path("eventId").textValue()) || !payload.path("revision").isIntegralNumber() || payload.path("revision").bigIntegerValue().signum()<=0)
                throw new IllegalStateException("Invalid durable Sync event");
            return Map.of("eventId",payload.get("eventId"),"kind",kind,"subjectId",payload.get("subjectId"),"revision",payload.get("revision"),
                "cursor",cursor(user,r.getLong(1)));
        },user,pos,limit+1);
        boolean more=events.size()>limit;
        if(more) events.removeLast();
        return Map.of("syncVersion","1.0","type","sync.user.page","requestId",request,"events",events,"nextCursor",events.isEmpty()?start:events.getLast().get("cursor"),"hasMore",more);
    }

    private Map<String,Object> history(UUID user,String request,JsonNode body,int limit,Runnable checkSession) {
        String raw=body.path("conversationId").textValue();
        if(raw==null||!Groups.validId(raw.toLowerCase(Locale.ROOT))||!body.path("afterSeq").isIntegralNumber()||body.path("afterSeq").longValue()<0) throw invalid();
        UUID conversation=UUID.fromString(raw);
        long after=body.path("afterSeq").longValue();
        var membership=db.queryForList("SELECT user_id FROM conversation_members WHERE conversation_id=? AND user_id=? AND left_at IS NULL FOR SHARE",conversation,user);
        checkSession.run();
        if(membership.isEmpty()) throw Groups.denied();
        var messages=db.query("""
            SELECT seq,server_message_id,sender_id,request_id,created_at,text_body,kind
            FROM messages WHERE conversation_id=? AND seq>? ORDER BY seq LIMIT ?
            """,(r,i)->{
                if(r.getLong(1)!=Math.addExact(after,i+1L) || !"TEXT".equals(r.getString(7))) throw new IllegalStateException("Invalid committed message history");
                return Map.of("conversationId",conversation,"seq",r.getLong(1),"messageId",r.getObject(2),"senderId",r.getObject(3),"requestId",r.getObject(4),
                    "createdAt",r.getTimestamp(5).toInstant().toString(),"content",Map.of("kind","TEXT","text",r.getString(6)));
            },conversation,after,limit+1);
        boolean more=messages.size()>limit;
        if(more) messages.removeLast();
        return Map.of("syncVersion","1.0","type","sync.conversation.page","requestId",request,"conversationId",conversation,"messages",messages,"hasMore",more);
    }
}

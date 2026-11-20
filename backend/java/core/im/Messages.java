package im.platform.core.im;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import im.platform.shared.authsupport.ApiFailure;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.*;

public final class Messages {
    private static final ObjectMapper JSON=new ObjectMapper();

    public static Map<String,Object> frame(String type,String request,Object body) {
        return Map.of("protocolVersion","1.0","type",type,"requestId",request,"payload",body);
    }

    public static Map<String,Object> send(JdbcTemplate db,UUID actor,JsonNode envelope,Runnable checkSession) {
        String request=envelope.path("requestId").textValue();
        var payload=envelope.path("payload");
        var content=payload.path("content");
        String conversation=payload.path("conversationId").textValue();
        String text=content.path("text").textValue();
        if(!envelope.isObject()||envelope.size()!=4||!"message.send".equals(envelope.path("type").textValue())||
            !"1.0".equals(envelope.path("protocolVersion").textValue())||!Groups.validId(request)||
            payload.size()!=2||!Groups.validId(conversation)||
            content.size()!=2||!"TEXT".equals(content.path("kind").textValue())||text==null||text.isEmpty()||text.codePointCount(0,text.length())>4096)
            throw new ApiFailure(400,"VALIDATION_FAILED","Request rejected");
        UUID conv=UUID.fromString(conversation),id=UUID.fromString(request);
        // Take the message sender FK lock before locking the Session, as same-slot login locks the user first.
        db.queryForObject("SELECT user_id FROM users WHERE user_id=? FOR KEY SHARE",UUID.class,actor);
        checkSession.run();
        // Acquire conversation then membership, in the same order as group ADD.
        var sequences=db.queryForList("""
            SELECT c.next_seq FROM conversations c JOIN conversation_members m USING(conversation_id)
            WHERE c.conversation_id=? AND m.user_id=? AND m.left_at IS NULL
            FOR UPDATE OF c FOR SHARE OF m
            """,Long.class,conv,actor);
        if(sequences.isEmpty()) throw Groups.denied();
        long seq=sequences.getFirst();
        var rows=db.queryForList("SELECT sender_id,seq,server_message_id,text_body,created_at FROM messages WHERE conversation_id=? AND request_id=?",conv,id);
        UUID message;
        java.sql.Timestamp stamp;
        if(rows.isEmpty()) {
            message=UUID.randomUUID();
            db.update("UPDATE conversations SET next_seq=next_seq+1 WHERE conversation_id=?",conv);
            stamp=db.queryForObject("""
                INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
                VALUES(?,?,?,?,?,'TEXT',?) RETURNING created_at
                """,java.sql.Timestamp.class,message,conv,actor,id,seq,text);
            var event=frame("message.created",id.toString(),Map.of("messageId",message,"seq",seq,"createdAt",stamp.toInstant().toString(),
                "senderId",actor,"conversationId",conv,"content",content));
            String json;
            try {json=JSON.writeValueAsString(event);}
            catch(com.fasterxml.jackson.core.JsonProcessingException failure){throw new IllegalStateException("Cannot serialize committed message event",failure);}
            db.update("""
                INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
                VALUES(?,'message',?,'message.created',?,?,?::jsonb)
                """,UUID.randomUUID(),message,conv,message,json);
        } else {
            var row=rows.getFirst();
            if(!actor.equals(row.get("sender_id"))||!text.equals(row.get("text_body"))) throw new ApiFailure(409,"MESSAGE_REQUEST_CONFLICT","Request rejected");
            seq=((Number)row.get("seq")).longValue();
            message=(UUID)row.get("server_message_id");
            stamp=(java.sql.Timestamp)row.get("created_at");
        }
        checkSession.run();
        return frame("message.ack",request,Map.of("status","committed","messageId",message,"seq",seq,"createdAt",stamp.toInstant().toString(),"conversationId",conv));
    }
}

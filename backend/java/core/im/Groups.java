package im.platform.core.im;

import com.fasterxml.jackson.databind.JsonNode;
import im.platform.shared.authsupport.ApiFailure;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.support.TransactionTemplate;
import java.util.*;

public final class Groups {
    private final JdbcTemplate db;
    private final TransactionTemplate tx;

    public Groups(JdbcTemplate db, TransactionTemplate tx) {
        this.db=db;
        this.tx=tx;
    }

    static ApiFailure invalid() {return new ApiFailure(400,"VALIDATION_FAILED","Group request is invalid.");}
    static ApiFailure denied() {return new ApiFailure(403,"AUTHORIZATION_DENIED","Conversation access is denied.");}
    public static boolean validId(String value) {
        return value!=null && value.matches("[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}");
    }
    private List<String> members(String conversation) {
        return db.queryForList("SELECT user_id::text FROM conversation_members WHERE conversation_id=?::uuid AND left_at IS NULL ORDER BY user_id",String.class,conversation);
    }

    public ResponseEntity<?> mutate(UUID actor,String conversation,JsonNode body,Runnable checkSession) {
        String request=body.path("requestId").asText("");
        var input=body.path("memberUserIds");
        if (!validId(request) || body.size()!=2 || !input.isArray() || input.isEmpty() || input.size()>100 ||
            (conversation!=null && !validId(conversation))) throw invalid();
        var targets=new TreeSet<String>();
        for (var node:input) {
            String id=node.asText("");
            if(!validId(id)||actor.toString().equals(id)) throw invalid();
            targets.add(id);
        }
        // A concurrent ADD may expand the set of users requiring invalidation.
        // Acquire all user locks in UUID order before allocating per-user cursors.
        while (true) {
            var result=tx.execute(s -> {
                var users=new TreeSet<>(targets);
                users.add(actor.toString());
                if(conversation!=null) users.addAll(members(conversation));
                for (var id:users) {
                    if(db.queryForList("SELECT user_id FROM users WHERE user_id=?::uuid FOR NO KEY UPDATE",id).isEmpty()) throw denied();
                }
                checkSession.run();
                if(conversation!=null) {
                    if(db.queryForList("""
                        SELECT c.kind FROM conversations c JOIN conversation_members m USING(conversation_id)
                        WHERE c.conversation_id=?::uuid AND m.user_id=? AND m.left_at IS NULL AND c.kind='GROUP'
                        FOR UPDATE OF c FOR SHARE OF m
                        """,conversation,actor).isEmpty()) throw denied();
                    if(!users.containsAll(members(conversation))) {s.setRollbackOnly();return null;}
                }
                for(var id:targets) if(!db.queryForObject("""
                    SELECT EXISTS(SELECT 1 FROM friendships WHERE user_low_id=least(?,?::uuid) AND user_high_id=greatest(?,?::uuid))
                    """,Boolean.class,actor,id,actor,id)) throw denied();
                var response=apply(actor,conversation,request,targets);
                checkSession.run();
                return response;
            });
            if(result!=null) return result;
        }
    }

    private ResponseEntity<?> apply(UUID actor,String conversation,String request,SortedSet<String> targets) {
        boolean create=conversation==null;
        String operation=create?"CREATE":"ADD";
        var receipts=db.queryForList("""
            SELECT conversation_id::text,target_user_ids::text,added_member_user_ids::text,created_at
            FROM group_operation_receipts WHERE actor_id=? AND operation=? AND request_id=?::uuid
            AND (?::uuid IS NULL OR conversation_id=?::uuid)
            """,actor,operation,request,conversation,conversation);
        var previous=create?db.queryForList("SELECT conversation_id::text FROM conversations WHERE created_by=? AND group_create_request_id=?::uuid",String.class,actor,request):List.of();
        String normalized="{"+String.join(",",targets)+"}";
        if(!receipts.isEmpty()) {
            var receipt=receipts.getFirst();
            if(create && !previous.equals(List.of(receipt.get("conversation_id")))) throw new IllegalStateException("Inconsistent persisted group create identity");
            if(!normalized.equals(receipt.get("target_user_ids"))) throw new ApiFailure(409,"GROUP_REQUEST_CONFLICT","Group request identity has different targets.");
            String values=(String)receipt.get("added_member_user_ids");
            var added=values.equals("{}")?List.of():List.of(values.substring(1,values.length()-1).split(","));
            return result(create,request,(String)receipt.get("conversation_id"),added,(java.sql.Timestamp)receipt.get("created_at"));
        }
        if(!previous.isEmpty()) throw new IllegalStateException("persisted-original-group-result-missing");
        var added=new TreeSet<String>();
        if(create) {
            conversation=UUID.randomUUID().toString();
            db.update("INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES(?::uuid,'GROUP',?,?::uuid)",conversation,actor,request);
            db.update("INSERT INTO conversation_members(conversation_id,user_id,role) VALUES(?::uuid,?,'OWNER')",conversation,actor);
            added.add(actor.toString());
        }
        for(var id:targets) {
            int changed=db.update("""
                INSERT INTO conversation_members(conversation_id,user_id,role) VALUES(?::uuid,?::uuid,'MEMBER')
                ON CONFLICT(conversation_id,user_id) DO UPDATE SET left_at=NULL WHERE conversation_members.left_at IS NOT NULL
                """,conversation,id);
            if(changed==1) added.add(id);
        }
        var stamp=db.queryForObject("""
            INSERT INTO group_operation_receipts(actor_id,operation,request_id,conversation_id,target_user_ids,added_member_user_ids)
            VALUES(?,?,?::uuid,?::uuid,?::uuid[],?::uuid[]) RETURNING created_at
            """,java.sql.Timestamp.class,actor,operation,request,conversation,normalized,"{"+String.join(",",added)+"}");
        if(!added.isEmpty()) for(var member:members(conversation)) {
            Social.event(db,UUID.fromString(member),"conversation.changed",UUID.fromString(conversation),true);
            Social.event(db,UUID.fromString(member),"membership.changed",UUID.fromString(conversation),true);
        }
        return result(create,request,conversation,added,stamp);
    }

    private static ResponseEntity<?> result(boolean create,String request,String conversation,Collection<?> added,java.sql.Timestamp stamp) {
        return ResponseEntity.status(create?201:200).header("Cache-Control","no-store")
            .body(Map.of("requestId",request,"conversationId",conversation,"addedMemberUserIds",added,"createdAt",stamp.toInstant().toString()));
    }

    public ResponseEntity<?> snapshot(UUID actor,String request,String limitText,String after,String member,Runnable checkSession) {
        if(!validId(request) || (after==null)!=(member==null) || (after!=null && (!validId(after)||!validId(member)))) throw invalid();
        if(limitText!=null && !limitText.matches("([1-9][0-9]?|100)")) throw invalid();
        int limit=limitText==null?100:Integer.parseInt(limitText);
        return tx.execute(s -> {
            db.queryForObject("SELECT user_id FROM users WHERE user_id=? FOR SHARE",UUID.class,actor);
            checkSession.run();
            var items=db.query("""
                SELECT c.conversation_id,c.kind,c.created_by,c.created_at,u.user_id,u.username,u.display_name,m.role,m.joined_at
                FROM conversations c JOIN conversation_members own ON own.conversation_id=c.conversation_id AND own.user_id=? AND own.left_at IS NULL
                JOIN conversation_members m ON m.conversation_id=c.conversation_id AND m.left_at IS NULL JOIN users u ON u.user_id=m.user_id
                WHERE (?::uuid IS NULL OR (c.conversation_id,m.user_id)>(?::uuid,?::uuid)) ORDER BY c.conversation_id,m.user_id LIMIT ?
                """,(r,i)->Map.<String,Object>of("conversationId",r.getString(1),"kind",r.getString(2),"createdBy",r.getString(3),
                    "createdAt",r.getTimestamp(4).toInstant().toString(),"member",Map.of("user",Map.of("userId",r.getString(5),"username",r.getString(6),
                    "displayName",r.getString(7)),"role",r.getString(8),"joinedAt",r.getTimestamp(9).toInstant().toString())),actor,after,after,member,limit+1);
            boolean more=items.size()>limit;
            String lastConversation="",lastMember="";
            if(more) {
                items.removeLast();
                var last=items.getLast();
                lastConversation=(String)last.get("conversationId");
                lastMember=(String)((Map<?,?>)((Map<?,?>)last.get("member")).get("user")).get("userId");
            }
            checkSession.run();
            return ResponseEntity.ok().header("Cache-Control","no-store").body(Map.of("requestId",request,"items",items,"hasMore",more,
                "next",Map.of("afterConversationId",lastConversation,"afterMemberUserId",lastMember)));
        });
    }
}

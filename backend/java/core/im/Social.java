package im.platform.core.im;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.ResponseEntity;
import im.platform.shared.authsupport.ApiFailure;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

public final class Social {
    private final JdbcTemplate db;

    public Social(JdbcTemplate db) {
        this.db = db;
    }

    private static UUID friendship(UUID low, UUID high) {
        byte[] hash;
        try {
            hash = MessageDigest.getInstance("SHA-256").digest(
                ("im-friendship-v1:" + low + ":" + high).getBytes(StandardCharsets.UTF_8));
        } catch (NoSuchAlgorithmException missing) {
            throw new IllegalStateException(missing);
        }
        hash[6] = (byte)((hash[6] & 15) | 128);
        hash[8] = (byte)((hash[8] & 63) | 128);
        var data = ByteBuffer.wrap(hash);
        return new UUID(data.getLong(), data.getLong());
    }

    public ResponseEntity<?> list(UUID user) {
        var rows = db.query("""
            SELECT u.user_id,u.username,u.display_name,f.user_low_id,f.user_high_id,f.direct_conversation_id
            FROM friendships f JOIN users u ON u.user_id=CASE WHEN f.user_low_id=? THEN f.user_high_id ELSE f.user_low_id END
            WHERE f.user_low_id=? OR f.user_high_id=? ORDER BY u.username
            """, (r,i) -> Map.of("user", Map.of("userId",r.getObject(1),"username",r.getString(2),"displayName",r.getString(3)),
                "friendshipId",friendship(r.getObject(4,UUID.class),r.getObject(5,UUID.class)),
                "directConversationId",r.getObject(6)), user,user,user);
        return ResponseEntity.ok(Map.of("friends",rows));
    }

    public ResponseEntity<?> add(UUID actor, String target, Runnable checkSession) {
        if (!target.matches("(?i)[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"))
            throw new ApiFailure(404,"USER_NOT_FOUND","Target user was not found.");
        UUID other = UUID.fromString(target);
        if (actor.equals(other)) throw new ApiFailure(422,"FRIEND_SELF_NOT_ALLOWED","A user cannot befriend itself.");
        var ids = new ArrayList<>(List.of(actor,other));
        ids.sort(Comparator.comparing(UUID::toString));
        UUID low = ids.getFirst(), high = ids.getLast();
        var users = db.queryForList("SELECT user_id FROM users WHERE user_id IN (?,?) ORDER BY user_id FOR NO KEY UPDATE", UUID.class,low,high);
        if (users.size()!=2) throw new ApiFailure(404,"USER_NOT_FOUND","Target user was not found.");
        checkSession.run();
        var pairs = db.queryForList("SELECT direct_conversation_id FROM friendships WHERE user_low_id=? AND user_high_id=?",UUID.class,low,high);
        boolean created = pairs.isEmpty();
        UUID conversation;
        if (created) {
            var existing = db.queryForList("SELECT conversation_id FROM conversations WHERE direct_user_low_id=? AND direct_user_high_id=?",UUID.class,low,high);
            conversation = existing.isEmpty() ? UUID.randomUUID() : existing.getFirst();
            if (existing.isEmpty()) db.update("INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by) VALUES(?,'DIRECT',?,?,?)",conversation,low,high,actor);
            db.update("INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id) VALUES(?,?,?)",low,high,conversation);
            for (var id:ids) db.update("INSERT INTO conversation_members(conversation_id,user_id,role) VALUES(?,?,?) ON CONFLICT(conversation_id,user_id) DO NOTHING",conversation,id,id.equals(actor)?"OWNER":"MEMBER");
        } else conversation = pairs.getFirst();
        var members = db.queryForList("""
            SELECT CASE WHEN m.left_at IS NULL THEN m.user_id END FROM conversations c JOIN conversation_members m ON m.conversation_id=c.conversation_id
            WHERE c.conversation_id=? AND c.kind='DIRECT' AND c.direct_user_low_id=? AND c.direct_user_high_id=?
            ORDER BY m.user_id
            """,UUID.class,conversation,low,high);
        if (!ids.equals(members)) throw new ApiFailure(409,"FRIENDSHIP_STATE_CONFLICT","Canonical friendship state conflicts.");
        if (created) for (var id:ids) {
            event(db,id,"friend.changed",id.equals(low)?high:low,false);
            event(db,id,"conversation.changed",conversation,false);
            event(db,id,"membership.changed",conversation,false);
        }
        checkSession.run();
        return ResponseEntity.status(created?201:200).body(Map.of("friendshipId",friendship(low,high),
            "directConversationId",conversation,"memberUserIds",ids,"normalizedPair",Map.of("lowUserId",low,"highUserId",high),"created",created));
    }

    static void event(JdbcTemplate db, UUID recipient,String kind,UUID subject,boolean revisionFromCursor) {
        Long cursor = db.queryForObject("INSERT INTO user_sync_events(user_id,event_type,payload) VALUES(?,?,'{}') RETURNING cursor_id",Long.class,recipient,kind);
        UUID event = UUID.randomUUID();
        db.update("""
            UPDATE user_sync_events SET payload=jsonb_build_object('eventId',?::uuid,'cursor',?::text,'kind',?::text,'subjectId',?::uuid,'revision',?::bigint)
            WHERE user_id=? AND cursor_id=?
            """,event,cursor,kind,subject,revisionFromCursor?cursor:1L,recipient,cursor);
        db.update("""
            INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload)
            SELECT ?,'user',user_id,event_type,jsonb_build_object('userId',user_id,'event',payload)
            FROM user_sync_events WHERE user_id=? AND cursor_id=?
            """,event,recipient,cursor);
    }
}

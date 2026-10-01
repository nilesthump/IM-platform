package core

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
)

// The schema identifies a friendship by its normalized pair. The public ID is
// derived from that pair so it is stable without introducing another table.
func friendshipID(low, high string) string {
	h := sha256.Sum256([]byte("im-friendship-v1:" + low + ":" + high))
	b := h[:16]
	// Version 8 denotes an application-defined UUID, rather than UUIDv5/SHA-1.
	b[6] = b[6]&0x0f | 0x80
	b[8] = b[8]&0x3f | 0x80
	s := hex.EncodeToString(b)
	return s[:8] + "-" + s[8:12] + "-" + s[12:16] + "-" + s[16:20] + "-" + s[20:]
}

var socialUUIDPattern = regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)

func pair(a, b string) (string, string) {
	if a < b {
		return a, b
	}
	return b, a
}

func socialResult(low, high, conversation string, created bool) map[string]any {
	return map[string]any{
		"friendshipId":         friendshipID(low, high),
		"normalizedPair":       map[string]string{"lowUserId": low, "highUserId": high},
		"directConversationId": conversation,
		"memberUserIds":        []string{low, high},
		"created":              created,
	}
}

func (s *authService) socialPrincipal(r *http.Request) (claims, error) {
	token, err := bearer(r)
	if err != nil {
		return claims{}, fail(401, "AUTH_REQUIRED", "Authentication is required.")
	}
	return s.authenticate(r.Context(), token)
}

func (s *authService) listFriends(w http.ResponseWriter, r *http.Request) {
	c, err := s.socialPrincipal(r)
	if err != nil {
		writeError(w, r, err)
		return
	}
	rows, err := s.db.Query(r.Context(), `SELECT u.user_id,u.username,u.display_name,f.user_low_id,f.user_high_id,f.direct_conversation_id
		FROM friendships f JOIN users u ON u.user_id=CASE WHEN f.user_low_id=$1 THEN f.user_high_id ELSE f.user_low_id END
		WHERE f.user_low_id=$1 OR f.user_high_id=$1 ORDER BY u.username`, c.UserID)
	if err != nil {
		writeError(w, r, err)
		return
	}
	defer rows.Close()
	friends := make([]any, 0)
	for rows.Next() {
		var id, name, display, low, high, conversation string
		if err = rows.Scan(&id, &name, &display, &low, &high, &conversation); err != nil {
			writeError(w, r, err)
			return
		}
		friends = append(friends, map[string]any{"user": map[string]string{"userId": id, "username": name, "displayName": display}, "friendshipId": friendshipID(low, high), "directConversationId": conversation})
	}
	if err = rows.Err(); err != nil {
		writeError(w, r, err)
		return
	}
	writeJSON(w, 200, map[string]any{"friends": friends})
}

func (s *authService) addFriend(w http.ResponseWriter, r *http.Request) {
	c, err := s.socialPrincipal(r)
	if err != nil {
		writeError(w, r, err)
		return
	}
	target := strings.ToLower(r.PathValue("friendUserId"))
	if !socialUUIDPattern.MatchString(target) {
		writeError(w, r, fail(404, "USER_NOT_FOUND", "Target user was not found."))
		return
	}
	if target == c.UserID {
		writeError(w, r, fail(422, "FRIEND_SELF_NOT_ALLOWED", "A user cannot befriend itself."))
		return
	}
	ctx := r.Context()
	tx, err := s.db.Begin(ctx)
	if err != nil {
		writeError(w, r, err)
		return
	}
	defer tx.Rollback(ctx)
	low, high := pair(c.UserID, target)
	// Both request directions lock the same rows in the same order, including
	// the absent-first-friendship case. This prevents reverse-order duplicates.
	for _, id := range []string{low, high} {
		var locked string
		err = tx.QueryRow(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, id).Scan(&locked)
		if errors.Is(err, pgx.ErrNoRows) {
			writeError(w, r, fail(404, "USER_NOT_FOUND", "Target user was not found."))
			return
		}
		if err != nil {
			writeError(w, r, err)
			return
		}
	}
	// A replacement login also locks its user row. Recheck the session after
	// taking that lock so a revoked token cannot commit a social mutation.
	var sessionID, status string
	var epoch int64
	var expiry time.Time
	err = tx.QueryRow(ctx, `SELECT session_id,session_epoch,status,expires_at FROM sessions WHERE user_id=$1 AND client_type=$2`, c.UserID, c.ClientType).Scan(&sessionID, &epoch, &status, &expiry)
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		writeError(w, r, err)
		return
	}
	if errors.Is(err, pgx.ErrNoRows) || !expiry.After(s.now()) || sessionID != c.SessionID || epoch != c.SessionEpoch || status != "ACTIVE" {
		writeError(w, r, fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked."))
		return
	}
	conversation, created, err := assembleFriendship(ctx, tx, low, high, c.UserID)
	if err != nil {
		writeError(w, r, err)
		return
	}
	if err = tx.Commit(ctx); err != nil {
		writeError(w, r, err)
		return
	}
	code := 200
	if created {
		code = 201
	}
	writeJSON(w, code, socialResult(low, high, conversation, created))
}

func assembleFriendship(ctx context.Context, tx pgx.Tx, low, high, actor string) (conversation string, created bool, err error) {
	err = tx.QueryRow(ctx, `SELECT direct_conversation_id FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high).Scan(&conversation)
	if err == nil {
		if err = validDirectState(ctx, tx, low, high, conversation); err != nil {
			return "", false, err
		}
		return conversation, false, nil
	}
	if !errors.Is(err, pgx.ErrNoRows) {
		return "", false, err
	}
	// A direct row may already exist for the pair. Reuse its canonical ID.
	err = tx.QueryRow(ctx, `SELECT conversation_id FROM conversations WHERE direct_user_low_id=$1 AND direct_user_high_id=$2`, low, high).Scan(&conversation)
	if errors.Is(err, pgx.ErrNoRows) {
		conversation, err = uuid()
		if err != nil {
			return "", false, err
		}
		_, err = tx.Exec(ctx, `INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by) VALUES($1,'DIRECT',$2,$3,$4)`, conversation, low, high, actor)
	}
	if err != nil {
		return "", false, err
	}
	_, err = tx.Exec(ctx, `INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id) VALUES($1,$2,$3)`, low, high, conversation)
	if err != nil {
		return "", false, err
	}
	for _, id := range []string{low, high} {
		role := "MEMBER"
		if id == actor {
			role = "OWNER"
		}
		_, err = tx.Exec(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,$3) ON CONFLICT(conversation_id,user_id) DO NOTHING`, conversation, id, role)
		if err != nil {
			return "", false, err
		}
	}
	if err = validDirectState(ctx, tx, low, high, conversation); err != nil {
		return "", false, err
	}
	for _, recipient := range []string{low, high} {
		other := high
		if recipient == high {
			other = low
		}
		for _, event := range []struct{ kind, subject string }{{"friend.changed", other}, {"conversation.changed", conversation}, {"membership.changed", conversation}} {
			if err = writeSocialEvent(ctx, tx, recipient, event.kind, event.subject); err != nil {
				return "", false, err
			}
		}
	}
	return conversation, true, nil
}

func validDirectState(ctx context.Context, tx pgx.Tx, low, high, conversation string) error {
	var count, active int
	err := tx.QueryRow(ctx, `SELECT count(*),count(*) FILTER (WHERE m.user_id IN ($2,$3) AND m.left_at IS NULL)
		FROM conversations c JOIN conversation_members m ON m.conversation_id=c.conversation_id
		WHERE c.conversation_id=$1 AND c.kind='DIRECT' AND c.direct_user_low_id=$2 AND c.direct_user_high_id=$3
		`, conversation, low, high).Scan(&count, &active)
	if err != nil {
		return err
	}
	if count != 2 || active != 2 {
		return fail(409, "FRIENDSHIP_STATE_CONFLICT", "Canonical friendship state conflicts.")
	}
	return nil
}

func writeSocialEvent(ctx context.Context, tx pgx.Tx, recipient, kind, subject string) error {
	id, err := uuid()
	if err != nil {
		return err
	}
	var cursor int64
	err = tx.QueryRow(ctx, `INSERT INTO user_sync_events(user_id,event_type,payload) VALUES($1,$2,'{}'::jsonb) RETURNING cursor_id`, recipient, kind).Scan(&cursor)
	if err != nil {
		return err
	}
	event := map[string]any{"eventId": id, "cursor": strconv.FormatInt(cursor, 10), "kind": kind, "subjectId": subject, "revision": 1}
	payload, err := json.Marshal(event)
	if err != nil {
		return err
	}
	_, err = tx.Exec(ctx, `UPDATE user_sync_events SET payload=$1 WHERE user_id=$2 AND cursor_id=$3`, payload, recipient, cursor)
	if err != nil {
		return err
	}
	outboxPayload, err := json.Marshal(map[string]any{"userId": recipient, "event": event})
	if err != nil {
		return err
	}
	_, err = tx.Exec(ctx, `INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,payload) VALUES($1,'user',$2,$3,NULL,$4)`, id, recipient, kind, outboxPayload)
	return err
}

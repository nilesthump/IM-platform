package core

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
	"net/http/httptest"
	"os"
	"reflect"
	"sync"
	"testing"
	"time"
)

type messageFixture struct {
	s            *authService
	db           *pgxpool.Pool
	users        []string
	claims       []claims
	conversation string
}

func newMessageFixture(t *testing.T, members int) *messageFixture {
	t.Helper()
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	if err = db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	f := &messageFixture{db: db, s: &authService{db: db, codec: &shared.Codec{Key: []byte("test-only-signing-key-at-least-32-bytes"), Now: time.Now}, now: time.Now}}
	t.Cleanup(func() { db.Close() })
	for i := 0; i < members; i++ {
		id, _ := uuid()
		f.users = append(f.users, id)
		if _, err = db.Exec(ctx, `INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1::uuid,$1::text,'Message test','test-only')`, id); err != nil {
			t.Fatal(err)
		}
		sid, epoch, _, _, err := f.s.newSession(ctx, id, clientInput{ClientType: "WEB", DeviceID: "msg-test"})
		if err != nil {
			t.Fatal(err)
		}
		f.claims = append(f.claims, claims{UserID: id, SessionID: sid, SessionEpoch: epoch, ClientType: "WEB", IssuedAt: time.Now().Unix(), ExpiresAt: time.Now().Add(time.Hour).Unix()})
	}
	f.conversation, _ = uuid()
	req, _ := uuid()
	if _, err = db.Exec(ctx, `INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES($1,'GROUP',$2,$3)`, f.conversation, f.users[0], req); err != nil {
		t.Fatal(err)
	}
	for _, id := range f.users {
		if _, err = db.Exec(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'MEMBER')`, f.conversation, id); err != nil {
			t.Fatal(err)
		}
	}
	t.Cleanup(func() {
		db.Exec(ctx, `DELETE FROM outbox_events WHERE conversation_id=$1`, f.conversation)
		db.Exec(ctx, `DELETE FROM messages WHERE conversation_id=$1`, f.conversation)
		db.Exec(ctx, `DELETE FROM conversation_members WHERE conversation_id=$1`, f.conversation)
		db.Exec(ctx, `DELETE FROM conversations WHERE conversation_id=$1`, f.conversation)
		for _, id := range f.users {
			db.Exec(ctx, `DELETE FROM sessions WHERE user_id=$1`, id)
			db.Exec(ctx, `DELETE FROM users WHERE user_id=$1`, id)
		}
	})
	return f
}
func (f *messageFixture) send(request, text string) sendFrame {
	v := sendFrame{ProtocolVersion: "1.0", Type: "message.send", RequestID: request}
	v.Payload.ConversationID = f.conversation
	v.Payload.Content = textContent{Kind: "TEXT", Text: text}
	return v
}
func (f *messageFixture) count(t *testing.T, query string) int {
	t.Helper()
	var n int
	if err := f.db.QueryRow(context.Background(), query, f.conversation).Scan(&n); err != nil {
		t.Fatal(err)
	}
	return n
}
func (f *messageFixture) adapter(t *testing.T, c claims, v sendFrame) map[string]any {
	t.Helper()
	b, _ := json.Marshal(v)
	token, err := f.s.codec.Sign(c)
	if err != nil {
		t.Fatal(err)
	}
	r := httptest.NewRequest("POST", "/__core/message", bytes.NewReader(b))
	r.Header.Set("Authorization", "Bearer "+token)
	w := httptest.NewRecorder()
	f.s.sendMessage(w, r)
	var out map[string]any
	if json.Unmarshal(w.Body.Bytes(), &out) != nil {
		t.Fatal("invalid ack")
	}
	return out
}
func TestMessageConcurrentIdentityAndSequence(t *testing.T) {
	f := newMessageFixture(t, 2)
	id, _ := uuid()
	v := f.send(id, "hello")
	var wg sync.WaitGroup
	results := make(chan storedMessage, 16)
	failures := make(chan error, 16)
	for i := 0; i < 16; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			m, e := f.s.commitMessage(context.Background(), f.claims[0], v)
			if e != nil {
				failures <- e
			}
			results <- m
		}()
	}
	wg.Wait()
	close(results)
	close(failures)
	for e := range failures {
		t.Fatal(e)
	}
	var original storedMessage
	for m := range results {
		if original.MessageID == "" {
			original = m
		}
		if !reflect.DeepEqual(m, original) {
			t.Fatal("retry identity changed")
		}
	}
	for _, q := range []string{`SELECT count(*) FROM messages WHERE conversation_id=$1`, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1 AND event_type='message.created'`} {
		if f.count(t, q) != 1 {
			t.Fatal("duplicate logical record")
		}
	}
	for i := 0; i < 12; i++ {
		id, _ := uuid()
		wg.Add(1)
		go func(id string) {
			defer wg.Done()
			_, e := f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "next"))
			if e != nil {
				t.Error(e)
			}
		}(id)
	}
	wg.Wait()
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 13 || f.count(t, `SELECT max(seq)::int FROM messages WHERE conversation_id=$1`) != 13 || f.count(t, `SELECT next_seq::int FROM conversations WHERE conversation_id=$1`) != 14 {
		t.Fatal("sequence gap")
	}
	for _, c := range []claims{f.claims[0], f.claims[1]} {
		conflict := v
		if c.UserID == f.claims[0].UserID {
			conflict.Payload.Content.Text = "different"
		}
		ack := f.adapter(t, c, conflict)
		if ack["payload"].(map[string]any)["error"].(map[string]any)["code"] != "MESSAGE_REQUEST_CONFLICT" {
			t.Fatal("content/sender identity conflict accepted")
		}
	}
}
func TestMessageAuthorizationAndIndependentConversations(t *testing.T) {
	f := newMessageFixture(t, 2)
	id, _ := uuid()
	v := f.send(id, "hello")
	m, err := f.s.commitMessage(context.Background(), f.claims[0], v)
	if err != nil {
		t.Fatal(err)
	}
	other := newMessageFixture(t, 2)
	second, err := other.s.commitMessage(context.Background(), other.claims[0], other.send(id, "hello"))
	if err != nil || second.MessageID == m.MessageID || second.Seq != 1 {
		t.Fatal("Conversation independence failed")
	}
	if _, err = f.db.Exec(context.Background(), `UPDATE conversation_members SET left_at=now() WHERE conversation_id=$1 AND user_id=$2`, f.conversation, f.users[1]); err != nil {
		t.Fatal(err)
	}
	fresh, _ := uuid()
	ack := f.adapter(t, f.claims[1], f.send(fresh, "denied"))
	if ack["payload"].(map[string]any)["error"].(map[string]any)["code"] != "AUTHORIZATION_DENIED" {
		t.Fatal("nonmember accepted")
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT next_seq::int FROM conversations WHERE conversation_id=$1`) != 2 {
		t.Fatal("denial persisted")
	}
	if _, err = f.db.Exec(context.Background(), `UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL WHERE user_id=$1`, f.users[0]); err != nil {
		t.Fatal(err)
	}
	ack = f.adapter(t, f.claims[0], f.send(fresh, "revoked"))
	if ack["payload"].(map[string]any)["error"].(map[string]any)["code"] != "AUTH_SESSION_REVOKED" {
		t.Fatal("revoked Session accepted")
	}
}
func TestMessageRollbackAndACKAfterCommit(t *testing.T) {
	f := newMessageFixture(t, 2)
	ctx := context.Background()
	id, _ := uuid()
	name := "msgprobe" + fmt.Sprint(time.Now().UnixNano())
	lockKey := int64(77461001)
	// A deferred constraint trigger pauses the actual COMMIT, not a mock hook.
	sql := fmt.Sprintf(`CREATE FUNCTION %s() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.conversation_id='%s'::uuid THEN PERFORM pg_advisory_xact_lock(%d); END IF; RETURN NEW; END $$; CREATE CONSTRAINT TRIGGER %s AFTER INSERT ON outbox_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION %s()`, name, f.conversation, lockKey, name, name)
	if _, err := f.db.Exec(ctx, sql); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() {
		f.db.Exec(ctx, fmt.Sprintf(`DROP TRIGGER IF EXISTS %s ON outbox_events; DROP FUNCTION IF EXISTS %s()`, name, name))
	})
	guard, err := f.db.Acquire(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer guard.Release()
	if _, err = guard.Exec(ctx, `SELECT pg_advisory_lock($1)`, lockKey); err != nil {
		t.Fatal(err)
	}
	defer guard.Exec(ctx, `SELECT pg_advisory_unlock($1)`, lockKey)
	ack := make(chan map[string]any, 1)
	go func() { ack <- f.adapter(t, f.claims[0], f.send(id, "hello")) }()
	deadline := time.Now().Add(5 * time.Second)
	waiting := false
	for time.Now().Before(deadline) {
		var n int
		err = f.db.QueryRow(ctx, `SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND wait_event='advisory'`).Scan(&n)
		if err != nil {
			t.Fatal(err)
		}
		if n > 0 {
			waiting = true
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !waiting {
		t.Fatal("COMMIT did not reach deferred probe")
	}
	select {
	case <-ack:
		t.Fatal("ACK before durable commit")
	default:
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 0 || f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1`) != 0 {
		t.Fatal("uncommitted data visible")
	}
	guard.Exec(ctx, `SELECT pg_advisory_unlock($1)`, lockKey)
	select {
	case result := <-ack:
		if result["payload"].(map[string]any)["status"] != "committed" {
			t.Fatal("commit rejected")
		}
	case <-time.After(5 * time.Second):
		t.Fatal("commit stuck")
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1`) != 1 {
		t.Fatal("ACK without records")
	}
	if _, err = f.db.Exec(ctx, fmt.Sprintf(`CREATE OR REPLACE FUNCTION %s() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.conversation_id='%s'::uuid THEN RAISE EXCEPTION 'injected rollback'; END IF; RETURN NEW; END $$`, name, f.conversation)); err != nil {
		t.Fatal(err)
	}
	retry, _ := uuid()
	result := f.adapter(t, f.claims[0], f.send(retry, "rollback"))
	if result["payload"].(map[string]any)["status"] != "rejected" {
		t.Fatal("rollback yielded success ACK")
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT next_seq::int FROM conversations WHERE conversation_id=$1`) != 2 {
		t.Fatal("rollback left effects or gap")
	}
}
func TestGroup500SingleLogicalMessageAndOutbox(t *testing.T) {
	f := newMessageFixture(t, 500)
	id, _ := uuid()
	if _, err := f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "group")); err != nil {
		t.Fatal(err)
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1`) != 1 {
		t.Fatal("GROUP persisted per member")
	}
}

package tests

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/core"
	"im-platform/backend/go/gateway"
	"im-platform/backend/go/shared"
	"net/http/httptest"
	"os"
	"reflect"
	"strings"
	"testing"
	"time"
)

type messagingHarness struct {
	db                                *pgxpool.Pool
	service                           *testService
	nc                                *nats.Conn
	users                             []string
	conversations                     []string
	tokens                            []string
	sender, receiver, other, outsider *websocket.Conn
	normal                            *messageNormalizer
}
type messageNormalizer struct {
	ids   map[string]string
	times map[string]string
}

func (n *messageNormalizer) check(t *testing.T, want, got any) {
	t.Helper()
	switch expected := want.(type) {
	case map[string]any:
		actual, ok := got.(map[string]any)
		if !ok || len(actual) != len(expected) {
			t.Fatalf("canonical object shape differs: expected keys %v, actual keys %v", reflect.ValueOf(expected).MapKeys(), reflect.ValueOf(got))
		}
		for k, v := range expected {
			n.check(t, v, actual[k])
		}
	case []any:
		actual, ok := got.([]any)
		if !ok || len(actual) != len(expected) {
			t.Fatal("canonical array differs")
		}
		for i, v := range expected {
			n.check(t, v, actual[i])
		}
	case string:
		actual, ok := got.(string)
		if !ok {
			t.Fatal("canonical string type differs")
		}
		if validUUID(expected) {
			if !validUUID(actual) {
				t.Fatal("invalid runtime UUID")
			}
			if prior, exists := n.ids[expected]; exists && prior != actual {
				t.Fatal("canonical identity changed")
			}
			n.ids[expected] = actual
		} else if _, err := time.Parse(time.RFC3339Nano, expected); err == nil {
			if _, err = time.Parse(time.RFC3339Nano, actual); err != nil {
				t.Fatal("invalid runtime time")
			}
			if prior, exists := n.times[expected]; exists && prior != actual {
				t.Fatal("committed timestamp changed")
			}
			n.times[expected] = actual
		} else if expected != actual {
			t.Fatalf("canonical scalar differs %q vs %q", expected, actual)
		}
	default:
		if !reflect.DeepEqual(want, got) {
			t.Fatalf("canonical value differs %v vs %v", want, got)
		}
	}
}
func newMessagingHarness(t *testing.T) *messagingHarness {
	t.Helper()
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL/NATS")
	}
	db, err := pgxpool.New(context.Background(), "")
	if err != nil {
		t.Fatal(err)
	}
	if err = db.Ping(context.Background()); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(db.Close)
	h := &messagingHarness{db: db, service: newService(db, []byte("test-only-signing-key-at-least-32-bytes")), nc: testNATS(t), normal: &messageNormalizer{ids: map[string]string{}, times: map[string]string{}}}
	for i := 0; i < 3; i++ {
		id, _ := shared.UUID()
		username := "msg" + strings.ReplaceAll(id, "-", "")
		r := call(t, h.service.handler, "POST", "/v1/auth/register", map[string]any{"username": username, "password": "fixture-password-not-a-real-secret", "displayName": "Message Fixture"}, "", nil)
		expect(t, r, 201)
		h.users = append(h.users, readResult(t, r)["user"].(map[string]any)["userId"].(string))
		login := call(t, h.service.handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": "fixture-password-not-a-real-secret", "clientType": "WEB", "deviceId": "msg-web", "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
		expect(t, login, 200)
		h.tokens = append(h.tokens, getToken(t, login))
		if i == 0 {
			desktop := call(t, h.service.handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": "fixture-password-not-a-real-secret", "clientType": "DESKTOP", "deviceId": "msg-desktop", "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
			expect(t, desktop, 200)
			h.tokens = append(h.tokens, getToken(t, desktop))
		}
	}
	// tokens: A WEB, A DESKTOP, B WEB, C WEB.
	friend := call(t, h.service.handler, "PUT", "/v1/friends/"+h.users[1], nil, h.tokens[0], nil)
	expect(t, friend, 201)
	conversation := readResult(t, friend)["directConversationId"].(string)
	h.conversations = append(h.conversations, conversation)
	h.normal.ids["30000000-0000-4000-8000-000000000001"] = conversation
	h.normal.ids["10000000-0000-4000-8000-000000000001"] = h.users[0]
	coreServer := httptest.NewServer(h.service.handler)
	t.Cleanup(coreServer.Close)
	handler, err := gateway.NewHandler(db, h.service.codec.Key, h.nc, coreServer.URL)
	if err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(handler)
	t.Cleanup(server.Close)
	bind := func(token string) *websocket.Conn {
		c := openFixtureSocket(t, "ws"+strings.TrimPrefix(server.URL, "http")+"/v1/ws")
		t.Cleanup(func() { c.Close() })
		id, _ := shared.UUID()
		if c.WriteJSON(frame("auth.bind", id, map[string]string{"accessToken": token})) != nil {
			t.Fatal("bind write")
		}
		v := readMessageFrame(t, c)
		if v["payload"].(map[string]any)["status"] != "bound" {
			t.Fatal("bind rejected")
		}
		return c
	}
	h.sender = bind(h.tokens[0])
	h.other = bind(h.tokens[1])
	h.receiver = bind(h.tokens[2])
	h.outsider = bind(h.tokens[3])
	t.Cleanup(func() {
		ctx := context.Background()
		for _, conv := range h.conversations {
			db.Exec(ctx, `DELETE FROM outbox_events WHERE conversation_id=$1`, conv)
			db.Exec(ctx, `DELETE FROM messages WHERE conversation_id=$1`, conv)
			db.Exec(ctx, `DELETE FROM friendships WHERE direct_conversation_id=$1`, conv)
			db.Exec(ctx, `DELETE FROM conversation_members WHERE conversation_id=$1`, conv)
			db.Exec(ctx, `DELETE FROM conversations WHERE conversation_id=$1`, conv)
		}
		for _, user := range h.users {
			db.Exec(ctx, `DELETE FROM outbox_events WHERE aggregate_id=$1 OR aggregate_id IN (SELECT session_id FROM sessions WHERE user_id=$1)`, user)
			db.Exec(ctx, `DELETE FROM user_sync_events WHERE user_id=$1`, user)
			db.Exec(ctx, `DELETE FROM sessions WHERE user_id=$1`, user)
			db.Exec(ctx, `DELETE FROM users WHERE user_id=$1`, user)
		}
	})
	return h
}
func readMessageFrame(t *testing.T, c *websocket.Conn) map[string]any {
	t.Helper()
	c.SetReadDeadline(time.Now().Add(5 * time.Second))
	var v map[string]any
	if err := c.ReadJSON(&v); err != nil {
		t.Fatal(err)
	}
	return v
}
func cloneFrame(v map[string]any) map[string]any {
	b, _ := json.Marshal(v)
	var result map[string]any
	json.Unmarshal(b, &result)
	return result
}
func (h *messagingHarness) input(v map[string]any) map[string]any {
	out := cloneFrame(v)
	p := out["payload"].(map[string]any)
	if id, ok := p["conversationId"].(string); ok {
		if actual, exists := h.normal.ids[id]; exists {
			p["conversationId"] = actual
		}
	}
	return out
}
func (h *messagingHarness) send(t *testing.T, v map[string]any, c *websocket.Conn) map[string]any {
	t.Helper()
	if err := c.WriteJSON(h.input(v)); err != nil {
		t.Fatal(err)
	}
	return readMessageFrame(t, c)
}
func (h *messagingHarness) rows(t *testing.T, conversation string) (messages, outbox, next int) {
	t.Helper()
	ctx := context.Background()
	if err := h.db.QueryRow(ctx, `SELECT count(*) FROM messages WHERE conversation_id=$1`, conversation).Scan(&messages); err != nil {
		t.Fatal(err)
	}
	if err := h.db.QueryRow(ctx, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1 AND event_type='message.created'`, conversation).Scan(&outbox); err != nil {
		t.Fatal(err)
	}
	if err := h.db.QueryRow(ctx, `SELECT next_seq FROM conversations WHERE conversation_id=$1`, conversation).Scan(&next); err != nil {
		t.Fatal(err)
	}
	return
}
func (h *messagingHarness) relay(t *testing.T) {
	t.Helper()
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	go func() { defer close(done); core.RelaySessionRevocations(ctx, h.db, h.nc) }()
	t.Cleanup(func() { cancel(); <-done })
}
func (h *messagingHarness) group(t *testing.T, count int) string {
	t.Helper()
	ctx := context.Background()
	conv, _ := shared.UUID()
	request, _ := shared.UUID()
	if _, err := h.db.Exec(ctx, `INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES($1,'GROUP',$2,$3)`, conv, h.users[0], request); err != nil {
		t.Fatal(err)
	}
	h.conversations = append(h.conversations, conv)
	for i := 0; i < count; i++ {
		var user string
		if i < 2 {
			user = h.users[i]
		} else {
			user, _ = shared.UUID()
			if _, err := h.db.Exec(ctx, `INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1::uuid,$1::text,'Group fixture','test-only')`, user); err != nil {
				t.Fatal(err)
			}
			h.users = append(h.users, user)
		}
		if _, err := h.db.Exec(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'MEMBER')`, conv, user); err != nil {
			t.Fatal(err)
		}
	}
	return conv
}
func TestCanonicalLiveMessageSendFixtures(t *testing.T) {
	all := readFixture(t, "../../../contracts/fixtures/websocket/golden.json")
	for _, id := range []string{"durable-send-and-created", "idempotent-retry", "same-request-different-conversation", "group-single-message", "non-member-send", "conflicting-retry", "rollback-before-ack"} {
		t.Run(id, func(t *testing.T) {
			h := newMessagingHarness(t)
			scenario := fixture(t, all, id)
			if id == "same-request-different-conversation" {
				h.normal.ids["30000000-0000-4000-8000-000000000002"] = h.group(t, 2)
			}
			if id == "group-single-message" {
				h.normal.ids["30000000-0000-4000-8000-000000000001"] = h.group(t, 500)
			}
			if id == "rollback-before-ack" {
				conv := h.conversations[0]
				name := "fixtureprobe" + fmt.Sprint(time.Now().UnixNano())
				q := fmt.Sprintf(`CREATE FUNCTION %s() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.conversation_id='%s'::uuid THEN RAISE EXCEPTION 'injected rollback'; END IF; RETURN NEW; END $$; CREATE TRIGGER %s BEFORE INSERT ON outbox_events FOR EACH ROW EXECUTE FUNCTION %s()`, name, conv, name, name)
				if _, err := h.db.Exec(context.Background(), q); err != nil {
					t.Fatal(err)
				}
				t.Cleanup(func() {
					h.db.Exec(context.Background(), fmt.Sprintf(`DROP TRIGGER IF EXISTS %s ON outbox_events;DROP FUNCTION IF EXISTS %s()`, name, name))
				})
			}
			socket := h.sender
			if id == "non-member-send" {
				socket = h.outsider
			}
			for _, step := range scenario.Steps {
				ack := h.send(t, step.In, socket)
				h.normal.check(t, step.Out[0], ack)
				if id == "durable-send-and-created" {
					m, o, n := h.rows(t, h.conversations[0])
					if m != 1 || o != 1 || n != 2 {
						t.Fatal("ACK before durable rows")
					}
					h.relay(t)
					h.normal.check(t, step.Out[1], readMessageFrame(t, h.receiver))
					h.normal.check(t, step.Out[1], readMessageFrame(t, h.other))
					for _, c := range []*websocket.Conn{h.sender, h.outsider} {
						ping, _ := shared.UUID()
						c.WriteJSON(frame("ping", ping, map[string]any{}))
						if readMessageFrame(t, c)["type"] != "pong" {
							t.Fatal("origin/wrong Conversation event")
						}
					}
				}
			}
			for _, conv := range h.conversations {
				m, o, _ := h.rows(t, conv)
				want := 1
				if id == "group-single-message" && conv == h.conversations[0] {
					want = 0
				}
				if id == "non-member-send" || id == "rollback-before-ack" {
					want = 0
				}
				if m != want || o != want {
					t.Fatalf("fixture %s logical effects %d/%d want %d", id, m, o, want)
				}
			}
		})
	}
}
func TestCanonicalDuplicateOutOfOrderAndSyncRecovery(t *testing.T) {
	all := readFixture(t, "../../../contracts/fixtures/websocket/golden.json")
	for _, id := range []string{"duplicate-fanout", "out-of-order-fanout", "wrong-conversation-fanout"} {
		t.Run(id, func(t *testing.T) {
			h := newMessagingHarness(t)
			scenario := fixture(t, all, id)
			if scenario.ID != id {
				t.Fatal("canonical scenario unavailable")
			}
			if id == "wrong-conversation-fanout" {
				conv := h.group(t, 2)
				h.normal.ids["30000000-0000-4000-8000-000000000002"] = conv
				if _, err := h.db.Exec(context.Background(), `DELETE FROM conversation_members WHERE conversation_id=$1 AND user_id=$2`, conv, h.users[1]); err != nil {
					t.Fatal(err)
				}
				if _, err := h.db.Exec(context.Background(), `INSERT INTO conversation_members(conversation_id,user_id,role) VALUES($1,$2,'MEMBER')`, conv, h.users[2]); err != nil {
					t.Fatal(err)
				}
				input := cloneFrame(fixture(t, all, "durable-send-and-created").Steps[0].In)
				input["requestId"] = scenario.Steps[0].In["requestId"]
				input["payload"].(map[string]any)["conversationId"] = conv
				h.send(t, input, h.sender)
				h.relay(t)
				h.normal.check(t, scenario.Steps[0].In, readMessageFrame(t, h.outsider))
				h.normal.check(t, scenario.Steps[0].In, readMessageFrame(t, h.other))
				ping, _ := shared.UUID()
				h.receiver.WriteJSON(frame("ping", ping, map[string]any{}))
				if readMessageFrame(t, h.receiver)["type"] != "pong" {
					t.Fatal("wrong Conversation delivered to nonmember")
				}
				m, o, _ := h.rows(t, conv)
				if m != 1 || o != 1 {
					t.Fatal("wrong Conversation fixture persistence")
				}
				return
			}
			send := fixture(t, all, "durable-send-and-created").Steps[0].In
			first := h.send(t, send, h.sender)
			h.normal.check(t, fixture(t, all, "durable-send-and-created").Steps[0].Out[0], first)
			var payload []byte
			if err := h.db.QueryRow(context.Background(), `SELECT payload FROM outbox_events WHERE conversation_id=$1 AND event_type='message.created'`, h.conversations[0]).Scan(&payload); err != nil {
				t.Fatal(err)
			}
			events := [][]byte{payload}
			if id == "out-of-order-fanout" {
				second := cloneFrame(send)
				second["requestId"] = "40000000-0000-4000-8000-000000000002"
				second["payload"].(map[string]any)["content"] = scenario.Steps[0].In["payload"].(map[string]any)["content"]
				h.send(t, second, h.sender)
				var b []byte
				if err := h.db.QueryRow(context.Background(), `SELECT payload FROM outbox_events WHERE conversation_id=$1 AND event_type='message.created' ORDER BY created_at DESC LIMIT 1`, h.conversations[0]).Scan(&b); err != nil {
					t.Fatal(err)
				}
				events = [][]byte{b, payload}
			}
			if id == "duplicate-fanout" {
				events = [][]byte{payload, payload}
			}
			materialized := map[string]bool{}
			sequences := map[int]bool{}
			expectedFrames := []map[string]any{}
			for _, step := range scenario.Steps {
				expectedFrames = append(expectedFrames, step.Out...)
			}
			for eventIndex, data := range events {
				h.nc.Publish("message.created."+h.users[1], data)
				h.nc.Flush()
				actual := readMessageFrame(t, h.receiver)
				h.normal.check(t, expectedFrames[eventIndex], actual)
				p := actual["payload"].(map[string]any)
				materialized[p["conversationId"].(string)+":"+actual["requestId"].(string)] = true
				sequences[int(p["seq"].(float64))] = true
			}
			want := 1
			if id == "out-of-order-fanout" {
				want = 2
			}
			if len(materialized) != want {
				t.Fatal("duplicate logical materialization")
			}
			// A committed next Message is deliberately never published; canonical
			// ConversationRequest/Page fills that real delivery gap without NATS.
			missed := cloneFrame(send)
			request, _ := shared.UUID()
			missed["requestId"] = request
			missed["payload"].(map[string]any)["content"].(map[string]any)["text"] = "missed"
			h.send(t, missed, h.sender)
			historyReq, _ := shared.UUID()
			w := call(t, h.service.handler, "POST", "/__core/history", map[string]any{"syncVersion": "1.0", "type": "sync.conversation.request", "requestId": historyReq, "conversationId": h.conversations[0], "afterSeq": 0, "limit": 10}, h.tokens[2], nil)
			expect(t, w, 200)
			page := readResult(t, w)
			if page["syncVersion"] != "1.0" || page["type"] != "sync.conversation.page" || page["conversationId"] != h.conversations[0] || page["requestId"] != historyReq || page["hasMore"] != false {
				t.Fatal("canonical history envelope")
			}
			messages := page["messages"].([]any)
			for i, v := range messages {
				m := v.(map[string]any)
				if len(m) != 7 || int(m["seq"].(float64)) != i+1 {
					t.Fatal("history shape/order gap")
				}
				materialized[m["conversationId"].(string)+":"+m["requestId"].(string)] = true
			}
			if len(messages) != want+1 || len(materialized) != want+1 {
				t.Fatal("Sync failed to close missed gap")
			}
			denied := call(t, h.service.handler, "POST", "/__core/history", map[string]any{"syncVersion": "1.0", "type": "sync.conversation.request", "requestId": historyReq, "conversationId": h.conversations[0], "afterSeq": 0, "limit": 10}, h.tokens[3], nil)
			expect(t, denied, 403)
		})
	}
}

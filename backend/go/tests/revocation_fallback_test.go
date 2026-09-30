package tests

import (
	"context"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/gateway"
	"im-platform/backend/go/shared"
)

// No NATS connection/relay is provided to this Gateway. The safety watch must
// deliver the committed Core reason even when the realtime notification is lost.
func TestPostgresRevocationFallbackWithoutNATS(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	db, err := pgxpool.New(context.Background(), "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	if err = db.Ping(context.Background()); err != nil {
		t.Fatal(err)
	}
	key := []byte("test-only-signing-key-at-least-32-bytes")
	s := newService(db, key)
	h, err := gateway.NewHandler(db, key, nil, "http://localhost:1")
	if err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(h)
	defer server.Close()
	wsURL := "ws" + strings.TrimPrefix(server.URL, "http") + "/v1/ws"
	for _, reason := range []string{"REPLACED", "LOGOUT", "REPLACED_THEN_LOGOUT"} {
		t.Run(reason, func(t *testing.T) {
			random, _ := shared.RandomToken(8)
			username := "fallback" + strings.ToLower(random[:10])
			password := "fixture-password-not-a-real-secret"
			registered := call(t, s.handler, "POST", "/v1/auth/register", map[string]any{"username": username, "password": password, "displayName": "Fallback"}, "", nil)
			expect(t, registered, 201)
			userID := readResult(t, registered)["user"].(map[string]any)["userId"].(string)
			defer func() {
				ctx := context.Background()
				_, _ = db.Exec(ctx, "DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked')", userID)
				_, _ = db.Exec(ctx, "DELETE FROM user_sync_events WHERE user_id=$1", userID)
				_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", userID)
				_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", userID)
			}()
			login := func(device string) *httptest.ResponseRecorder {
				return call(t, s.handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": password, "clientType": "WEB", "deviceId": device, "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
			}
			first := login("fallback-first")
			expect(t, first, 200)
			token := getToken(t, first)
			sid := getSession(t, first)["sessionId"].(string)
			conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
			if err != nil {
				t.Fatal(err)
			}
			defer conn.Close()
			_ = conn.WriteJSON(frame("auth.bind", "80000000-0000-4000-8000-000000000020", map[string]string{"accessToken": token}))
			var ack map[string]any
			if err = conn.ReadJSON(&ack); err != nil {
				t.Fatal(err)
			}
			if ack["payload"].(map[string]any)["status"] != "bound" {
				t.Fatalf("bind: %v", ack)
			}
			if strings.HasPrefix(reason, "REPLACED") {
				replacement := login("fallback-replacement")
				expect(t, replacement, 200)
				if reason == "REPLACED_THEN_LOGOUT" {
					expect(t, call(t, s.handler, "POST", "/v1/auth/logout", map[string]any{}, getToken(t, replacement), nil), 204)
					reason = "REPLACED"
				}
			} else {
				expect(t, call(t, s.handler, "POST", "/v1/auth/logout", map[string]any{}, token, nil), 204)
			}
			var committed string
			if err = db.QueryRow(context.Background(), "SELECT payload->>'reason' FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked' AND payload->>'sessionId'=$2", userID, sid).Scan(&committed); err != nil || committed != reason {
				t.Fatalf("Core committed reason %q: %v", committed, err)
			}
			_ = conn.SetReadDeadline(time.Now().Add(3 * time.Second))
			var event map[string]any
			if err = conn.ReadJSON(&event); err != nil {
				t.Fatal(err)
			}
			payload := event["payload"].(map[string]any)
			if event["type"] != "session.revoked" || payload["sessionId"] != sid || payload["reason"] != reason {
				t.Fatalf("fallback reason: got %v want %s", event, reason)
			}
			if err = conn.ReadJSON(&event); err == nil {
				t.Fatal("revoked socket remained open")
			}
			stale, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
			if err != nil {
				t.Fatal(err)
			}
			defer stale.Close()
			_ = stale.SetReadDeadline(time.Now().Add(3 * time.Second))
			_ = stale.WriteJSON(frame("auth.bind", "80000000-0000-4000-8000-000000000021", map[string]string{"accessToken": token}))
			if err = stale.ReadJSON(&ack); err != nil {
				t.Fatal(err)
			}
			if ack["payload"].(map[string]any)["status"] != "rejected" {
				t.Fatal("old credential rebound")
			}
		})
	}
}

// Token expiry and Session authority failure must still notify and close, even
// without a business revocation fact or realtime event.
func TestPostgresFallbackExpiryAndDatabaseFailureClose(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	for _, cause := range []string{"expiry", "database"} {
		t.Run(cause, func(t *testing.T) {
			ctx := context.Background()
			db, err := pgxpool.New(ctx, "")
			if err != nil {
				t.Fatal(err)
			}
			defer db.Close()
			if err = db.Ping(ctx); err != nil {
				t.Fatal(err)
			}
			gatewayDB, err := pgxpool.New(ctx, "")
			if err != nil {
				t.Fatal(err)
			}
			defer gatewayDB.Close()
			key := []byte("test-only-signing-key-at-least-32-bytes")
			s := newService(db, key)
			random, _ := shared.RandomToken(8)
			username := "failclose" + strings.ToLower(random[:10])
			password := "fixture-password-not-a-real-secret"
			registered := call(t, s.handler, "POST", "/v1/auth/register", map[string]any{"username": username, "password": password, "displayName": "Close control"}, "", nil)
			expect(t, registered, 201)
			uid := readResult(t, registered)["user"].(map[string]any)["userId"].(string)
			defer func() {
				_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", uid)
				_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", uid)
			}()
			login := call(t, s.handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": password, "clientType": "WEB", "deviceId": "control", "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
			expect(t, login, 200)
			token := getToken(t, login)
			if cause == "expiry" {
				claims, err := s.codec.Parse(token)
				if err != nil {
					t.Fatal(err)
				}
				claims.ExpiresAt = time.Now().Unix() + 2
				token, err = s.codec.Sign(claims)
				if err != nil {
					t.Fatal(err)
				}
			}
			h, err := gateway.NewHandler(gatewayDB, key, nil, "http://localhost:1")
			if err != nil {
				t.Fatal(err)
			}
			server := httptest.NewServer(h)
			defer server.Close()
			conn, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http")+"/v1/ws", nil)
			if err != nil {
				t.Fatal(err)
			}
			defer conn.Close()
			_ = conn.WriteJSON(frame("auth.bind", "80000000-0000-4000-8000-000000000022", map[string]string{"accessToken": token}))
			var event map[string]any
			if err = conn.ReadJSON(&event); err != nil {
				t.Fatal(err)
			}
			if event["payload"].(map[string]any)["status"] != "bound" {
				t.Fatal("bind failed")
			}
			if cause == "database" {
				gatewayDB.Close()
			}
			_ = conn.SetReadDeadline(time.Now().Add(4 * time.Second))
			if err = conn.ReadJSON(&event); err != nil {
				t.Fatal(err)
			}
			if event["type"] != "session.revoked" || event["payload"].(map[string]any)["reason"] != "REVOKED" {
				t.Fatalf("unsafe cause %s: %v", cause, event)
			}
			if err = conn.ReadJSON(&event); err == nil {
				t.Fatal("unsafe socket remained open")
			}
		})
	}
}

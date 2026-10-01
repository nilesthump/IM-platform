package tests

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/core"
	"im-platform/backend/go/gateway"
	"im-platform/backend/go/shared"
)

func call(t *testing.T, h http.Handler, method, path string, body any, token string, cookie *http.Cookie) *httptest.ResponseRecorder {
	t.Helper()
	var b []byte
	if body != nil {
		b, _ = json.Marshal(body)
	}
	r := httptest.NewRequest(method, path, bytes.NewReader(b))
	if body != nil {
		r.Header.Set("Content-Type", "application/json")
	}
	if token != "" {
		r.Header.Set("Authorization", "Bearer "+token)
	}
	if cookie != nil {
		r.AddCookie(cookie)
	}
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w
}

func readResult(t *testing.T, w *httptest.ResponseRecorder) map[string]any {
	t.Helper()
	var v map[string]any
	if err := json.Unmarshal(w.Body.Bytes(), &v); err != nil {
		t.Fatal(err)
	}
	return v
}
func getToken(t *testing.T, w *httptest.ResponseRecorder) string {
	t.Helper()
	return readResult(t, w)["tokens"].(map[string]any)["accessToken"].(string)
}
func getSession(t *testing.T, w *httptest.ResponseRecorder) map[string]any {
	t.Helper()
	return readResult(t, w)["session"].(map[string]any)
}
func expect(t *testing.T, w *httptest.ResponseRecorder, status int) {
	t.Helper()
	if w.Code != status {
		t.Fatalf("status %d want %d: %s", w.Code, status, w.Body.String())
	}
}

func TestPostgresAuthSessionAndWSS(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	if err = db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	s := newService(db, []byte("test-only-signing-key-at-least-32-bytes"))
	coreServer := httptest.NewServer(s.handler)
	defer coreServer.Close()
	h, err := gateway.NewHandler(s.db, s.codec.Key, testNATS(t), coreServer.URL)
	if err != nil {
		t.Fatal(err)
	}
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = "nats://127.0.0.1:4222"
	}
	nc, err := nats.Connect(natsURL)
	if err != nil {
		t.Fatal(err)
	}
	defer nc.Close()
	if err = nc.Flush(); err != nil {
		t.Fatal(err)
	}
	relayCtx, stopRelay := context.WithCancel(ctx)
	defer stopRelay()
	go core.RelaySessionRevocations(relayCtx, db, nc)
	handler := s.handler
	random, _ := shared.RandomToken(8)
	username := "auth" + strings.ToLower(random[:10])
	password := "fixture-password-not-a-real-secret"
	w := call(t, handler, "POST", "/v1/auth/register", map[string]any{"username": username, "password": password, "displayName": "Auth Test"}, "", nil)
	expect(t, w, 201)
	userID := readResult(t, w)["user"].(map[string]any)["userId"].(string)
	defer func() {
		_, _ = db.Exec(ctx, "DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked')", userID)
		_, _ = db.Exec(ctx, "DELETE FROM user_sync_events WHERE user_id=$1", userID)
		_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", userID)
		_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", userID)
	}()
	login := func(typ, device string) *httptest.ResponseRecorder {
		return call(t, handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": password, "clientType": typ, "deviceId": device, "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
	}
	web := login("WEB", "browser-1")
	expect(t, web, 200)
	webToken := getToken(t, web)
	webSession := getSession(t, web)
	search := call(t, handler, "GET", "/v1/users/search?username="+strings.ToUpper(username), nil, webToken, nil)
	expect(t, search, 200)
	users := readResult(t, search)["users"].([]any)
	if len(users) != 1 || users[0].(map[string]any)["userId"] != userID {
		t.Fatalf("search mismatch: %v", users)
	}
	expect(t, call(t, handler, "GET", "/v1/users/search?username=missinguser", nil, webToken, nil), 200)
	if strings.Contains(web.Body.String(), "refreshToken\"") {
		t.Fatal("WEB refresh token leaked into JSON")
	}
	if len(web.Result().Cookies()) != 1 || !web.Result().Cookies()[0].HttpOnly || !web.Result().Cookies()[0].Secure {
		t.Fatal("WEB refresh cookie lacks security attributes")
	}
	badLogin := call(t, handler, "POST", "/v1/auth/login", map[string]any{"username": username, "password": "wrong-password-not-secret", "clientType": "WEB", "deviceId": "browser-1", "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
	expect(t, badLogin, 401)
	if strings.Contains(badLogin.Body.String(), "wrong-password-not-secret") {
		t.Fatal("password appeared in error")
	}
	query := call(t, handler, "GET", "/v1/users/me?accessToken=untrusted-secret", nil, "", nil)
	expect(t, query, 400)
	if strings.Contains(query.Body.String(), "untrusted-secret") {
		t.Fatal("query secret appeared in error")
	}
	desktop := login("DESKTOP", "desktop-1")
	expect(t, desktop, 200)
	desktopToken := getToken(t, desktop)
	mobile := login("MOBILE", "mobile-1")
	expect(t, mobile, 200)
	mobileRefresh := readResult(t, mobile)["tokens"].(map[string]any)["refreshToken"].(string)
	// Exercise real WebSocket pre-bind rejection and bind/replace notification.
	server := httptest.NewServer(h)
	defer server.Close()
	wsURL := "ws" + strings.TrimPrefix(server.URL, "http") + "/v1/ws"
	pre, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatal(err)
	}
	_ = pre.WriteJSON(frame("message.send", "80000000-0000-4000-8000-000000000001", map[string]any{"conversationId": userID, "content": map[string]string{"kind": "TEXT", "text": "x"}}))
	var rejected map[string]any
	if err = pre.ReadJSON(&rejected); err != nil {
		t.Fatal(err)
	}
	if rejected["type"] != "message.ack" || rejected["payload"].(map[string]any)["status"] != "rejected" {
		t.Fatalf("prebind accepted: %v", rejected)
	}
	_ = pre.Close()
	conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	_ = conn.WriteJSON(frame("auth.bind", "80000000-0000-4000-8000-000000000002", map[string]string{"accessToken": webToken}))
	var ack map[string]any
	if err = conn.ReadJSON(&ack); err != nil {
		t.Fatal(err)
	}
	if ack["type"] != "auth.ack" || ack["payload"].(map[string]any)["status"] != "bound" {
		t.Fatalf("bind failed: %v", ack)
	}
	// A bound operation must not query PostgreSQL (canonical7.3). An exclusive
	// Session table lock makes a regression block rather than silently pass.
	lock, err := db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	if _, err = lock.Exec(ctx, "LOCK TABLE sessions IN ACCESS EXCLUSIVE MODE"); err != nil {
		t.Fatal(err)
	}
	_ = conn.SetReadDeadline(time.Now().Add(500 * time.Millisecond))
	_ = conn.WriteJSON(frame("message.send", "80000000-0000-4000-8000-000000000010", map[string]any{}))
	var operation map[string]any
	err = conn.ReadJSON(&operation)
	_ = lock.Rollback(ctx)
	if err != nil {
		t.Fatalf("bound operation blocked by PostgreSQL: %v", err)
	}
	if operation["type"] != "message.ack" || operation["payload"].(map[string]any)["error"].(map[string]any)["code"] != "VALIDATION_FAILED" {
		t.Fatalf("bound operation response: %v", operation)
	}
	_ = conn.SetReadDeadline(time.Time{})
	web2 := login("WEB", "browser-2")
	expect(t, web2, 200)
	if getSession(t, web2)["sessionEpoch"] != float64(2) {
		t.Fatal("WEB epoch did not advance")
	}
	oldCookie := web.Result().Cookies()[0]
	webRefreshBody := map[string]any{"clientType": "WEB", "deviceId": "browser-1", "clientVersion": "1.0.0", "protocolVersion": "1"}
	expect(t, call(t, handler, "POST", "/v1/auth/refresh/web", webRefreshBody, "", oldCookie), 401)
	_ = conn.SetReadDeadline(time.Now().Add(3 * time.Second))
	var revoked map[string]any
	if err = conn.ReadJSON(&revoked); err != nil {
		t.Fatal(err)
	}
	if revoked["type"] != "session.revoked" || revoked["payload"].(map[string]any)["reason"] != "REPLACED" {
		t.Fatalf("revocation missing: %v", revoked)
	}
	var closed map[string]any
	if err = conn.ReadJSON(&closed); err == nil {
		t.Fatal("replaced socket stayed open")
	}
	expect(t, call(t, handler, "GET", "/v1/users/me", nil, webToken, nil), 401)
	expect(t, call(t, handler, "GET", "/v1/users/me", nil, desktopToken, nil), 200)
	// Same-slot concurrent logins must serialize under the PostgreSQL user lock.
	var wg sync.WaitGroup
	results := make(chan *httptest.ResponseRecorder, 2)
	for i := 0; i < 2; i++ {
		wg.Add(1)
		go func(i int) { defer wg.Done(); results <- login("WEB", fmt.Sprintf("browser-%d", i+3)) }(i)
	}
	wg.Wait()
	close(results)
	epochs := map[float64]bool{}
	for r := range results {
		expect(t, r, 200)
		epochs[getSession(t, r)["sessionEpoch"].(float64)] = true
	}
	if !epochs[3] || !epochs[4] {
		t.Fatalf("concurrent epochs: %v", epochs)
	}
	// Native refresh rotates the stored hash and rejects reuse.
	refreshBody := map[string]any{"clientType": "MOBILE", "deviceId": "mobile-1", "clientVersion": "1.0.0", "protocolVersion": "1", "refreshToken": mobileRefresh}
	rotated := call(t, handler, "POST", "/v1/auth/refresh/native", refreshBody, "", nil)
	expect(t, rotated, 200)
	expect(t, call(t, handler, "POST", "/v1/auth/refresh/native", refreshBody, "", nil), 401)
	newRefresh := readResult(t, rotated)["tokens"].(map[string]any)["refreshToken"].(string)
	mobileSocket, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatal(err)
	}
	defer mobileSocket.Close()
	_ = mobileSocket.WriteJSON(frame("auth.bind", "80000000-0000-4000-8000-000000000011", map[string]string{"accessToken": getToken(t, rotated)}))
	var mobileAck map[string]any
	if err = mobileSocket.ReadJSON(&mobileAck); err != nil {
		t.Fatal(err)
	}
	if mobileAck["payload"].(map[string]any)["status"] != "bound" {
		t.Fatal("mobile bind failed")
	}
	logout := call(t, handler, "POST", "/v1/auth/logout", nil, getToken(t, rotated), nil)
	expect(t, logout, 204)
	_ = mobileSocket.SetReadDeadline(time.Now().Add(3 * time.Second))
	var logoutEvent map[string]any
	if err = mobileSocket.ReadJSON(&logoutEvent); err != nil {
		t.Fatal(err)
	}
	if logoutEvent["type"] != "session.revoked" || logoutEvent["payload"].(map[string]any)["reason"] != "LOGOUT" {
		t.Fatalf("logout revocation: %v", logoutEvent)
	}
	if err = mobileSocket.ReadJSON(&closed); err == nil {
		t.Fatal("logout socket stayed open")
	}

	refreshBody["refreshToken"] = newRefresh
	expect(t, call(t, handler, "POST", "/v1/auth/refresh/native", refreshBody, "", nil), 401)
	var status string
	var stored *string
	err = db.QueryRow(ctx, "SELECT status,refresh_token_hash FROM sessions WHERE user_id=$1 AND client_type='MOBILE'", userID).Scan(&status, &stored)
	if err != nil || status != "REVOKED" || stored != nil {
		t.Fatalf("logout state: %s %v %v", status, stored, err)
	}
	var n int
	err = db.QueryRow(ctx, "SELECT count(*) FROM outbox_events WHERE aggregate_type='session' AND aggregate_id=$1", webSession["sessionId"]).Scan(&n)
	if err != nil || n != 1 {
		t.Fatalf("replacement outbox: %d %v", n, err)
	}
}

package main

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
)

func TestTokenTamperAndExpiry(t *testing.T) {
	s := &authService{key: []byte("test-only-signing-key-at-least-32-bytes"), now: func() time.Time { return time.Unix(1000, 0) }}
	c := claims{"10000000-0000-4000-8000-000000000001", "50000000-0000-4000-8000-000000000001", "WEB", 1, 999, 1001}
	token, err := s.sign(c)
	if err != nil {
		t.Fatal(err)
	}
	if _, err = s.parse(token); err != nil {
		t.Fatal(err)
	}
	if _, err = s.parse(token + "x"); err == nil {
		t.Fatal("tampered signature accepted")
	}
	s.now = func() time.Time { return time.Unix(1001, 0) }
	if _, err = s.parse(token); err == nil || err.(apiError).code != "AUTH_TOKEN_EXPIRED" {
		t.Fatalf("expired token: %v", err)
	}
}

func TestConfigReadsExternalCredentialFiles(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(dir+"/pg_password", []byte("local-test-password\n"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(dir+"/jwt_key", []byte("test-only-signing-key-at-least-32-bytes\n"), 0600); err != nil {
		t.Fatal(err)
	}
	config := []byte(`{"postgresHost":"localhost","postgresPort":5432,"postgresUser":"test","postgresDatabase":"test","postgresPasswordFile":"pg_password","jwtSigningKeyFile":"jwt_key","coreUrl":"http://localhost:8080","natsUrl":"nats://localhost:4222"}`)
	if err := os.WriteFile(dir+"/config.json", config, 0600); err != nil {
		t.Fatal(err)
	}
	_, key, pg, err := readConfig(dir + "/config.json")
	if err != nil {
		t.Fatal(err)
	}
	if string(key) != "test-only-signing-key-at-least-32-bytes" || pg.ConnConfig.Password != "local-test-password" {
		t.Fatal("credential files were not loaded")
	}
	if strings.Contains(string(config), "local-test-password") || strings.Contains(string(config), string(key)) {
		t.Fatal("credential embedded in configuration")
	}
	if err := os.Remove(dir + "/jwt_key"); err != nil {
		t.Fatal(err)
	}
	if _, _, _, err := readConfig(dir + "/config.json"); err == nil {
		t.Fatal("missing signing key accepted")
	}
}

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
	s := &authService{db: db, key: []byte("test-only-signing-key-at-least-32-bytes"), now: time.Now}
	h := newHub(s)
	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		natsURL = "nats://127.0.0.1:4222"
	}
	nc, err := nats.Connect(natsURL)
	if err != nil {
		t.Fatal(err)
	}
	defer nc.Close()
	_, err = nc.Subscribe("session.revoked", func(m *nats.Msg) {
		var v struct {
			SessionID string `json:"sessionId"`
			Reason    string `json:"reason"`
		}
		if json.Unmarshal(m.Data, &v) == nil {
			h.revoke(v.SessionID, v.Reason)
		}
	})
	if err != nil {
		t.Fatal(err)
	}
	if err = nc.Flush(); err != nil {
		t.Fatal(err)
	}
	relayCtx, stopRelay := context.WithCancel(ctx)
	defer stopRelay()
	go relaySessionRevocations(relayCtx, db, nc)
	handler := s.handler()
	random, _ := randomToken(8)
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
	server := httptest.NewServer(http.HandlerFunc(h.serve))
	defer server.Close()
	wsURL := "ws" + strings.TrimPrefix(server.URL, "http")
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
	logout := call(t, handler, "POST", "/v1/auth/logout", nil, getToken(t, rotated), nil)
	expect(t, logout, 204)
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
	// A failed revocation side effect rolls back its Session change.
	tx, err := db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	_, err = tx.Exec(ctx, "UPDATE sessions SET status='REVOKED' WHERE user_id=$1 AND client_type='DESKTOP'", userID)
	if err != nil {
		t.Fatal(err)
	}
	err = writeRevocation(ctx, tx, "00000000-0000-4000-8000-000000000000", getSession(t, desktop)["sessionId"].(string), "REVOKED")
	if err == nil {
		t.Fatal("expected foreign-key failure")
	}
	if err := tx.Rollback(ctx); err != nil {
		t.Fatal(err)
	}
	var desktopStatus string
	err = db.QueryRow(ctx, "SELECT status FROM sessions WHERE user_id=$1 AND client_type='DESKTOP'", userID).Scan(&desktopStatus)
	if err != nil || desktopStatus != "ACTIVE" {
		t.Fatalf("rollback lost active session: %s %v", desktopStatus, err)
	}
}

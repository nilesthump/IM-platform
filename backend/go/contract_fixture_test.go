package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	"github.com/jackc/pgx/v5/pgxpool"
)

// These tests consume the versioned contract fixtures as input, rather than
// keeping a second copy of their expected HTTP and WSS outcomes in Go.
type fixtureDocument struct {
	Scenarios []fixtureScenario `json:"scenarios"`
}
type fixtureScenario struct {
	ID       string        `json:"id"`
	Polarity string        `json:"polarity"`
	Steps    []fixtureStep `json:"steps"`
}
type fixtureStep struct {
	Request  *fixtureRequest `json:"request"`
	Expected *struct {
		Status  int               `json:"status"`
		Body    map[string]any    `json:"body"`
		Headers map[string]string `json:"headers"`
	} `json:"expected"`
	In  map[string]any   `json:"in"`
	Out []map[string]any `json:"out"`
}
type fixtureRequest struct {
	Method  string            `json:"method"`
	Path    string            `json:"path"`
	Headers map[string]string `json:"headers"`
	Query   map[string]string `json:"query"`
	Body    map[string]any    `json:"body"`
}

func readFixture(t *testing.T, path string) map[string]fixtureScenario {
	t.Helper()
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var doc fixtureDocument
	if err := json.Unmarshal(b, &doc); err != nil {
		t.Fatal(err)
	}
	out := make(map[string]fixtureScenario, len(doc.Scenarios))
	for _, s := range doc.Scenarios {
		if _, exists := out[s.ID]; exists {
			t.Fatalf("duplicate fixture %s", s.ID)
		}
		out[s.ID] = s
	}
	return out
}

func fixture(t *testing.T, all map[string]fixtureScenario, id string) fixtureScenario {
	t.Helper()
	s, ok := all[id]
	if !ok {
		t.Fatalf("canonical fixture %s missing", id)
	}
	return s
}

type fixtureNormalizer struct {
	username string
	ids      map[string]string
	tokens   map[string]string
}

func newFixtureNormalizer(username string) *fixtureNormalizer {
	return &fixtureNormalizer{username: username, ids: make(map[string]string), tokens: make(map[string]string)}
}
func (n *fixtureNormalizer) check(t *testing.T, expected, actual any, path string) {
	t.Helper()
	switch e := expected.(type) {
	case map[string]any:
		a, ok := actual.(map[string]any)
		if !ok {
			t.Fatalf("%s: expected object, got %T", path, actual)
		}
		for key, value := range e {
			got, exists := a[key]
			if !exists {
				t.Fatalf("%s.%s missing in %v", path, key, a)
			}
			n.check(t, value, got, path+"."+key)
		}
	case []any:
		a, ok := actual.([]any)
		if !ok || len(a) != len(e) {
			t.Fatalf("%s: expected %d items, got %v", path, len(e), actual)
		}
		for i := range e {
			n.check(t, e[i], a[i], fmt.Sprintf("%s[%d]", path, i))
		}
	case string:
		a, ok := actual.(string)
		if !ok {
			t.Fatalf("%s: expected string, got %T", path, actual)
		}
		if validUUID(e) {
			if !validUUID(a) {
				t.Fatalf("%s: %q is not a UUID", path, a)
			}
			if old, exists := n.ids[e]; exists && old != a {
				t.Fatalf("%s: fixture ID changed", path)
			}
			n.ids[e] = a
		} else if strings.HasPrefix(e, "<") && strings.HasSuffix(e, ">") {
			if a == "" {
				t.Fatalf("%s: empty credential", path)
			}
			if old, exists := n.tokens[e]; exists && old != a {
				t.Fatalf("%s: fixture credential changed", path)
			}
			n.tokens[e] = a
		} else if e == "alice" && path != "body.error.message" {
			if a != n.username {
				t.Fatalf("%s: username %q, want %q", path, a, n.username)
			}
		} else if path == "body.requestId" {
			if !validUUID(a) {
				t.Fatalf("%s: request ID %q is not UUID", path, a)
			}
		} else if e != a {
			t.Fatalf("%s: got %q, want fixture %q", path, a, e)
		}
	default:
		if !reflect.DeepEqual(expected, actual) {
			t.Fatalf("%s: got %v, want fixture %v", path, actual, expected)
		}
	}
}

func fixtureBody(v map[string]any, username string) map[string]any {
	b, _ := json.Marshal(v)
	var out map[string]any
	_ = json.Unmarshal(b, &out)
	if u, ok := out["username"].(string); ok && strings.EqualFold(u, "alice") {
		if u == strings.ToUpper(u) {
			out["username"] = strings.ToUpper(username)
		} else {
			out["username"] = username
		}
	}
	return out
}

func runFixtureHTTP(t *testing.T, h http.Handler, st fixtureStep, n *fixtureNormalizer, token string, cookie *http.Cookie, bodyOverride map[string]any) *httptest.ResponseRecorder {
	t.Helper()
	if st.Request == nil || st.Expected == nil {
		t.Fatal("fixture is not an HTTP step")
	}
	r := st.Request
	path := r.Path
	if len(r.Query) != 0 {
		query := url.Values{}
		for k, v := range r.Query {
			if strings.EqualFold(v, "alice") {
				v = n.username
			}
			query.Set(k, v)
		}
		path += "?" + query.Encode()
	}
	body := fixtureBody(r.Body, n.username)
	if bodyOverride != nil {
		for k, v := range bodyOverride {
			body[k] = v
		}
	}
	w := call(t, h, r.Method, path, body, token, cookie)
	if w.Code != st.Expected.Status {
		t.Fatalf("%s %s: status %d, want fixture %d: %s", r.Method, path, w.Code, st.Expected.Status, w.Body.String())
	}
	if st.Expected.Body != nil {
		n.check(t, st.Expected.Body, readResult(t, w), "body")
	}
	if raw, ok := st.Expected.Headers["Set-Cookie"]; ok {
		cookies := w.Result().Cookies()
		if len(cookies) != 1 || cookies[0].Name != "__Host-im_refresh" || cookies[0].Value == "" || !cookies[0].Secure || !cookies[0].HttpOnly || cookies[0].Path != "/" || cookies[0].SameSite != http.SameSiteStrictMode {
			t.Fatalf("Set-Cookie does not match fixture %q: %v", raw, cookies)
		}
	}
	return w
}

func TestCanonicalAuthHTTPFixtures(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	positive := readFixture(t, "../../contracts/fixtures/auth-user-friend/positive.json")
	negative := readFixture(t, "../../contracts/fixtures/auth-user-friend/negative.json")
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	if err := db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	s := &authService{db: db, key: []byte("test-only-signing-key-at-least-32-bytes"), now: time.Now}
	h := s.handler()
	random, _ := randomToken(8)
	username := "fixture" + strings.ToLower(random[:10])
	n := newFixtureNormalizer(username)
	defer func() {
		var userID string
		if db.QueryRow(ctx, "SELECT user_id FROM users WHERE username=$1", username).Scan(&userID) == nil {
			_, _ = db.Exec(ctx, "DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked')", userID)
			_, _ = db.Exec(ctx, "DELETE FROM user_sync_events WHERE user_id=$1", userID)
			_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", userID)
			_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", userID)
		}
	}()
	reg := fixture(t, positive, "registration-and-authorized-user-search")
	runFixtureHTTP(t, h, reg.Steps[0], n, "", nil, nil)
	loginBody := fixtureBody(fixture(t, positive, "same-slot-login-replaces-only-that-slot").Steps[0].Request.Body, username)
	initial := call(t, h, "POST", "/v1/auth/login", loginBody, "", nil)
	expect(t, initial, 200)
	runFixtureHTTP(t, h, reg.Steps[1], n, getToken(t, initial), nil, nil)

	slots := fixture(t, positive, "same-slot-login-replaces-only-that-slot")
	// The search setup login occupies WEB epoch 1; reuse it as the fixture's first outcome.
	n.check(t, slots.Steps[0].Expected.Body, readResult(t, initial), "body")
	web1 := initial
	desktop := runFixtureHTTP(t, h, slots.Steps[1], n, "", nil, nil)
	web2 := runFixtureHTTP(t, h, slots.Steps[2], n, "", nil, nil)
	runFixtureHTTP(t, h, slots.Steps[3], n, getToken(t, web2), nil, nil)
	runFixtureHTTP(t, h, slots.Steps[4], n, getToken(t, desktop), nil, nil)
	oldWebToken := getToken(t, web1)
	var webCount, desktopCount int
	userID := getSession(t, web2)["userId"].(string)
	if err := db.QueryRow(ctx, "SELECT count(*) FROM sessions WHERE user_id=$1 AND client_type='WEB' AND status='ACTIVE'", userID).Scan(&webCount); err != nil || webCount != 1 {
		t.Fatalf("WEB slot state %d: %v", webCount, err)
	}
	if err := db.QueryRow(ctx, "SELECT count(*) FROM sessions WHERE user_id=$1 AND client_type='DESKTOP' AND status='ACTIVE'", userID).Scan(&desktopCount); err != nil || desktopCount != 1 {
		t.Fatalf("DESKTOP slot state %d: %v", desktopCount, err)
	}

	// Fixture preconditions explicitly start MOBILE at epoch 4 and WEB at epoch 5.
	mobileLogin := fixtureBody(slots.Steps[1].Request.Body, username)
	mobileLogin["clientType"] = "MOBILE"
	mobileLogin["deviceId"] = "mobile-1"
	var mobile *httptest.ResponseRecorder
	for i := 0; i < 4; i++ {
		mobile = call(t, h, "POST", "/v1/auth/login", mobileLogin, "", nil)
		expect(t, mobile, 200)
	}
	oldMobileRefresh := readResult(t, mobile)["tokens"].(map[string]any)["refreshToken"].(string)
	native := fixture(t, positive, "native-refresh-rotates-current-session-credential")
	rotated := runFixtureHTTP(t, h, native.Steps[0], n, "", nil, map[string]any{"refreshToken": oldMobileRefresh})
	newMobileRefresh := readResult(t, rotated)["tokens"].(map[string]any)["refreshToken"].(string)
	if oldMobileRefresh == newMobileRefresh {
		t.Fatal("native refresh did not rotate credential")
	}
	loginBody["deviceId"] = "browser-5"
	for i := 0; i < 3; i++ {
		web2 = call(t, h, "POST", "/v1/auth/login", loginBody, "", nil)
		expect(t, web2, 200)
	}
	web := fixture(t, positive, "web-refresh-rotates-secure-cookie")
	webRefreshed := runFixtureHTTP(t, h, web.Steps[0], n, "", web2.Result().Cookies()[0], nil)
	if web2.Result().Cookies()[0].Value == webRefreshed.Result().Cookies()[0].Value {
		t.Fatal("WEB refresh did not rotate cookie")
	}

	// Negative fixture requests are executed against the state just established.
	negativeCases := []string{"invalid-credentials", "token-in-query-rejected", "invalid-client-type", "refresh-client-type-mismatch", "unsupported-protocol-version", "authorization-binding-mismatch", "invalid-access-token", "expired-access-token", "username-already-exists", "web-refresh-missing-cookie", "native-refresh-missing-token", "stale-session-epoch-rejected", "revoked-refresh-token-rejected"}
	for _, id := range negativeCases {
		t.Run(id, func(t *testing.T) {
			st := fixture(t, negative, id).Steps[0]
			var token string
			var override map[string]any
			switch id {
			case "refresh-client-type-mismatch":
				override = map[string]any{"refreshToken": readResult(t, desktop)["tokens"].(map[string]any)["refreshToken"]}
			case "authorization-binding-mismatch":
				c, _ := s.parse(getToken(t, webRefreshed))
				c.SessionID, _ = uuid()
				token, _ = s.sign(c)
			case "invalid-access-token":
				token = getToken(t, webRefreshed) + "x"
			case "expired-access-token":
				c, _ := s.parse(getToken(t, webRefreshed))
				c.IssuedAt = time.Now().Add(-2 * time.Hour).Unix()
				c.ExpiresAt = time.Now().Add(-time.Hour).Unix()
				token, _ = s.sign(c)
			case "stale-session-epoch-rejected":
				token = oldWebToken
			case "revoked-refresh-token-rejected":
				override = map[string]any{"refreshToken": oldMobileRefresh}
			}
			runFixtureHTTP(t, h, st, n, token, nil, override)
		})
	}
	// Explicit logout from the positive fixture revokes both session and refresh.
	logout := fixture(t, positive, "logout-revokes-session-refresh-and-connection")
	runFixtureHTTP(t, h, logout.Steps[0], n, getToken(t, desktop), nil, nil)
	runFixtureHTTP(t, h, fixture(t, negative, "revoked-session-token").Steps[0], n, getToken(t, desktop), nil, nil)
	var status string
	var hash *string
	if err := db.QueryRow(ctx, "SELECT status,refresh_token_hash FROM sessions WHERE user_id=$1 AND client_type='DESKTOP'", userID).Scan(&status, &hash); err != nil || status != "REVOKED" || hash != nil {
		t.Fatalf("logout persistence: %s %v %v", status, hash, err)
	}
}

func openFixtureSocket(t *testing.T, wsURL string) *websocket.Conn {
	t.Helper()
	c, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatal(err)
	}
	return c
}

func assertWSSStep(t *testing.T, c *websocket.Conn, st fixtureStep, n *fixtureNormalizer, token string) {
	t.Helper()
	in := st.In
	if in == nil {
		t.Fatal("fixture lacks WSS input")
	}
	b, _ := json.Marshal(in)
	var sent map[string]any
	_ = json.Unmarshal(b, &sent)
	if token != "" {
		sent["payload"].(map[string]any)["accessToken"] = token
	}
	if err := c.WriteJSON(sent); err != nil {
		t.Fatal(err)
	}
	for _, expected := range st.Out {
		var actual map[string]any
		_ = c.SetReadDeadline(time.Now().Add(3 * time.Second))
		if err := c.ReadJSON(&actual); err != nil {
			t.Fatal(err)
		}
		n.check(t, expected, actual, "wss")
	}
}

func TestCanonicalWSSPrebindFixturesAndMalformedRequestID(t *testing.T) {
	all := readFixture(t, "../../contracts/fixtures/websocket/golden.json")
	server := httptest.NewServer(http.HandlerFunc(newHub(&authService{key: []byte("test-only-signing-key-at-least-32-bytes"), now: time.Now}).serve))
	defer server.Close()
	wsURL := "ws" + strings.TrimPrefix(server.URL, "http")
	n := newFixtureNormalizer("alice")
	for _, id := range []string{"ping-before-bind", "unauthenticated-send", "invalid-signature-bind", "expired-token-bind"} {
		t.Run(id, func(t *testing.T) {
			c := openFixtureSocket(t, wsURL)
			defer c.Close()
			var token string
			if id == "invalid-signature-bind" {
				token = "not-a-valid-JWT"
			}
			if id == "expired-token-bind" {
				s := &authService{key: []byte("test-only-signing-key-at-least-32-bytes"), now: time.Now}
				c, _ := s.sign(claims{"10000000-0000-4000-8000-000000000001", "50000000-0000-4000-8000-000000000001", "WEB", 1, time.Now().Add(-2 * time.Hour).Unix(), time.Now().Add(-time.Hour).Unix()})
				token = c
			}
			assertWSSStep(t, c, fixture(t, all, id).Steps[0], n, token)
		})
	}
	for _, typ := range []string{"ping", "auth.bind"} {
		t.Run("malformed-requestId-"+typ, func(t *testing.T) {
			c := openFixtureSocket(t, wsURL)
			defer c.Close()
			payload := map[string]any{}
			if typ == "auth.bind" {
				payload["accessToken"] = "not-a-valid-JWT"
			}
			if err := c.WriteJSON(frame(typ, "not-a-uuid", payload)); err != nil {
				t.Fatal(err)
			}
			_ = c.SetReadDeadline(time.Now().Add(2 * time.Second))
			var response map[string]any
			if err := c.ReadJSON(&response); err == nil {
				t.Fatalf("malformed requestId accepted: %v", response)
			}
		})
	}
}

func TestCanonicalWSSAuthSessionFixtures(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	all := readFixture(t, "../../contracts/fixtures/websocket/golden.json")
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	if err := db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	s := &authService{db: db, key: []byte("test-only-signing-key-at-least-32-bytes"), now: time.Now}
	hub := newHub(s)
	server := httptest.NewServer(http.HandlerFunc(hub.serve))
	defer server.Close()
	wsURL := "ws" + strings.TrimPrefix(server.URL, "http")
	random, _ := randomToken(8)
	username := "wssfixture" + strings.ToLower(random[:10])
	registration := call(t, s.handler(), "POST", "/v1/auth/register", map[string]any{"username": username, "password": "fixture-password-not-a-real-secret", "displayName": "Alice"}, "", nil)
	expect(t, registration, 201)
	userID := readResult(t, registration)["user"].(map[string]any)["userId"].(string)
	defer func() {
		_, _ = db.Exec(ctx, "DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked')", userID)
		_, _ = db.Exec(ctx, "DELETE FROM user_sync_events WHERE user_id=$1", userID)
		_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", userID)
		_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", userID)
	}()
	loginBody := map[string]any{"username": username, "password": "fixture-password-not-a-real-secret", "clientType": "WEB", "deviceId": "browser-1", "clientVersion": "1.0.0", "protocolVersion": "1"}
	first := call(t, s.handler(), "POST", "/v1/auth/login", loginBody, "", nil)
	expect(t, first, 200)
	firstToken := getToken(t, first)
	firstSession := getSession(t, first)["sessionId"].(string)
	n := newFixtureNormalizer(username)
	bound := openFixtureSocket(t, wsURL)
	defer bound.Close()
	assertWSSStep(t, bound, fixture(t, all, "bind-valid-session").Steps[0], n, firstToken)

	second := call(t, s.handler(), "POST", "/v1/auth/login", loginBody, "", nil)
	expect(t, second, 200)
	stale := openFixtureSocket(t, wsURL)
	defer stale.Close()
	assertWSSStep(t, stale, fixture(t, all, "stale-epoch-bind").Steps[0], n, firstToken)
	wrongClaims, err := s.parse(getToken(t, second))
	if err != nil {
		t.Fatal(err)
	}
	wrongClaims.ClientType = "DESKTOP"
	wrongToken, err := s.sign(wrongClaims)
	if err != nil {
		t.Fatal(err)
	}
	wrong := openFixtureSocket(t, wsURL)
	defer wrong.Close()
	assertWSSStep(t, wrong, fixture(t, all, "wrong-client-type-bind").Steps[0], n, wrongToken)

	// The golden revoked-socket case models a committed same-slot replacement event.
	hub.revoke(firstSession, "REPLACED")
	revoked := fixture(t, all, "revoked-socket")
	_ = bound.SetReadDeadline(time.Now().Add(3 * time.Second))
	var event map[string]any
	if err := bound.ReadJSON(&event); err != nil {
		t.Fatal(err)
	}
	n.check(t, revoked.Steps[0].Out[0], event, "wss")
	var afterClose map[string]any
	if err := bound.ReadJSON(&afterClose); err == nil {
		t.Fatalf("revoked socket remained open: %v", afterClose)
	}
	if err := db.QueryRow(ctx, "SELECT status FROM sessions WHERE user_id=$1 AND client_type='WEB'", userID).Scan(new(string)); err != nil {
		t.Fatal(err)
	}
}

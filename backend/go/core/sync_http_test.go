package core

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
	"math"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestSyncExactIntegerBounded(t *testing.T) {
	for _, tc := range []struct {
		raw   string
		want  int64
		valid bool
	}{
		{"0", 0, true}, {"-0", 0, true}, {"0.0e999999999999999999999999", 0, true}, {"1", 1, true}, {"1.0", 1, true}, {"1e2", 100, true}, {"10e-1", 1, true}, {"1000e-3", 1, true},
		{"1e100000000", 100, true}, {"1e9999999999999999999999999", 100, true}, {"999999999999999999999999999999", 100, true},
		{"1e-2", 0, false}, {"1.01", 0, false}, {"-1", 0, false}, {"null", 0, false}, {"true", 0, false}, {`"1"`, 0, false}, {"1e-999999999999999999999", 0, false},
	} {
		t.Run(tc.raw, func(t *testing.T) {
			got, ok := syncInteger(json.RawMessage(tc.raw), 100)
			if got != tc.want || ok != tc.valid {
				t.Fatalf("%s got %d %v", tc.raw, got, ok)
			}
		})
	}
	if v, ok := syncInteger(json.RawMessage("9223372036854775808"), math.MaxInt64); !ok || v != math.MaxInt64 {
		t.Fatal("overflow saturation")
	}
}

func syncFixture(t *testing.T) *messageFixture {
	f := newMessageFixture(t, 2)
	t.Cleanup(func() {
		for _, id := range f.users {
			f.db.Exec(context.Background(), `DELETE FROM outbox_events WHERE aggregate_type='user' AND aggregate_id=$1`, id)
			f.db.Exec(context.Background(), `DELETE FROM user_sync_events WHERE user_id=$1`, id)
		}
	})
	return f
}

func syncBody(user bool, id, position, conversation string) map[string]any {
	if user {
		return map[string]any{"syncVersion": "1.0", "type": "sync.user.request", "requestId": id, "cursor": position, "limit": 100}
	}
	return map[string]any{"syncVersion": "1.0", "type": "sync.conversation.request", "requestId": id, "conversationId": conversation, "afterSeq": json.Number(position), "limit": 100}
}

func syncCall(f *messageFixture, user bool, body any, token, pathSuffix string) *httptest.ResponseRecorder {
	b, _ := json.Marshal(body)
	path := "/v1/sync/conversation"
	if user {
		path = "/v1/sync/user"
	}
	r := httptest.NewRequest("POST", path+pathSuffix, bytes.NewReader(b))
	if token != "" {
		r.Header.Set("Authorization", "Bearer "+token)
	}
	w := httptest.NewRecorder()
	f.s.handler().ServeHTTP(w, r)
	return w
}

func syncDecode(t *testing.T, w *httptest.ResponseRecorder, status int, id string) map[string]any {
	t.Helper()
	var v map[string]any
	if w.Code != status || json.Unmarshal(w.Body.Bytes(), &v) != nil {
		t.Fatalf("sync status %d want %d body %s", w.Code, status, w.Body.String())
	}
	if w.Header().Get("Cache-Control") != "no-store" {
		t.Fatal("cache allowed")
	}
	if v["requestId"] != id {
		t.Fatalf("request correlation %v want %s", v["requestId"], id)
	}
	return v
}

func syncEvent(t *testing.T, f *messageFixture, kind string) {
	t.Helper()
	ctx := context.Background()
	tx, e := f.db.Begin(ctx)
	if e != nil {
		t.Fatal(e)
	}
	defer tx.Rollback(ctx)
	if _, e = tx.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, f.users[0]); e != nil {
		t.Fatal(e)
	}
	if e = writeSocialEvent(ctx, tx, f.users[0], kind, f.conversation); e != nil {
		t.Fatal(e)
	}
	if e = tx.Commit(ctx); e != nil {
		t.Fatal(e)
	}
}

func TestPublicSyncPaginationReplayAndLatest(t *testing.T) {
	f := syncFixture(t)
	ctx := context.Background()
	kinds := []string{"friend.changed", "conversation.changed", "membership.changed", "plugin.changed"}
	for i := 0; i < 205; i++ {
		syncEvent(t, f, kinds[i%4])
		id, _ := uuid()
		if _, e := f.s.commitMessage(ctx, f.claims[0], f.send(id, "sync")); e != nil {
			t.Fatal(e)
		}
	}
	// Session control events must not enter metadata projection.
	if _, e := f.db.Exec(ctx, `INSERT INTO user_sync_events(user_id,event_type,payload) VALUES($1,'session.revoked','{}')`, f.users[0]); e != nil {
		t.Fatal(e)
	}
	token, _ := f.s.codec.Sign(f.claims[0])
	request, _ := uuid()
	for _, user := range []bool{true, false} {
		position := "0"
		total := 0
		seen := map[string]bool{}
		for {
			body := syncBody(user, request, position, f.conversation)
			body["limit"] = json.Number("1e100000000")
			v := syncDecode(t, syncCall(f, user, body, token, ""), 200, request)
			key := "messages"
			if user {
				key = "events"
			}
			items := v[key].([]any)
			if len(items) > 100 {
				t.Fatal("page cap exceeded")
			}
			if len(items) == 0 && v["hasMore"].(bool) {
				t.Fatal("empty nonterminal")
			}
			for _, raw := range items {
				item := raw.(map[string]any)
				identity := item["messageId"]
				if user {
					identity = item["eventId"]
					position = item["cursor"].(string)
					if item["kind"] == "session.revoked" {
						t.Fatal("control event leak")
					}
				} else {
					totalSeq := int(item["seq"].(float64))
					if totalSeq != total+1 {
						t.Fatal("sequence gap")
					}
					position = fmt.Sprint(totalSeq)
				}
				if seen[fmt.Sprint(identity)] {
					t.Fatal("duplicate across pages")
				}
				seen[fmt.Sprint(identity)] = true
				total++
			}
			if !v["hasMore"].(bool) {
				break
			}
		}
		if total != 205 {
			t.Fatalf("truncated stream %d", total)
		}
		terminal := syncBody(user, request, position, f.conversation)
		v := syncDecode(t, syncCall(f, user, terminal, token, ""), 200, request)
		if v["hasMore"] != false {
			t.Fatal("terminal")
		}
		if user {
			syncEvent(t, f, "plugin.changed")
		} else {
			id, _ := uuid()
			if _, e := f.s.commitMessage(ctx, f.claims[0], f.send(id, "new commit")); e != nil {
				t.Fatal(e)
			}
		}
		v = syncDecode(t, syncCall(f, user, terminal, token, ""), 200, request)
		key := "messages"
		if user {
			key = "events"
		}
		if len(v[key].([]any)) != 1 || v["hasMore"] != false {
			t.Fatal("new committed item missed")
		}
		replay := syncDecode(t, syncCall(f, user, terminal, token, ""), 200, request)
		a, _ := json.Marshal(v)
		b, _ := json.Marshal(replay)
		if !bytes.Equal(a, b) {
			t.Fatal("replay changed")
		}
		if user {
			foreign, _ := f.s.codec.Sign(f.claims[1])
			errPage := syncDecode(t, syncCall(f, true, syncBody(true, request, position, f.conversation), foreign, ""), 400, request)
			if errPage["error"].(map[string]any)["code"] != "VALIDATION_FAILED" {
				t.Fatal("foreign cursor accepted")
			}
			// Same account replacement Session must retain cursor usability.
			sid, epoch, _, _, e := f.s.newSession(ctx, f.users[0], clientInput{ClientType: "WEB", DeviceID: "replacement"})
			if e != nil {
				t.Fatal(e)
			}
			f.claims[0].SessionID = sid
			f.claims[0].SessionEpoch = epoch
			token, _ = f.s.codec.Sign(f.claims[0])
			syncDecode(t, syncCall(f, true, terminal, token, ""), 200, request)
		}
	}
	// Any above-head integer remains authorized, exact and terminal.
	body := syncBody(false, request, "1e100000000", f.conversation)
	v := syncDecode(t, syncCall(f, false, body, token, ""), 200, request)
	if len(v["messages"].([]any)) != 0 || v["hasMore"] != false {
		t.Fatal("huge afterSeq")
	}
	if f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1 AND event_type='message.created'`) != 206 {
		t.Fatal("read changed Outbox")
	}
}

func TestPublicSyncValidationAuthAndIsolation(t *testing.T) {
	f := syncFixture(t)
	token, _ := f.s.codec.Sign(f.claims[0])
	request, _ := uuid()
	for _, user := range []bool{true, false} {
		for _, tc := range []struct {
			name               string
			mutate             func(map[string]any)
			suffix, credential string
			status             int
			code               string
		}{
			{"noauth", func(b map[string]any) {}, "", "", 401, "AUTH_REQUIRED"},
			{"badtoken", func(b map[string]any) {}, "", "invalid", 401, "AUTH_TOKEN_INVALID"},
			{"version", func(b map[string]any) { b["syncVersion"] = "2.0" }, "", token, 426, "PROTOCOL_VERSION_UNSUPPORTED"},
			{"unknown", func(b map[string]any) { b["extra"] = 1 }, "", token, 400, "VALIDATION_FAILED"},
			{"fraction", func(b map[string]any) { b["limit"] = json.Number("1e-2") }, "", token, 400, "VALIDATION_FAILED"},
			{"zero", func(b map[string]any) { b["limit"] = 0 }, "", token, 400, "VALIDATION_FAILED"},
			{"ordinaryquery", func(b map[string]any) {}, "?x=1", token, 400, "VALIDATION_FAILED"},
			{"credentialquery", func(b map[string]any) {}, "?accessToken=fake", token, 400, "VALIDATION_FAILED"},
			{"authtakesprecedence", func(b map[string]any) { b["syncVersion"] = "2.0" }, "", "", 401, "AUTH_REQUIRED"},
		} {
			t.Run(fmt.Sprint(user)+tc.name, func(t *testing.T) {
				b := syncBody(user, request, "0", f.conversation)
				tc.mutate(b)
				v := syncDecode(t, syncCall(f, user, b, tc.credential, tc.suffix), tc.status, request)
				if v["error"].(map[string]any)["code"] != tc.code {
					t.Fatal(v)
				}
			})
		}
	}
	for _, cursor := range []string{"junk", f.s.syncCursor(f.users[0], math.MaxInt64), strings.Repeat("x", 257)} {
		syncDecode(t, syncCall(f, true, syncBody(true, request, cursor, f.conversation), token, ""), 400, request)
	}
	for _, num := range []json.Number{"1.0", "1e2", "10e-1"} {
		body := syncBody(true, request, "0", f.conversation)
		body["limit"] = num
		syncDecode(t, syncCall(f, true, body, token, ""), 200, request)
	}
	nonexistent, _ := uuid()
	syncDecode(t, syncCall(f, false, syncBody(false, request, "0", nonexistent), token, ""), 403, request)
	f.db.Exec(context.Background(), `UPDATE conversation_members SET left_at=now() WHERE user_id=$1 AND conversation_id=$2`, f.users[0], f.conversation)
	syncDecode(t, syncCall(f, false, syncBody(false, request, "0", f.conversation), token, ""), 403, request)
	for _, tc := range []struct {
		mutation string
		code     string
	}{
		{`UPDATE sessions SET session_epoch=session_epoch+1 WHERE user_id=$1`, "AUTH_SESSION_EPOCH_STALE"},
		{`UPDATE sessions SET session_epoch=session_epoch-1,status='REVOKED' WHERE user_id=$1`, "AUTH_SESSION_REVOKED"},
		{`UPDATE sessions SET status='ACTIVE',expires_at=now()-interval '1 second' WHERE user_id=$1`, "AUTH_SESSION_REVOKED"},
	} {
		if _, e := f.db.Exec(context.Background(), tc.mutation, f.users[0]); e != nil {
			t.Fatal(e)
		}
		v := syncDecode(t, syncCall(f, true, syncBody(true, request, "0", f.conversation), token, ""), 401, request)
		if v["error"].(map[string]any)["code"] != tc.code {
			t.Fatal(v)
		}
	}
}

func syncWaitLock(t *testing.T, f *messageFixture) {
	t.Helper()
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		var count int
		if e := f.db.QueryRow(context.Background(), `SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND wait_event_type='Lock' AND query LIKE 'SELECT u.user_id FROM users u WHERE u.user_id=%'`).Scan(&count); e != nil {
			t.Fatal(e)
		}
		if count > 0 {
			return
		}
		time.Sleep(10 * time.Millisecond)
	}
	t.Fatal("Sync did not wait for serialized producer")
}

func TestUserSyncCommittedPrefixAndAuthAfterWait(t *testing.T) {
	f := syncFixture(t)
	ctx := context.Background()
	token, _ := f.s.codec.Sign(f.claims[0])
	request, _ := uuid()
	tx, e := f.db.Begin(ctx)
	if e != nil {
		t.Fatal(e)
	}
	defer tx.Rollback(ctx)
	tx.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, f.users[0])
	if e = writeSocialEvent(ctx, tx, f.users[0], "friend.changed", f.conversation); e != nil {
		t.Fatal(e)
	}
	result := make(chan *httptest.ResponseRecorder, 1)
	go func() { result <- syncCall(f, true, syncBody(true, request, "0", f.conversation), token, "") }()
	syncWaitLock(t, f)
	// A producer on another account may commit a higher global identity first.
	other, e := f.db.Begin(ctx)
	if e != nil {
		t.Fatal(e)
	}
	other.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, f.users[1])
	if e = writeSocialEvent(ctx, other, f.users[1], "membership.changed", f.conversation); e != nil {
		t.Fatal(e)
	}
	if e = other.Commit(ctx); e != nil {
		t.Fatal(e)
	}
	select {
	case <-result:
		t.Fatal("read crossed uncommitted prefix")
	default:
	}
	if e = tx.Commit(ctx); e != nil {
		t.Fatal(e)
	}
	var v map[string]any
	select {
	case w := <-result:
		v = syncDecode(t, w, 200, request)
	case <-time.After(5 * time.Second):
		t.Fatal("read blocked")
	}
	if len(v["events"].([]any)) != 1 {
		t.Fatal("late lower ID missing")
	}
	cursor := v["nextCursor"].(string)
	syncEvent(t, f, "conversation.changed")
	v = syncDecode(t, syncCall(f, true, syncBody(true, request, cursor, f.conversation), token, ""), 200, request)
	if len(v["events"].([]any)) != 1 {
		t.Fatal("later event missing")
	}
	tx, e = f.db.Begin(ctx)
	if e != nil {
		t.Fatal(e)
	}
	defer tx.Rollback(ctx)
	tx.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, f.users[0])
	go func() { result <- syncCall(f, true, syncBody(true, request, cursor, f.conversation), token, "") }()
	syncWaitLock(t, f)
	if _, e = tx.Exec(ctx, `UPDATE sessions SET expires_at=now()-interval '1 second' WHERE user_id=$1`, f.users[0]); e != nil {
		t.Fatal(e)
	}
	tx.Commit(ctx)
	select {
	case w := <-result:
		syncDecode(t, w, 401, request)
	case <-time.After(5 * time.Second):
		t.Fatal("auth recheck hung")
	}
}

func TestPublicSyncMalformedCorrelationAndAuthFailures(t *testing.T) {
	f := syncFixture(t)
	request, _ := uuid()
	token, _ := f.s.codec.Sign(f.claims[0])
	for _, path := range []string{"/v1/sync/user", "/v1/sync/conversation"} {
		for _, raw := range []string{`{`, `{"requestId":null}`, `{"requestId":"invalid"}`, `[]`} {
			r := httptest.NewRequest("POST", path+"?accessToken=fake", strings.NewReader(raw))
			w := httptest.NewRecorder()
			f.s.handler().ServeHTTP(w, r)
			var v map[string]any
			if w.Code != 400 || w.Header().Get("Cache-Control") != "no-store" || json.Unmarshal(w.Body.Bytes(), &v) != nil {
				t.Fatal("malformed failure")
			}
			if !socialUUIDPattern.MatchString(v["requestId"].(string)) || v["requestId"] == request {
				t.Fatal("missing fresh server UUID")
			}
		}
	}
	b := syncBody(true, request, "0", f.conversation)
	b["syncVersion"] = nil
	syncDecode(t, syncCall(f, true, b, token, ""), 400, request)
	// Existing Auth query restriction still precedes Auth business decoding.
	r := httptest.NewRequest("POST", "/v1/auth/login?accessToken=fake", strings.NewReader("{}"))
	w := httptest.NewRecorder()
	f.s.handler().ServeHTTP(w, r)
	if w.Code != 400 || !strings.Contains(w.Body.String(), "Authentication material is forbidden") {
		t.Fatal("legacy query rule changed")
	}
	for _, tc := range []struct {
		modify func(*claims)
		code   string
	}{
		{func(c *claims) {
			c.IssuedAt = time.Now().Add(-time.Hour).Unix()
			c.ExpiresAt = time.Now().Add(-time.Second).Unix()
		}, "AUTH_TOKEN_EXPIRED"},
		{func(c *claims) { c.ClientType = "MOBILE" }, "AUTH_CLIENT_TYPE_MISMATCH"},
		{func(c *claims) { c.SessionID, _ = uuid() }, "AUTH_TOKEN_INVALID"},
	} {
		c := f.claims[0]
		tc.modify(&c)
		tok, _ := f.s.codec.Sign(c)
		for _, user := range []bool{true, false} {
			v := syncDecode(t, syncCall(f, user, syncBody(user, request, "0", f.conversation), tok, ""), 401, request)
			if v["error"].(map[string]any)["code"] != tc.code {
				t.Fatal(v)
			}
		}
	}
}

func TestUserSyncSessionChangesDuringLockWait(t *testing.T) {
	for _, tc := range []struct{ name, sql, code string }{
		{"revoked", `UPDATE sessions SET status='REVOKED' WHERE user_id=$1`, "AUTH_SESSION_REVOKED"},
		{"epoch", `UPDATE sessions SET session_epoch=session_epoch+1 WHERE user_id=$1`, "AUTH_SESSION_EPOCH_STALE"},
		{"tokenexpiry", "", "AUTH_TOKEN_EXPIRED"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			f := syncFixture(t)
			ctx := context.Background()
			request, _ := uuid()
			current := time.Now()
			var clock atomic.Int64
			clock.Store(current.UnixNano())
			f.s.now = func() time.Time { return time.Unix(0, clock.Load()) }
			f.s.codec.Now = f.s.now
			c := f.claims[0]
			c.ExpiresAt = current.Add(time.Second).Unix()
			token, _ := f.s.codec.Sign(c)
			tx, e := f.db.Begin(ctx)
			if e != nil {
				t.Fatal(e)
			}
			defer tx.Rollback(ctx)
			tx.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, f.users[0])
			result := make(chan *httptest.ResponseRecorder, 1)
			go func() { result <- syncCall(f, true, syncBody(true, request, "0", f.conversation), token, "") }()
			syncWaitLock(t, f)
			if tc.sql != "" {
				if _, e = tx.Exec(ctx, tc.sql, f.users[0]); e != nil {
					t.Fatal(e)
				}
			} else {
				clock.Store(current.Add(2 * time.Second).UnixNano())
			}
			tx.Commit(ctx)
			select {
			case w := <-result:
				v := syncDecode(t, w, 401, request)
				if v["error"].(map[string]any)["code"] != tc.code {
					t.Fatal(v)
				}
			case <-time.After(5 * time.Second):
				t.Fatal("wait")
			}
		})
	}
}

func TestPublicSyncSingleConnectionConcurrentReaders(t *testing.T) {
	f := syncFixture(t)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	config := f.db.Config()
	config.MaxConns = 1
	config.MinConns = 0
	pool, e := pgxpool.NewWithConfig(ctx, config)
	if e != nil {
		t.Fatal(e)
	}
	defer pool.Close()
	f.s.db = pool
	token, _ := f.s.codec.Sign(f.claims[0])
	request, _ := uuid()
	data, _ := json.Marshal(syncBody(true, request, "0", f.conversation))
	results := make(chan int, 8)
	for i := 0; i < 8; i++ {
		go func() {
			r := httptest.NewRequest("POST", "/v1/sync/user", bytes.NewReader(data)).WithContext(ctx)
			r.Header.Set("Authorization", "Bearer "+token)
			w := httptest.NewRecorder()
			f.s.handler().ServeHTTP(w, r)
			results <- w.Code
		}()
	}
	for i := 0; i < 8; i++ {
		select {
		case code := <-results:
			if code != 200 {
				t.Fatalf("bounded pool read %d", code)
			}
		case <-ctx.Done():
			t.Fatal("pool starvation")
		}
	}
}

func TestSyncStreamingNumbersAndOriginalGrammar(t *testing.T) {
	long := "1" + strings.Repeat("0", 70000)
	for _, tc := range []struct {
		raw, want string
		valid     bool
	}{
		{long, "9223372036854775807", true}, {long + "e-70000", "1", true},
		{"1e" + strings.Repeat("9", 70000), "9223372036854775807", true},
		{"0e-" + strings.Repeat("9", 70000), "0", true},
		{"-0.000e" + strings.Repeat("9", 70000), "0", true},
		{"1.0", "1", true}, {"100e-2", "1", true}, {"1e-2", "0.5", true}, {"-1.2", "-1", true},
		{"0.0001e4", "1", true}, {"0.0001e3", "0.5", true},
		{"001", "", false}, {"1.", "", false}, {"1e+", "", false}, {"-", "", false}, {"1e2x", "", false}, {"1e-", "", false}, {"1-2", "", false}, {"1 2", "", false},
	} {
		got, e := syncJSON(strings.NewReader("{\"afterSeq\":" + tc.raw + "}"))
		if e == nil && !json.Valid(got) {
			e = fmt.Errorf("invalid original JSON")
		}
		if (e == nil) != tc.valid {
			t.Fatalf("stream numeric validity input prefix %s", tc.raw[:min(len(tc.raw), 20)])
		}
		if e == nil && string(got) != "{\"afterSeq\":"+tc.want+"}" {
			t.Fatalf("normalized %s", got)
		}
		if len(got) > 100 {
			t.Fatal("unbounded normalization buffer")
		}
	}
	raw := ` { "cursor" : "123\\\"456 789", "limit": 1.0 } `
	got, e := syncJSON(strings.NewReader(raw))
	if e != nil || !bytes.Contains(got, []byte(`"123\\\"456 789"`)) {
		t.Fatal("escaped string changed")
	}
	if _, e = syncJSON(strings.NewReader("{\"cursor\":\"" + strings.Repeat("x", 70000) + "\"}")); e == nil {
		t.Fatal("nonnumeric buffer boundary removed")
	}
	for _, raw := range []string{`{"limit":1}`, `[1,2.0,3e0]`, `1`, `1 `} {
		got, e = syncJSON(strings.NewReader(raw))
		if e != nil || !json.Valid(got) {
			t.Fatal("EOF/delimiter handling")
		}
	}
}

func TestPublicSyncArbitraryNumericLength(t *testing.T) {
	f := syncFixture(t)
	token, _ := f.s.codec.Sign(f.claims[0])
	request, _ := uuid()
	long := "1" + strings.Repeat("0", 70000)
	for _, user := range []bool{true, false} {
		for _, limit := range []string{long, "1e" + strings.Repeat("9", 70000), long + "e-70000"} {
			body := syncBody(user, request, "0", f.conversation)
			body["limit"] = json.Number(limit)
			syncDecode(t, syncCall(f, user, body, token, ""), 200, request)
		}
	}
	for _, after := range []string{long, "1e" + strings.Repeat("9", 70000), "-0e-" + strings.Repeat("9", 70000), "0.0e" + strings.Repeat("9", 70000)} {
		body := syncBody(false, request, after, f.conversation)
		syncDecode(t, syncCall(f, false, body, token, ""), 200, request)
	}
	for _, number := range []string{"001", "1.", "1e+", "-", "1e2x", "1e-", "1-2", "1 2"} {
		raw := fmt.Sprintf("{\"syncVersion\":\"1.0\",\"type\":\"sync.user.request\",\"requestId\":\"%s\",\"cursor\":\"0\",\"limit\":%s}", request, number)
		r := httptest.NewRequest("POST", "/v1/sync/user", strings.NewReader(raw))
		r.Header.Set("Authorization", "Bearer "+token)
		w := httptest.NewRecorder()
		f.s.handler().ServeHTTP(w, r)
		if w.Code != 400 {
			t.Fatal("malformed original number legalized")
		}
	}
}

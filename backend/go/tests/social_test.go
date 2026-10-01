package tests

import (
	"context"
	"encoding/json"
	"fmt"
	"im-platform/backend/go/shared"
	"net/http/httptest"
	"os"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

func socialDatabase(t *testing.T) (*pgxpool.Pool, *testService) {
	t.Helper()
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(db.Close)
	if err := db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	return db, newService(db, []byte("test-only-signing-key-at-least-32-bytes"))
}

func socialUser(t *testing.T, s *testService) (string, string, string) {
	t.Helper()
	random, _ := shared.RandomToken(8)
	name := "social" + strings.ToLower(random[:10])
	h := s.handler
	registration := call(t, h, "POST", "/v1/auth/register", map[string]any{"username": name, "password": "fixture-password-not-a-real-secret", "displayName": name}, "", nil)
	expect(t, registration, 201)
	id := readResult(t, registration)["user"].(map[string]any)["userId"].(string)
	login := call(t, h, "POST", "/v1/auth/login", map[string]any{"username": name, "password": "fixture-password-not-a-real-secret", "clientType": "WEB", "deviceId": "browser-1", "clientVersion": "1.0.0", "protocolVersion": "1"}, "", nil)
	expect(t, login, 200)
	return id, name, getToken(t, login)
}

func cleanupSocialUsers(t *testing.T, db *pgxpool.Pool, ids ...string) {
	t.Helper()
	t.Cleanup(func() {
		ctx := context.Background()
		for _, id := range ids {
			_, _ = db.Exec(ctx, `DELETE FROM outbox_events WHERE aggregate_type='user' AND aggregate_id=$1`, id)
			_, _ = db.Exec(ctx, `DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'sessionId')::uuid FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked')`, id)
			_, _ = db.Exec(ctx, `DELETE FROM user_sync_events WHERE user_id=$1`, id)
		}
		_, _ = db.Exec(ctx, `DELETE FROM friendships WHERE user_low_id=$1 OR user_high_id=$1`, ids[0])
		_, _ = db.Exec(ctx, `DELETE FROM conversation_members WHERE user_id=$1 OR user_id=$2`, ids[0], ids[1])
		_, _ = db.Exec(ctx, `DELETE FROM conversations WHERE direct_user_low_id=$1 OR direct_user_high_id=$1`, ids[0])
		for _, id := range ids {
			_, _ = db.Exec(ctx, `DELETE FROM sessions WHERE user_id=$1`, id)
			_, _ = db.Exec(ctx, `DELETE FROM users WHERE user_id=$1`, id)
		}
	})
}

func socialCount(t *testing.T, db *pgxpool.Pool, query string, args ...any) int {
	t.Helper()
	var n int
	if err := db.QueryRow(context.Background(), query, args...).Scan(&n); err != nil {
		t.Fatal(err)
	}
	return n
}

func TestCanonicalSocialFixturesAndAtomicity(t *testing.T) {
	db, s := socialDatabase(t)
	a, nameA, tokenA := socialUser(t, s)
	b, _, tokenB := socialUser(t, s)
	cleanupSocialUsers(t, db, a, b)
	h := s.handler
	positive := readFixture(t, "../../../contracts/fixtures/auth-user-friend/positive.json")
	negative := readFixture(t, "../../../contracts/fixtures/auth-user-friend/negative.json")
	n := newFixtureNormalizer(nameA)
	add := fixture(t, positive, "friend-add-normalizes-and-reuses-direct")
	first := call(t, h, "PUT", "/v1/friends/"+b, nil, tokenA, nil)
	expect(t, first, add.Steps[0].Expected.Status)
	n.check(t, add.Steps[0].Expected.Body, readResult(t, first), "body")
	second := call(t, h, "PUT", "/v1/friends/"+a, nil, tokenB, nil)
	expect(t, second, add.Steps[1].Expected.Status)
	n.check(t, add.Steps[1].Expected.Body, readResult(t, second), "body")
	low, high := a, b
	if low > high {
		low, high = high, low
	}
	conversation := readResult(t, first)["directConversationId"].(string)
	if socialCount(t, db, `SELECT count(*) FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high) != 1 ||
		socialCount(t, db, `SELECT count(*) FROM conversations WHERE kind='DIRECT' AND direct_user_low_id=$1 AND direct_user_high_id=$2`, low, high) != 1 ||
		socialCount(t, db, `SELECT count(*) FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, conversation) != 2 {
		t.Fatal("friendship, conversation, or memberships did not converge")
	}
	for _, id := range []string{a, b} {
		if socialCount(t, db, `SELECT count(*) FROM user_sync_events WHERE user_id=$1 AND event_type IN ('friend.changed','conversation.changed','membership.changed')`, id) != 3 ||
			socialCount(t, db, `SELECT count(*) FROM outbox_events WHERE aggregate_type='user' AND aggregate_id=$1 AND event_type IN ('friend.changed','conversation.changed','membership.changed')`, id) != 3 {
			t.Fatal("sync or outbox effects missing from friend commit")
		}
		list := call(t, h, "GET", "/v1/friends", nil, map[string]string{a: tokenA, b: tokenB}[id], nil)
		expect(t, list, 200)
		friends := readResult(t, list)["friends"].([]any)
		if len(friends) != 1 || friends[0].(map[string]any)["directConversationId"] != conversation {
			t.Fatalf("friend list not bidirectional: %v", friends)
		}
	}
	// The canonical negative fixtures are run against their stated preconditions.
	for _, tc := range []struct{ fixture, path, token string }{
		{"missing-authentication", "/v1/friends", ""},
		{"friend-target-not-found", "/v1/friends/20000000-0000-4000-8000-000000000002", tokenA},
		{"friend-self-rejected", "/v1/friends/" + a, tokenA},
	} {
		t.Run(tc.fixture, func(t *testing.T) {
			st := fixture(t, negative, tc.fixture).Steps[0]
			response := call(t, h, st.Request.Method, tc.path, nil, tc.token, nil)
			expect(t, response, st.Expected.Status)
			n.check(t, st.Expected.Body, readResult(t, response), "body")
		})
	}
	// A broken existing friendship must report the canonical conflict without repair.
	_, err := db.Exec(context.Background(), `DELETE FROM conversation_members WHERE conversation_id=$1 AND user_id=$2`, conversation, b)
	if err != nil {
		t.Fatal(err)
	}
	conflict := fixture(t, negative, "friendship-state-conflict").Steps[0]
	w := call(t, h, "PUT", "/v1/friends/"+b, nil, tokenA, nil)
	expect(t, w, conflict.Expected.Status)
	n.check(t, conflict.Expected.Body, readResult(t, w), "body")
	if socialCount(t, db, `SELECT count(*) FROM conversation_members WHERE conversation_id=$1`, conversation) != 1 {
		t.Fatal("conflicting state was rewritten")
	}
}

func TestConcurrentReverseFriendAdd(t *testing.T) {
	db, s := socialDatabase(t)
	a, _, tokenA := socialUser(t, s)
	b, _, tokenB := socialUser(t, s)
	cleanupSocialUsers(t, db, a, b)
	low, high := a, b
	if low > high {
		low, high = high, low
	}
	var wg sync.WaitGroup
	responses := make(chan *httptest.ResponseRecorder, 2)
	for _, side := range []struct{ target, token string }{{b, tokenA}, {a, tokenB}} {
		wg.Add(1)
		go func(target, token string) {
			defer wg.Done()
			responses <- call(t, s.handler, "PUT", "/v1/friends/"+target, nil, token, nil)
		}(side.target, side.token)
	}
	wg.Wait()
	close(responses)
	statuses := map[int]int{}
	var id string
	for r := range responses {
		statuses[r.Code]++
		if r.Code != 200 && r.Code != 201 {
			t.Fatalf("concurrent add failed: %s", r.Body.String())
		}
		got := readResult(t, r)["directConversationId"].(string)
		if id != "" && got != id {
			t.Fatalf("concurrent IDs diverged: %s vs %s", id, got)
		}
		id = got
	}
	if statuses[201] != 1 || statuses[200] != 1 {
		t.Fatalf("concurrent statuses: %v", statuses)
	}
	if socialCount(t, db, `SELECT count(*) FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high) != 1 ||
		socialCount(t, db, `SELECT count(*) FROM conversations WHERE direct_user_low_id=$1 AND direct_user_high_id=$2`, low, high) != 1 ||
		socialCount(t, db, `SELECT count(*) FROM conversation_members WHERE conversation_id=$1`, id) != 2 {
		t.Fatal(fmt.Sprintf("reverse concurrent add did not converge for %s", id))
	}
}

func TestSocialLoop1Applicability(t *testing.T) {
	b, err := os.ReadFile("../../../contracts/fixtures/auth-user-friend/loop1-exceptions.json")
	if err != nil {
		t.Fatal(err)
	}
	var profile struct {
		Loop       string `json:"loop"`
		Exceptions []struct {
			ID       string `json:"scenarioId"`
			Status   string `json:"status"`
			Required bool   `json:"runtimeAcceptanceRequired"`
			Pass     bool   `json:"countsAsPass"`
		} `json:"exceptions"`
	}
	if err = json.Unmarshal(b, &profile); err != nil {
		t.Fatal(err)
	}
	if profile.Loop != "Loop1" || len(profile.Exceptions) != 1 {
		t.Fatal("unexpected applicability profile")
	}
	e := profile.Exceptions[0]
	if e.ID != "friend-add-authorization-denied" || e.Status != "DEFERRED_BY_HUMAN" || e.Required || e.Pass {
		t.Fatal("unapproved exception")
	}
	fixture(t, readFixture(t, "../../../contracts/fixtures/auth-user-friend/negative.json"), e.ID)
	t.Log("DISPOSITION friend-add-authorization-denied DEFERRED_BY_HUMAN; runtime not executed; does not count as canonical PASS")
}
func TestSocialMutationRechecksSessionAfterUserLock(t *testing.T) {
	db, s := socialDatabase(t)
	a, _, token := socialUser(t, s)
	b, _, _ := socialUser(t, s)
	cleanupSocialUsers(t, db, a, b)
	ctx := context.Background()
	tx, err := db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer tx.Rollback(ctx)
	if _, err = tx.Exec(ctx, `SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE`, a); err != nil {
		t.Fatal(err)
	}
	done := make(chan *httptest.ResponseRecorder, 1)
	go func() { done <- call(t, s.handler, "PUT", "/v1/friends/"+b, nil, token, nil) }()
	deadline := time.Now().Add(3 * time.Second)
	blocked := false
	for time.Now().Before(deadline) {
		var n int
		err = db.QueryRow(ctx, `SELECT count(*) FROM pg_stat_activity WHERE datname=current_database() AND wait_event_type='Lock' AND query LIKE 'SELECT user_id FROM users WHERE user_id=%'`).Scan(&n)
		if err != nil {
			t.Fatal(err)
		}
		if n > 0 {
			blocked = true
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	if !blocked {
		t.Fatal("Social request did not wait for account lock")
	}
	if _, err = tx.Exec(ctx, `UPDATE sessions SET expires_at=now()-interval '1 second' WHERE user_id=$1 AND client_type='WEB'`, a); err != nil {
		t.Fatal(err)
	}
	if err = tx.Commit(ctx); err != nil {
		t.Fatal(err)
	}
	select {
	case w := <-done:
		expect(t, w, 401)
		if readResult(t, w)["error"].(map[string]any)["code"] != "AUTH_SESSION_REVOKED" {
			t.Fatal("expired Session accepted after lock")
		}
	case <-time.After(3 * time.Second):
		t.Fatal("request did not unblock")
	}
	if socialCount(t, db, `SELECT count(*) FROM friendships WHERE user_low_id=$1 OR user_high_id=$1`, a) != 0 || socialCount(t, db, `SELECT count(*) FROM user_sync_events WHERE user_id=$1`, a) != 0 || socialCount(t, db, `SELECT count(*) FROM outbox_events WHERE aggregate_type='user' AND aggregate_id=$1`, a) != 0 {
		t.Fatal("rejected Session left social effects")
	}
}

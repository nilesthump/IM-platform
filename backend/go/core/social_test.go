package core

import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5/pgxpool"
	"os"
	"strconv"
	"testing"
)

func TestSocialAssemblyReuseAndRollback(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	a, _ := uuid()
	b, _ := uuid()
	low, high := pair(a, b)
	for _, id := range []string{a, b} {
		if _, err = db.Exec(ctx, `INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,'Social rollback','test-only')`, id, "social"+id); err != nil {
			t.Fatal(err)
		}
	}
	defer func() {
		for _, id := range []string{a, b} {
			db.Exec(ctx, `DELETE FROM outbox_events WHERE aggregate_type='user' AND aggregate_id=$1`, id)
			db.Exec(ctx, `DELETE FROM user_sync_events WHERE user_id=$1`, id)
		}
		db.Exec(ctx, `DELETE FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high)
		db.Exec(ctx, `DELETE FROM conversation_members WHERE conversation_id IN (SELECT conversation_id FROM conversations WHERE direct_user_low_id=$1 AND direct_user_high_id=$2)`, low, high)
		db.Exec(ctx, `DELETE FROM conversations WHERE direct_user_low_id=$1 AND direct_user_high_id=$2`, low, high)
		for _, id := range []string{a, b} {
			db.Exec(ctx, `DELETE FROM users WHERE user_id=$1`, id)
		}
	}()
	count := func(query string, args ...any) int {
		t.Helper()
		var n int
		if err := db.QueryRow(ctx, query, args...).Scan(&n); err != nil {
			t.Fatal(err)
		}
		return n
	}
	tx, err := db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	_, created, err := assembleFriendship(ctx, tx, low, high, a)
	if err != nil || !created {
		t.Fatalf("assembly: %v %v", created, err)
	}
	if err = tx.Rollback(ctx); err != nil {
		t.Fatal(err)
	}
	for _, q := range []string{`SELECT count(*) FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, `SELECT count(*) FROM conversations WHERE direct_user_low_id=$1 AND direct_user_high_id=$2`, `SELECT count(*) FROM conversation_members WHERE user_id IN ($1,$2)`, `SELECT count(*) FROM user_sync_events WHERE user_id IN ($1,$2)`, `SELECT count(*) FROM outbox_events WHERE aggregate_type='user' AND aggregate_id IN ($1,$2)`} {
		if count(q, low, high) != 0 {
			t.Fatal("caller rollback left effects")
		}
	}
	direct, _ := uuid()
	if _, err = db.Exec(ctx, `INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by) VALUES($1,'DIRECT',$2,$3,$2)`, direct, low, high); err != nil {
		t.Fatal(err)
	}
	// A departed membership makes validation fail after friendship/other membership insertion.
	if _, err = db.Exec(ctx, `INSERT INTO conversation_members(conversation_id,user_id,role,left_at) VALUES($1,$2,'MEMBER',now())`, direct, low); err != nil {
		t.Fatal(err)
	}
	tx, err = db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	_, _, err = assembleFriendship(ctx, tx, low, high, a)
	if err == nil {
		t.Fatal("expected partial-assembly conflict")
	}
	if err = tx.Rollback(ctx); err != nil {
		t.Fatal(err)
	}
	if count(`SELECT count(*) FROM friendships WHERE user_low_id=$1 AND user_high_id=$2`, low, high) != 0 || count(`SELECT count(*) FROM conversation_members WHERE conversation_id=$1`, direct) != 1 || count(`SELECT count(*) FROM user_sync_events WHERE user_id IN ($1,$2)`, low, high) != 0 {
		t.Fatal("failed assembly leaked writes")
	}
	if _, err = db.Exec(ctx, `DELETE FROM conversation_members WHERE conversation_id=$1`, direct); err != nil {
		t.Fatal(err)
	}
	tx, err = db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	got, created, err := assembleFriendship(ctx, tx, low, high, a)
	if err != nil || !created || got != direct {
		t.Fatalf("reuse %s %v %v", got, created, err)
	}
	if err = tx.Commit(ctx); err != nil {
		t.Fatal(err)
	}
	rows, err := db.Query(ctx, `SELECT s.user_id,s.cursor_id,s.event_type,s.payload,o.event_id,o.payload FROM user_sync_events s JOIN outbox_events o ON o.aggregate_id=s.user_id AND o.event_id=(s.payload->>'eventId')::uuid WHERE s.user_id IN ($1,$2)`, low, high)
	if err != nil {
		t.Fatal(err)
	}
	defer rows.Close()
	n := 0
	for rows.Next() {
		var user, kind, eventID string
		var cursor int64
		var syncJSON, outJSON []byte
		if err = rows.Scan(&user, &cursor, &kind, &syncJSON, &eventID, &outJSON); err != nil {
			t.Fatal(err)
		}
		var event map[string]any
		var out struct {
			User  string         `json:"userId"`
			Event map[string]any `json:"event"`
		}
		if json.Unmarshal(syncJSON, &event) != nil || json.Unmarshal(outJSON, &out) != nil {
			t.Fatal("malformed event")
		}
		if event["eventId"] != eventID || event["cursor"] != strconv.FormatInt(cursor, 10) || event["kind"] != kind || event["revision"] != float64(1) || out.User != user {
			t.Fatal("event metadata mismatch")
		}
		expected, _ := json.Marshal(event)
		actual, _ := json.Marshal(out.Event)
		if string(expected) != string(actual) {
			t.Fatal("Sync/Outbox payload mismatch")
		}
		n++
	}
	if err = rows.Err(); err != nil {
		t.Fatal(err)
	}
	if n != 6 {
		t.Fatalf("matched event count %d", n)
	}
	tx, err = db.Begin(ctx)
	if err != nil {
		t.Fatal(err)
	}
	got, created, err = assembleFriendship(ctx, tx, low, high, b)
	if err != nil || created || got != direct {
		t.Fatalf("existing reuse %s %v %v", got, created, err)
	}
	if err = tx.Commit(ctx); err != nil {
		t.Fatal(err)
	}
	if count(`SELECT count(*) FROM outbox_events WHERE aggregate_type='user' AND aggregate_id IN ($1,$2)`, low, high) != 6 {
		t.Fatal("retry duplicated effects")
	}
}

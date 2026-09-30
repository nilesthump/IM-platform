package gateway

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
	"os"
	"testing"
)

func TestRevocationReasonDoesNotInventBusinessCause(t *testing.T) {
	// A nil pool makes any accidental lookup fail loudly. These failures must
	// close conservatively without looking up an unrelated business event.
	s := &validator{}
	for _, err := range []error{errors.New("database unavailable"), shared.Fail(401, "AUTH_TOKEN_EXPIRED", "expired"), shared.Fail(401, "AUTH_TOKEN_INVALID", "invalid"), nil} {
		if got := s.revocationReason(context.Background(), shared.Claims{}, err); got != "REVOKED" {
			t.Fatalf("reason %q for %v", got, err)
		}
	}
}

func TestPostgresRevocationReasonUsesExactCommittedIdentity(t *testing.T) {
	if os.Getenv("DB_TEST_ENABLE") != "1" {
		t.Skip("set DB_TEST_ENABLE=1 with migrated disposable PostgreSQL")
	}
	ctx := context.Background()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	s := &validator{db: db}
	uid, _ := shared.UUID()
	other, _ := shared.UUID()
	sid, _ := shared.UUID()
	nextSID, _ := shared.UUID()
	for _, id := range []string{uid, other} {
		if _, err = db.Exec(ctx, "INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,'Reason control','test-only-non-login-hash')", id, "reason"+id); err != nil {
			t.Fatal(err)
		}
	}
	defer func() {
		_, _ = db.Exec(ctx, "DELETE FROM user_sync_events WHERE user_id=$1 OR user_id=$2", uid, other)
		_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1 OR user_id=$2", uid, other)
	}()
	c := shared.Claims{UserID: uid, SessionID: sid}
	revoked := shared.Fail(401, "AUTH_SESSION_REVOKED", "revoked")
	add := func(user, session, reason string) {
		t.Helper()
		if _, err := db.Exec(ctx, "INSERT INTO user_sync_events(user_id,event_type,payload) VALUES($1,'session.revoked',jsonb_build_object('sessionId',$2::text,'reason',$3::text))", user, session, reason); err != nil {
			t.Fatal(err)
		}
	}
	add(other, sid, "LOGOUT")
	add(uid, nextSID, "REPLACED")
	if got := s.revocationReason(ctx, c, revoked); got != "REVOKED" {
		t.Fatalf("unrelated identity accepted %q", got)
	}
	add(uid, sid, "UNKNOWN")
	if got := s.revocationReason(ctx, c, revoked); got != "REVOKED" {
		t.Fatalf("unknown reason accepted %q", got)
	}
	add(uid, sid, "REPLACED")
	add(uid, nextSID, "LOGOUT")
	if got := s.revocationReason(ctx, c, revoked); got != "REPLACED" {
		t.Fatalf("latest slot event replaced bound event: %q", got)
	}
	cancelled, cancel := context.WithCancel(ctx)
	cancel()
	if got := s.revocationReason(cancelled, c, revoked); got != "REVOKED" {
		t.Fatalf("query error fabricated %q", got)
	}
	if got := s.revocationReason(ctx, c, shared.Fail(401, "AUTH_TOKEN_EXPIRED", "expired")); got != "REVOKED" {
		t.Fatalf("expiry fabricated %q", got)
	}
}

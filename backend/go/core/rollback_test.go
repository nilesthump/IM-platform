package core

import (
	"context"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
	"os"
	"testing"
	"time"
)

func TestRevocationRollback(t *testing.T) {
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
	userID, _ := uuid()
	_, err = db.Exec(ctx, "INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,'Rollback','test-only')", userID, "rollback"+userID)
	if err != nil {
		t.Fatal(err)
	}
	defer func() {
		_, _ = db.Exec(ctx, "DELETE FROM sessions WHERE user_id=$1", userID)
		_, _ = db.Exec(ctx, "DELETE FROM users WHERE user_id=$1", userID)
	}()
	s := &authService{db: db, codec: &shared.Codec{Key: []byte("test-only-signing-key-at-least-32-bytes"), Now: time.Now}, now: time.Now}
	sid, _, _, _, err := s.newSession(ctx, userID, clientInput{ClientType: "DESKTOP", DeviceID: "desktop-1"})
	if err != nil {
		t.Fatal(err)
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
	err = writeRevocation(ctx, tx, "00000000-0000-4000-8000-000000000000", sid, "REVOKED")
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

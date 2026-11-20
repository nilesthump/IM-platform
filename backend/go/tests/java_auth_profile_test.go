package tests

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/core"
	"im-platform/backend/go/gateway"
	"net/http/httptest"
	"os"
	"testing"
	"time"
)

// Only the explicit cross-profile command starts this real HTTP fixture host.
func TestJavaAuthProfileHost(t *testing.T) {
	if os.Getenv("JAVA_AUTH_PROFILE_HOST") != "1" {
		t.Skip("explicit Java/Go blackbox fixture host only")
	}
	if os.Getenv("DB_TEST_ENABLE") != "1" || os.Getenv("NATS_URL") == "" {
		t.Fatal("live services required")
	}
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	db, err := pgxpool.New(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	if err = db.Ping(ctx); err != nil {
		t.Fatal(err)
	}
	key, err := os.ReadFile(os.Getenv("JAVA_AUTH_SIGNING_KEY_FILE"))
	if err != nil {
		t.Fatal(err)
	}
	nc, err := nats.Connect(os.Getenv("NATS_URL"))
	if err != nil {
		t.Fatal(err)
	}
	defer nc.Close()
	coreServer := httptest.NewServer(core.NewHandler(db, key))
	defer coreServer.Close()
	handler, err := gateway.NewHandler(db, key, nc, coreServer.URL)
	if err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(handler)
	defer server.Close()
	relay := make(chan error, 1)
	go func() { relay <- core.RelaySessionRevocations(ctx, db, nc) }()
	if err = os.WriteFile(os.Getenv("JAVA_AUTH_URL_FILE"), []byte(server.URL), 0600); err != nil {
		t.Fatal(err)
	}
	tick := time.NewTicker(100 * time.Millisecond)
	defer tick.Stop()
	deadline := time.NewTimer(3 * time.Minute)
	defer deadline.Stop()
	for {
		select {
		case err := <-relay:
			t.Fatalf("relay stopped: %v", err)
		case <-deadline.C:
			t.Fatal("fixture host timed out")
		case <-tick.C:
			_, err = os.Stat(os.Getenv("JAVA_AUTH_STOP_FILE"))
			if err == nil {
				cancel()
				if err = <-relay; !errors.Is(err, context.Canceled) {
					t.Fatal(err)
				}
				return
			}
			if !errors.Is(err, os.ErrNotExist) {
				t.Fatal(err)
			}
		}
	}
}

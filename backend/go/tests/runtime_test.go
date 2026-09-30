package tests

import (
	"encoding/json"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/core"
	"im-platform/backend/go/gateway"
	"im-platform/backend/go/shared"
	"net/http"
	"os"
	"regexp"
	"testing"
	"time"
)

type testService struct {
	db      *pgxpool.Pool
	codec   *shared.Codec
	handler http.Handler
}

func newService(db *pgxpool.Pool, key []byte) *testService {
	return &testService{db, &shared.Codec{Key: key, Now: time.Now}, core.NewHandler(db, key)}
}
func testNATS(t *testing.T) *nats.Conn {
	t.Helper()
	u := os.Getenv("NATS_URL")
	if u == "" {
		u = "nats://127.0.0.1:4222"
	}
	nc, e := nats.Connect(u)
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(nc.Close)
	return nc
}
func newGateway(t *testing.T, db *pgxpool.Pool, key []byte) http.Handler {
	t.Helper()
	var nc *nats.Conn
	if db != nil {
		nc = testNATS(t)
	}
	h, e := gateway.NewHandler(db, key, nc, "http://localhost:1")
	if e != nil {
		t.Fatal(e)
	}
	return h
}
func publishRevocation(t *testing.T, nc *nats.Conn, sid, reason string) {
	t.Helper()
	b, _ := json.Marshal(map[string]string{"sessionId": sid, "reason": reason})
	if e := nc.Publish("session.revoked", b); e != nil {
		t.Fatal(e)
	}
	if e := nc.Flush(); e != nil {
		t.Fatal(e)
	}
}
func publishEvent(t *testing.T, sid, reason string) { publishRevocation(t, testNATS(t), sid, reason) }
func frame(typ, id string, payload any) any {
	return map[string]any{"protocolVersion": "1.0", "type": typ, "requestId": id, "payload": payload}
}
func validUUID(id string) bool {
	return regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`).MatchString(id)
}

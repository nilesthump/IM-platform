package core

import (
	"context"
	"encoding/json"
	"github.com/nats-io/nats.go"
	"os"
	"testing"
	"time"
)

func TestMessageOutboxPublicationCanRepeatWithoutNewMessage(t *testing.T) {
	f := newMessageFixture(t, 3)
	u := os.Getenv("NATS_URL")
	if u == "" {
		u = "nats://127.0.0.1:4222"
	}
	nc, err := nats.Connect(u)
	if err != nil {
		t.Fatal(err)
	}
	defer nc.Close()
	active, err := nc.SubscribeSync("message.created." + f.users[1])
	if err != nil {
		t.Fatal(err)
	}
	defer active.Unsubscribe()
	departed, err := nc.SubscribeSync("message.created." + f.users[2])
	if err != nil {
		t.Fatal(err)
	}
	defer departed.Unsubscribe()
	nc.Flush()
	f.db.Exec(context.Background(), `UPDATE conversation_members SET left_at=now() WHERE conversation_id=$1 AND user_id=$2`, f.conversation, f.users[2])
	id, _ := uuid()
	m, err := f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "delivery"))
	if err != nil {
		t.Fatal(err)
	}
	relaySessionBatch(context.Background(), f.db, nc)
	first, err := active.NextMsg(3 * time.Second)
	if err != nil {
		t.Fatal(err)
	}
	var event map[string]any
	if json.Unmarshal(first.Data, &event) != nil || event["type"] != "message.created" || event["requestId"] != id {
		t.Fatal("not canonical created")
	}
	if _, err = departed.NextMsg(80 * time.Millisecond); err != nats.ErrTimeout {
		t.Fatal("departed member received event")
	}
	var published bool
	if err = f.db.QueryRow(context.Background(), `SELECT published_at IS NOT NULL FROM outbox_events WHERE message_id=$1`, m.MessageID).Scan(&published); err != nil || !published {
		t.Fatal("publish not marked")
	}
	// Reproduce publish-before-mark crash: retry reuses the single durable event.
	if _, err = f.db.Exec(context.Background(), `UPDATE outbox_events SET published_at=NULL WHERE message_id=$1`, m.MessageID); err != nil {
		t.Fatal(err)
	}
	relaySessionBatch(context.Background(), f.db, nc)
	again, err := active.NextMsg(3 * time.Second)
	if err != nil || string(first.Data) != string(again.Data) {
		t.Fatal("publication retry changed logical event")
	}
	if f.count(t, `SELECT count(*) FROM messages WHERE conversation_id=$1`) != 1 || f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1`) != 1 {
		t.Fatal("publication duplicated persistence")
	}
}
func TestClosedNATSPublicationLeavesOutboxRetryable(t *testing.T) {
	f := newMessageFixture(t, 2)
	u := os.Getenv("NATS_URL")
	if u == "" {
		u = "nats://127.0.0.1:4222"
	}
	nc, err := nats.Connect(u)
	if err != nil {
		t.Fatal(err)
	}
	nc.Close()
	id, _ := uuid()
	_, err = f.s.commitMessage(context.Background(), f.claims[0], f.send(id, "retry"))
	if err != nil {
		t.Fatal(err)
	}
	relaySessionBatch(context.Background(), f.db, nc)
	if f.count(t, `SELECT count(*) FROM outbox_events WHERE conversation_id=$1 AND published_at IS NULL`) != 1 {
		t.Fatal("failed publisher marked outbox")
	}
}

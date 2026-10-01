package core

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
)

// Session and message events are stored in the same transaction as their writes.
// Publishing can repeat after a crash; the gateway handles duplicate events.
func RelaySessionRevocations(ctx context.Context, db *pgxpool.Pool, nc *nats.Conn) {
	ticker := time.NewTicker(500 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			relaySessionBatch(ctx, db, nc)
		}
	}
}

func relaySessionBatch(ctx context.Context, db *pgxpool.Pool, nc *nats.Conn) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	tx, err := db.Begin(ctx)
	if err != nil {
		return
	}
	defer tx.Rollback(ctx)
	rows, err := tx.Query(ctx, `SELECT event_id,event_type,payload,conversation_id FROM outbox_events WHERE event_type IN ('session.revoked','message.created') AND published_at IS NULL ORDER BY created_at,event_id LIMIT 32 FOR UPDATE SKIP LOCKED`)
	if err != nil {
		return
	}
	type event struct {
		id           string
		payload      []byte
		kind         string
		conversation *string
	}
	var events []event
	for rows.Next() {
		var e event
		if rows.Scan(&e.id, &e.kind, &e.payload, &e.conversation) != nil {
			rows.Close()
			return
		}
		events = append(events, e)
	}
	err = rows.Err()
	rows.Close()
	if err != nil {
		return
	}
	for _, e := range events {
		if e.kind == "session.revoked" {
			if nc.Publish("session.revoked", e.payload) != nil {
				return
			}
		} else {
			// Core owns recipient membership. Subjects are private routing
			// locators; every payload remains the canonical created frame.
			members, err := tx.Query(ctx, `SELECT user_id FROM conversation_members WHERE conversation_id=$1 AND left_at IS NULL`, e.conversation)
			if err != nil {
				return
			}
			var users []string
			for members.Next() {
				var user string
				if members.Scan(&user) != nil {
					members.Close()
					return
				}
				users = append(users, user)
			}
			err = members.Err()
			members.Close()
			if err != nil {
				return
			}
			for _, user := range users {
				if nc.Publish("message.created."+user, e.payload) != nil {
					return
				}
			}
		}
	}
	if len(events) > 0 {
		if nc.FlushTimeout(2*time.Second) != nil {
			return
		}
	}
	for _, e := range events {
		if _, err = tx.Exec(ctx, `UPDATE outbox_events SET published_at=now(),attempts=attempts+1 WHERE event_id=$1`, e.id); err != nil {
			return
		}
	}
	_ = tx.Commit(ctx)
}

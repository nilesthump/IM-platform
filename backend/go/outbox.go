package main

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
)

// Session revocations are stored in the same transaction as the Session change.
// Publishing can repeat after a crash; the gateway handles duplicate events.
func relaySessionRevocations(ctx context.Context, db *pgxpool.Pool, nc *nats.Conn) {
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
	rows, err := tx.Query(ctx, `SELECT event_id,payload FROM outbox_events WHERE event_type='session.revoked' AND published_at IS NULL ORDER BY created_at,event_id LIMIT 32 FOR UPDATE SKIP LOCKED`)
	if err != nil {
		return
	}
	type event struct {
		id      string
		payload []byte
	}
	var events []event
	for rows.Next() {
		var e event
		if rows.Scan(&e.id, &e.payload) != nil {
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
		if nc.Publish("session.revoked", e.payload) != nil {
			return
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

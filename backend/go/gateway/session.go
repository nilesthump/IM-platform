package gateway

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
	"time"
)

type validator struct {
	db    *pgxpool.Pool
	codec *shared.Codec
	now   func() time.Time
}

func (s *validator) authenticate(ctx context.Context, token string) (shared.Claims, error) {
	c, err := s.codec.Parse(token)
	if err != nil {
		return c, err
	}
	var sid, typ, status string
	var epoch int64
	var expiry time.Time
	err = s.db.QueryRow(ctx, `SELECT session_id, client_type, session_epoch, status, expires_at FROM sessions WHERE user_id=$1 AND client_type=$2`, c.UserID, c.ClientType).Scan(&sid, &typ, &epoch, &status, &expiry)
	if errors.Is(err, pgx.ErrNoRows) {
		var actualType string
		if s.db.QueryRow(ctx, `SELECT client_type FROM sessions WHERE user_id=$1 AND session_id=$2`, c.UserID, c.SessionID).Scan(&actualType) == nil && actualType != c.ClientType {
			return c, shared.Fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Access token does not match the active client session.")
		}
		return c, shared.Fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if err != nil {
		return c, err
	}
	if status != "ACTIVE" || !expiry.After(s.now()) {
		return c, shared.Fail(401, "AUTH_SESSION_REVOKED", "Session has been revoked.")
	}
	if epoch != c.SessionEpoch {
		return c, shared.Fail(401, "AUTH_SESSION_EPOCH_STALE", "Access token carries a stale session epoch.")
	}
	if sid != c.SessionID || typ != c.ClientType {
		var actualType string
		if s.db.QueryRow(ctx, `SELECT client_type FROM sessions WHERE user_id=$1 AND session_id=$2`, c.UserID, c.SessionID).Scan(&actualType) == nil && actualType != c.ClientType {
			return c, shared.Fail(401, "AUTH_CLIENT_TYPE_MISMATCH", "Access token does not match the active client session.")
		}
		return c, shared.Fail(401, "AUTH_TOKEN_INVALID", "Access token and session binding disagree.")
	}
	return c, nil
}

// A safety-watch failure can precede (or replace) NATS delivery. Only a
// committed revocation for this exact bound identity supplies a business reason;
// expiry, database faults and missing/unrecognized facts remain conservative.
func (s *validator) revocationReason(ctx context.Context, c shared.Claims, err error) string {
	e, ok := err.(shared.Error)
	if !ok || (e.Code != "AUTH_SESSION_REVOKED" && e.Code != "AUTH_SESSION_EPOCH_STALE") {
		return "REVOKED"
	}
	var reason string
	if s.db.QueryRow(ctx, `SELECT payload->>'reason' FROM user_sync_events WHERE user_id=$1 AND event_type='session.revoked' AND payload->>'sessionId'=$2 ORDER BY cursor_id DESC LIMIT 1`, c.UserID, c.SessionID).Scan(&reason) != nil {
		return "REVOKED"
	}
	switch reason {
	case "REPLACED", "LOGOUT":
		return reason
	default:
		return "REVOKED"
	}
}

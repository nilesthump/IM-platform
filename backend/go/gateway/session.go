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

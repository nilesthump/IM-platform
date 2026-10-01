package core

import (
	"github.com/jackc/pgx/v5/pgxpool"
	"im-platform/backend/go/shared"
	"net/http"
	"time"
)

func NewHandler(db *pgxpool.Pool, key []byte) http.Handler {
	s := &authService{db: db, codec: &shared.Codec{Key: key, Now: time.Now}, now: time.Now}
	m := shared.InfraMux("core")
	m.Handle("/v1/", s.handler())
	m.HandleFunc("POST /__core/message", s.sendMessage)
	m.HandleFunc("POST /__core/history", s.conversationHistory)
	return m
}

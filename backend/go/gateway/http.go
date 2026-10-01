package gateway

import (
	"crypto/sha1"
	"encoding/base64"
	"encoding/json"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/shared"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"time"
)

func NewHandler(db *pgxpool.Pool, key []byte, nc *nats.Conn, coreURL string) (http.Handler, error) {
	h := newHub(&validator{db: db, codec: &shared.Codec{Key: key, Now: time.Now}, now: time.Now})
	h.coreURL = coreURL
	if nc != nil {
		if _, err := nc.Subscribe("session.revoked", func(m *nats.Msg) {
			var v struct {
				SessionID string `json:"sessionId"`
				Reason    string `json:"reason"`
			}
			if json.Unmarshal(m.Data, &v) == nil {
				h.revoke(v.SessionID, v.Reason)
			}
		}); err != nil {
			return nil, err
		}
		if _, err := nc.Subscribe("message.created.*", func(m *nats.Msg) { h.fanout(strings.TrimPrefix(m.Subject, "message.created."), m.Data) }); err != nil {
			return nil, err
		}
		if err := nc.Flush(); err != nil {
			return nil, err
		}
	}
	m := shared.InfraMux("gateway")
	m.HandleFunc("/__infra/ws", func(w http.ResponseWriter, r *http.Request) {
		if !strings.EqualFold(r.Header.Get("Upgrade"), "websocket") || r.Header.Get("Sec-WebSocket-Key") == "" {
			http.NotFound(w, r)
			return
		}
		sum := sha1.Sum([]byte(r.Header.Get("Sec-WebSocket-Key") + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
		w.Header().Set("Upgrade", "websocket")
		w.Header().Set("Connection", "Upgrade")
		w.Header().Set("Sec-WebSocket-Accept", base64.StdEncoding.EncodeToString(sum[:]))
		w.WriteHeader(101)
	})

	m.HandleFunc("GET /v1/ws", h.serve)
	u, err := url.Parse(coreURL)
	if err != nil {
		return nil, err
	}
	m.Handle("/v1/", httputil.NewSingleHostReverseProxy(u))
	return m, nil
}

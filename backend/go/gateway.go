package main

import (
	"context"
	"encoding/json"
	"net/http"
	"regexp"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type hub struct {
	auth     *authService
	mu       sync.Mutex
	sessions map[string]map[*connection]bool
}
type connection struct {
	ws    *websocket.Conn
	mu    sync.Mutex
	done  chan struct{}
	once  sync.Once
	bound *claims
}
type envelope struct {
	ProtocolVersion string          `json:"protocolVersion"`
	Type            string          `json:"type"`
	RequestID       string          `json:"requestId"`
	Payload         json.RawMessage `json:"payload"`
}

var requestIDPattern = regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)

func validUUID(id string) bool { return requestIDPattern.MatchString(id) }

func newHub(auth *authService) *hub {
	return &hub{auth: auth, sessions: make(map[string]map[*connection]bool)}
}
func (c *connection) send(v any) error { c.mu.Lock(); defer c.mu.Unlock(); return c.ws.WriteJSON(v) }
func (c *connection) close() {
	c.once.Do(func() { close(c.done); c.mu.Lock(); _ = c.ws.Close(); c.mu.Unlock() })
}
func (h *hub) add(sid string, c *connection) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.sessions[sid] == nil {
		h.sessions[sid] = make(map[*connection]bool)
	}
	h.sessions[sid][c] = true
}
func (h *hub) remove(sid string, c *connection) {
	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.sessions[sid], c)
	if len(h.sessions[sid]) == 0 {
		delete(h.sessions, sid)
	}
}
func frame(typ, id string, payload any) any {
	return map[string]any{"protocolVersion": "1.0", "type": typ, "requestId": id, "payload": payload}
}
func (h *hub) revoke(sid, reason string) {
	h.mu.Lock()
	conns := make([]*connection, 0, len(h.sessions[sid]))
	for c := range h.sessions[sid] {
		conns = append(conns, c)
	}
	delete(h.sessions, sid)
	h.mu.Unlock()
	for _, c := range conns {
		id, _ := uuid()
		_ = c.send(frame("session.revoked", id, map[string]string{"sessionId": sid, "reason": reason}))
		c.close()
	}
}

func (h *hub) serve(w http.ResponseWriter, r *http.Request) {
	if len(r.URL.RawQuery) > 0 {
		writeError(w, r, fail(400, "VALIDATION_FAILED", "Query parameters are not permitted on WebSocket upgrade."))
		return
	}
	upgrader := websocket.Upgrader{}
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}
	c := &connection{ws: ws, done: make(chan struct{})}
	defer c.close()
	defer func() {
		if c.bound != nil {
			h.remove(c.bound.SessionID, c)
		}
	}()
	ws.SetReadLimit(65536)
	for {
		var raw map[string]json.RawMessage
		if err := ws.ReadJSON(&raw); err != nil {
			return
		}
		if len(raw) != 4 {
			return
		}
		b, _ := json.Marshal(raw)
		var e envelope
		if json.Unmarshal(b, &e) != nil || e.ProtocolVersion != "1.0" || !validUUID(e.RequestID) || len(e.Payload) == 0 {
			return
		}
		if e.Type == "ping" || e.Type == "pong" {
			var p map[string]any
			if json.Unmarshal(e.Payload, &p) != nil || len(p) != 0 {
				return
			}
			if e.Type == "ping" {
				_ = c.send(frame("pong", e.RequestID, map[string]any{}))
			}
			continue
		}
		if c.bound == nil {
			if e.Type != "auth.bind" {
				if e.Type == "message.send" {
					_ = c.send(frame("message.ack", e.RequestID, map[string]any{"status": "rejected", "error": map[string]string{"code": "AUTH_REQUIRED", "message": "Request rejected"}}))
				}
				return
			}
			var p struct {
				AccessToken string `json:"accessToken"`
			}
			if json.Unmarshal(e.Payload, &p) != nil || p.AccessToken == "" {
				h.reject(c, e.RequestID, "VALIDATION_FAILED", "Access token is required.")
				return
			}
			var pfields map[string]any
			_ = json.Unmarshal(e.Payload, &pfields)
			if len(pfields) != 1 {
				h.reject(c, e.RequestID, "VALIDATION_FAILED", "Auth binding payload is invalid.")
				return
			}
			cl, err := h.auth.authenticate(r.Context(), p.AccessToken)
			if err != nil {
				if ae, ok := err.(apiError); ok {
					h.reject(c, e.RequestID, ae.code, ae.message)
				} else {
					h.reject(c, e.RequestID, "AUTH_TOKEN_INVALID", "Access token is invalid.")
				}
				return
			}
			c.bound = &cl
			h.add(cl.SessionID, c)
			_ = c.send(frame("auth.ack", e.RequestID, map[string]any{"status": "bound", "userId": cl.UserID, "sessionId": cl.SessionID, "clientType": cl.ClientType, "sessionEpoch": cl.SessionEpoch}))
			go h.watch(c, cl)
			continue
		}
		// This slice has no message handling. A bound socket still checks PostgreSQL on each operation.
		if _, err := h.auth.authenticate(r.Context(), h.auth.mustSign(*c.bound)); err != nil {
			h.revoke(c.bound.SessionID, "REVOKED")
			return
		}
		if e.Type == "auth.bind" {
			h.reject(c, e.RequestID, "VALIDATION_FAILED", "Connection is already bound.")
			return
		}
		if e.Type == "message.send" {
			_ = c.send(frame("message.ack", e.RequestID, map[string]any{"status": "rejected", "error": map[string]string{"code": "AUTHORIZATION_DENIED", "message": "Request rejected"}}))
			continue
		}
		return
	}
}

func (s *authService) mustSign(c claims) string { t, _ := s.sign(c); return t }
func (h *hub) reject(c *connection, id, code, message string) {
	_ = c.send(frame("auth.ack", id, map[string]any{"status": "rejected", "error": map[string]string{"code": code, "message": "Request rejected"}}))
}

func (h *hub) watch(c *connection, cl claims) {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-c.done:
			return
		case <-ticker.C:
			ctx, cancel := context.WithTimeout(context.Background(), time.Second)
			_, err := h.auth.authenticate(ctx, h.auth.mustSign(cl))
			cancel()
			if err != nil {
				h.revoke(cl.SessionID, "REVOKED")
				return
			}
		}
	}
}

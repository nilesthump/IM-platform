package gateway

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"regexp"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
	"im-platform/backend/go/shared"
)

type hub struct {
	auth     *validator
	mu       sync.Mutex
	sessions map[string]map[*connection]bool
	coreURL  string
	client   *http.Client
}
type connection struct {
	ws      *websocket.Conn
	mu      sync.Mutex
	done    chan struct{}
	once    sync.Once
	bound   *shared.Claims
	token   string
	origins map[string]bool
}
type envelope struct {
	ProtocolVersion string          `json:"protocolVersion"`
	Type            string          `json:"type"`
	RequestID       string          `json:"requestId"`
	Payload         json.RawMessage `json:"payload"`
}

var requestIDPattern = regexp.MustCompile(`^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$`)

func validUUID(id string) bool { return requestIDPattern.MatchString(id) }

func newHub(auth *validator) *hub {
	return &hub{auth: auth, sessions: make(map[string]map[*connection]bool), client: &http.Client{Timeout: 10 * time.Second}}
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
		id, _ := shared.UUID()
		_ = c.send(frame("session.revoked", id, map[string]string{"sessionId": sid, "reason": reason}))
		c.close()
	}
}

func (h *hub) serve(w http.ResponseWriter, r *http.Request) {
	if len(r.URL.RawQuery) > 0 {
		writeError(w, r, shared.Fail(400, "VALIDATION_FAILED", "Query parameters are not permitted on WebSocket upgrade."))
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
				if ae, ok := err.(shared.Error); ok {
					h.reject(c, e.RequestID, ae.Code, ae.Message)
				} else {
					h.reject(c, e.RequestID, "AUTH_TOKEN_INVALID", "Access token is invalid.")
				}
				return
			}
			c.bound = &cl
			c.token = p.AccessToken
			h.add(cl.SessionID, c)
			_ = c.send(frame("auth.ack", e.RequestID, map[string]any{"status": "bound", "userId": cl.UserID, "sessionId": cl.SessionID, "clientType": cl.ClientType, "sessionEpoch": cl.SessionEpoch}))
			go h.watch(c, cl)
			continue
		}
		// A bound connection uses its validated binding, token expiry and the
		// NATS revocation registry. PostgreSQL is checked on bind/reconnect and
		// by the existing safety watch, never in the message operation path.
		if h.auth.now().Unix() >= c.bound.ExpiresAt {
			h.revoke(c.bound.SessionID, "REVOKED")
			return
		}
		if e.Type == "auth.bind" {
			h.reject(c, e.RequestID, "VALIDATION_FAILED", "Connection is already bound.")
			return
		}
		if e.Type == "message.send" {
			h.forward(r.Context(), c, e)
			continue
		}
		return
	}
}

func (h *hub) reject(c *connection, id, code, message string) {
	_ = c.send(frame("auth.ack", id, map[string]any{"status": "rejected", "error": map[string]string{"code": code, "message": "Request rejected"}}))
}

func (h *hub) watch(c *connection, cl shared.Claims) {
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-c.done:
			return
		case <-ticker.C:
			ctx, cancel := context.WithTimeout(context.Background(), time.Second)
			_, err := h.auth.authenticate(ctx, c.token)
			if err != nil {
				reason := h.auth.revocationReason(ctx, cl, err)
				cancel()
				h.revoke(cl.SessionID, reason)
				return
			}
			cancel()
		}
	}
}

func writeError(w http.ResponseWriter, r *http.Request, err error) {
	e := shared.Error{Status: 500, Code: "INTERNAL_ERROR", Message: "Internal server error."}
	if v, ok := err.(shared.Error); ok {
		e = v
	}
	id, _ := shared.UUID()
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(e.Status)
	_ = json.NewEncoder(w).Encode(map[string]any{"error": map[string]string{"code": e.Code, "message": e.Message}, "requestId": id})
}

// Forward only the canonical frame, using the validated connection's bearer.
// There are no membership or persistence decisions in Gateway.
func (h *hub) forward(ctx context.Context, c *connection, e envelope) {
	var payload struct {
		ConversationID string `json:"conversationId"`
	}
	_ = json.Unmarshal(e.Payload, &payload)
	key := strings.ToLower(payload.ConversationID) + ":" + strings.ToLower(e.RequestID)
	c.mu.Lock()
	if c.origins == nil {
		c.origins = make(map[string]bool)
	}
	previousOrigin := c.origins[key]
	c.origins[key] = true
	c.mu.Unlock()
	reject := func() {
		_ = c.send(frame("message.ack", e.RequestID, map[string]any{"status": "rejected", "error": map[string]string{"code": "MESSAGE_COMMIT_FAILED", "message": "Request rejected"}}))
	}
	b, err := json.Marshal(e)
	if err != nil {
		reject()
		return
	}
	req, err := http.NewRequestWithContext(ctx, "POST", strings.TrimRight(h.coreURL, "/")+"/__core/message", bytes.NewReader(b))
	if err != nil {
		reject()
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	response, err := h.client.Do(req)
	if err != nil {
		reject()
		return
	}
	defer response.Body.Close()
	var ack envelope
	if response.StatusCode != 200 || json.NewDecoder(io.LimitReader(response.Body, 65536)).Decode(&ack) != nil || ack.ProtocolVersion != "1.0" || ack.Type != "message.ack" || !strings.EqualFold(ack.RequestID, e.RequestID) {
		reject()
		return
	}
	var outcome struct {
		Status string `json:"status"`
	}
	if json.Unmarshal(ack.Payload, &outcome) != nil {
		reject()
		return
	}
	// A rejected retry cannot erase an earlier committed or uncertain send.
	if outcome.Status != "committed" && !previousOrigin {
		c.mu.Lock()
		delete(c.origins, key)
		c.mu.Unlock()
	}
	_ = c.send(ack)
}

func (h *hub) fanout(user string, data []byte) {
	if !validUUID(user) {
		return
	}
	var e envelope
	if json.Unmarshal(data, &e) != nil || e.ProtocolVersion != "1.0" || e.Type != "message.created" || !validUUID(e.RequestID) {
		return
	}
	var p struct {
		ConversationID string `json:"conversationId"`
		MessageID      string `json:"messageId"`
		SenderID       string `json:"senderId"`
		Seq            int64  `json:"seq"`
		CreatedAt      string `json:"createdAt"`
		Content        struct {
			Kind string `json:"kind"`
			Text string `json:"text"`
		} `json:"content"`
	}
	if json.Unmarshal(e.Payload, &p) != nil || !validUUID(p.ConversationID) || !validUUID(p.MessageID) || !validUUID(p.SenderID) || p.Seq < 1 || p.Content.Kind != "TEXT" {
		return
	}
	if _, err := time.Parse(time.RFC3339Nano, p.CreatedAt); err != nil {
		return
	}
	h.mu.Lock()
	var conns []*connection
	for _, slot := range h.sessions {
		for c := range slot {
			if c.bound != nil && c.bound.UserID == user {
				conns = append(conns, c)
			}
		}
	}
	h.mu.Unlock()
	key := strings.ToLower(p.ConversationID) + ":" + strings.ToLower(e.RequestID)
	for _, c := range conns {
		select {
		case <-c.done:
			continue
		default:
		}
		if h.auth.now().Unix() >= c.bound.ExpiresAt {
			continue
		}
		c.mu.Lock()
		origin := p.SenderID == user && c.origins[key]
		c.mu.Unlock()
		if !origin {
			_ = c.send(e)
		}
	}
}

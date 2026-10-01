package gateway

import (
	"encoding/json"
	"github.com/gorilla/websocket"
	"im-platform/backend/go/shared"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestPrivateForwardUsesBoundBearerAndCanonicalFrame(t *testing.T) {
	id := "40000000-0000-4000-8000-000000000001"
	conv := "30000000-0000-4000-8000-000000000001"
	received := make(chan bool, 1)
	core := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var e envelope
		json.NewDecoder(r.Body).Decode(&e)
		received <- r.URL.Path == "/__core/message" && r.Header.Get("Authorization") == "Bearer fixture-not-a-credential" && e.Type == "message.send" && e.RequestID == id
		json.NewEncoder(w).Encode(frame("message.ack", id, map[string]any{"status": "committed", "conversationId": conv, "messageId": "50000000-0000-4000-8000-000000000001", "seq": 1, "createdAt": "2026-09-28T00:00:01Z"}))
	}))
	defer core.Close()
	h := newHub(&validator{now: time.Now})
	h.coreURL = core.URL
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ws, e := (&websocket.Upgrader{}).Upgrade(w, r, nil)
		if e != nil {
			return
		}
		defer ws.Close()
		c := &connection{ws: ws, done: make(chan struct{}), token: "fixture-not-a-credential"}
		h.forward(r.Context(), c, envelope{ProtocolVersion: "1.0", Type: "message.send", RequestID: id, Payload: json.RawMessage(`{"conversationId":"` + conv + `","content":{"kind":"TEXT","text":"hello"}}`)})
	}))
	defer server.Close()
	ws, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), nil)
	if err != nil {
		t.Fatal(err)
	}
	defer ws.Close()
	var ack envelope
	if ws.ReadJSON(&ack) != nil || ack.Type != "message.ack" {
		t.Fatal("ACK not forwarded")
	}
	if !<-received {
		t.Fatal("transport changed identity/frame")
	}
}
func TestLocalFanoutSelectsUserAndSuppressesOriginOnly(t *testing.T) {
	user := "10000000-0000-4000-8000-000000000001"
	other := "10000000-0000-4000-8000-000000000002"
	request := "40000000-0000-4000-8000-000000000001"
	conv := "30000000-0000-4000-8000-000000000001"
	h := newHub(&validator{now: time.Now})
	connections := make(chan *connection, 3)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ws, e := (&websocket.Upgrader{}).Upgrade(w, r, nil)
		if e != nil {
			return
		}
		c := &connection{ws: ws, done: make(chan struct{}), bound: &shared.Claims{UserID: user, SessionID: r.URL.Path, ExpiresAt: time.Now().Add(time.Hour).Unix()}}
		if r.URL.Path == "/other" {
			c.bound.UserID = other
		}
		if r.URL.Path == "/origin" {
			c.origins = map[string]bool{conv + ":" + request: true}
		}
		h.add(c.bound.SessionID, c)
		connections <- c
		<-c.done
	}))
	defer server.Close()
	var clients []*websocket.Conn
	var conns []*connection
	for _, path := range []string{"/origin", "/another", "/other"} {
		ws, _, e := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http")+path, nil)
		if e != nil {
			t.Fatal(e)
		}
		clients = append(clients, ws)
		conns = append(conns, <-connections)
	}
	defer func() {
		for _, c := range conns {
			c.close()
		}
		for _, c := range clients {
			c.Close()
		}
	}()
	b, _ := json.Marshal(frame("message.created", request, map[string]any{"conversationId": conv, "messageId": "50000000-0000-4000-8000-000000000001", "senderId": user, "seq": 1, "createdAt": "2026-09-28T00:00:01Z", "content": map[string]string{"kind": "TEXT", "text": "hello"}}))
	h.fanout(user, b)
	h.fanout(user, b)
	for i := 0; i < 2; i++ {
		clients[1].SetReadDeadline(time.Now().Add(time.Second))
		var e envelope
		if clients[1].ReadJSON(&e) != nil || e.Type != "message.created" {
			t.Fatal("sender other session missing/repeated event")
		}
	}
	for _, i := range []int{0, 2} {
		clients[i].SetReadDeadline(time.Now().Add(80 * time.Millisecond))
		var e envelope
		if clients[i].ReadJSON(&e) == nil {
			t.Fatal("origin/unauthorized local user received event")
		}
	}
}

func TestRejectedRetryPreservesCommittedOrigin(t *testing.T) {
	user := "10000000-0000-4000-8000-000000000001"
	request := "40000000-0000-4000-8000-000000000001"
	conv := "30000000-0000-4000-8000-000000000001"
	core := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var e envelope
		if json.NewDecoder(r.Body).Decode(&e) != nil {
			t.Error("decode send")
			return
		}
		var p struct {
			Content struct {
				Text string `json:"text"`
			} `json:"content"`
		}
		json.Unmarshal(e.Payload, &p)
		payload := map[string]any{"status": "committed", "conversationId": conv, "messageId": "50000000-0000-4000-8000-000000000001", "seq": 1, "createdAt": "2026-09-28T00:00:01Z"}
		if p.Content.Text == "conflict" {
			payload = map[string]any{"status": "rejected", "error": map[string]string{"code": "MESSAGE_REQUEST_CONFLICT", "message": "Request rejected"}}
		}
		json.NewEncoder(w).Encode(frame("message.ack", request, payload))
	}))
	defer core.Close()
	h := newHub(&validator{now: time.Now})
	h.coreURL = core.URL
	connections := make(chan *connection, 2)
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ws, err := (&websocket.Upgrader{}).Upgrade(w, r, nil)
		if err != nil {
			return
		}
		c := &connection{ws: ws, done: make(chan struct{}), bound: &shared.Claims{UserID: user, SessionID: r.URL.Path, ExpiresAt: time.Now().Add(time.Hour).Unix()}}
		h.add(c.bound.SessionID, c)
		connections <- c
		if r.URL.Path == "/origin" {
			for i := 0; i < 2; i++ {
				var e envelope
				if ws.ReadJSON(&e) != nil {
					return
				}
				h.forward(r.Context(), c, e)
			}
		}
		<-c.done
	}))
	defer server.Close()
	var clients []*websocket.Conn
	var conns []*connection
	for _, path := range []string{"/origin", "/other"} {
		ws, _, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http")+path, nil)
		if err != nil {
			t.Fatal(err)
		}
		clients = append(clients, ws)
		conns = append(conns, <-connections)
	}
	defer func() {
		for _, c := range conns {
			c.close()
		}
		for _, c := range clients {
			c.Close()
		}
	}()
	for i, text := range []string{"hello", "conflict"} {
		if err := clients[0].WriteJSON(frame("message.send", request, map[string]any{"conversationId": conv, "content": map[string]string{"kind": "TEXT", "text": text}})); err != nil {
			t.Fatal(err)
		}
		clients[0].SetReadDeadline(time.Now().Add(time.Second))
		var ack struct {
			Payload struct {
				Status string `json:"status"`
			} `json:"payload"`
		}
		if clients[0].ReadJSON(&ack) != nil {
			t.Fatal("ACK missing")
		}
		want := "committed"
		if i == 1 {
			want = "rejected"
		}
		if ack.Payload.Status != want {
			t.Fatal("unexpected ACK")
		}
	}
	b, _ := json.Marshal(frame("message.created", request, map[string]any{"conversationId": conv, "messageId": "50000000-0000-4000-8000-000000000001", "senderId": user, "seq": 1, "createdAt": "2026-09-28T00:00:01Z", "content": map[string]string{"kind": "TEXT", "text": "hello"}}))
	for i := 0; i < 2; i++ {
		h.fanout(user, b)
		clients[1].SetReadDeadline(time.Now().Add(time.Second))
		var e envelope
		if clients[1].ReadJSON(&e) != nil || e.Type != "message.created" {
			t.Fatal("other session missing event")
		}
	}
	clients[0].SetReadDeadline(time.Now().Add(100 * time.Millisecond))
	var e envelope
	err := clients[0].ReadJSON(&e)
	if err == nil {
		t.Fatal("rejected retry erased original suppression")
	}
	if !strings.Contains(err.Error(), "timeout") {
		t.Fatal(err)
	}
}

package gateway

import (
	"github.com/gorilla/websocket"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// Exercise actual Gateway admission and its unbound state, not a copied checker.
func TestOriginAdmissionRetainsAuthenticationBoundary(t *testing.T) {
	h := newHub(nil)
	server := httptest.NewServer(http.HandlerFunc(h.serve))
	defer server.Close()
	sameHost := server.URL
	tests := []struct {
		name     string
		origins  []string
		admitted bool
	}{
		{"absent", nil, true},
		{"same host", []string{sameHost}, true},
		{"same host ASCII case", []string{strings.ToUpper(sameHost)}, true},
		{"exact Windows Tauri", []string{"http://tauri.localhost"}, true},
		{"unrelated", []string{"http://example.invalid"}, false},
		{"lookalike suffix", []string{"http://tauri.localhost.example.invalid"}, false},
		{"lookalike userinfo", []string{"http://tauri.localhost@example.invalid"}, false},
		{"alternate scheme", []string{"https://tauri.localhost"}, false},
		{"alternate case", []string{"http://TAURI.localhost"}, false},
		{"port", []string{"http://tauri.localhost:80"}, false},
		{"trailing slash", []string{"http://tauri.localhost/"}, false},
		{"malformed", []string{"http://%"}, false},
		{"empty", []string{""}, false},
		{"multiple Tauri", []string{"http://tauri.localhost", "http://tauri.localhost"}, false},
		{"Tauri followed by same host", []string{"http://tauri.localhost", sameHost}, false},
		{"same host first preserves default", []string{sameHost, "http://example.invalid"}, true},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			for _, kind := range []string{"message.send", "auth.bind"} {
				header := http.Header{}
				if tc.origins != nil {
					header["Origin"] = tc.origins
				}
				ws, response, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http"), header)
				if !tc.admitted {
					if err == nil {
						ws.Close()
						t.Fatal("unapproved Origin admitted")
					}
					if response == nil || response.StatusCode != http.StatusForbidden {
						t.Fatalf("expected403, got %v", response)
					}
					response.Body.Close()
					return
				}
				if err != nil {
					t.Fatalf("approved/default Origin rejected: %v", err)
				}
				ws.SetReadDeadline(time.Now().Add(2 * time.Second))
				id := "40000000-0000-4000-8000-000000000001"
				if err = ws.WriteJSON(frame(kind, id, map[string]any{})); err != nil {
					ws.Close()
					t.Fatal(err)
				}
				var ack struct {
					Type      string `json:"type"`
					RequestID string `json:"requestId"`
					Payload   struct {
						Status string `json:"status"`
						Error  struct {
							Code string `json:"code"`
						} `json:"error"`
					} `json:"payload"`
				}
				err = ws.ReadJSON(&ack)
				ws.Close()
				if err != nil {
					t.Fatal(err)
				}
				wantType, wantCode := "message.ack", "AUTH_REQUIRED"
				if kind == "auth.bind" {
					wantType, wantCode = "auth.ack", "VALIDATION_FAILED"
				}
				if ack.Type != wantType || ack.RequestID != id || ack.Payload.Status != "rejected" || ack.Payload.Error.Code != wantCode {
					t.Fatalf("Origin bypassed binding: %+v", ack)
				}
			}
		})
	}
	// Kelvin folds to ASCII K under Unicode folding, but not Gorilla's default.
	kelvinServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { r.Host = "k.example"; h.serve(w, r) }))
	defer kelvinServer.Close()
	ws, response, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(kelvinServer.URL, "http"), http.Header{"Origin": []string{"http://\u212a.example"}})
	if err == nil {
		ws.Close()
		t.Fatal("Unicode host equivalence admitted")
	}
	if response == nil || response.StatusCode != http.StatusForbidden {
		t.Fatalf("Kelvin expected403, got %v", response)
	}
	response.Body.Close()
}

func TestWindowsOriginDoesNotPermitQueryCredentials(t *testing.T) {
	h := newHub(nil)
	server := httptest.NewServer(http.HandlerFunc(h.serve))
	defer server.Close()
	ws, response, err := websocket.DefaultDialer.Dial("ws"+strings.TrimPrefix(server.URL, "http")+"?access_token=fixture-not-a-credential", http.Header{"Origin": []string{"http://tauri.localhost"}})
	if err == nil {
		ws.Close()
		t.Fatal("query credential admitted")
	}
	if response == nil || response.StatusCode != http.StatusBadRequest {
		t.Fatalf("expected400, got %v", response)
	}
	response.Body.Close()
}

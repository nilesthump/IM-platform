package main

import (
	"crypto/sha1"
	"encoding/base64"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatal("expected gateway, core, or plugin-host role")
	}
	role := os.Args[1]
	if role != "gateway" && role != "core" && role != "plugin-host" {
		log.Fatal("unknown role")
	}
	http.HandleFunc("/__infra/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		fmt.Fprintf(w, "profile=go role=%s\n", role)
	})
	http.HandleFunc("/__infra/ws", func(w http.ResponseWriter, r *http.Request) {
		if role != "gateway" || !strings.EqualFold(r.Header.Get("Upgrade"), "websocket") || r.Header.Get("Sec-WebSocket-Key") == "" {
			http.NotFound(w, r)
			return
		}
		key := r.Header.Get("Sec-WebSocket-Key")
		sum := sha1.Sum([]byte(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
		w.Header().Set("Upgrade", "websocket")
		w.Header().Set("Connection", "Upgrade")
		w.Header().Set("Sec-WebSocket-Accept", base64.StdEncoding.EncodeToString(sum[:]))
		w.WriteHeader(http.StatusSwitchingProtocols)
	})
	log.Fatal(http.ListenAndServe(":8080", nil))
}

package main

import (
	"context"
	"crypto/sha1"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatal("expected gateway, core, or plugin-host role")
	}
	role := os.Args[1]
	if role != "gateway" && role != "core" && role != "plugin-host" {
		log.Fatal("unknown role")
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/__infra/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			http.Error(w, "method not allowed", 405)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		fmt.Fprintf(w, "profile=go role=%s\n", role)
	})
	mux.HandleFunc("/__infra/ws", func(w http.ResponseWriter, r *http.Request) {
		if role != "gateway" || !strings.EqualFold(r.Header.Get("Upgrade"), "websocket") || r.Header.Get("Sec-WebSocket-Key") == "" {
			http.NotFound(w, r)
			return
		}
		sum := sha1.Sum([]byte(r.Header.Get("Sec-WebSocket-Key") + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"))
		w.Header().Set("Upgrade", "websocket")
		w.Header().Set("Connection", "Upgrade")
		w.Header().Set("Sec-WebSocket-Accept", base64.StdEncoding.EncodeToString(sum[:]))
		w.WriteHeader(101)
	})
	if role == "plugin-host" {
		log.Fatal(http.ListenAndServe(":8080", mux))
	}
	configPath := os.Getenv("IM_CONFIG_FILE")
	if configPath == "" {
		configPath = "/run/im-config/config.json"
	}
	cfg, key, pgConfig, err := readConfig(configPath)
	if err != nil {
		log.Fatal("Go runtime configuration unavailable")
	}
	db, err := pgxpool.NewWithConfig(context.Background(), pgConfig)
	if err != nil {
		log.Fatal("database configuration failed")
	}
	defer db.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	err = db.Ping(ctx)
	cancel()
	if err != nil {
		log.Fatal("database unavailable")
	}
	s := &authService{db: db, key: key, now: time.Now}
	nc, err := nats.Connect(cfg.NATSURL, nats.MaxReconnects(-1))
	if err != nil {
		log.Fatal("NATS unavailable")
	}
	defer nc.Close()
	if role == "core" {
		go relaySessionRevocations(context.Background(), db, nc)
		mux.Handle("/v1/", s.handler())
	} else {
		h := newHub(s)
		_, err = nc.Subscribe("session.revoked", func(m *nats.Msg) {
			var v struct {
				SessionID string `json:"sessionId"`
				Reason    string `json:"reason"`
			}
			if json.Unmarshal(m.Data, &v) == nil {
				h.revoke(v.SessionID, v.Reason)
			}
		})
		if err != nil {
			log.Fatal("NATS subscription failed")
		}
		mux.HandleFunc("GET /v1/ws", h.serve)
		u, err := url.Parse(cfg.CoreURL)
		if err != nil {
			log.Fatal("invalid core address")
		}
		mux.Handle("/v1/", httputil.NewSingleHostReverseProxy(u))
	}
	log.Fatal(http.ListenAndServe(":8080", mux))
}

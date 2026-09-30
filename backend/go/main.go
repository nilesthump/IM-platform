package main

import (
	"context"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/nats-io/nats.go"
	"im-platform/backend/go/core"
	"im-platform/backend/go/gateway"
	pluginhost "im-platform/backend/go/plugin-host"
	"im-platform/backend/go/shared"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatal("expected gateway, core, or plugin-host role")
	}
	role := os.Args[1]
	if role != "gateway" && role != "core" && role != "plugin-host" {
		log.Fatal("unknown role")
	}
	if role == "plugin-host" {
		log.Fatal(http.ListenAndServe(":8080", pluginhost.NewHandler()))
	}
	path := os.Getenv("IM_CONFIG_FILE")
	if path == "" {
		path = "/run/im-config/config.json"
	}
	cfg, key, pg, err := shared.ReadConfig(path)
	if err != nil {
		log.Fatal("Go runtime configuration unavailable")
	}
	db, err := pgxpool.NewWithConfig(context.Background(), pg)
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
	nc, err := nats.Connect(cfg.NATSURL, nats.MaxReconnects(-1))
	if err != nil {
		log.Fatal("NATS unavailable")
	}
	defer nc.Close()
	var h http.Handler
	if role == "core" {
		ctx, stop := context.WithCancel(context.Background())
		defer stop()
		go core.RelaySessionRevocations(ctx, db, nc)
		h = core.NewHandler(db, key)
	} else {
		h, err = gateway.NewHandler(db, key, nc, cfg.CoreURL)
		if err != nil {
			log.Fatal("gateway configuration failed")
		}
	}
	log.Fatal(http.ListenAndServe(":8080", h))
}

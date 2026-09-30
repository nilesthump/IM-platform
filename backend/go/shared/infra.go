package shared

import (
	"fmt"
	"net/http"
)

// InfraMux is the existing non-business role health and transport probe.
func InfraMux(role string) *http.ServeMux {
	m := http.NewServeMux()
	m.HandleFunc("/__infra/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			http.Error(w, "method not allowed", 405)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		fmt.Fprintf(w, "profile=go role=%s\n", role)
	})
	return m
}

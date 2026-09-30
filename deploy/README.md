# Loop 1 infrastructure skeleton

From a clean checkout with Docker Compose, start exactly one backend profile:

```powershell
docker compose -f deploy/compose.yaml --profile go up -d --build
docker compose -f deploy/compose.yaml --profile go down
docker compose -f deploy/compose.yaml --profile java up -d --build
```

The HTTPS/WSS entrypoint is `https://localhost:8443`. Caddy creates a local development certificate; clients must explicitly trust its local CA or opt into insecure certificate verification for development smoke tests. Set `IM_HTTPS_PORT` if 8443 is occupied, and `IM_POSTGRES_PASSWORD` to replace the development-only database password. Only the proxy port is published. Do not run both profiles in one Compose project.

Java remains an S0 transport placeholder. Go Core owns the implemented Auth/User HTTP routes and Session/Outbox writes; Go Gateway forwards HTTP to Core and owns `/v1/ws` binding, readonly Session validation and revocation connections. Each role retains `/__infra/health`; Gateway retains the `/__infra/ws` transport smoke probe. Go reads the external configuration directory named by `IM_GO_CONFIG_DIR` (see `backend/go/config.example.json`); no credentials are stored in Git. The independent `migrate` service applies the canonical `contracts/database` migration before profile services start. PostgreSQL is persistent in a named volume; `docker compose -f deploy/compose.yaml --profile go down --volumes` discards local data.

Run `tests/infrastructure/smoke.ps1 -Profile go` and then `-Profile java` from PowerShell 7 to build disposable isolated projects and verify running services, migration, Core NATS, HTTPS, and a WebSocket upgrade through actual TLS. The smoke cleans up its own projects and volumes.

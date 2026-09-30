# Go Auth/Session implementation development evidence

- Actor: fresh Implementation Agent `/root/go_auth_impl`; isolated branch `task/LOOP1-GO-AUTH-001` based on activation `f187cfa2b7c083447aa5f1694ef8553a9d26758c`. This is development evidence, not independent review or CI acceptance.
- Scope: Go Core registration/login/refresh/logout and user self/search, PostgreSQL slot/epoch/refresh state, JWT access tokens, bcrypt password hashes with SHA-256 prehash, Gateway WSS `auth.bind`, durable session revocation Outbox relay through NATS, config-file credential loading, Go CI job, and read-only Go Compose config mounts. No public contract, migration, architecture, Java, or client file changed.
- Human explicitly approved the exact `deploy/compose.yaml` path for config-file connection on 2026-09-29 after an earlier automatic approval review rejected Coordinator-only scope expansion. The Task Spec was amended before that deploy file was edited. `config.example.json` names external credential files; test-only secrets and production secrets are not committed. The Go Core and Gateway mount one operator-provided directory read-only at `/run/im-config`.
- New dependencies serve current requirements: pgx for authoritative PostgreSQL transactions, Gorilla WebSocket for RFC 6455 framing, NATS client for the existing event bus, and x/crypto bcrypt for password hashing. No new database object or contract was added.
- Research Recorder prompt `P-4842e715-701e-4666-87f5-ce9a8068d23a`; run `R-20260929T113637Z-033a1064-c4d8-4276-b309-717762d4d6ab` uses `prospective_resume` because startup inspection preceded run creation. The initial system Python 2 registration attempt failed; bundled Python 3 registration succeeded after sandbox write access was granted. Recorder artifacts are research instrumentation, not Task acceptance.

## Local verification

| Command or check | Result |
| --- | --- |
| `go -C backend/go test -race -count=1 ./...` with `DB_TEST_ENABLE=1`, isolated migrated PostgreSQL 16 and NATS 2.10 | PASS, exit 0; deterministic unit and live DB/NATS/WSS integration including three slots, same-slot concurrent replacement, epoch rejection, pre-bind denial, bind, `session.revoked` then close, refresh rotation, logout, and rollback. Recorder-wrapped final run passed. |
| `go -C backend/go build ./...` | PASS, exit 0; a generated Windows `go.exe` was subsequently removed after resolved-path verification. CI builds to `$RUNNER_TEMP/im-go`. |
| `go vet ./...` in `backend/go` | PASS, exit 0. |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` | PASS, exit 0; 9 paths, 9 operations, 6 positive and 21 negative scenarios. |
| `python contracts/websocket/verify.py` using bundled Python 3 | PASS, exit 0; 8 positive, 10 negative scenarios. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | PASS, exit 0; canonical Markdown and historical PDF hashes match manifest. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | PASS, exit 0; development mode is not acceptance evidence. |
| `python -m unittest discover -s tests/ci -v` using bundled Python 3 | PASS, exit 0; 19 tests, 4 Windows symlink subcases skipped due missing OS privilege. Initial run failed because S0 tests expected no Go source; only the Go S0 boundary and its assertions were replaced, then all tests passed. |
| `docker compose -f deploy/compose.yaml --profile go config --quiet` | PASS, exit 0. |
| `git diff --check`; `go -C backend/go test ./...` | PASS, exit 0. |

## Limits and next acceptance

- Local `tests/infrastructure/smoke.ps1 -Profile go` did not reach the service: Docker's configured `docker.1panel.live` mirror returned HTTP 403 while resolving `golang:1.25-alpine` for the Go builder (`failed to resolve source metadata`). This is an external local image-access failure, not a profile PASS. The disposable Compose project was torn down by the smoke script. Existing unrelated Docker containers were untouched.
- Production config must supply `config.json`, `pg_password`, and `jwt_key` in the read-only mounted directory via `IM_GO_CONFIG_DIR`; local test files were created outside Git. Go profile behavior behind Caddy TLS is still unverified locally because of the builder fetch failure.
- Applicable real hosted CI and clean independent review remain required. Coordinator should move this clean committed candidate to `review`, delegate a fresh Review Agent, then obtain CI PASS before `done`. No self-review or Gate PASS is claimed.

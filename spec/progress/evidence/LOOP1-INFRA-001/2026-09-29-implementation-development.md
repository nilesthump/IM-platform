# LOOP1-INFRA-001 implementation development evidence

- Branch: `task/LOOP1-INFRA-001`; base: `1a6ade7` (Infra activation), accepted dependency base: `3e4d0f3cb3030731345288f677d2048d72651fd5`.
- Actor: fresh Implementation Agent `/root/infra001_impl`; not independent acceptance.
- Product paths: `deploy/**`, non-business `backend/go/**` and `backend/java/**`, `tests/infrastructure/**`. Recovery and instrumentation paths are Task-authorized. Frozen Architecture, public contracts, schema, and migration SQL were not edited.
- Prompt: `P-c5e10382-3faa-4cf2-89d8-1cb9feb8fcea`; prospective Recorder run: `R-20260928T184630Z-a4f1554d-496f-4b5a-8d30-a4bc46edfb7b`.
- `docker compose -f deploy/compose.yaml --profile go config --quiet`: exit 0.
- `docker compose -f deploy/compose.yaml --profile java config --quiet`: exit 0.
- `pwsh -NoProfile -File tests/infrastructure/smoke.ps1 -Profile go`: initial run exit 1 due to smoke script PowerShell array construction (`gateway-`); corrected. Re-run exit 0: PostgreSQL migration, NATS health, HTTPS health and WebSocket Upgrade via Caddy TLS 1.3. Disposable project and volumes removed.
- `pwsh -NoProfile -File tests/infrastructure/smoke.ps1 -Profile java`: exit 0 with the same checks; disposable project and volumes removed.
- `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`: exit 0. This is explicitly non-acceptance.
- `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`: exit 0; canonical Markdown and historical PDF hashes match the manifest.
- Remaining: fresh independent review must verify a clean committed checkout and run both profiles and CTRL-002 Acceptance. The local Caddy CA is intentionally development-only; production certificate provisioning is outside this S0 skeleton.

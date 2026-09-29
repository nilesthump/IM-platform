---
task_id: LOOP1-GO-AUTH-001
title: Implement Go Auth and Session vertical slice
status: review
owner: fresh independent reviewer pending Fix 1 candidate
stage: S1
gate: S1
---

# Goal

Implement Go registration/login, refresh, logout, Session slot and epoch handling, and WSS `auth.bind` against the frozen HTTP/WSS contracts and canonical database migration.

# Inputs

- Frozen Architecture v1.0 chapters 2, 4, 7, 11, 19 and appendix B, resolved and hash-checked through `spec/architecture/README.md`.
- Approved ADRs in `spec/architecture/decisions/` and `spec/governance/minimality.md`.
- `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, `spec/acceptance/s0-auth-user-friend.md`.
- `contracts/http/`, `contracts/errors/`, `contracts/websocket/`, relevant fixtures under `contracts/fixtures/`, and `contracts/database/`.

# Dependencies

- S0 Gate PASS on merged `main`.
- `LOOP1-CI-001`, `LOOP1-INFRA-001`, `LOOP1-DB-001`, and all three Contract tasks `done`.

# Allowed Paths

- `backend/go/**`
- `deploy/compose.yaml` only for read-only Go Core/Gateway mounts of one operator-provided directory containing `config.json`, `pg_password`, and `jwt_key`; no credential file is committed and Java/TLS service behavior remains unchanged.
- Go Auth/Session integration tests under `tests/go/**`
- `ci/**`, `.github/workflows/ci.yml`, and `tests/ci/**` only to replace the S0 Go placeholder boundary with actual Go build/test/contract execution; preserve other jobs and Gate semantics.
- `spec/tasks/**/LOOP1-GO-AUTH-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-AUTH-001/**`
- `spec/progress/checkpoints/*loop1-go-auth-001*.md`
- `research/prompts/**` and `research/runs/**` only for Recorder artifacts linked to this task.

The Coordinator prospectively authorized the exact task-linked evidence, checkpoint, and Recorder paths at S1 activation. No path here authorizes changes to architecture, public contracts, migrations, or other backends.

The Human explicitly approved modifying `deploy/compose.yaml` for this configuration-file connection after the automatic approval review rejected the earlier Coordinator-only scope expansion. This exact-path authorization was received on 2026-09-29; it does not authorize any other deployment path or secret material in Git.

# Acceptance

- Go HTTP behavior matches the canonical Auth/User contract and shared errors for registration, login, refresh, and logout.
- Three client-type slots can coexist; same-slot login atomically revokes the prior Session and advances epoch. Old tokens cannot bind or reconnect; successful logout revokes Session and Refresh Token and closes its WSS connection.
- WSS remains unauthenticated until valid `auth.bind`, rejects non-allowed pre-bind operations, and binds user, Session and client type. Same-slot replacement emits `session.revoked` before close.
- PostgreSQL is authoritative; secrets never enter URL query, logs, traces, or error responses. Production transport stays behind HTTPS/WSS/TLS.
- Deterministic Go contract/integration tests exercise positive and negative fixtures, transaction rollback, revocation, epoch, and refresh-token handling. Applicable real CI passes after independent review.

# Forbidden

- Change Frozen Architecture, public contracts, database migration, ACK/Sync/Plugin semantics, or security boundary.
- Implement social, messages, Java, clients, or future-stage mechanisms.
- Treat a local test PASS or self-review as acceptance.

# Minimality

Implement one direct Go path using the existing PostgreSQL schema, NATS/TLS skeleton, and canonical fixtures. Add dependencies or layers only for a present contract, transaction, security, or test need; record their justification in evidence.

# Verification

- Run the existing HTTP and WSS contract verifiers and Go Auth/Session integration suite, including failure and concurrency cases.
- Run frozen-architecture verification and `tools/verify-loop1-ctrl-002.ps1 -Mode Development` during development.
- Fresh independent review must use a clean committed checkout and applicable real CI. Do not use ADR-0001 bootstrap acceptance: it expired at S0.

# Evidence

- Entry checkpoint: `spec/progress/checkpoints/2026-09-29-loop1-ci-001-remote-main-s0-gate-pass.md`; clean S0 `main` at `09cec968f64faf0db319aea8d9c21d4fffe8ec49`.
- Coordinator activation evidence: `spec/progress/evidence/LOOP1-GO-AUTH-001/2026-09-29-s1-activation-development.md`; Recorder run `R-20260929T110755Z-54301c59-3bb4-4bb6-a884-ec0b3fc7fa49`. This is development/recovery evidence, not independent task acceptance. Implementation evidence pending.
- Implementation development evidence: `spec/progress/evidence/LOOP1-GO-AUTH-001/2026-09-29-go-auth-implementation-development.md`; linked Recorder `R-20260929T113637Z-033a1064-c4d8-4276-b309-717762d4d6ab`. Local Go race/integration, HTTP/WSS verifiers, frozen hashes, CTRL-002 Development, CI tests, and Compose config passed. Full local Go profile smoke stopped before service startup on Docker registry mirror HTTP 403. Hosted CI and independent review remain pending.
- Candidate `a93569d2153e8766c298e11d12ef1549565312b7` is committed and the implementation worktree was clean at handoff. Coordinator moved the task to `review` for an independent clean-checkout reviewer; acceptance and hosted CI remain pending.
- Independent Review 1 FAIL for candidate `a93569d`: the Go suite does not execute the canonical HTTP/WSS fixtures, and a focused WSS probe received `pong` for a non-UUID `requestId` contrary to `contracts/websocket/envelope.schema.json`. Evidence: `spec/progress/evidence/LOOP1-GO-AUTH-001/2026-09-29-independent-review1-fail.md`; Recorder `R-20260929T143107Z-279b7a3e-f218-418d-925a-5a7f42e4421e` finished FAIL and integrity-valid. Task remains `review`; hosted CI is still pending.
- Fresh Fix 1 executes the current Auth/User positive and negative fixture outcomes and applicable WSS golden scenarios in Go tests; dynamic IDs and credentials are normalized. WSS rejects malformed UUID `requestId` for every inbound envelope, including ping. Live PostgreSQL/NATS Go race tests, contract verifiers, frozen hashes, CTRL-002 Development, Go vet, and 19 CI unit tests pass locally. Evidence: `spec/progress/evidence/LOOP1-GO-AUTH-001/2026-09-29-go-auth-fix1-development.md`; Recorder `R-20260929T151415Z-c0d03dff-1c6a-4238-86b0-96a4f38d19e5`. This is development evidence only; fresh independent review and hosted CI remain required.

# Handoff

- The isolated branch `task/LOOP1-GO-AUTH-001` contains the Auth/Session implementation and development evidence. No architecture, contract, migration, Java, or client files changed. The Implementation Agent owns only task-allowed implementation, CI, config mount, Task Spec/current recovery, evidence, and linked Recorder artifacts until the clean candidate commit. Last independently accepted base remains `09cec968f64faf0db319aea8d9c21d4fffe8ec49`.

# Next Action

- Commit this Fix 1 candidate, delegate a new independent Review Agent in a clean checkout, then obtain applicable hosted CI on PASS. Retain `review` until both are accepted. Local Go Compose smoke remains unverified because of Docker image access.

---
task_id: LOOP1-SYNC-GO-001
title: Go Core public Sync runtime prerequisite
status: active
owner: /root/sync_go_implementation
stage: S2
gate: S2
---

# Goal

Implement the two accepted public HTTPS Sync pull operations in Go Core, backed by real authoritative PostgreSQL reads, so the existing Desktop/Mobile SYNC task can consume an independently accepted runtime input. Human separately consented to the displayed Go proposal on 2026-10-03 with the exact reply "同意". This is a current proven prerequisite, not future-stage task selection. Final batch endpoint remains LOOP1-SYNC-001 complete then stop.

# Inputs

- spec/architecture/README.md -> baseline.md -> frozen-architecture.md, SHA ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03; canonical sections 2.3,3,6.1,7,10 SRC-01..SRC-07,11.
- Approved ADR-0005-client-technology-clarification.md, ADR-0006-client-ui-architecture.md, ADR-0007-client-mvp-task-planning.md, ADR-0008-sync-https-transport.md in spec/architecture/decisions/.
- spec/governance/minimality.md, execution-boundaries.md, independent-review.md, technology-selection.md.
- spec/domain/messaging.md, sync-plugin.md, auth-user-friend.md; spec/invariants/messaging.md, sync-plugin.md, auth-user-friend.md.
- spec/acceptance/s0-sync-plugin.md and s0-auth-user-friend.md; relevant Sync/Auth sections only, not plugin implementation.
- contracts/http/sync.openapi.json, auth-user-friend.openapi.json; contracts/websocket/sync-v1.schema.json, envelope.schema.json; contracts/errors/http-errors.schema.json; contracts/database/README.md, migrate.py and migrations/0001_initial.up.sql / 0001_initial.down.sql.
- spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/go-implementation-proposal.md and acceptance/acceptance.md.
- spec/progress/evidence/LOOP1-SYNC-GO-001/human-consent.md.

# Technology Authorization

Canonical sections 3/7/10 and accepted ADR-0008 authorize existing Go Core + PostgreSQL, existing pgx and existing crypto/token support. Use Go/Python standard libraries and existing approved infrastructure/test dependencies only. No new framework, library, service, DB object, signing key source/config or runtime. Gateway existing /v1/ proxy requires no product change. Core owns auth/session authorization and Sync queries.

# Dependencies

- LOOP1-SYNC-TRANSPORT-001: done, product b820078/c2ff050 independently accepted; administrative3588/actualmain4d5fe1235e4f01111d78cc67b2880b52cac072f2 independently accepted and preservation-verified synchronized.
- LOOP1-SEND-001: independently accepted main a0304fcc7be18b87f5986d014849d6b48b96a071.
- Explicit Human implementation consent after prerequisite acceptance/displayed proposal: received. No remaining Go consent hold.

# Allowed Paths

- backend/go/core/sync.go
- backend/go/core/auth.go (only two route registrations; existing Auth semantics unchanged)
- backend/go/core/sync_test.go
- backend/go/core/sync_http_test.go
- backend/go/tests/sync_test.go
- backend/go/tests/sync_tls_test.go
- tools/verify_sync_runtime.py (bounded real entrypoint acceptance, reusing existing deployment harness where suitable)
- .github/workflows/ci.yml (only necessary explicit Sync runtime verification in existing Go/deploy jobs)
- spec/tasks/active/LOOP1-SYNC-GO-001.md
- spec/tasks/review/LOOP1-SYNC-GO-001.md
- spec/tasks/done/LOOP1-SYNC-GO-001.md
- spec/tasks/backlog/LOOP1-SYNC-001.md (runtime prerequisite recovery facts only; no activation before accepted runtime)
- spec/progress/current.md
- spec/progress/evidence/LOOP1-SYNC-GO-001/**
- spec/progress/checkpoints/*sync-go*.md

Coordinator alone creates this task/current/evidence activation before delegating the sole writer. Every writer verifies exact assigned Git root H:/.codex/worktrees/sync-resume/IM-platform. Preserve H:/IM-platform unknown work. No blanket backend paths; actual producer/auth inspection outside write scope is read-only. No new worktree/clone needed.

# Acceptance

- Both two canonical HTTPS operations actually work through TLS proxy -> Gateway -> Core; auth derived solely from Bearer and authoritative Session checked per request including after blocking authorization locks.
- Exact existing four shapes, UUID correlation/error precedence, strict fields/types, no query parameters, canonical error/status codes, no credentials in logs/errors and no-store. Unexpected infrastructure failure non-2xx, never successful page.
- Any positive integer limit accepted exactly and capped min(limit,100) before conversion. Any nonnegative integer afterSeq accepted exactly; above committed head empty terminal. No integer overflow/loss.
- User initial0; opaque account-bound stable cursor reusable across same account Sessions, no expiry; invalid/fabricated/foreign/unknown positions rejected400. Four existing metadata kinds only, never Message/session.revoked. Empty retains input cursor; nonempty nextCursor last event token; additional committed eligible item determines hasMore.
- Existing producer paths audited for shared user-row serialization before ID allocation; read uses matching locks to ensure stable committed prefix. Real PostgreSQL blocked writers/concurrent commits prove no missed late lower IDs. No producer/schema rewrite.
- Current membership authorization each Conversation request; nonexistent/nonmember identical403. Single consistent query returns seq afterSeq+1 gap-free committed Messages plus correct hasMore. Read-only, no Message/Outbox/ACK writes.
- Real runtime fixtures for each stream >100 items page until terminal, per-page cap, complete total, dedupe and final position; terminal-after-new-commit subsequent pull observes new write. Replays, huge exact integers, auth/session negative cases, forged/foreign cursor, member isolation and old regressions actually executed.
- Fresh independent Review of clean committed candidate including logic/imports/minimality; exact-head applicable hosted CI with actual enabled PG/race/runtime checks, protected integration, independent actual-main audit/CI and preservation-verified H:/IM-platform synchronization. Local/Recorder PASS is not acceptance and runtime task acceptance is not SYNC/S2 PASS.

# Forbidden

No contracts/frozen/ADR changes, database/schema/migration/producer writes, shared codec/config rewrite, Gateway business, client/UI/Web/plugin product work, new sensitive dependency, ACK/security/compatibility change, key-expiry/retention/reset/future infrastructure. Existing private history endpoint consumers remain unchanged. Genuine architecture conflict stops affected work rather than being legalized by task scope.

# Minimality

Direct Core handlers and narrow Sync decoding/cursor projection/read queries. Reuse existing token key with domain-separated standard HMAC/base64url cursor; no new cryptographic authority/config. Shared user-row serialization is justified by approved stable committed-prefix requirement and observed BIGSERIAL allocation before commit; verify all producers and live concurrency before claiming safety. Avoid generic protocol/validation/query frameworks. Existing Go tests/harness and existing CI jobs supply acceptance; bounded extra runtime verifier only for real deployed TLS proof missing from existing tests.

# Verification

Minimum baseline: `tools/verify_frozen_architecture.py` and `ci/check_architecture.py` --scope all --json (Coordinator recorded PASS at accepted4d5fe before task activation).
Go checks from backend/go: gofmt, go build ./..., go vet ./..., go test -count=1 ./..., go test -race -count=1 ./... with DB_TEST_ENABLE=1, actual canonical migrated PostgreSQL and NATS_URL for relevant old tests; record environment presence/services, do not count unset-variable skips.
Bounded entrypoints: `tools/verify_sync_runtime.py` (if needed) and existing `tools/verify-loop1-ctrl-002.ps1` -Mode Acceptance, clean committed checkout.
Frozen verification, architecture --scope all and tests/architecture; existing contracts HTTP/WSS/Sync/plugin checks, Sync binding tests and Auth/social/message/ACK regressions.
Existing go hosted job already builds/vets/tests/races with real PostgreSQL16+NATS; deployment acceptance must use existing real Go roles/TLS proxy and strict CA verification. CI hook cannot simulate results or silently skip a necessary case.
Applicable exact candidate/actual-main hosted job set independently derived from unchanged classifier, actual selected job/step conclusions inspected.

# Evidence

Activation baseline: accepted4d5fe1235e4f01111d78cc67b2880b52cac072f2; assigned clean task/LOOP1-SYNC-001. Human consent and administrative closure references in human-consent.md. All new run history under this evidence root or Git-private Recorder root, sealed old evidence immutable.

# Handoff

Active implementation not yet begun. Coordinator owns task/current/consent activation; sole writer transfers to /root/sync_go_implementation after activation commit. Last known good actual main4d5fe1235e4f01111d78cc67b2880b52cac072f2, no migrations. SYNC remains backlog on actual runtime input; S1 PASS/S2 OPEN. Existing main781unknown entries preserved. Every failure/risk and exact verification/evidence/commit/synchronization fact must be recorded before handoff.

# Next Action

Fresh Implementation Agent reads mandatory startup and complete inputs, verifies assigned root, registers Human/delegation prompt and starts Recorder, implements/test-proves minimal Go runtime within allowed paths, commits clean review candidate and hands sole writer back. Coordinator delegates a fresh independent Review, repairs through fresh Fix/new Review as necessary, obtains exact hosted acceptance/integration/synchronization, then resumes dependency-satisfied client SYNC and stops after its full acceptance.

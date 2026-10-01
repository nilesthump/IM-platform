---
task_id: LOOP1-GO-MSG-001
title: Implement Go text messaging, durable ACK, Outbox, and NATS
status: active
owner: /root/message_implementation (sole product writer after Coordinator release)
stage: S1
gate: S1
---

# Goal

Implement one logical text Message per authorized send with Conversation sequence, durable ACK, idempotent retry, Outbox dispatch, and realtime NATS delivery.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- `spec/domain/messaging.md`, `spec/invariants/messaging.md`, `spec/acceptance/s0-messaging.md`.
- Canonical WSS/error/fixture, Sync and database contracts in `contracts/`.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-SOCIAL-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

# Allowed Paths

- `backend/go/core/message.go` (private canonical text write transaction/internal send adapter)
- `backend/go/core/message_test.go` (atomicity/idempotency/ACK/authorization fault tests)
- `backend/go/core/http.go` (only existing Core assembly/private adapter registration)
- `backend/go/core/outbox.go` (message-created dispatch, existing Session behavior preserved)
- `backend/go/core/outbox_test.go` (actual publication/retry/marking tests)
- `backend/go/core/sync.go` (only canonical ConversationRequest/Page gap compensation, no full client/user-sync feature)
- `backend/go/core/sync_test.go` (history authorization/order/page tests)
- `backend/go/gateway/gateway.go` (canonical WSS forwarding/local bound fan-out only)
- `backend/go/gateway/http.go` (existing transport/subscription assembly only)
- `backend/go/gateway/message_test.go` (transport/duplicate/wrong-Conversation local delivery tests)
- `backend/go/tests/message_test.go` (blackbox canonical/live combined tests using existing helpers)
- `backend/go/main.go` (only dispatcher startup assembly if a name change is necessary)
- `spec/tasks/**/LOOP1-GO-MSG-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-MSG-001/**`
- `spec/progress/checkpoints/*loop1-go-msg-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

Coordinator prospectively binds exact existing flat stage-four service layout before any product write on 2026-10-01. This is ordinary feature scope under canonical SRC-01..07, not language-wide migration or architecture exemption. No shared/Auth/Social/schema/workflow edits authorized. Existing Gateway-to-Core HTTP and Core/NATS/Gateway event boundaries may use private Core-only adapter locators carrying unchanged canonical send/ACK/history shapes and bound bearer; per-user NATS subjects carry unchanged canonical message.created. No new public /v1 endpoint/frame field or direct cross-service import. Core retains credential/membership/routing decisions and durable commit; Gateway only forwards and fans out to local bound connections. Concrete mapping/readiness: 2026-10-01-activation-and-path-map.md under Task evidence.

# Acceptance

- Non-member sends reject before persistence. Sequence allocation, Message and one logical Outbox event commit atomically; success ACK follows durable commit only.
- Retry with the same sender, Conversation and request identity returns the same logical Message and sequence; distinct Conversations remain independent.
- Dispatcher/NATS duplication cannot create duplicate logical Messages or client materialization; Sync closes missed-delivery gaps. One GROUP send stays one Message and Outbox event.
- Canonical fixtures, fault-injection integration tests, independent review, and applicable real CI pass.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Weaken ACK/idempotency/order/authorization rules, make NATS the source of truth, change contracts/migrations, or implement clients/Java/future-stage mechanisms.

# Minimality

Use the existing PostgreSQL transaction and Outbox/NATS skeleton directly; add no speculative broker or ordering layer.

# Verification

- Discoverable entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`.

- During edits run `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`; clean committed independent candidate runs Acceptance. Run `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`.

- Run WSS fixtures and Go messaging integration tests for rollback, ACK timing, duplicate retry/delivery, sequence and wrong-Conversation rejection; run recovery and architecture checks.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Activated backlog -> ready -> active on 2026-10-01 after independently accepted Social actual-main merge b442acd and hostedCI36813501417 SUCCESS. Readiness/path evidence: 2026-10-01-activation-and-path-map.md.

# Handoff

- Fresh /root/message_implementation completed read-only input/path planning. Coordinator release grants sole writer ownership of this Task only after activation commit. No product files changed at activation.

# Next Action

- Implementation Agent: read active task/current, register delegated visible prompt and start prospective Recorder before work; run minimum baseline, then implement bounded message transaction/dispatch/forwarding/gap checks. Commit development candidate and handoff to NEW independent Review plus exact hosted CI. Never self-accept or claim S1 Gate PASS.

# Bound verification and recovery (2026-10-01)

Minimum pre-edit baseline: `python -B contracts/websocket/verify.py`, `python -B ci/check_architecture.py --scope all --json`, Development recovery, existing live normal/race Go suites on unique migrated disposable PostgreSQL16/NATS2.10 with DB_TEST_ENABLE=1. Record actual enable variables/services/skips; environment skips are not live PASS. Frozen verifier/source tests/CI controls plus recursive gofmt/build/vet and normal/race remain applicable before handoff. Clean committed Acceptance only; NEW independent Review then applicable real exact-head hosted CI before done. Last known good actualmain b442acd26777c481620a6bd917863cebfaf79b35/CI36813501417. No known product baseline failure; Social friend403 DEFERRED_BY_HUMAN never applies to message membership. Governance activation owned by Coordinator until commit; product writes owned solely by fresh Implementation Agent after release.

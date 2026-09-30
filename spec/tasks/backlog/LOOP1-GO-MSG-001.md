---
task_id: LOOP1-GO-MSG-001
title: Implement Go text messaging, durable ACK, Outbox, and NATS
status: backlog
owner: unassigned
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

- `backend/go/core/message/**`
- `backend/go/core/outbox/**`
- `backend/go/gateway/** only WSS forwarding/local fan-out/connection handling and related tests`
- Go messaging integration tests under `tests/go/**`
- `spec/tasks/**/LOOP1-GO-MSG-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-MSG-001/**`
- `spec/progress/checkpoints/*loop1-go-msg-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

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

- Run WSS fixtures and Go messaging integration tests for rollback, ACK timing, duplicate retry/delivery, sequence and wrong-Conversation rejection; run recovery and architecture checks.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Pending activation after Go Social acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Remain backlog until remediation batch PASS; then promote only when `LOOP1-GO-SOCIAL-001` is independently accepted and `done`.

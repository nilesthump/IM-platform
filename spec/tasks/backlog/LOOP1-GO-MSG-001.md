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

- Frozen Architecture v1.0 chapters 2, 4, 5, 7, 8, 11, 19 and appendix B; approved ADRs and Minimality Contract.
- `spec/domain/messaging.md`, `spec/invariants/messaging.md`, `spec/acceptance/s0-messaging.md`.
- Canonical WSS/error/fixture, Sync and database contracts in `contracts/`.

# Dependencies

- `LOOP1-GO-SOCIAL-001` done; S0 Gate PASS.

# Allowed Paths

- `backend/go/**`
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

# Forbidden

- Weaken ACK/idempotency/order/authorization rules, make NATS the source of truth, change contracts/migrations, or implement clients/Java/future-stage mechanisms.

# Minimality

Use the existing PostgreSQL transaction and Outbox/NATS skeleton directly; add no speculative broker or ordering layer.

# Verification

- Run WSS fixtures and Go messaging integration tests for rollback, ACK timing, duplicate retry/delivery, sequence and wrong-Conversation rejection; run recovery and architecture checks.

# Evidence

- Pending activation after Go Social acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Promote only when `LOOP1-GO-SOCIAL-001` is independently accepted and `done`.

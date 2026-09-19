---
task_id: LOOP1-CONTRACT-002
title: Freeze WSS Envelope, Auth, and Message contracts
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Define canonical WSS envelopes and auth.bind/ack, message.send/ack/created, and session.revoked contracts.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 5, 7, 11, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- `spec/domain/messaging.md`
- `spec/invariants/messaging.md`
- `spec/acceptance/s0-messaging.md`
- Approved error and HTTP contracts from LOOP1-CONTRACT-001.

# Dependencies

- LOOP1-CONTRACT-001 done.
- LOOP1-SPEC-001 done.

# Allowed Paths

- `contracts/websocket/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- Relevant `spec/domain/**`, `spec/invariants/**`, and `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-002.md`
- `spec/progress/current.md`

# Acceptance

- Required WSS envelopes and message types are machine-verifiable.
- Contract generation and tests pass, including durable-commit ACK and idempotent retry vectors.

# Forbidden

- Implement Gateway/Core behavior.
- Weaken ACK, authentication, authorization, ordering, or idempotency semantics.
- Modify Sync or Plugin API beyond referenced shared envelope types.

# Verification

- Run contract generator and WSS positive/negative fixture tests.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after LOOP1-CONTRACT-001 is independently accepted.

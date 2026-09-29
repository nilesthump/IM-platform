---
task_id: LOOP1-E2E-001
title: Verify first Go end-to-end messaging slice
status: backlog
owner: unassigned
stage: S1
gate: S1
---

# Goal

Prove A can log in, search/add B, obtain the unique DIRECT Conversation, send `hello`, receive durable ACK, and B receives it in realtime through the real TLS entrypoint.

# Inputs

- Frozen Architecture v1.0 chapters 5, 7, 11, 15, 19 and appendix A; approved ADRs and Minimality Contract.
- Canonical HTTP, WSS, Sync, error, fixture and database contracts; accepted Go Auth/Social/Message implementations.

# Dependencies

- `LOOP1-GO-MSG-001` done; S0 Gate PASS.

# Allowed Paths

- `tests/e2e/**`
- Go profile test wiring under `deploy/**` only if required for the real TLS E2E run.
- `spec/tasks/**/LOOP1-E2E-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-E2E-001/**`
- `spec/progress/checkpoints/*loop1-e2e-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

# Acceptance

- A-to-B `hello` succeeds through HTTPS/WSS/TLS and B receives one correct realtime Message after a durable ACK.
- End-to-end retries, authorization, revocation, transaction rollback, Outbox/NATS delivery, and contract outcomes preserve the S1 correctness red lines.
- Clean-checkout integration/E2E checks, independent review, and applicable real CI pass; S1 Gate evidence is durable and a stable checkpoint exists.

# Forbidden

- Rewrite contracts, migrations, or product semantics to make E2E pass; introduce client UI, Java implementation, or future-stage infrastructure.

# Minimality

Exercise the accepted Go path with a direct fixture-driven harness; add only test wiring needed for actual TLS and service interaction.

# Verification

- Run Go profile Compose and E2E over real TLS plus all S1 contract/integration checks; evaluate the S1 Gate checklist on a clean integrated candidate.

# Evidence

- Pending activation after Go Message acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Promote only when `LOOP1-GO-MSG-001` is independently accepted and `done`.

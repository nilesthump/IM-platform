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

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- Canonical HTTP, WSS, Sync, error, fixture and database contracts; accepted Go Auth/Social/Message implementations.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-MSG-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

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

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Rewrite contracts, migrations, or product semantics to make E2E pass; introduce client UI, Java implementation, or future-stage infrastructure.

# Minimality

Exercise the accepted Go path with a direct fixture-driven harness; add only test wiring needed for actual TLS and service interaction.

# Verification

- Run Go profile Compose and E2E over real TLS plus all S1 contract/integration checks; evaluate the S1 Gate checklist on a clean integrated candidate.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Pending activation after Go Message acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Remain backlog until remediation batch PASS; then promote only when `LOOP1-GO-MSG-001` is independently accepted and `done`.

---
task_id: LOOP1-GO-SOCIAL-001
title: Implement Go search, friendship, and unique direct conversation
status: backlog
owner: unassigned
stage: S1
gate: S1
---

# Goal

Implement Go user search, immediate bidirectional friendship, and unique DIRECT Conversation creation or reuse.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, `spec/acceptance/s0-auth-user-friend.md`.
- Canonical HTTP/error/fixture, database and Sync contracts in `contracts/`.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-AUTH-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

# Allowed Paths

- `backend/go/core/user/**`
- `backend/go/core/friend/**`
- `backend/go/core/conversation/**`
- `backend/go/core/sync/**`
- `backend/go/core/outbox/**`
- Go social integration tests under `tests/go/**`
- `spec/tasks/**/LOOP1-GO-SOCIAL-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-SOCIAL-001/**`
- `spec/progress/checkpoints/*loop1-go-social-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

# Acceptance

- Search and friend operations match canonical HTTP/errors and authorization.
- Concurrent A-to-B and B-to-A add converges on one normalized friendship and one DIRECT Conversation, with both memberships, Sync events, and Outbox effects in one atomic transaction.
- Immediate bidirectional friendship is observable; no pending approval flow is exposed.
- Integration and canonical fixture checks pass; fresh independent review and applicable real CI accept the candidate.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Change public contracts or database invariants; add approval flow, messaging implementation, Java/client behavior, or speculative infrastructure.

# Minimality

Use the canonical uniqueness constraints and one direct transaction path; no extra social workflow or persistence model.

# Verification

- Run Go social contract/integration tests including concurrent reverse-order add and rollback, plus recovery and architecture checks.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Pending activation after Go Auth acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Remain backlog until remediation batch PASS; then promote only when `LOOP1-GO-AUTH-001` is independently accepted and `done`.

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

- Frozen Architecture v1.0 chapters 2, 4, 7, 11, 19 and appendix B; approved ADRs and Minimality Contract.
- `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, `spec/acceptance/s0-auth-user-friend.md`.
- Canonical HTTP/error/fixture, database and Sync contracts in `contracts/`.

# Dependencies

- `LOOP1-GO-AUTH-001` done; S0 Gate PASS.

# Allowed Paths

- `backend/go/**`
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

# Forbidden

- Change public contracts or database invariants; add approval flow, messaging implementation, Java/client behavior, or speculative infrastructure.

# Minimality

Use the canonical uniqueness constraints and one direct transaction path; no extra social workflow or persistence model.

# Verification

- Run Go social contract/integration tests including concurrent reverse-order add and rollback, plus recovery and architecture checks.

# Evidence

- Pending activation after Go Auth acceptance.

# Handoff

- Unassigned. No files owned or changed for this task.

# Next Action

- Promote only when `LOOP1-GO-AUTH-001` is independently accepted and `done`.

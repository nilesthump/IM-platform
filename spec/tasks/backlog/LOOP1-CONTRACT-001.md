---
task_id: LOOP1-CONTRACT-001
title: Freeze HTTP Auth, User, and Friend contracts
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Define the canonical HTTP Auth/User/Friend OpenAPI contract, shared errors, and positive and negative golden fixtures.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 7, 11, 19 and appendix B.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- Relevant domain, invariant, and S0 acceptance documents.

# Dependencies

- LOOP1-CTRL-002 done.
- Required Auth/User/Friend domain, invariant, and acceptance inputs complete.

# Allowed Paths

- `contracts/http/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- `spec/domain/**`
- `spec/invariants/**`
- `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-001.md`
- `spec/progress/current.md`

# Acceptance

- Canonical OpenAPI and error contracts exist for Auth/User/Friend.
- Schema lint passes and positive/negative fixtures are complete.

# Forbidden

- Implement either backend.
- Invent semantics that conflict with Frozen Architecture.
- Change WSS, Sync, Plugin API, ACK, or compatibility semantics outside this task.

# Verification

- Run schema lint and all positive/negative fixture checks defined by this task.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after all dependencies and inputs are complete.

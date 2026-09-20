---
task_id: LOOP1-CONTRACT-001
title: Freeze HTTP Auth, User, and Friend contracts
status: active
owner: loop1-contract-001-implementation-agent
stage: S0
gate: S0
---

# Goal

Define the canonical HTTP Auth/User/Friend OpenAPI contract, shared errors, and positive and negative golden fixtures.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 7, 11, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- `spec/domain/auth-user-friend.md`
- `spec/invariants/auth-user-friend.md`
- `spec/acceptance/s0-auth-user-friend.md`

# Dependencies

- LOOP1-CTRL-002 done.
- LOOP1-SPEC-001 done.

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

- While editing, run `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`; run default Acceptance mode only from a clean committed review checkout.
- Run schema lint and all positive/negative fixture checks defined by this task.

# Evidence

- Dependency `LOOP1-CTRL-002` is `done` with independent acceptance evidence at `spec/progress/evidence/LOOP1-CTRL-002/2026-09-20-independent-review-d86bf17-pass.md`.
- Dependency `LOOP1-SPEC-001` is `done` with independent acceptance evidence at `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-independent-review-aef6497-pass.md`.
- Required inputs `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, and `spec/acceptance/s0-auth-user-friend.md` are present and were independently accepted as part of reviewed commit `aef6497d6216d9a8251250d157935e7af418d86b`.
- Activated from local `main` closure commit `e5482b135a2ab7451c24c29c7517e1a8f19ce420` on dedicated branch `task/LOOP1-CONTRACT-001` after dependency and input validation.

# Handoff

- Active and assigned to fresh Implementation Agent identity `loop1-contract-001-implementation-agent`; no contract implementation has started at activation handoff.

# Next Action

- A fresh Implementation Agent must read all declared authority inputs, then define only the HTTP Auth/User/Friend contracts, shared errors, and positive/negative golden fixtures within `allowed_paths`; prepare deterministic schema lint and fixture verification before review.

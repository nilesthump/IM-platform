---
task_id: LOOP1-CONTRACT-003
title: Freeze Sync and Plugin API v1 contracts
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Define canonical user cursor, per-conversation sequence Sync, and Plugin API v1 Events/Queries/Actions/UI Host contracts.

# Inputs

- Architecture Baseline v1.0 chapters 2, 6, 8, 9, 11, 19 and appendix B.
- Approved ADRs/frozen decisions and relevant domain, invariant, acceptance, HTTP, WSS, and error contracts.

# Dependencies

- LOOP1-CONTRACT-002 done.

# Allowed Paths

- `contracts/plugin-api/**`
- `contracts/websocket/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- Relevant `spec/domain/**`, `spec/invariants/**`, and `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-003.md`
- `spec/progress/current.md`

# Acceptance

- User cursor and conversation sequence Sync contracts are machine-verifiable.
- Plugin API v1 Events/Queries/Actions/UI Host contracts are machine-verifiable.
- Fixtures cover duplicate, out-of-order, gap, and permission-denial cases.

# Forbidden

- Implement Sync or plugin runtime behavior.
- Weaken cursor, contiguous sequence, capability, permission, sandbox, or immutable-version rules.

# Verification

- Run schema lint and duplicate/out-of-order/gap/permission fixture tests.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after LOOP1-CONTRACT-002 is independently accepted.

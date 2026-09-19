---
task_id: LOOP1-CTRL-002
title: Validate and harden Agent recovery context, current state, and Task schema
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Validate and harden the handoff context, current-state document, and Task Spec schema so a new Agent dry-run can recover work in the mandated order.

# Inputs

- Architecture Baseline v1.0 chapters 10, 12, 13, 19 and 21.
- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- `spec/tasks/TASK_TEMPLATE.md`

# Dependencies

- LOOP1-CTRL-001 done with independent CI acceptance.

# Allowed Paths

- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/tasks/**/LOOP1-CTRL-002.md`
- `tools/**`
- `tests/**`

# Acceptance

- A clean-context Agent dry-run finds the current task, its authority inputs, allowed paths, verification, and next exact action in the required order.
- Handoff and current-state fields cover every chapter 13 requirement without copying the architecture baseline.

# Forbidden

- Duplicate repository rules in `CLAUDE.md` or create a parallel Agent authority.
- Change Frozen Architecture or public contracts.
- Implement product behavior.

# Verification

- Run the repository control-plane lint and a documented clean-context recovery dry-run.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- After LOOP1-CTRL-001 is done, move this Task Spec to `ready/`.

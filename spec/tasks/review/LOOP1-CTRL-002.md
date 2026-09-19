---
task_id: LOOP1-CTRL-002
title: Validate and harden Agent recovery context, current state, and Task schema
status: review
owner: loop1-control-agent
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

# Plan

1. Derive machine-checkable recovery requirements from the mandated startup order and chapter 13 handoff fields.
2. Add a CTRL-002 verifier under `tools/` that performs a clean-context dry-run without scanning implementation as architecture.
3. Harden only the allowed control-plane documents if the dry-run exposes a real gap.
4. Run the CTRL-001 baseline plus CTRL-002 recovery verification, review the diff, and prepare handoff without claiming S0 Gate PASS.

# Evidence

- Dependency evidence: LOOP1-CTRL-001 is in `done/` with final review-closure PASS.
- `& .\tools\verify-loop1-ctrl-001.ps1`: final exit code 0; PASS for 6 control files, 44 directories, and 7 tracked S0 tasks.
- `& .\tools\verify-loop1-ctrl-002.ps1`: exit code 0; all six clean-context recovery steps PASS across 8 Task Specs and 5 queues.
- The initial CTRL-001 baseline run exposed a stale assumption that every follow-up S0 task must remain in `backlog/`; the verifier now requires each task to exist exactly once across the five queues with matching declared status.
- Review exposed and corrected a second stale assumption: the CTRL-002 verifier now validates both its active recovery state and its review handoff state instead of failing when the Task Spec follows its prescribed queue transition.
- No business implementation, public contract, Frozen Architecture, or `.github/workflows/` change was introduced.

# Handoff

- Activated on branch `task/LOOP1-CTRL-002` from remote-verified main `53815faf92f80d425f1bd1e286d653c87f8a1087`.
- Added `tools/verify-loop1-ctrl-002.ps1` for the documented clean-context recovery dry-run.
- Hardened `tools/verify-loop1-ctrl-001.ps1` so legitimate task queue transitions do not invalidate the repository baseline.
- Hardened `spec/progress/current.md` with exact verification, changed-file/migration, risk/assumption, and uncommitted-change ownership evidence required for handoff.
- Changed no migrations, contracts, architecture decisions, business implementation, or CI workflows.
- Known non-blocking limitation: minimal private-repository branch protection is unavailable on the current GitHub plan; no required checks were configured.
- Last known good main commit: `53815faf92f80d425f1bd1e286d653c87f8a1087`.
- Latest checkpoint remains `spec/progress/checkpoints/2026-09-19-loop1-ctrl-001-local-review.md`; no new Gate, contract/schema transition, or release recovery point was created in this Task.
- Current branch changes are owned by `loop1-control-agent`; architecture conflicts or ACP/ADR required: none.
- Local branch-diff review found no remaining acceptance, scope, or forbidden-work issue after correcting review-state validation and handoff evidence; this is local evidence, not independent CI Gate PASS.

# Next Action

- Run independent review/CI acceptance; move LOOP1-CTRL-002 to `done/` only after PASS and accepted review, without claiming S0 Gate PASS.

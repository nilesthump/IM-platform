---
task_id: LOOP1-MIN-001
title: Establish evidence-driven minimality guard
status: review
owner: unassigned-fresh-independent-review-agent
stage: S0
gate: S0
---

# Goal

Establish a small, evidence-driven minimality rule for implementation and independent review without changing product authority or the unfinished `LOOP1-CONTRACT-001` task.

# Inputs

- Frozen Architecture resolved through `spec/architecture/README.md`, especially chapters 1.3, 2, 5, and 21.
- Approved ADR-0001 in `spec/architecture/decisions/`.
- `AGENTS.md`, `spec/tasks/TASK_TEMPLATE.md`, and `research/README.md`.
- Human Architect's LOOP1-MIN-001 control-plane insertion prompt registered as `P-d7268d90-c7bb-4440-9406-7a27b633f0bb`.

# Dependencies

- `LOOP1-RESEARCH-001` independently accepted; Recorder Instrumentation Epoch established.
- `LOOP1-CONTRACT-001` remains in review under its original ownership and is not a dependency for this control task.

# Allowed Paths

- `AGENTS.md`
- `spec/governance/minimality.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/tasks/{active,review,done}/LOOP1-MIN-001.md`
- `tools/verify-loop1-min-001.ps1`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-MIN-001/**`
- `spec/progress/checkpoints/*loop1-min-001*`
- `research/prompts/P-d7268d90-c7bb-4440-9406-7a27b633f0bb/**`
- `research/runs/R-20260923T012916Z-b5c2c3a1-df94-402c-9360-647e21e0ea2b/**`
- Additional fresh independent review Recorder prompt/run paths created by the reviewer for this task only.

# Acceptance

- Canonical minimality guidance is discoverable from `AGENTS.md` and the Task Template, and binds implementation and review to current requirements and evidence.
- Necessary complexity remains allowed; future-stage speculation alone is insufficient.
- A deterministic verifier checks governance links, review controls, authority boundary, scope, and representative negative cases.
- Frozen Architecture, public contracts, product code, and `LOOP1-CONTRACT-001` ownership/state/work remain unchanged.
- Recorder run validates, fresh independent review passes under ADR-0001, and accepted closure is safely merged and verified on local `main`.

# Forbidden

- Change Frozen Architecture, product contracts or implementation, or `LOOP1-CONTRACT-001` files/ownership/state.
- Introduce a second product architecture authority or a numeric complexity score.
- Merge before independent acceptance, or overwrite another Agent's work.

# Verification

- `& .\tools\verify-loop1-min-001.ps1`
- `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development` during implementation; Acceptance mode only from a clean independent checkout.
- `& .\tools\research\recorder.ps1 validate-run --run-id R-20260923T012916Z-b5c2c3a1-df94-402c-9360-647e21e0ea2b` after finish.

# Evidence

- Implementation Recorder: `R-20260923T012916Z-b5c2c3a1-df94-402c-9360-647e21e0ea2b`.
- Development evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-development.md`. Minimality verifier, CTRL-002 Development, and diff check passed locally; none is acceptance.
- Acceptance evidence pending independent review.

# Handoff

- Implementation complete in isolated worktree `H:\.codex\worktrees\loop1-min-001\IM-platform` from accepted control-plane commit `1c274bcbf92ebcc05c1bc208386c5976437d8221`; independent review pending.
- `LOOP1-CONTRACT-001` remains the separate unfinished current product task.
- A direct fast-forward to `main` would import unaccepted `LOOP1-CONTRACT-001` ancestors. Preserve this as a merge blocker until a safe, independently accepted reconciliation exists.

# Next Action

- Request a fresh independent review of the clean committed candidate, then resolve the main ancestry blocker without importing unfinished Contract content.

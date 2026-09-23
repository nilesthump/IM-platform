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
- `research/prompts/P-41263ca4-df41-4cc7-8089-58611e95c6ff/**`
- `research/prompts/P-abd528ee-c978-4af7-8020-03fcd4b45222/**`
- `research/runs/R-20260923T015212Z-f95e2e89-cf8c-4ac2-b3af-7a2137c0d83e/**`

The Coordinator prospectively authorized the three exact Fix-cycle Recorder paths above on 2026-09-23. The first prompt is an empty registration attempt caused by an incorrect PowerShell pipeline; it remains as factual Recorder evidence. The second prompt contains the exact Fix delegation and is associated with the Fix run.

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
- Acceptance evidence pending a new independent review. Fresh independent review of `03c32867205e098c84f0f289711ea1767913de68` returned FAIL: the fixed Recorder-ID scope allowlist rejects the task-authorized new review prompt/run artifacts required for closure. Evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-03c3286-fail.md`; review run `R-20260923T020500Z-b75d8ea3-9d8a-42bd-828e-351f355fd3a3` validated.
- Independent review of `4f954ea76ce694aa4f7256ef1d14bf7ed1389da8` returned FAIL because appended contradictory governance clauses were accepted by the verifier. Permanent evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-4f954ea-fail.md`; FAIL closure: `ca803b789b167f6e511a5229224250ee53ea937e`.
- Fresh Fix Agent `/root/min001_fix` repaired the verifier on isolated branch `fix/LOOP1-MIN-001-verifier`; prospective Recorder run `R-20260923T015212Z-f95e2e89-cf8c-4ac2-b3af-7a2137c0d83e`. The task verifier and CTRL-002 Development mode passed. In a disposable checkout, the independent review's exact contradictory clause was rejected (exit `1`), while a justified current transaction-boundary abstraction passed (exit `0`). A PowerShell-quoted diff check passed. Development evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-fix-verifier-development.md`. Independent acceptance remains pending.

# Handoff

- Original implementation in isolated worktree `H:\.codex\worktrees\loop1-min-001\IM-platform` was rejected by independent review. The Fix Agent owns only the new isolated Fix worktree; no product or Contract task path is modified.
- `LOOP1-CONTRACT-001` remains the separate unfinished current product task.
- A direct fast-forward to `main` would import unaccepted `LOOP1-CONTRACT-001` ancestors. Preserve this as a merge blocker until a safe, independently accepted reconciliation exists.

# Next Action

- Delegate a fresh Fix Agent to repair Recorder scope classification for authorized review artifacts, then a fresh independent Review Agent. Resolve the main ancestry blocker without importing unfinished Contract content.

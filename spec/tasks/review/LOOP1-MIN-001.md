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
- `research/prompts/P-3938e88c-ea8d-4dfa-94f4-edd7c4b17812/**`
- `research/runs/R-20260923T021826Z-679d5d5a-4016-4481-bf0f-6ea135fa78bd/**`
- `research/prompts/P-b064b456-d3d4-4b8e-8cee-ff007cacf3fc/**`
- `research/runs/R-20260924T012720Z-19b85628-de32-47a3-b539-96e1027ff19b/**`

The Coordinator prospectively authorized the three earlier Fix-cycle Recorder paths on 2026-09-23. The first prompt is an empty registration attempt caused by an incorrect PowerShell pipeline; it remains as factual Recorder evidence. The second prompt contains the exact earlier Fix delegation and is associated with that Fix run.

The Coordinator prospectively authorized the two exact fresh Fix-cycle Recorder paths immediately above on 2026-09-23 before their creation. This authorization covers one prompt and one run for `LOOP1-MIN-001` only; it does not authorize arbitrary research paths or other tasks' artifacts.

The Human's final-merge instruction authorizes the exact Coordinator prompt and prospective-resume Run paths above for this task's local-main integration. The run-local `blobs/.gitattributes` preserves Recorder output bytes across Git checkout and is valid only with exact content `* -text`; this does not authorize other research files. The integration verifier scopes the Minimality delta against accepted Contract closure `2a3812e0b4a23157ecd6fe341f0011ca96390229` rather than the shared Recorder base, so accepted Contract files are not misclassified as Minimality changes. These integration adjustments require fresh independent review.

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
- Fresh independent review of candidate `c18ec53e65e297f2e8b7eba4c3e2a9ba686a84b7` returned PASS in a clean committed checkout, including the task verifier, CTRL-002 Acceptance, Recorder validation, and disposable negative controls. Durable evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-c18ec53-pass.md`; Review run `R-20260923T023219Z-0bbe8cd8-6ae7-4aae-a0f5-f6c1c717423e`. This is content acceptance, not local-main post-merge acceptance.
- Fresh Fix Agent `/root/min001_fix` repaired the verifier on isolated branch `fix/LOOP1-MIN-001-verifier`; prospective Recorder run `R-20260923T015212Z-f95e2e89-cf8c-4ac2-b3af-7a2137c0d83e`. The task verifier and CTRL-002 Development mode passed. In a disposable checkout, the independent review's exact contradictory clause was rejected (exit `1`), while a justified current transaction-boundary abstraction passed (exit `0`). A PowerShell-quoted diff check passed. Development evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-fix-verifier-development.md`. Independent acceptance remains pending.
- Fresh Fix Agent `/root/min001_fix2` repairs the fixed-ID Recorder scope failure in isolated branch `fix/LOOP1-MIN-001-recorder-scope`; prospective Recorder prompt `P-3938e88c-ea8d-4dfa-94f4-edd7c4b17812`, run `R-20260923T021826Z-679d5d5a-4016-4481-bf0f-6ea135fa78bd`. The verifier now checks the Recorder artifact form and its metadata task/ID instead of maintaining an ID allowlist. A disposable checkout accepted the new review artifacts and rejected other-task artifacts, arbitrary research files, and extra files inside a valid task prompt. Development evidence is recorded separately; this remains unaccepted until fresh independent review.

# Handoff

- Original implementation and Fix cycles remain documented in their isolated worktrees and durable evidence. Fresh independent Review PASS applies to the corrected candidate, not to the later integration-specific verifier adjustment.
- `LOOP1-CONTRACT-001` is independently accepted and `done` at closure `2a3812e0b4a23157ecd6fe341f0011ca96390229`; the prior ancestry blocker is resolved. Its original untracked work remains owned by the original Agent.
- Coordinator is integrating both accepted lineages in isolated branch `integration/loop1-contract-min-20260923`. The integration-specific verifier and recovery-state changes require fresh independent review before local `main` advances.

# Next Action

- Commit and verify the isolated integration candidate, obtain a fresh independent review of its integration-specific changes, then safely fast-forward local `main`, perform post-merge verification, and close this task only if all acceptance conditions pass.

---
task_id: LOOP1-MIN-001
title: Establish evidence-driven minimality guard
status: done
owner: /root/min001_integration_review2
stage: S0
gate: S0
---

# Goal

Establish a small, evidence-driven minimality rule for implementation and independent review without changing product authority or `LOOP1-CONTRACT-001` work or ownership. That separate Contract task is now independently accepted and `done`.

# Inputs

- Frozen Architecture resolved through `spec/architecture/README.md`, especially chapters 1.3, 2, 5, and 21.
- Approved ADR-0001 in `spec/architecture/decisions/`.
- `AGENTS.md`, `spec/tasks/TASK_TEMPLATE.md`, and `research/README.md`.
- Human Architect's LOOP1-MIN-001 control-plane insertion prompt registered as `P-d7268d90-c7bb-4440-9406-7a27b633f0bb`.

# Dependencies

- `LOOP1-RESEARCH-001` independently accepted; Recorder Instrumentation Epoch established.
- `LOOP1-CONTRACT-001` was not a dependency for this control task. It is now independently accepted and `done` at `2a3812e0b4a23157ecd6fe341f0011ca96390229`; its accepted closure is the integration base.

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
- `research/prompts/P-9a16f48f-e439-4bbd-91d8-093a30397aac/**`
- `research/runs/R-20260924T015550Z-a800f61f-4e6a-4d26-9eb0-1802f7594bb2/**`
- `research/prompts/P-3fec0b47-2fc9-4ca0-87fc-0519b858eedc/**`
- `research/runs/R-20260924T063710Z-8018f93d-e54c-4772-a738-1027e0c783ac/**`

The Coordinator prospectively authorized the three earlier Fix-cycle Recorder paths on 2026-09-23. The first prompt is an empty registration attempt caused by an incorrect PowerShell pipeline; it remains as factual Recorder evidence. The second prompt contains the exact earlier Fix delegation and is associated with that Fix run.

The Coordinator prospectively authorized the two exact fresh Fix-cycle Recorder paths immediately above on 2026-09-23 before their creation. This authorization covers one prompt and one run for `LOOP1-MIN-001` only; it does not authorize arbitrary research paths or other tasks' artifacts.

The Human's earlier final-merge instruction requested inclusion of Minimality changes; it did not itself authorize Coordinator Recorder paths. After the independent integration FAIL, the Human answered `ok` to a separate explicit authorization question covering the exact Coordinator prompt and prospective-resume Run paths above, including that run's `blobs/.gitattributes`. This authorization is recorded in `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-recorder-path-authorization.md`. The Coordinator prospectively delegated one task-owned Fix prompt/run pair (the exact new IDs listed above) and a future independent reviewer task-owned prompt/run for this repair cycle. The Human did not specify those later-generated IDs. No arbitrary research paths or other tasks' artifacts are authorized.

The Coordinator run's committed `blobs/.gitattributes` has canonical content `* -text` to preserve Recorder output bytes across Git checkout; the verifier accepts that value after trimming surrounding whitespace and does not enforce byte-exact spelling. The integration verifier scopes the Minimality delta against accepted Contract closure `2a3812e0b4a23157ecd6fe341f0011ca96390229` rather than the shared Recorder base, so accepted Contract files are not misclassified as Minimality changes. These integration adjustments require fresh independent review.

After independent Review PASS closure `09cac596ca527fa80b187c63e5beb8308e946762`, the Coordinator prospectively authorizes one additional task-owned Recorder prompt/Run pair for the final local-`main` fast-forward and post-merge verification. Their generated IDs must be recorded here once created. This bounded authorization follows the Human's instruction to include Minimality in the final merge and the repository's Recorder mandate; it is not represented as Human-specified IDs or permission for arbitrary research artifacts. The existing merge prompt cannot be reused because Recorder binds a prompt to one Run. Any pre-Run authorization edit is a disclosed instrumentation limitation, not prospective trace.

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
- For final acceptance, run the Minimality verifier, CTRL-002 Acceptance, accepted Contract verifier, and Recorder repository validation from the clean local-`main` checkout; exact command IDs/results are in `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-post-main-merge.md`.

# Evidence

- Implementation Recorder: `R-20260923T012916Z-b5c2c3a1-df94-402c-9360-647e21e0ea2b`.
- Development evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-development.md`. Minimality verifier, CTRL-002 Development, and diff check passed locally; none is acceptance.
- An earlier fresh independent review of `03c32867205e098c84f0f289711ea1767913de68` returned FAIL: the fixed Recorder-ID scope allowlist rejected task-authorized new review prompt/run artifacts required for closure. Evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-03c3286-fail.md`; review run `R-20260923T020500Z-b75d8ea3-9d8a-42bd-828e-351f355fd3a3` validated. Later corrected integration acceptance is recorded below.
- Independent review of `4f954ea76ce694aa4f7256ef1d14bf7ed1389da8` returned FAIL because appended contradictory governance clauses were accepted by the verifier. Permanent evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-4f954ea-fail.md`; FAIL closure: `ca803b789b167f6e511a5229224250ee53ea937e`.
- Fresh independent review of candidate `c18ec53e65e297f2e8b7eba4c3e2a9ba686a84b7` returned PASS in a clean committed checkout, including the task verifier, CTRL-002 Acceptance, Recorder validation, and disposable negative controls. Durable evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-independent-review-c18ec53-pass.md`; Review run `R-20260923T023219Z-0bbe8cd8-6ae7-4aae-a0f5-f6c1c717423e`. This is content acceptance, not local-main post-merge acceptance.
- Fresh independent integration review of committed merge `b1a6e13dd044a80e42055c5e02278785df9c0a13` returned FAIL. The clean candidate passed the Minimality verifier, CTRL-002 Acceptance, and integrated Recorder validation, but Coordinator Recorder write-path authority is not established by the visible Human merge instruction and committed Task/progress recovery facts are stale. Evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-independent-integration-review-b1a6e13-fail.md`; Review run `R-20260924T013955Z-45b942f1-b123-45fd-9be0-51f910fe589e`.
- Following that FAIL, the Human explicitly authorized the existing Coordinator Recorder paths and a fresh Fix/Review cycle as documented in `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-recorder-path-authorization.md`. Fresh Fix prompt `P-9a16f48f-e439-4bbd-91d8-093a30397aac` and prospective run `R-20260924T015550Z-a800f61f-4e6a-4d26-9eb0-1802f7594bb2` document this repair. Development results remain separate from acceptance.
- This factual Fix passed Recorder-wrapped Minimality verifier, CTRL-002 Development mode, accepted Contract verifier, and tracked-source `git diff --check`; exact command IDs, exit codes, and durations are in `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-integration-fix-development.md`. The prospective Fix run finished `PASS` with 18 events and passed `validate-run` and repository validation after finish. These are development and instrumentation checks, not independent acceptance.
- Fresh independent Review Agent `/root/min001_integration_review2` accepted corrected committed candidate `fa0099cf2b6cc887d02328b6d433eb4f66147320` in a clean detached checkout under ADR-0001. PASS closure `09cac596ca527fa80b187c63e5beb8308e946762`, evidence `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-independent-integration-review-fa0099c-pass.md`, Review Run `R-20260924T021010Z-23d39be1-65fb-4e9c-9851-084b7972aa29` validated with 26 events.
- Local `main` safely fast-forwarded from `e5482b135a2ab7451c24c29c7517e1a8f19ce420` to that independent PASS closure. Clean post-merge Minimality, CTRL-002 Acceptance, Contract, and Recorder repository verifiers all returned exit `0`; ancestry checks confirmed both Contract and `task/LOOP1-MIN-001` content are included. Durable evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-24-post-main-merge.md`. Coordinator merge Run `R-20260924T063710Z-8018f93d-e54c-4772-a738-1027e0c783ac` finished `PASS` and validated with 27 events; it is not independent acceptance or Stage Gate PASS.
- Fresh Fix Agent `/root/min001_fix` repaired the verifier on isolated branch `fix/LOOP1-MIN-001-verifier`; prospective Recorder run `R-20260923T015212Z-f95e2e89-cf8c-4ac2-b3af-7a2137c0d83e`. The task verifier and CTRL-002 Development mode passed. In a disposable checkout, the independent review's exact contradictory clause was rejected (exit `1`), while a justified current transaction-boundary abstraction passed (exit `0`). A PowerShell-quoted diff check passed. Development evidence: `spec/progress/evidence/LOOP1-MIN-001/2026-09-23-fix-verifier-development.md`. Independent acceptance remains pending.
- Fresh Fix Agent `/root/min001_fix2` repaired the fixed-ID Recorder scope failure in isolated branch `fix/LOOP1-MIN-001-recorder-scope`; prospective Recorder prompt `P-3938e88c-ea8d-4dfa-94f4-edd7c4b17812`, run `R-20260923T021826Z-679d5d5a-4016-4481-bf0f-6ea135fa78bd`. The verifier now checks the Recorder artifact form and its metadata task/ID instead of maintaining an ID allowlist. A disposable checkout accepted the new review artifacts and rejected other-task artifacts, arbitrary research files, and extra files inside a valid task prompt. This Fix cycle was later superseded by the accepted Minimality content review.

# Handoff

- Original implementation and Fix cycles remain documented in their isolated worktrees and durable evidence. Fresh independent Review PASS applies to the corrected candidate, not to the later integration-specific verifier adjustment.
- `LOOP1-CONTRACT-001` is independently accepted and `done` at closure `2a3812e0b4a23157ecd6fe341f0011ca96390229`; the prior ancestry blocker is resolved. Its original untracked work remains owned by the original Agent.
- Rejected integration candidate `b1a6e13` and its FAIL evidence remain permanent history; corrected integration closure `09cac596` received fresh independent PASS and reached local `main` after safe fast-forward. The original Contract task worktree and its untracked files remain separate.

# Next Action

- Task accepted and merged locally. Coordinator may select the next dependency-satisfied S0 task in a new authorized task context; do not treat this Task PASS as S0 Gate PASS and do not start product work as part of this merge closure.

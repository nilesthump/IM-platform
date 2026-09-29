---
task_id: LOOP1-CI-001
title: Establish path-aware CI skeleton
status: review
owner: /root
stage: S0
gate: S0
---

# Goal

Create the path-aware diff classifier and Go, Java, client, shared-contract, deploy, and compatibility job skeletons.

# Inputs

- Architecture Baseline v1.0 chapters 11, 12, 14, 15, 19 and appendix A, resolved through `spec/architecture/README.md` and its canonical Markdown manifest. Apply approved ADRs.
- Existing S0 repository, contract, database, and infrastructure skeletons.

# Dependencies

- LOOP1-INFRA-001 done.

# Allowed Paths

- `ci/**`
- `.github/workflows/**` (only after this task becomes `active`)
- CI verification tests under `tests/**`
- Minimal CI entry files at repository root if explicitly added to this Task Spec before activation
- `spec/tasks/**/LOOP1-CI-001.md`
- `spec/progress/current.md`
- `spec/tasks/backlog/.gitkeep` (exact queue-presence marker only; Coordinator-authorized after clean-checkout Review 1 FAIL)

The Coordinator prospectively authorizes task-linked `spec/progress/evidence/LOOP1-CI-001/**`, accepted checkpoint `spec/progress/checkpoints/*loop1-ci-001*.md`, and this task's `research/prompts/**` and `research/runs/**` artifacts for instrumentation, review, and handoff only. These paths do not authorize product-scope expansion.

# Acceptance

- Diff classification maps Go, Java, each client, shared contracts/database/SDKs, and deploy/CI paths to the mandated jobs.
- Path matrix unit tests pass and shared changes fan out to the full compatibility matrix.

# Forbidden

- Let Agent self-reporting replace isolated CI Gate judgment.
- Add skips, lower acceptance, or re-record golden fixtures to make CI pass.
- Implement product behavior.

# Verification

- Run path classifier and job-matrix unit tests.
- Run `tools/verify-loop1-ctrl-002.ps1 -Mode Development` during development; Acceptance only from a clean committed independent checkout.

# Evidence

- Fresh independent Review 4 `/root/ci001_review4` **PASS** for exact clean detached diagnostic candidate `6f1293cfdf4efbb527f3c7e19d08a1f31f569a37`: CTRL-002 Acceptance with zero status entries, 12 CI tests, frozen hashes, no-weakening/scope/minimality inspection, and Fix 3 Recorder validity passed. The only product change prints Git porcelain status before unchanged Acceptance, to identify the dirty path in a new hosted run. Exact commands, exits, elapsed times, clean-state method, branch/diff range, and independence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-review4-6f1293c-pass.md`; review Recorder `R-20260929T035629Z-d3fafb03-67fd-42b1-95ee-bc842f9aa4d0`. Hosted root cause is unknown; task remains `review`, S0 Gate NOT YET PASSED.

- Fresh Fix 3 added a checkout-status diagnostic before unchanged CTRL-002 Acceptance in the `classify` job. The failed hosted run did not expose the offending porcelain entries, and a clean local PowerShell probe did not reproduce the suspected empty-output bug; the exact hosted cause is still unknown. Twelve path/gate tests and CTRL-002 Development passed. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-fix3-diagnostic-development.md`; Recorder `R-20260929T032745Z-2c2aaba9-5225-46c0-9bab-6a6e44e31d22`. This is a diagnostic candidate, not a repair PASS. Task stays `review`; independent review and a new hosted run are required.

- User approved and the reviewed `f07e353` branch was pushed to `origin/task/LOOP1-CI-001`. Actual GitHub Actions run `36515716353` **FAIL**: the classify job's CTRL-002 Acceptance check reported a dirty checkout; the gate rejected it. The offending status entries are not in the log yet. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-github-run-36515716353-fail.md`. Fresh Fix Agent diagnosis and a new independent review are required. Task stays `review`; S0 Gate NOT YET PASSED.

- Independent Review 3 PASS is recorded, but actual GitHub Actions execution is blocked: automatic approval review rejected pushing the reviewed branch to the repository remote. No push occurred. Exact reason, target, unchanged remote state, and requested approval: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-external-ci-dispatch-blocker.md`. Task remains `review`; S0 Gate NOT YET PASSED.

- Fresh independent Review 3 `/root/ci001_review3` **PASS** at clean detached candidate `57de113614a754afc69f39a7971d02197a984df2`: CTRL-002 Acceptance, all 12 CI tests, prior rename probe, new independent SDK-rename/path/gate controls, frozen hashes, and Recorder repository integrity passed. The clean checkout stayed clean. Exact commands, exits, elapsed times, scope/minimality judgment, and independence are in `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-review3-57de113-pass.md`; review Recorder `R-20260928T212920Z-2d064d71-4eae-4ae2-bdfc-58ccd5965034`. Task remains `review` pending actual GitHub workflow run and Coordinator closure; S0 Gate NOT YET PASSED.

- Fresh Fix 2 changes Git diff collection to `--no-renames`, exposing both the removed source and added destination of a rename. Regression tests cover moves from contract, database, and SDK trees to unclassified docs paths; all 12 path/gate tests and the former Review 2 negative probe pass. CTRL-002 Acceptance, 12 tests, and frozen hashes pass from a clean detached checkout of `4dc41b5`; exact commands and Recorder run are in `spec/progress/evidence/LOOP1-CI-001/2026-09-29-fix2-development.md`. This Fix-Agent run is not independent acceptance; the task remains `review` and S0 Gate is NOT YET PASSED.
- Fresh independent Review 2 `/root/ci001_review2` returned **FAIL** at clean detached candidate `f508750`: the backlog marker repairs CTRL-002 Acceptance, but a rename from `contracts/wire.json` to `docs/wire.json` is reported only by its destination, so the classifier schedules no compatibility jobs. Eleven CI tests, 24 gate status controls, frozen hashes, and Recorder integrity passed. Exact evidence/probe: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-review2-f508750-fail.md` and `review2-negative-probe.py`; review Recorder `R-20260928T205355Z-d9e2feba-fa5d-431a-ab08-dd4d405a67af`. Task remains `review`; actual GitHub workflow execution and S0 Gate remain pending.
- Fresh Fix Agent `/root/ci001_fix1` added only the prospectively authorized zero-byte `spec/tasks/backlog/.gitkeep` marker at `ba0bbe7`. A new detached clean checkout passed CTRL-002 Acceptance, 11 CI path/gate tests, frozen hashes, and Recorder repository validation. Exact commands, exits, elapsed times, clean-state method, and linked Recorder: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-fix1-development.md`. This remains development evidence; fresh independent re-review and an actual GitHub workflow run are pending. S0 Gate NOT YET PASSED.

- Coordinator prospectively authorized only `spec/tasks/backlog/.gitkeep` after independent Review 1 clean-checkout FAIL. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-queue-marker-authorization.md`; a fresh Fix Agent must add the marker before fresh re-review.

- Fresh independent Review 1 `/root/ci001_review1` returned **FAIL** at clean detached handoff `2c335cd` for product candidate `97db67e`. Eleven CI unit tests, frozen hashes, and implementation Recorder integrity passed, but clean-checkout CTRL-002 Acceptance exited 1 because `spec/tasks/backlog/` has no tracked marker after this task left the queue. The workflow's first job invokes this check, so the candidate cannot serve as an operational CI judge. Exact commands, exits, elapsed times, clean-state method, and independence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-review1-97db67e-fail.md`; review Recorder `R-20260928T202247Z-2951ca94-5b67-47a5-ba6d-c6f00f3f4a15`. Keep task in `review`; S0 Gate NOT YET PASSED.

- Coordinator review transition from clean candidate `97db67e` passed CTRL-002 Development recovery; the correctly linked Recorder run and an unused disclosed instrumentation FAIL are at `spec/progress/evidence/LOOP1-CI-001/2026-09-29-review-transition.md`. Independent acceptance remains pending.

- Fresh Implementation Agent `/root/ci001_impl` built the path-aware classifier, full shared fan-out, GitHub Actions job skeletons and a selected-job gate. Eleven classifier/gate unit tests pass, including a real Git deletion case; Go compile, both Compose configurations, HTTP/WSS/Sync/Plugin verifiers, and CTRL-002 Development pass. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-implementation-development.md`; Recorder run `R-20260928T194702Z-28ed6ab3-9f1c-4240-9d1f-6e217d7265d4`. This is local development evidence; the workflow has not yet run on GitHub and independent review/acceptance remains pending. No product behavior, contract, migration, or Frozen Architecture file changed.

- Activation prompt `P-7892975a-f2c8-4bfd-85d4-b11926c0b759`, Recorder run `R-20260928T193552Z-5891a0f5-0fe0-4415-8492-4b997360cc3c`; CTRL-002 Development and frozen-hash verification passed. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-activation-development.md`. This is not independent acceptance.

- Dependency `LOOP1-INFRA-001` is independently accepted and `done` on verified clean local `main` `10406be70bf66482836164400cd5b8be07709c58`; both profile smokes, frozen hashes, Recorder repository, and CTRL-002 Acceptance passed after integration. S0 Gate remains NOT YET PASSED.

# Handoff

- Implementation files are confined to `ci/**`, `.github/workflows/**`, and `tests/ci/**`. Client source is absent at S0; each client job rejects future source until its actual test command is added. The Go/Java jobs similarly reject unexpected future source. Shared changes select Go, Java, every client, old-client/plugin/migration compatibility, and shared contract checks. The selected-job gate rejects skipped, failed, or cancelled selected jobs. The development candidate will be committed clean for a fresh independent reviewer under ADR-0001.
- Last known good independently accepted main commit: `10406be70bf66482836164400cd5b8be07709c58`. Implementation Agent owns only task-allowed uncommitted candidate files until commit; no unrelated work was changed.

- Coordinator activated this task on isolated branch `task/LOOP1-CI-001` from clean local `main` `10406be70bf66482836164400cd5b8be07709c58`. Fresh Implementation Agent will take product CI work. No product CI file has changed.

# Next Action

- Coordinator obtains a new hosted run on the independently reviewed diagnostic candidate to reveal exact Git porcelain status. A fresh Fix/Review cycle then repairs the root cause before operational CI acceptance if the run still fails. S0 Gate remains pending.

---
task_id: LOOP1-CI-001
title: Establish path-aware CI skeleton
status: done
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
- `research/runs/R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb/blobs/.gitattributes` (exact portable Git transport metadata only; Coordinator-authorized after hosted run 36521060867 exposed CRLF blob checkout dirt)
- `research/runs/R-20260928T053447Z-5aa0c014-0381-4fba-9457-7acb7cf3da9a/blobs/.gitattributes` (same exact transport repair; historical Recorder blob bytes must remain unchanged)

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

- Final remote sync **PASS**: `git ls-remote origin main` returned `8dc64ad5293fb038c7ff26a92aaa3a29b8e0de67`, equal to clean local `main` before this record. Hosted main Actions [36554068269](https://github.com/nilesthump/IM-platform/actions/runs/36554068269) completed success at that exact SHA; classify and selected-job gate passed, while profile jobs were correctly skipped for the documentation-only diff. The preceding merged-main [full matrix 36550304940](https://github.com/nilesthump/IM-platform/actions/runs/36550304940) passed all ten jobs at `485a071bc80afb1b6f3c252779444e1be275c562`. S0 Gate **PASS** stands with all nine S0 tasks `done`, and S1 remains inactive. Durable evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-final-remote-main-sync.md`; latest historical checkpoint: `spec/progress/checkpoints/2026-09-29-loop1-ci-001-remote-main-s0-gate-pass.md`; linked Recorder `R-20260929T102259Z-2399002f-07b6-45c8-9fc3-45cdd3645ca5`. Last Known Good Commit: `8dc64ad5293fb038c7ff26a92aaa3a29b8e0de67`. Governance record changes are locally committed after verification; no product or authority paths changed. Next: separate S1 Stage selection only after its manifest and dependency-satisfied task are resolved and the Stage action is authorized.

- Post-PR remote-main S0 Gate **PASS**: PR #1 merged at 485a071bc80afb1b6f3c252779444e1be275c562; clean isolated local main fast-forwarded to that exact origin/main. Hosted main Actions [36550304940](https://github.com/nilesthump/IM-platform/actions/runs/36550304940) completed success for all ten jobs, including both profile smokes, compatibility, and selected-job gate. Local frozen hashes, recovery, S0 spec/HTTP/WSS/Sync/Plugin verifiers and 19 CI tests passed, with five real-symlink Windows subcases skipped but hosted Linux matrix successful. All nine S0 tasks remain done; no contract, authority, migration, backend or deploy path changed in the merge. Evidence: spec/progress/evidence/LOOP1-CI-001/2026-09-29-remote-main-s0-gate-reevaluation.md; checkpoint: spec/progress/checkpoints/2026-09-29-loop1-ci-001-remote-main-s0-gate-pass.md; Recorder R-20260929T094727Z-9394dc7c-0aee-45bb-88a3-ff602ef9d4f6. Last Known Good Commit: 485a071bc80afb1b6f3c252779444e1be275c562. Coordinator owns only these documentation/evidence and Recorder artifacts until committed. Next: push local checkpoint commit and verify remote CI; S1 inactive.


- Coordinator closure **PASS**: independent Review 2 accepted candidate `856e4d0ea90b4c87df8d5130b45bdbb3d4b7e7e4` in a clean detached clone. Review closure `0c00ea19cc9f2018c3540c2dabf5741d2a2705cb` was incorporated on this branch as `3235996`. Hosted GitHub Actions [run 36545406958](https://github.com/nilesthump/IM-platform/actions/runs/36545406958) completed `success` at exact `0c00ea1`; classify, Go, Java, Web, Desktop, Mobile, shared, compatibility, deploy, and gate all succeeded. Exact durable hosted evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-placeholder-hosted-acceptance.md`; closure Recorder `R-20260929T090505Z-ed62b6fb-ed72-4213-8219-c00aaa435c7b`. Local 19 CI tests and frozen hashes passed; five real-symlink Windows supplemental subcases were skipped, but deterministic controls passed and Linux hosted matrix passed. Task moves `review -> done`. S0 Gate stays FAIL pending clean main integration and post-merge Gate evaluation; S1 inactive.

- Fresh independent placeholder Review 2 `/root/ci_placeholder_review2` **PASS locally** for clean committed `856e4d0ea90b4c87df8d5130b45bdbb3d4b7e7e4`: separate detached clone passed strict CTRL-002 Acceptance and Recorder repository validation with zero status entries; 19 CI tests passed (five actual symlink cases skipped for Windows privilege, equivalent mock controls passed); actual `686dbf2..856e4d0` diff selects all 11 jobs; frozen hashes match, no gate weakening or out-of-scope product changes. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-placeholder-review2-856e4d0-pass.md`; Reviewer Recorder `R-20260929T082617Z-34ed37ce-5d8a-4b03-8f39-35d495bf7373`. Task remains `review`, S0 Gate FAIL until hosted full-matrix CI PASS and Coordinator reevaluation.

- Fresh Fix 2 incorporated independent FAIL closure `e250e62` as `00b8a4e` without conflict. `ci/check_s0_boundary.py` now rejects profile-root and nested symlinks before allowed-name checks; `ci/classify.py` selects every job for changes to `ci/**`, `.github/workflows/**`, or `tests/ci/**`. Focused regressions cover both bypasses. Nineteen CI tests pass, with five supplemental real-symlink subtests skipped because this Windows host lacks symlink creation privilege; a deterministic mock-backed negative test passes for both root and allowed-name cases. CTRL-002 Development and frozen hash verification pass. Exact development evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-placeholder-fix2-development.md`; Recorder `R-20260929T075614Z-e89fde53-720e-4829-9d9a-05691009c1ad`. Task stays `review`, S0 Gate FAIL pending fresh independent review and hosted full-matrix CI.

- Fresh independent placeholder Review `/root/ci_placeholder_review` **FAIL** for committed `502342358d11fc6e77ff2b7e1f86ed5f07220ea8`: a clean detached clone passes CTRL-002 Acceptance and all 16 CI tests pass, but the changed workflow/checker paths select deploy only, so a branch push skips all five repaired profile jobs and compatibility; root allowed-name symlinks bypass `ci/check_s0_boundary.py`. Frozen hashes match. Exact evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-placeholder-review-fail.md`; reviewer Recorder `R-20260929T072807Z-af85971f-4b19-44a4-a4b6-ebec51b430bf` exposed a GBK instrumentation failure. Task stays `review`, S0 Gate FAIL; fresh Fix/Review and hosted full-matrix PASS remain required.

- Post-push full-matrix hosted GitHub Actions [36532087481](https://github.com/nilesthump/IM-platform/actions/runs/36532087481) **FAIL** on `origin/main` `686dbf2`: the existing S0 boundary commands interpret tracked `.gitkeep` markers as new Go/Java source and the tracked client placeholder directories as implemented clients. The earlier research-only hosted PASS did not select these profile jobs. S0 Gate PASS at this commit is invalidated; this task reopens in `review`. The Fix Agent candidate changes only the CI boundary checks, plus regression tests, and is local development evidence pending fresh independent review and a new full-matrix hosted CI PASS. Exact local evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-s0-placeholder-fix-development.md`; Recorder run `R-20260929T065402Z-b5ded5ba-57c3-4972-b08e-2933abaee492`.

- S0 Stage Gate evaluation on integrated clean local `main` `037c88c` passed current recovery, frozen hashes, S0 spec/contract/CI verifiers, and both Go/Java PostgreSQL/NATS/TLS 1.3 smokes. The actual CI run and independent Review 5 remain the acceptance basis for this task. Gate evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-s0-gate-evaluation.md`; stable checkpoint: `spec/progress/checkpoints/2026-09-29-loop1-ci-001-s0-gate-pass.md`. Remote `main` was not pushed; S1 remains inactive.

- Operational CI acceptance **PASS**: user-approved reviewed evidence commit `9d1abc1` ran on GitHub Actions [36525934147](https://github.com/nilesthump/IM-platform/actions/runs/36525934147). Clean checkout, strict CTRL-002 Acceptance, 12 path/gate tests, classifier, and selected-job gate passed. This push selected no profile jobs because only research transport/review paths changed; independent matrix tests cover classification. Exact evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-operational-ci-acceptance.md`. Independent Review 5 accepted `0621f2b`; task moves `review -> done`. ADR-0001 bootstrap acceptance expires. S0 Stage Gate still requires clean main integration/evaluation.

- Fresh independent Review 5 `/root/ci001_review5` **PASS** for exact committed candidate `0621f2b76aedecfb4fcb7a657bd977cc79e8e8ac`. Two separate `--no-local` clones with `core.autocrlf=true` and `false`, neither with `info/attributes`, passed strict CTRL-002 Acceptance with zero status/diff entries. All 42 historical Recorder blob object IDs and raw checkout bytes matched, both historical runs and Fix 4's run validated, 12 CI tests and frozen hashes passed, and no contract/architecture/Acceptance/workflow/gate path changed. Exact independent evidence, commands, exits, elapsed times, clean state, branch/diff range, and an exposed non-acceptance Recorder invocation failure: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-independent-review5-0621f2b-pass.md`; review Recorder `R-20260929T045735Z-19594017-8996-43dd-98a8-670c028c15c4`. Actual hosted CI remains pending; task stays `review`, S0 Gate NOT YET PASSED.

- Fresh Fix 4 added exactly two Coordinator-authorized historical Recorder `blobs/.gitattributes` transport files at `21c10e3`. Two genuinely separate clones without machine-local `info/attributes`, with `core.autocrlf=true` and `false`, both pass strict CTRL-002 Acceptance with zero status entries. All 42 historical blob object IDs and raw checkout bytes match; both original Recorder runs validate. Twelve CI tests pass. This remains Fix Agent development evidence pending fresh independent review and hosted CI. Exact evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-fix4-portable-recorder-checkout-development.md`; Fix 4 Recorder `R-20260929T043656Z-cdc8ce0f-06f4-460c-989b-c2f3603ee365`. Task `review`, S0 Gate NOT YET PASSED.

- Coordinator prospectively authorized the two exact historical Recorder `blobs/.gitattributes` paths above after hosted diagnostic run `36521060867` identified 17 checkout-modified stdout blobs. The repair must preserve every historical blob Git object ID and Recorder validation result, and pass a fresh clone with no machine-local `info/attributes` overrides. No broader `research/**` write permission is granted.

- User-approved diagnostic branch push `0e6ce82` triggered actual GitHub Actions run `36521060867`, which **FAIL** with 17 modified historical Recorder stdout blobs immediately after checkout. Machine-local Git info attributes masked those bytes in local clean checkouts; repository `research/.gitattributes` applies LF checkout. The strict CTRL-002 Acceptance and gate rejected the dirty tree. Exact run/cause: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-github-run-36521060867-fail.md`. Fresh Fix/Review required; task `review`, S0 Gate NOT YET PASSED.

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

- Return control at S0 Gate PASS. Resolve the S1 batch manifest and a dependency-satisfied next task in a separately authorized Stage action; S1 remains inactive.

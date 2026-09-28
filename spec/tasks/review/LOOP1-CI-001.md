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

- Coordinator review transition from clean candidate `97db67e` passed CTRL-002 Development recovery; the correctly linked Recorder run and an unused disclosed instrumentation FAIL are at `spec/progress/evidence/LOOP1-CI-001/2026-09-29-review-transition.md`. Independent acceptance remains pending.

- Fresh Implementation Agent `/root/ci001_impl` built the path-aware classifier, full shared fan-out, GitHub Actions job skeletons and a selected-job gate. Eleven classifier/gate unit tests pass, including a real Git deletion case; Go compile, both Compose configurations, HTTP/WSS/Sync/Plugin verifiers, and CTRL-002 Development pass. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-implementation-development.md`; Recorder run `R-20260928T194702Z-28ed6ab3-9f1c-4240-9d1f-6e217d7265d4`. This is local development evidence; the workflow has not yet run on GitHub and independent review/acceptance remains pending. No product behavior, contract, migration, or Frozen Architecture file changed.

- Activation prompt `P-7892975a-f2c8-4bfd-85d4-b11926c0b759`, Recorder run `R-20260928T193552Z-5891a0f5-0fe0-4415-8492-4b997360cc3c`; CTRL-002 Development and frozen-hash verification passed. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-activation-development.md`. This is not independent acceptance.

- Dependency `LOOP1-INFRA-001` is independently accepted and `done` on verified clean local `main` `10406be70bf66482836164400cd5b8be07709c58`; both profile smokes, frozen hashes, Recorder repository, and CTRL-002 Acceptance passed after integration. S0 Gate remains NOT YET PASSED.

# Handoff

- Implementation files are confined to `ci/**`, `.github/workflows/**`, and `tests/ci/**`. Client source is absent at S0; each client job rejects future source until its actual test command is added. The Go/Java jobs similarly reject unexpected future source. Shared changes select Go, Java, every client, old-client/plugin/migration compatibility, and shared contract checks. The selected-job gate rejects skipped, failed, or cancelled selected jobs. The development candidate will be committed clean for a fresh independent reviewer under ADR-0001.
- Last known good independently accepted main commit: `10406be70bf66482836164400cd5b8be07709c58`. Implementation Agent owns only task-allowed uncommitted candidate files until commit; no unrelated work was changed.

- Coordinator activated this task on isolated branch `task/LOOP1-CI-001` from clean local `main` `10406be70bf66482836164400cd5b8be07709c58`. Fresh Implementation Agent will take product CI work. No product CI file has changed.

# Next Action

- Fresh independent Review Agent: review clean candidate `97db67ebead3e8d98ee966cc52d23a5e69377381` under ADR-0001; inspect scope, matrix, workflow/gate behavior, clean-checkout tests, frozen hashes and Recorder integrity. A real GitHub workflow run remains necessary for operational CI and Stage Gate.

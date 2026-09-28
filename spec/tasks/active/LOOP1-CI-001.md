---
task_id: LOOP1-CI-001
title: Establish path-aware CI skeleton
status: active
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

- Activation prompt `P-7892975a-f2c8-4bfd-85d4-b11926c0b759`, Recorder run `R-20260928T193552Z-5891a0f5-0fe0-4415-8492-4b997360cc3c`; CTRL-002 Development and frozen-hash verification passed. Evidence: `spec/progress/evidence/LOOP1-CI-001/2026-09-29-activation-development.md`. This is not independent acceptance.

- Dependency `LOOP1-INFRA-001` is independently accepted and `done` on verified clean local `main` `10406be70bf66482836164400cd5b8be07709c58`; both profile smokes, frozen hashes, Recorder repository, and CTRL-002 Acceptance passed after integration. S0 Gate remains NOT YET PASSED.

# Handoff

- Coordinator activated this task on isolated branch `task/LOOP1-CI-001` from clean local `main` `10406be70bf66482836164400cd5b8be07709c58`. Fresh Implementation Agent will take product CI work. No product CI file has changed.

# Next Action

- Fresh Implementation Agent: implement only the allowed path classifier, job skeletons, and meaningful path-matrix tests; record development verification, then hand off a clean candidate for fresh independent review.

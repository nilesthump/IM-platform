---
task_id: LOOP1-CI-001
title: Establish path-aware CI skeleton
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Create the path-aware diff classifier and Go, Java, client, shared-contract, deploy, and compatibility job skeletons.

# Inputs

- Architecture Baseline v1.0 chapters 11, 12, 14, 15, 19 and appendix A.
- Existing S0 repository, contract, database, and infrastructure skeletons.

# Dependencies

- LOOP1-INFRA-001 done.

# Allowed Paths

- `ci/**`
- CI verification tests under `tests/**`
- Minimal CI entry files at repository root if explicitly added to this Task Spec before activation
- `spec/tasks/**/LOOP1-CI-001.md`
- `spec/progress/current.md`

# Acceptance

- Diff classification maps Go, Java, each client, shared contracts/database/SDKs, and deploy/CI paths to the mandated jobs.
- Path matrix unit tests pass and shared changes fan out to the full compatibility matrix.

# Forbidden

- Let Agent self-reporting replace isolated CI Gate judgment.
- Add skips, lower acceptance, or re-record golden fixtures to make CI pass.
- Implement product behavior.

# Verification

- Run path classifier and job-matrix unit tests.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after LOOP1-INFRA-001 is independently accepted.

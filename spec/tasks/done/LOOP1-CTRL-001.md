---
task_id: LOOP1-CTRL-001
title: Establish Monorepo and AI Agent governance control plane
status: done
owner: loop1-first-implementation-agent
stage: S0
gate: S0
---

# Goal

Create the Loop 1 repository skeleton and the minimum authoritative Agent control plane without implementing product behavior.

# Inputs

- Architecture Baseline v1.0: `scalable-distributed-im-architecture.pdf`, especially chapters 2, 10, 12, 13, 15, 19, 20, 21 and appendices A-B.
- User-approved LOOP1-CTRL-001 execution and review-closure requests.

# Dependencies

- none

# Allowed Paths

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `spec/**`
- `contracts/**`
- `backend/**`
- `clients/**`
- `plugins/**`
- `tests/**`
- `deploy/**`
- `ci/**`
- `tools/verify-loop1-ctrl-001.ps1`
- `.git/**` only for repository initialization metadata

# Acceptance

- Required Monorepo and control-plane directories exist in the architecture-defined shape.
- `AGENTS.md` is the single repository-level Agent authority and contains the required startup, architecture-protection, scope, CI, handoff, and checkpoint rules.
- `CLAUDE.md` only routes to `AGENTS.md`; `README.md` points agents to `AGENTS.md` and does not duplicate Frozen Architecture.
- Handoff context, current execution state, the Task Spec template, and the first S0 task specifications exist.
- A minimum automated directory and policy verification passes locally.
- No duplicate architecture authority or S1 business implementation is introduced.

# Forbidden

- Change Frozen Architecture, public contracts, security boundaries, ACK semantics, compatibility rules, or architecture invariants.
- Implement chat UI, messaging, friendship, plugins, Go/Java business modules, or any S1 behavior.
- Introduce Redis, Kafka, Kubernetes, or other unapproved infrastructure.
- Claim that CTRL-001 completion is S0 Gate PASS.

# Verification

- `& .\tools\verify-loop1-ctrl-001.ps1`
- Final review-closure checklist covering all 15 requested acceptance groups.
- `git status --short --branch`
- Review all non-`.gitkeep` files under `backend/`, `clients/`, and `plugins/`; expected result is none.

# Evidence

- Final verification command run on 2026-09-19 with exit code 0.
- Verifier result: PASS - 6 required control files, 44 required directories, and 7 queued S0 tasks checked.
- Final review closure: PASS - all 15 acceptance groups and the no-workflow condition passed.
- Product implementation scan: PASS; no non-placeholder files exist under `backend/`, `clients/`, or `plugins/`.
- Architecture/contract scope scan: PASS; no frozen architecture document or machine-verifiable contract semantics were added or changed.
- Initial stable control-plane commit: `bc982a330ab52d7f79d4e7865bb4dd80f0b25eb7`.
- Evidence checkpoint: `spec/progress/checkpoints/2026-09-19-loop1-ctrl-001-local-review.md`.
- S0 Gate result: NOT YET PASSED; remaining S0 Contract, DB, Infra, and CI tasks are incomplete.

# Handoff

- Completed the repository skeleton, authoritative Agent entrypoint, compatibility route, project README, long-lived handoff context, current execution state, Task template, and first S0 Task Specs.
- Added one PowerShell verifier; added no migrations, contracts, infrastructure definitions, GitHub workflows, or product implementation.
- Review closure accepted under the user-authorized bootstrap procedure on 2026-09-19.
- The initial stable commit was created on `main`; GitHub repository bootstrap is the remaining closure action before activating LOOP1-CTRL-002.
- No prior user or other-Agent work was overwritten.
- Architecture conflicts or ACP/ADR required: none.

# Next Action

- Bootstrap the private GitHub repository, push `main`, then activate LOOP1-CTRL-002 without claiming S0 Gate PASS.

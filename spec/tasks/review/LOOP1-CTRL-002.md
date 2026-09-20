---
task_id: LOOP1-CTRL-002
title: Validate and harden Agent recovery context, current state, and Task schema
status: review
owner: loop1-control-agent
stage: S0
gate: S0
---

# Goal

Validate and harden the handoff context, current-state document, and Task Spec schema so a new Agent dry-run can recover work in the mandated order.

# Inputs

- Architecture Baseline v1.0 chapters 10, 12, 13, 19 and 21, resolved through `spec/architecture/README.md`.
- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- `spec/tasks/TASK_TEMPLATE.md`

# Dependencies

- LOOP1-CTRL-001 done with accepted bootstrap closure recorded in its Task/checkpoint.

# Allowed Paths

- `AGENTS.md`
- `scalable-distributed-im-architecture.pdf` (track the architect-supplied bytes unchanged)
- `spec/architecture/**`
- `spec/batches/**`
- `spec/handoff/agent-context.md`
- `spec/progress/**`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/tasks/**/*.md`
- `tools/**`
- `tests/**`

The architect's 2026-09-19 batch-orchestration instruction explicitly authorizes this CTRL-002 recovery to expand `allowed_paths` for the control-plane repair, architecture baseline registration, bootstrap acceptance ADR, batch manifest, durable evidence, verifier correction, and minimum missing S0 spec-producer Task Specs/dependency edges. This authorization does not permit changing the PDF bytes, Frozen business architecture, public contract semantics, or product behavior.

# Acceptance

- A clean-context Agent dry-run finds the current task, its authority inputs, allowed paths, verification, and next exact action in the required order.
- Handoff and current-state fields cover every chapter 13 requirement without copying the architecture baseline.
- Default acceptance verification rejects a dirty worktree; explicit development mode is labeled non-acceptance.
- The immutable repository architecture artifact resolves through the index/manifest and its SHA-256 verifies.
- Prior review failure and subsequent runs use durable evidence under `spec/progress/evidence/LOOP1-CTRL-002/`.

# Forbidden

- Duplicate repository rules in `CLAUDE.md` or create a parallel Agent authority.
- Change Frozen Architecture or public contracts.
- Implement product behavior.

# Verification

- Development only: `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`
- Baseline: `& .\tools\verify-loop1-ctrl-001.ps1`
- Independent acceptance from a clean committed checkout: `& .\tools\verify-loop1-ctrl-002.ps1`

# Plan

1. Derive machine-checkable recovery requirements from the mandated startup order and chapter 13 handoff fields.
2. Add a CTRL-002 verifier under `tools/` that performs a clean-context dry-run without scanning implementation as architecture.
3. Harden only the allowed control-plane documents if the dry-run exposes a real gap.
4. Run the CTRL-001 baseline plus CTRL-002 recovery verification, review the diff, and prepare handoff without claiming S0 Gate PASS.

# Evidence

- Dependency evidence: LOOP1-CTRL-001 is in `done/`.
- Permanent prior independent FAIL: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-19-independent-review-fail.md`.
- Permanent independent review FAIL for `841b669`: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-19-independent-review-841b669-fail.md`.
- Fix-Agent development verification: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-19-fix-development-verification.md` (not acceptance evidence).
- Post-`841b669` Fix-Agent development verification and reduced-current negative control: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-20-fix2-development-verification.md` (not acceptance evidence).
- Permanent independent review FAIL for `b65a9a8`: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-20-independent-review-b65a9a8-fail.md`.
- Post-`b65a9a8` Fix-Agent development verification, including the clean committed S1-before-S0 negative control: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-20-fix3-development-verification.md` (not acceptance evidence).
- Fresh independent acceptance evidence: pending.

# Handoff

- Review repair covers generic cross-queue recovery, real input/index/hash/git verification, clean acceptance mode, chapter 13 fields, durable evidence, repository-resident architecture resolution, bootstrap CI ADR, the S0 batch, the missing spec-producer dependency, and generic rejection of active S1 tasks before S0 Gate PASS.
- The complete fixed-point change inventory from `67bb82b1cd3880090095425384d52c933f0518fb` is: governance/context (`AGENTS.md`, `spec/handoff/agent-context.md`); immutable architecture (`scalable-distributed-im-architecture.pdf`, `spec/architecture/README.md`, `spec/architecture/baseline.md`, `spec/architecture/decisions/ADR-0001-temporary-s0-bootstrap-acceptance-before-ci-availability.md`); batch (`spec/batches/LOOP1-S0.md`); recovery/checkpoints/evidence (`spec/progress/current.md`, both CTRL-002 checkpoint files, `spec/progress/evidence/README.md`, and all six CTRL-002 evidence records); Task Specs (`spec/tasks/backlog/LOOP1-SPEC-001.md`, the three Contract Task Specs, `spec/tasks/backlog/LOOP1-CI-001.md`, and this CTRL-002 Task Spec); and both control verifiers (`tools/verify-loop1-ctrl-001.ps1`, `tools/verify-loop1-ctrl-002.ps1`). `spec/tasks/TASK_TEMPLATE.md` was verified as the governing schema and is unchanged in this fixed-point diff.
- Database migrations: none. Machine-verifiable public contract files: none. Product implementation: none. `.github/workflows/`: absent. Frozen Architecture PDF bytes: unchanged, SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Development verification passed CTRL-001 and CTRL-002 Development mode; disposable reduced-current and clean committed S1-before-S0 controls were rejected as required. Exact commands, exit codes, and elapsed times are in the 2026-09-20 fix3 development evidence. This is not acceptance evidence.
- Known non-blocking limitation: desired private-repository branch protection is unavailable on the current GitHub plan.
- Last known good accepted commit: `53815faf92f80d425f1bd1e286d653c87f8a1087`.
- Latest checkpoint metadata will be finalized in a second commit after the exact first repair commit is known; until then, recovery still points to `spec/progress/checkpoints/2026-09-19-loop1-ctrl-002-repair-candidate.md`.
- No uncommitted changes are expected after this Fix Agent commits the repair; any later dirty state must be identified before work continues. Architecture conflict requiring human action: none.

# Next Action

- Delegate a new fresh independent reviewer to inspect the fix commit and run CTRL-001 plus CTRL-002 in default acceptance mode from a clean isolated checkout. Move LOOP1-CTRL-002 to `done/` only after PASS; do not claim S0 Gate PASS.

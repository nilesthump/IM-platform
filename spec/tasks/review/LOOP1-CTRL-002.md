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
- `.gitattributes`
- `spec/handoff/agent-context.md`
- `spec/progress/current.md`
- `spec/tasks/TASK_TEMPLATE.md`

# Dependencies

- LOOP1-CTRL-001 done with independent CI acceptance.

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
- Fix-Agent development verification: `spec/progress/evidence/LOOP1-CTRL-002/2026-09-19-fix-development-verification.md` (not acceptance evidence).
- Fresh independent acceptance evidence: pending.

# Handoff

- Review repair covers every inherited finding: generic cross-queue recovery, real input/index/hash/git verification, clean acceptance mode, durable evidence, concise current state, repository-resident architecture resolution, bootstrap CI ADR, S0 batch manifest, and the missing spec-producer dependency.
- `tools/verify-loop1-ctrl-001.ps1` now accepts the legal PDF/index/manifest/ADR and additional Task Spec without treating them as duplicate authority; `.gitattributes` keeps the immutable PDF binary in Git tooling.
- Frozen Architecture bytes are unchanged from the architect-supplied asset; no public contract, domain semantics, migration, product implementation, or `.github/workflows/` was created.
- Known non-blocking limitation: desired private-repository branch protection is unavailable on the current GitHub plan.
- Last known good accepted commit: `53815faf92f80d425f1bd1e286d653c87f8a1087`.
- Latest checkpoint: `spec/progress/checkpoints/2026-09-19-loop1-ctrl-002-repair-candidate.md`.
- All repair changes are owned by the fresh LOOP1-CTRL-002 Fix Agent. Architecture conflict requiring human action: none.

# Next Action

- Commit this repair, then run a fresh independent acceptance review from a clean isolated checkout. Move LOOP1-CTRL-002 to `done/` only after PASS; do not claim S0 Gate PASS.

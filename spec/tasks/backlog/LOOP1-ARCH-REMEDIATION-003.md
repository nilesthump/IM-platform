---
task_id: LOOP1-ARCH-REMEDIATION-003
title: Enforce architecture in CI and independent review
status: backlog
owner: unassigned
stage: S1 remediation 3/4
gate: LOOP1-ARCH-REMEDIATION
---

# Goal

Enforce architecture in CI and independent review within the explicitly authorized four-stage remediation.

# Inputs

- User four-stage instruction; approval-and-recovery evidence for stage 1.
- spec/architecture/README.md -> baseline.md -> current Frozen Architecture, all approved ADRs; applicable §3/§10/§11/§12-14 and Minimality Contract.
- spec/domain/, spec/invariants/, spec/acceptance/ and contracts/ for every affected responsibility. Contracts remain unchanged.
- spec/batches/LOOP1-ARCH-REMEDIATION.md; original Auth done task and accepted checkpoint.

# Dependencies

- LOOP1-ARCH-REMEDIATION-002 independently accepted bounded deliverable; no blocking architecture decision.

# Allowed Paths

- `ci/**`
- `.github/workflows/**`
- `tests/ci/**`
- `tests/architecture/**`
- `tools/** only architecture/constraint verification`
- `spec/acceptance/** only checker and review rules`
- `spec/tasks/**/LOOP1-ARCH-REMEDIATION-*.md`
- `spec/batches/LOOP1-ARCH-REMEDIATION.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-003/**`
- `spec/progress/checkpoints/*architecture-remediation*.md`
- `research/prompts/** and research/runs/** only this task-linked artifacts`

User authority explicitly permits these task-control and bounded stage paths. Stage 4 backend/go/** is a one-time migration authorization, not an architecture exemption; it exits on batch completion. Normal later tasks must narrow paths. No unknown original-worktree files may be read or changed.

# Acceptance

Positive controls and negatives catch root business source, forbidden service imports, shared-to-service imports, invalid active Task paths, missed governance triggers, and original Go layout. Go import graph and stage-appropriate Java fixtures are exercised. Exact root whitelist, backend-specific placeholder exits, rename/delete handling, required job missing/skip/failure/cancellation fail Gate. Report expected old-Go failures without grandfathering. Independent reviewer validates checker effectiveness before stage 4.

# Forbidden

- No changes to public HTTP/WSS/database/ACK/Sync/compatibility/security semantics or history; unresolved substantive decisions block their dependent portion.
- No future business, RPC, multi-module mandate, infrastructure, or broad abstraction expansion.
- No Go/Java product implementation edits.
- No self-acceptance, old-head CI substitution, main push, force push, remote deletion or automatic merge.

# Minimality

Use existing mechanisms and smallest presently necessary changes. Boundaries are existing responsibilities; no additional layers without a present justification.

# Verification

- Minimum entry point: `tools/verify-frozen-architecture.ps1`; execute with `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`; existing task/recovery checker in Development during edits and Acceptance from clean candidate.
- Execute acceptance-specific positive/negative checks; record exact commands, exit code, duration, environment, skips, SHA and reviewer independence.
- Fresh independent review plus applicable hosted CI; stage 3 transition evidence distinguishes checker PASS and expected product violations.

# Evidence

- spec/progress/evidence/LOOP1-ARCH-REMEDIATION-003/ (pending independent acceptance).

# Handoff

- Base inherited 8cd90a7; last independently accepted Auth head 59d92f39234596a5b66841e8aa2ef7db0bf65e8a. Old Auth PASS retained, does not cover new rules.
- Sole writer is current fresh Implementation/Fix Agent; original and Social worktrees remain untouched.

# Next Action

- Wait for predecessor bounded independent acceptance, then activate in a fresh Implementation Agent context.

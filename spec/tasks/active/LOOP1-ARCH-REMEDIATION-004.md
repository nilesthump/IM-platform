---
task_id: LOOP1-ARCH-REMEDIATION-004
title: Migrate Go responsibility packages and regress
status: active
owner: /root/stage4_impl sole writer
stage: S1 remediation 4/4
gate: LOOP1-ARCH-REMEDIATION
---

# Goal

Migrate Go responsibility packages and regress within the explicitly authorized four-stage remediation.

# Inputs

- User four-stage instruction; approval-and-recovery evidence for stage 1.
- spec/architecture/README.md -> baseline.md -> current Frozen Architecture, all approved ADRs; applicable §3/§10/§11/§12-14 and Minimality Contract.
- spec/domain/, spec/invariants/, spec/acceptance/ and contracts/ for every affected responsibility. Contracts remain unchanged.
- spec/batches/LOOP1-ARCH-REMEDIATION.md; original Auth done task and accepted checkpoint.

# Execution Constraints

Apply spec/governance/execution-boundaries.md and spec/governance/independent-review.md, canonical §3/§10 SRC-01 through SRC-07/§11. allowed_paths does not waive responsibility/import rules. Boundaries are authority; neither Go implementation nor future Java layout can redefine them.

# Dependencies

- LOOP1-ARCH-REMEDIATION-003 independently accepted bounded deliverable; no blocking architecture decision.

# Allowed Paths

- `backend/go/**`
- `tests/go/**`
- `tests/ci/** only migration regression`
- `deploy/** only existing role/build/config adaptation`
- `ci/** and .github/workflows/** only recursive Go verification and regression activation`
- `spec/tasks/**/LOOP1-ARCH-REMEDIATION-*.md`
- `spec/batches/LOOP1-ARCH-REMEDIATION.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/**`
- `spec/progress/checkpoints/*architecture-remediation*.md`
- `research/prompts/** and research/runs/** only this task-linked artifacts`

User authority explicitly permits these task-control and bounded stage paths. Stage 4 backend/go/** is a one-time migration authorization, not an architecture exemption; it exits on batch completion. Normal later tasks must narrow paths. No unknown original-worktree files may be read or changed.

# Acceptance

Publish actual before/after file/responsibility migration map, preserve Core Auth writes and narrow Gateway validation, minimize shared support and exported interfaces. Recursive formatting/build/vet/unit/race, live migrated PostgreSQL/NATS integration and canonical fixtures, register/login/three slots/replacement/epoch/refresh/logout/bind/revocation/close/rollback/security, each role startup/routes/events, Compose/TLS smoke, all structural checks. Explicit test enable conditions; skipped integration is unexecuted. Fresh final independent review and hosted CI exact head/jobs; close batch only after all criteria.

# Forbidden

- No changes to public HTTP/WSS/database/ACK/Sync/compatibility/security semantics or history; unresolved substantive decisions block their dependent portion.
- No future business, RPC, multi-module mandate, infrastructure, or broad abstraction expansion.
- No copied/modified canonical fixture expectations, mass export of internals, deleted tests, or moving full Auth into shared.
- No self-acceptance, old-head CI substitution, main push, force push, remote deletion or automatic merge.

# Minimality

Use existing mechanisms and smallest presently necessary changes. Boundaries are existing responsibilities; no additional layers without a present justification.

# Verification

Before migration, bind exact commands/results from independently accepted stage003 evidence; publish the actual file/responsibility migration table before edits. Pending checker tools cannot be counted as executable PASS. The broad migration scope is a one-time authorization ending at batch completion; preserve behavioral fixtures and minimize exported APIs.


- Minimum entry point: `tools/verify-frozen-architecture.ps1`; execute with `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`; existing task/recovery checker in Development during edits and Acceptance from clean candidate.
- Execute acceptance-specific positive/negative checks; record exact commands, exit code, duration, environment, skips, SHA and reviewer independence.
- Fresh independent review plus applicable hosted CI; stage 3 transition evidence distinguishes checker PASS and expected product violations.

# Evidence

- spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/ (pending independent acceptance).

# Handoff

- Base inherited 8cd90a7; last independently accepted Auth head 59d92f39234596a5b66841e8aa2ef7db0bf65e8a. Old Auth PASS retained, does not cover new rules.
- Sole writer is current fresh Implementation/Fix Agent; original and Social worktrees remain untouched.

# Next Action

- Wait for predecessor bounded independent acceptance, then activate in a fresh Implementation Agent context.

# Activation

003 bounded accepted exact2afeac8/run36726926394 after new independentReview. Backlog->ready->active; only004 migration authorized, overallGate remainsred. Accepted executable checks: bundledPython ci/check_architecture.py --scope all --json; bundledPython -m unittest discover -s tests/architecture -v; bundledPython -m unittest discover -s tests/ci -v; pwsh tools/verify-frozen-architecture.ps1. Publish actual migration table before product edits.

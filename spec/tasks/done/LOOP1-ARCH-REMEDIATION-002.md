---
task_id: LOOP1-ARCH-REMEDIATION-002
title: Synchronize execution constraints
status: done
owner: Coordinator bounded acceptance complete
stage: S1 remediation 2/4
gate: LOOP1-ARCH-REMEDIATION
---

# Goal

Synchronize execution constraints within the explicitly authorized four-stage remediation.

# Inputs

- User four-stage instruction; approval-and-recovery evidence for stage 1.
- spec/architecture/README.md -> baseline.md -> current Frozen Architecture, all approved ADRs; applicable 搂3/搂10/搂11/搂12-14 and Minimality Contract.
- spec/domain/, spec/invariants/, spec/acceptance/ and contracts/ for every affected responsibility. Contracts remain unchanged.
- spec/batches/LOOP1-ARCH-REMEDIATION.md; original Auth done task and accepted checkpoint.

# Dependencies

- LOOP1-ARCH-REMEDIATION-001 independently accepted bounded deliverable; no blocking architecture decision.

# Allowed Paths

- `AGENTS.md`
- `CLAUDE.md only if present`
- `spec/handoff/agent-context.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/tasks/backlog/**`
- `spec/tasks/ready/**`
- `spec/batches/**`
- `spec/acceptance/** only execution constraints`
- `spec/governance/**`
- `spec/architecture/baseline.md` only acceptance discovery metadata
- `spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md` only current Status and appended actual acceptance
- `README.md and tools/** documentation only`
- `spec/tasks/**/LOOP1-ARCH-REMEDIATION-*.md`
- `spec/batches/LOOP1-ARCH-REMEDIATION.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-002/**`
- `spec/progress/checkpoints/*architecture-remediation*.md`
- `research/prompts/** and research/runs/** only this task-linked artifacts`

User authority explicitly permits these task-control and bounded stage paths. Stage 4 backend/go/** is a one-time migration authorization, not an architecture exemption; it exits on batch completion. Normal later tasks must narrow paths. No unknown original-worktree files may be read or changed.

# Acceptance

New Agent can recover the unique current remediation task, responsibilities, allowed scope and acceptance. Active templates/tasks reference service ownership; allowed_paths never exempts authority; Java task source inherits boundaries. Reviewer checks behavior, ownership, imports and minimality. Preserve done tasks and historical evidence.

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

- spec/progress/evidence/LOOP1-ARCH-REMEDIATION-002/implementation-evidence.md and recovery-controls.py: completed D01 propagation, exact local command results/limits and remaining stage003 enforcement. Fresh independent Review/hosted acceptance pending.
- Recorder R-20260930T124045Z-bb6d4855-0e9d-45ba-8b8c-62830da56365 is implementation evidence only.

# Handoff

- Completed canonical execution read/scope, actual behavior+ownership/import/minimality Review, expiry/head/jobs, Java future task creation, narrowed suspended business tasks, recovery and baseline acceptance discovery synchronization. No product/contracts/canonical body/history edits.
- Local integrity four tests, recovery Development, isolated three recovery negatives/scope and minimality policy PASS. Historical minimality task scope invocation failed as in evidence; source/import/live regressions and hosted acceptance not executed in this stage.
- Last bounded accepted head: 3e6e89fa2b378f1fcb4c944466fef2e3bc905379 (001 only). Latest accepted checkpoint unchanged. /root/stage2_impl owns current new changes until commit, then releases write ownership.

- Base inherited 8cd90a7; last independently accepted Auth head 59d92f39234596a5b66841e8aa2ef7db0bf65e8a. Old Auth PASS retained, does not cover new rules.
- Sole writer is current fresh Implementation/Fix Agent; original and Social worktrees remain untouched.

# Next Action

- Coordinator delegates a new independent Review Agent for this committed candidate; after accepted local Review obtain applicable exact-head hosted CI. Do not activate stage003 or resume business before bounded stage002 acceptance.

# Coordinator Scope Clarification

Coordinator /root authorized stage-two discovery metadata synchronization on 2026-09-30 under the Human scope: baseline.md status/acceptance discovery only; ADR-0003 current Status and appended actual acceptance only. No canonical body/hash/version/decision change or historical ADR/evidence change.

# Activation

Predecessor 001 bounded independent Review and exact-head hosted matrix accepted at 3e6e89f/run36714913796. No known blocking architecture decision. Inputs inspected and v1.1 integrity independently verified. Coordinator transitions backlog->ready->active in dependency order; fresh Implementation Agent must implement stage two only. New run-local Recorder .gitattributes blobs/** -text is authorized within task-linked research/runs/** before capture, preserving evidence transport. No business implementation authorized.

# Independent Review handoff

Fresh /root/stage2_review independently accepted exact candidate 3b04904666530687705dfcb189b34337f3e3ae41 against base5ca5089 from clean managed checkout. Evidence: spec/progress/evidence/LOOP1-ARCH-REMEDIATION-002/independent-review.md; Recorder R-20260930T125435Z-95638b32-0cfc-4de8-ade7-34ef5f27c798. Frozen four tests, recovery Acceptance, three memory negative controls/scope and implementation Recorder32events/28rawblobs PASS. No implementation edited. First reviewer command omitted explicit repo and failed on dirty original; retained and corrected clean rerun PASS. No product/live/hosted acceptance claimed. Task remains review; Coordinator must obtain exact review-closure-head applicable hosted CI before done/checkpoint/003 activation. Last known good remains3e6e89f. Reviewer owns only linked new evidence/recovery until closure commit, then releases write ownership.

# Bounded acceptance closure

Fresh independent Review PASS plus exact review-closure headc0373ab hostedrun36719353192 accepted under old applicable classifier scope. Evidence hosted-acceptance.md and raw JSON; profile skips disclosed, stage003/004 and overall Gate pending. Next exact action activate003, no business continuation.

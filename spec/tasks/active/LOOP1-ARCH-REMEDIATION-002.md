---
task_id: LOOP1-ARCH-REMEDIATION-002
title: Synchronize execution constraints
status: active
owner: fresh Implementation Agent pending delegation
stage: S1 remediation 2/4
gate: LOOP1-ARCH-REMEDIATION
---

# Goal

Synchronize execution constraints within the explicitly authorized four-stage remediation.

# Inputs

- User four-stage instruction; approval-and-recovery evidence for stage 1.
- spec/architecture/README.md -> baseline.md -> current Frozen Architecture, all approved ADRs; applicable §3/§10/§11/§12-14 and Minimality Contract.
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

- spec/progress/evidence/LOOP1-ARCH-REMEDIATION-002/ (pending independent acceptance).

# Handoff

- Base inherited 8cd90a7; last independently accepted Auth head 59d92f39234596a5b66841e8aa2ef7db0bf65e8a. Old Auth PASS retained, does not cover new rules.
- Sole writer is current fresh Implementation/Fix Agent; original and Social worktrees remain untouched.

# Next Action

- Wait for predecessor bounded independent acceptance, then activate in a fresh Implementation Agent context.

# Activation

Predecessor 001 bounded independent Review and exact-head hosted matrix accepted at 3e6e89f/run36714913796. No known blocking architecture decision. Inputs inspected and v1.1 integrity independently verified. Coordinator transitions backlog->ready->active in dependency order; fresh Implementation Agent must implement stage two only. New run-local Recorder .gitattributes blobs/** -text is authorized within task-linked research/runs/** before capture, preserving evidence transport. No business implementation authorized.

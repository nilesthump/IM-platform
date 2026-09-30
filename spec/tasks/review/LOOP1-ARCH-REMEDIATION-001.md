---
task_id: LOOP1-ARCH-REMEDIATION-001
title: Audit and repair the whole Frozen Architecture
status: review
owner: Coordinator awaiting fresh independent Review Agent
stage: S1 remediation 1/4
gate: LOOP1-ARCH-REMEDIATION
---

# Goal

Audit and repair the whole Frozen Architecture within the explicitly authorized four-stage remediation.

# Inputs

- User four-stage instruction; approval-and-recovery evidence for stage 1.
- spec/architecture/README.md -> baseline.md -> current Frozen Architecture, all approved ADRs; applicable §3/§10/§11/§12-14 and Minimality Contract.
- spec/domain/, spec/invariants/, spec/acceptance/ and contracts/ for every affected responsibility. Contracts remain unchanged.
- spec/batches/LOOP1-ARCH-REMEDIATION.md; original Auth done task and accepted checkpoint.

# Dependencies

- LOOP1-GO-AUTH-001 done; explicit Human authority and isolated clean inherited checkout.

# Allowed Paths

- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/README.md`
- `spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md`
- `tools/verify-frozen-architecture.ps1`
- `tools/verify_frozen_architecture.py`
- `tests/architecture/**`
- `spec/tasks/**/LOOP1-ARCH-REMEDIATION-*.md`
- `spec/batches/LOOP1-ARCH-REMEDIATION.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/**`
- `spec/progress/checkpoints/*architecture-remediation*.md`
- `research/prompts/** and research/runs/** only this task-linked artifacts`
- Exact run-local `research/runs/{R-20260929T183826Z-8cd6416f-9684-4596-bc81-bc6f8ee8ce56,R-20260929T185051Z-4ba6947e-5726-4f55-ba96-a1b9bed48769,R-20260930T120604Z-82f5344c-b7a0-4876-a454-f4b2bf344fa8}/.gitattributes`: `blobs/** -text` only, preserving raw evidence bytes; Human-authorized necessary execution constraint, Coordinator approved transport repair. No historical run policy change.

User authority explicitly permits these task-control and bounded stage paths. Stage 4 backend/go/** is a one-time migration authorization, not an architecture exemption; it exits on batch completion. Normal later tasks must narrow paths. No unknown original-worktree files may be read or changed.

# Acceptance

Audit all 22 chapters, both appendices, tables, examples, nine diagrams and references against existing authority; classify real conflicts versus implementation deviations. Repair every determinate conflict in current prose, record coverage/ledger and approval source. Preserve historical PDF/ADR/evidence bytes; distinguish old representation-only migration from current normative tightening. Verify actual hashes and semantic structure with negative controls. Fresh independent review and applicable hosted CI; no product edits.

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

- spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/ (pending independent acceptance).

# Handoff

- Base inherited 8cd90a7; last independently accepted Auth head 59d92f39234596a5b66841e8aa2ef7db0bf65e8a. Old Auth PASS retained, does not cover new rules.
- Sole writer is current fresh Implementation/Fix Agent; original and Social worktrees remain untouched.

# Next Action

- Run a new independent Review Agent against the committed candidate, then applicable real hosted CI. Stage two remains blocked until bounded stage-one acceptance.

# Candidate handoff

- Full 22-chapter/two-appendix coverage and 25 repaired determinate findings: `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/conflict-ledger.md`; two explicitly pending downstream items. No known blocking equal-authority decision in audit scope; independent review pending.
- v1.1 actual canonical SHA: `83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e`; original PDF hash unchanged. ADR-0003 records explicit Human authorization and semantic tightening, separately from historical ADR-0002.
- `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/development.md` records exact verifier results/failures/skips; linked Recorder contains argv/exit/time/output hashes. New integrity, old HTTP/WSS/Sync-Plugin, recovery Development, and 21 CI regressions pass locally; four CI symlink subcases skipped due Windows privilege.
- No Go/Java product, public contract, historical evidence/ADR or PDF edited. New candidate checkpoint records transition only, not acceptance. Last known good remains historical Auth head `59d92f39234596a5b66841e8aa2ef7db0bf65e8a`; inherited base `8cd90a7`.
- Implementation Agent owns only stage-one candidate artifacts until clean commit, then releases write ownership. No independent acceptance or hosted remediation CI yet.

# Transport fix handoff

- Usage-interrupted implementation transport run preserved as partial; new fresh Fix context uses related R-20260930T120604Z-82f5344c-b7a0-4876-a454-f4b2bf344fa8.
- 22 original blobs restored through exact run-local -text policy and ordinary corrective commit; all 38 persisted original bytes verified against working/index/committed SHA. One pre-existing raw subprocess vs UTF-8 persisted stderr hash mismatch is disclosed, not repaired by editing history.
- Exact failures, reruns and preservation method: spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/transport-repair.md and verify-transport.py. Authority integrity rerun exit 0, four tests PASS. No product modification or self-acceptance. Independent Review/hosted CI remain pending; last known good historical Auth head unchanged.

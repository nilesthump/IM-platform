---
task_id: LOOP1-ARCH-REMEDIATION-003
title: Enforce architecture in CI and independent review
status: done
owner: Coordinator; fresh independent Review and exact hosted bounded acceptance
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

# Execution Constraints

Apply spec/governance/execution-boundaries.md and spec/governance/independent-review.md, canonical §3/§10 SRC-01 through SRC-07/§11. allowed_paths does not waive responsibility/import rules. Boundaries are authority; neither Go implementation nor future Java layout can redefine them.

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

- Coordinator delegates new independent Review on the committed checker candidate and verifies exact-head hosted job outcomes under explicit stage003 bounded scope; real source_go/Gate remain red until004 migration. Do not activate004 before bounded checker acceptance.

# Activation and bounded transition

002 fresh independently reviewed product3b049046/closurec0373ab and exact hostedrun36719353192 accepted. Backlog->ready->active, all dependencies satisfied. Fresh /root/stage3_impl sole writer. Checker/regression/authority delivery may pass with actual old Go product-compliance FAIL and overall Gate red exposed. Temporary003 acceptance scope permits only004 migration next, exits upon004 actual tree compliance. No exemption, continue-on-error, product or Gate PASS.

# Implementation candidate handoff

Effective checks delivered, local30architecture/24CI tests PASS (four historical Windows symlink subcases skipped), authority/governance/currentJava PASS; actualGo source FAIL expected inventory in evidence003/expected-old-go-violations.md and raw JSON. Commands ci/check_architecture.py --scope governance/go/java/all; unittest tests/architecture and tests/ci. No product/canonical/contracts/history edits. Fresh independent Reviewer plus exact hosted jobs still required, no selfacceptance; overall Gate stays red. Last bounded acceptedheadc0373ab, checkpointstage2. Implementation writer /root/stage3_impl releases after candidate commit, Coordinator delegates new Reviewer. Stage004 remainsbacklog.

# Fresh JDBC repair candidate

Independent read-only Review FAIL on a27f655 recorded in evidence003/jdbc-fix-evidence.md. New /root/stage3_jdbc_fix repaired Gateway execute SELECT-decoy loophole and non-Core JDBC transaction calls; architecture34 PASS/no skip,CI24 PASS/four historical Windows symlink subcase skips,canonical/recovery Development PASS; oldGo72 violations unchangedFAIL. Task remainsreview and004backlog; new independentReview/exact-hosted required,overallGate red. No product/history changes. Fixer releases writer after clean ordinary commit.

# Fresh final independent Review

New /root/stage3_final_review independently reviewed exact94b2f366dd1bee6652ec433b213c90f6c84fb4c9 in clean detached checkout. Bounded localcheckerPASS,34architecture tests/no skip,24CI tests/four disclosed historical Windows symlink subcases skipped,independent six-class variantsPASS,canonical/cleanRecoveryAcceptancePASS. ActualGo72FAIL expected,Java/governancePASS; manualmaintransport/fullAuthcoupling remains004. Evidence003/final-independent-review.md. Hosted exact closure pending; task staysreview,004backlog,overallGate NOT PASSED. Reviewer releases after evidence commit.

# Bounded hosted closure

Exact2afeac8/run36726926394 accepted bounded checker delivery:11 jobs success,source_go/gate actualFAIL; no product/Gate PASS. Evidence003/hosted-acceptance.md. Fresh004 Implementation owns next migration. One-time closure scope additionally includes AGENTS.md,spec/handoff/agent-context.md,spec/governance/execution-boundaries.md and3spec/acceptance/*.md only accepted-command/state references under Coordinator explicit authorization; final fresh004Review/hosted verifies this metadata.

---
task_id: LOOP1-ARCH-REMEDIATION-004
title: Migrate Go responsibility packages and regress
status: review
owner: Fresh Fix completed candidate pending new independent Review
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

- Coordinator delegates NEW independent Review of the clean reason-repair candidate, then normally pushes its reviewed dedicated task branch and verifies NEW exact-head hosted allrequiredjobs before004/batch closure/checkpoint. No other business advancement.

# Activation

003 bounded accepted exact2afeac8/run36726926394 after new independentReview. Backlog->ready->active; only004 migration authorized, overallGate remainsred. Accepted executable checks: bundledPython ci/check_architecture.py --scope all --json; bundledPython -m unittest discover -s tests/architecture -v; bundledPython -m unittest discover -s tests/ci -v; pwsh tools/verify-frozen-architecture.ps1. Publish actual migration table before product edits.

# Implementation candidate handoff

Actual migrationmap/evidence004/migration-map.md BEFORE products; privateCoreAuth/transactions/Outbox, readonlyGatewaynofullAuth,no permessageDB, minimalshared/rootassembly. All17recursiveformattedGo/build/vet/fullDB_TEST_ENABLE=1unit/race/canonical/livePGNATS/3rolesHTTPforwardandTLSbusiness/revocationclose/GoJavaComposeTLSsmokesPASS;34architecture0skip/27CI4historicWindows symlinksubcase skips. ExpectedoldGo72now actualsource0violations. No contracts/canonical/historicalProduct changes. Recorder004R-20260930T141457Z-8721259a-6a39-4e6f-baf8-2931ea75f14e andimplementation-evidence.md exactcommands. PendingnewindependentReview/finalexactheadhosted; no selfacceptance/batchorS1PASS.

# Independent Review local acceptance

Fresh /root/stage4_review accepted exact87c0ee2 from clean isolatedcheckout after fullrealPGNATS/unit/race/canonical/3rolesTLS/GoJavaCompose/negative controls, source0violations; evidence004/independent-review.md. Four historicalWindows symlinksubcase skips explicitly requireLinuxconfirmation; integration0skip. Task remainsreview pendingfresh exact-headhosted allrequiredjobs. Coordinator resumesnormal dedicatedbranchpush/CI/checkpoint only; no batch/S1PASS yet.

# Corrective metadata recovery point

Root identified candidate recovery metadata FAIL after product Review: section signs in Inputs/Execution Constraints were decoded as U+6402, and Next Action still described completed predecessor activation. This fresh Fix restores exact UTF-8 references from 6cdd981, updates current ownership and recovery only, and preserves prior local product Review PASS of 87c0ee2. New independent post-fix Review and final hosted acceptance remain pending; task004 stays review, batch/S1 NOT PASSED. Evidence: spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/metadata-fix.md.

# Final post-fix independent Review

Fresh /root/stage4_final_review local PASS exactb84cd0f from clean isolatedcheckout; new realPG16NATS/fullunitrace/canonical/3Go rolesComposeTLS/negativecontrols passed, zerointegration skips. Evidence004/final-independent-review.md. Four historicalWindows symlink subcases need hostedLinux confirmation. Unique004 stays review, remediation/S1 NOT PASSED pending fresh exact-head allrequiredjobs hosted. Coordinator owns next ordinarypush/CI/closure; Review releases onlynew evidence and handoff after commit.

# Hosted acceptance repair loop

Exact closure92306df/run36738064831 completed failure:11success,Go race andGate fail. Revocation expectedREPLACED butreceivedREVOKED at auth_test.go:211. Evidence004/hosted-failure-36738064831.md. Next exact action is freshFix diagnosis and bounded repair, then new independentReview and new hostedcandidate; do not relax existing expectations, suppressGate or closebatch.

# Fresh hosted-revocation repair handoff

Fresh /root/stage4_revocation_fix deterministically reproduced Corecommittedreplacement/logout withoutNATSGateway notification, both oldfallbackREVOKEDFAIL; minimalprivateGatewayexactbound readonlyreason lookup fixescauses whileexpired/DB/query/missing/unknownfacts closeREVOKED. Core/shared/contracts/schema/timeout/messagepath unchanged. NewrealPG16NATS fullunitrace/canonical/securityrollback/500msmessageDBnegative, targetedrace3times,19recursivefmtbuildvet/allsource0/34architecture0skip/27CI4historicWindows subcase skips/actual3rolesComposeTLSOutboxNATS PASSlocally. Evidence004/revocation-fix.md and freshRecorder. Task004 remainsreview, requiresNEW independentReview thenNEW exactheadhosted; no selfacceptance/batch/S1PASS. Fixownsnewchangesuntilcleancommit, then releases.

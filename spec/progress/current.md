# Current Execution State

Current Loop: `Loop 1`
Current Stage: `S3`
Current Gate: `S3`
Gate Status: `OPEN`
Current Batch: `LOOP1-PARITY-001`
Batch Status: OPEN
Current Task: `LOOP1-PARITY-001`
Current Task State: `review`
Execution Status: PR109 shared contract regression repaired locally, fresh independent reviews pending
Assigned Worktree: H:/.codex/worktrees/p/IM-platform
Task Branch: task/LOOP1-PARITY-001
Coordinator: /root

## Immediately Relevant Completed Work

PR108 finalized Java IM closure. Both profiles passed the local identical Web artifact run and the same live TLS messaging, retry, rollback, Sync and revocation checks. The Web application and both backend implementations retain their accepted source bytes.

## Current Blockers

PR109 push and pull-request runs on d990c045 failed the shared contract job and its dependent required gate. The repaired candidate requires fresh independent reviews and hosted verification.

## Verification

- Command: `python -Xutf8 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v`
  - Result: All 29 tests passed after reproducing and repairing PR109's shared job failure.
  - Evidence: `spec/progress/evidence/LOOP1-PARITY-001/hosted-fix-d990c045.md`

- Command: `python -Xutf8 -B tests/e2e/parity.py`
  - Result: PASS on Go and Java with the same built Web artifact.
  - Evidence: `spec/progress/evidence/LOOP1-PARITY-001/fix-58e87827.md`

## Changed Files or Migrations

The task changes the dual-profile TLS tests, the Web build helper, CI routing and workflow, and task records. The fixes cover shared deployment inputs, preserve primary and cleanup failures, and exercise readiness and cleanup fault injection in Java CI. Database migrations remain 0001/0002.

## Known Failures, Risks, and Assumptions

ADR-0004's single Friend authorization deferral remains. The Web application code runs on real HTTPS/WSS in the Node test runtime. S4 owns live plugin permissions. Initial malformed allowed-path formatting was corrected and verified.

## Next Exact Action

Delegate fresh regular review of the committed repair, then a different fresh error-handling review on the same SHA. Verify the hosted push and PR109 runs, protected integration, actual-main CI and safe main synchronization.

## Last Known Good Commit

`3a5a54abff6410762d2039c4acf880abbe3269a5` (PR108, actual-main run 44872421363).

## Latest Checkpoint

`spec/progress/checkpoints/2026-11-20-java-im.md`

## Uncommitted Changes / Ownership

The implementation writer owns the original parity candidate. /root/fix1 owns the earlier routing/recovery fixes. /root/fix2 owns the runner repairs, fault regressions and retained second-round reports. /root/hostedfix owns the shared regression repair and recovery updates. /root owns the retained d990c045 review reports. Each Recorder run owns its local research files. The H:/IM-platform checkout retains its pre-existing files.

## Architecture Conflicts / ACP / ADR

None. S1 and S2 remain accepted, S3 OPEN.

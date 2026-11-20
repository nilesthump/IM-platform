# Current Execution State

Current Loop: `Loop 1`
Current Stage: `S3`
Current Gate: `S3`
Gate Status: `OPEN`
Current Batch: `LOOP1-JAVA-IM-001`
Batch Status: REVIEW
Current Task: `LOOP1-JAVA-IM-001`
Current Task State: `review`
Execution Status: WSS timestamp hour verifier repaired after hosted Java failure, awaiting both independent reviews
Assigned Worktree: H:/.codex/worktrees/java-im/IM-platform
Task Branch: task/LOOP1-JAVA-IM-001
Coordinator: /root

## Immediately Relevant Completed Work

Java Auth product PR105 and closure PR106 are integrated. Java IM product commit 54fa46a6351c82bc4ac1d8f44adc8ba7021aa487 implements the approved Friend, Group, Message, Outbox, NATS and Sync responsibilities and live tests.

## Current Blockers

The Human authorized the WSS verifier hour correction after the prior candidate failed CI. Fresh regular and specialist reviews of the replacement, hosted CI, protected integration and main synchronization are pending.

## Verification

- Command: `python -Xutf8 -B contracts/websocket/verify.py`
  - Result: PASS on CPython 3.13.14 and 3.14.3. Java/Go/Java live IM also passed under 3.14.3.
  - Evidence: `spec/progress/evidence/LOOP1-JAVA-IM-001/hosted-hour-fix.md`

## Changed Files or Migrations

WSS timestamp verifier and live controls, Go message.send Gateway/Core checks, Java Core/Gateway, Docker build inputs, hosted Java checks, fixture drivers and task records. The migration baseline remains 0001/0002.

## Known Failures, Risks, and Assumptions

Regular and specialist reviews passed on 7ff6d1ed. The push and PR Java jobs both failed on that SHA because Python 3.14 accepted hour 24. The exact reports and failure evidence are retained. Independent reviews and hosted acceptance of the replacement are outstanding.

## Next Exact Action

Delegate a fresh regular review on final committed HEAD, then a different fresh error-handling specialist on the same SHA. Submit to hosted CI only after both pass.

## Last Known Good Commit

`18597c06f15c6ba5d50e055a88890a54f737fd52` (Java Auth closure).

## Latest Checkpoint

`spec/progress/checkpoints/2026-11-20-java-auth.md`

## Uncommitted Changes / Ownership

Initial product and control changes belong to /root/java_im. First fix, tests and evidence belong to /root/fix1. The second fix, regression and evidence belong to /root/fix2. /root/fix3 owns the third recovery-record correction and preserved /root/regular3 report. /root/fix4 owns the committed message validation, delivery regressions and preserved regular/specialist reports for 86ebf351. /root/fix5 owns the fifth Java repair, the approved Go conformance fix, shared tests, preserved review and UUID evidence. /root/hostedfix owns the WSS verifier repair, live regression and review/failure records. Recorder and test-generated artifacts remain owned by their creating runs. Main recovery changes remain with their original owners.

## Architecture Conflicts / ACP / ADR

Human resolved both the UUID divergence and the WSS timestamp hour boundary. No open architecture conflict. ADR-0004 remains applicable. S1 and S2 accepted; S3 OPEN.

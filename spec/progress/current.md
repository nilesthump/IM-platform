# Current Execution State

Current Loop: `Loop 1`
Current Stage: `S3`
Current Gate: `S3`
Gate Status: `OPEN`
Current Batch: `LOOP1-JAVA-IM-001`
Batch Status: REVIEW
Current Task: `LOOP1-JAVA-IM-001`
Current Task State: `review`
Execution Status: Java IM fix candidate awaiting fresh independent reviews
Assigned Worktree: H:/.codex/worktrees/java-im/IM-platform
Task Branch: task/LOOP1-JAVA-IM-001
Coordinator: /root

## Immediately Relevant Completed Work

Java Auth product PR105 and closure PR106 are integrated. Java IM product commit 54fa46a6351c82bc4ac1d8f44adc8ba7021aa487 implements the approved Friend, Group, Message, Outbox, NATS and Sync responsibilities and live tests.

## Current Blockers

Fresh regular review passed on 86ebf351, followed by a specialist FAIL on committed message validation and serialization failure classification. Both defects are fixed on the replacement candidate. Both fresh reviews, exact-head hosted CI, protected integration and verified synchronization remain pending.

## Verification

- Command: `python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL`
  - Result: The fourth fix passed in 71.719 seconds against PostgreSQL/NATS on Java and Go, including malformed committed events, serializer failure isolation and disconnected-peer retirement.
  - Evidence: `spec/progress/evidence/LOOP1-JAVA-IM-001/fix4.md`

## Changed Files or Migrations

Java Core/Gateway, Docker build inputs, hosted Java checks, fixture drivers and task records. The migration baseline remains 0001/0002.

## Known Failures, Risks, and Assumptions

Earlier setup and fixture regressions are retained in implementation evidence. Final regular review, different fresh specialist review, exact-head hosted CI and main verification remain pending.

## Next Exact Action

Review the final committed candidate from a clean checkout. After regular PASS, delegate a different fresh error specialist, then submit to hosted CI.

## Last Known Good Commit

`18597c06f15c6ba5d50e055a88890a54f737fd52` (Java Auth closure).

## Latest Checkpoint

`spec/progress/checkpoints/2026-11-20-java-auth.md`

## Uncommitted Changes / Ownership

Initial product and control changes belong to /root/java_im. First fix, tests and evidence belong to /root/fix1. The second fix, regression and evidence belong to /root/fix2. /root/fix3 owns the third recovery-record correction and preserved /root/regular3 report. /root/fix4 owns the committed message validation, delivery regressions and preserved regular/specialist reports for 86ebf351. Recorder and test-generated artifacts remain owned by their creating runs. Main recovery changes remain with their original owners.

## Architecture Conflicts / ACP / ADR

None at activation. ADR-0004 remains applicable. S1 and S2 accepted; S3 OPEN.

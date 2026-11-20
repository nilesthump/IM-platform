# Current Execution State

Current Loop: `Loop 1`
Current Stage: `S3`
Current Gate: `S3`
Gate Status: `OPEN`
Current Batch: `LOOP1-JAVA-IM-001`
Batch Status: REVIEW
Current Task: `LOOP1-JAVA-IM-001`
Current Task State: `review`
Execution Status: BLOCKED_BY_ARCHITECTURE pending message.send UUID compatibility decision
Assigned Worktree: H:/.codex/worktrees/java-im/IM-platform
Task Branch: task/LOOP1-JAVA-IM-001
Coordinator: /root

## Immediately Relevant Completed Work

Java Auth product PR105 and closure PR106 are integrated. Java IM product commit 54fa46a6351c82bc4ac1d8f44adc8ba7021aa487 implements the approved Friend, Group, Message, Outbox, NATS and Sync responsibilities and live tests.

## Current Blockers

Go commits and echoes an uppercase message.send request ID rejected by the frozen WSS verifier. Java now closes that invalid request before forwarding. Go product and compatibility changes are forbidden in this task. See fix5.md and uuid-case-observations.json in the task evidence directory.

## Verification

- Command: `python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL`
  - Result: Final Java/Go/Java suite passed in 72.422 seconds, including both committed timestamp boundaries. Separate live comparison confirmed the UUID divergence.
  - Evidence: `spec/progress/evidence/LOOP1-JAVA-IM-001/fix5.md`

## Changed Files or Migrations

Java Core/Gateway, Docker build inputs, hosted Java checks, fixture drivers and task records. The migration baseline remains 0001/0002.

## Known Failures, Risks, and Assumptions

Regular review failed on 57b98c54. The final Java repair passed local fixtures. A canonical lowercase request committed once on each profile. The uppercase request committed only on Go. No reviews or hosted acceptance of this replacement.

## Next Exact Action

Obtain Human/Architect decision on a separate Go conformance change versus a compatibility/contract decision for mixed-case UUIDs. Then resume independent regular and specialist reviews, hosted CI and protected integration as applicable.

## Last Known Good Commit

`18597c06f15c6ba5d50e055a88890a54f737fd52` (Java Auth closure).

## Latest Checkpoint

`spec/progress/checkpoints/2026-11-20-java-auth.md`

## Uncommitted Changes / Ownership

Initial product and control changes belong to /root/java_im. First fix, tests and evidence belong to /root/fix1. The second fix, regression and evidence belong to /root/fix2. /root/fix3 owns the third recovery-record correction and preserved /root/regular3 report. /root/fix4 owns the committed message validation, delivery regressions and preserved regular/specialist reports for 86ebf351. /root/fix5 owns the fifth Java repair, tests, preserved review and UUID evidence. Recorder and test-generated artifacts remain owned by their creating runs. Main recovery changes remain with their original owners.

## Architecture Conflicts / ACP / ADR

BLOCKED_BY_ARCHITECTURE on the message.send UUID compatibility decision above. ADR-0004 remains applicable. S1 and S2 accepted; S3 OPEN.

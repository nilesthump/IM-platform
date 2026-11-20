# Current Execution State

Current Loop: `Loop 1`
Current Stage: `S3`
Current Gate: `S3`
Gate Status: `OPEN`
Current Batch: `LOOP1-JAVA-IM-001`
Batch Status: REVIEW
Current Task: `LOOP1-JAVA-IM-001`
Current Task State: `review`
Execution Status: Java and Go message.send UUID agreement restored, awaiting independent reviews
Assigned Worktree: H:/.codex/worktrees/java-im/IM-platform
Task Branch: task/LOOP1-JAVA-IM-001
Coordinator: /root

## Immediately Relevant Completed Work

Java Auth product PR105 and closure PR106 are integrated. Java IM product commit 54fa46a6351c82bc4ac1d8f44adc8ba7021aa487 implements the approved Friend, Group, Message, Outbox, NATS and Sync responsibilities and live tests.

## Current Blockers

The Human resolved the earlier UUID compatibility question by authorizing Go conformance to the existing lowercase contract. Fresh final-SHA regular and specialist reviews, hosted CI, protected integration and main synchronization are pending.

## Verification

- Command: `python -Xutf8 -B tests/e2e/go_tls_messaging.py --profile go`
  - Result: PASS on Go in 35.297 seconds. The same HTTPS/WSS regression passed on Java in 150.906 seconds. Both reject uppercase inputs before durable writes and deliver the canonical control.
  - Evidence: `spec/progress/evidence/LOOP1-JAVA-IM-001/go-uuid-conformance.md`

## Changed Files or Migrations

Go message.send Gateway/Core checks, Java Core/Gateway, Docker build inputs, hosted Java checks, fixture drivers and task records. The migration baseline remains 0001/0002.

## Known Failures, Risks, and Assumptions

Regular review failed on 57b98c54. Its report and the historical divergence observed before the Human decision are preserved. Local fixes pass shared regressions. Independent reviews and hosted acceptance of the replacement are outstanding.

## Next Exact Action

Delegate a fresh regular review on final committed HEAD, then a different fresh error-handling specialist on the same SHA. Submit to hosted CI only after both pass.

## Last Known Good Commit

`18597c06f15c6ba5d50e055a88890a54f737fd52` (Java Auth closure).

## Latest Checkpoint

`spec/progress/checkpoints/2026-11-20-java-auth.md`

## Uncommitted Changes / Ownership

Initial product and control changes belong to /root/java_im. First fix, tests and evidence belong to /root/fix1. The second fix, regression and evidence belong to /root/fix2. /root/fix3 owns the third recovery-record correction and preserved /root/regular3 report. /root/fix4 owns the committed message validation, delivery regressions and preserved regular/specialist reports for 86ebf351. /root/fix5 owns the fifth Java repair, the approved Go conformance fix, shared tests, preserved review and UUID evidence. Recorder and test-generated artifacts remain owned by their creating runs. Main recovery changes remain with their original owners.

## Architecture Conflicts / ACP / ADR

Human resolved the UUID divergence in favor of existing lowercase contract conformance. No open architecture conflict. ADR-0004 remains applicable. S1 and S2 accepted; S3 OPEN.

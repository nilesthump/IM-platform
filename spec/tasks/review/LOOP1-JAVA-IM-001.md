---
task_id: LOOP1-JAVA-IM-001
title: Java IM implementation
status: review
owner: /root
stage: S3
gate: S3
---

# Goal

Serve the frozen Friend/DIRECT, Group, WSS messaging and HTTPS Sync operations from the Java profile. Core owns authorization, transactions, receipts, message ordering, sync and Outbox. Gateway forwards HTTP/WSS and delivers committed events to local connections. Keep the database and clients interoperable with Go.

# Inputs

Resolve and hash-check spec/architecture/README.md and baseline.md. Apply canonical §2.3, §3–7, §10 SRC-01..07, §11–14, §20 and Appendix B. Apply ADR-0004, ADR-0008, ADR-0013 and ADR-0014. Read spec/domain and spec/invariants for auth-user-friend, messaging, group and sync-plugin, and their spec/acceptance documents. Apply contracts/http/{auth-user-friend,group,sync}.openapi.json, contracts/websocket/{envelope,sync-v1}.schema.json, contracts/errors/http-errors.schema.json, contracts/database/migrations/0001 and 0002, and the corresponding contracts/fixtures. Apply governance/minimality, execution-boundaries, independent-review, error-handling and technology-selection, plus research/README.md.

# Technology Authorization

Use the accepted Spring Boot MVC/WebSocket, JDBC/PostgreSQL, Jackson, JDK crypto and JNATS stack (ADR-0014). Reuse current role wiring and dependencies.

# Dependencies

LOOP1-JAVA-AUTH-001, LOOP1-CONTRACT-001, LOOP1-CONTRACT-002, LOOP1-CONTRACT-003, LOOP1-DB-001, LOOP1-GROUP-001, LOOP1-SYNC-GO-001 and LOOP1-CI-001 are done.

# Allowed Paths

- backend/java/core/im/** (Friend, Group and snapshots, Message and Sync.)
- backend/java/core/auth/CoreAuth.java (route and reuse current Session checks.)
- backend/java/core/auth/SessionOutbox.java (extend existing publisher to committed IM events.)
- backend/java/gateway/auth/Gateway.java (HTTP forwarding, bound send and local fan-out.)
- backend/java/gateway/im/** (transport and local fan-out.)
- backend/java/Main.java (role assembly and dispatcher lifecycle.)
- backend/java/Dockerfile (copy IM sources for the runtime artifact; Coordinator approved)
- tests/e2e/go_tls_messaging.py (select Java or Go profile for existing TLS tests; Coordinator approved)
- tools/verify_sync_runtime.py (select Java or Go for the existing real Sync harness; Coordinator approved)
- backend/java/tests/auth/RevocationDeliveryProbe.java (existing test peer per-socket attributes; Coordinator approved)
- backend/java/tests/im/**
- tools/verify_java_im.py
- ci/classify.py (select Java for its three live fixture runners and deploy for shared Go TLS runners; Coordinator approved)
- tests/ci/test_classify.py (existing exact matrix for the shared TLS runner; Coordinator approved)
- tests/ci/test_java_im_job.py
- .github/workflows/ci.yml
- spec/tasks/backlog/LOOP1-JAVA-IM-001.md
- spec/tasks/ready/LOOP1-JAVA-IM-001.md
- spec/tasks/active/LOOP1-JAVA-IM-001.md
- spec/tasks/review/LOOP1-JAVA-IM-001.md
- spec/tasks/done/LOOP1-JAVA-IM-001.md
- spec/progress/current.md
- spec/progress/evidence/LOOP1-JAVA-IM-001/**
- spec/progress/checkpoints/*java-im*.md

# Acceptance

Use identical applicable contract fixtures on both real profiles and check durable PostgreSQL state. Verify atomic immediate friendship and unique DIRECT even for concurrent inverse adds. Group create/add must authorize current member/friend/session, bind normalized targets to original durable receipt, and commit changes plus all affected users' events together. Exercise authenticated snapshot pagination. Assert committed ACK follows Message+sequence+Outbox commit, rollback yields no success, unknown commit stays unconfirmed, replay yields original identity and conflict cannot create state. One logical group message and event; NATS local fan-out respects effective membership, sending connection exclusion and other sessions. Duplicated, reordered and missed delivery converges by authorized Sync. Verify both paginated Sync endpoints, cursor ownership, stable committed prefixes and gap-free conversation pages. Exercise failures, boundaries and post-switch interoperability. Preserve ADR-0004's sole deferred friend case.

# Forbidden

No public contract, migration, client, Go product, plugin runtime, ACK semantics or security change. Later LOOP1-PARITY-001 and S3 Gate are separate.

# Minimality

The allowed_paths list restricts writes and preserves SRC-01 through SRC-07. Use existing role startup, JDBC transaction manager, Session validation and transport. Add only concrete Core operations and the Gateway behavior used by current contracts.

# Error Handling Review

Record per-file catch/fallback inventory. Propagate unexpected faults. No fabricated results or confirmed rollback on unknown commit. Fresh regular Review then different fresh specialist on final SHA before CI. After any fix repeat both.

# Verification

Recovery entry point: `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance`. Live entry point: `tools/verify_java_im.py --build-dir EXTERNAL`.

Baseline: python -Xutf8 -B tools/verify_frozen_architecture.py; python -Xutf8 -B ci/check_architecture.py --scope all --json; python -Xutf8 -B -m unittest discover -s tests/architecture. Run Control Acceptance against clean candidate. Verify canonical HTTP/group/WSS/Sync fixtures, Maven verify in an external build directory, accepted Java Auth suite and live IM fixtures on both profiles against migrated PostgreSQL 16/NATS. Add the real Java IM checks to hosted Java job. Missing services are unexecuted.

# Evidence

Exact SHA/range, selected jobs and steps, independent reviews, actual-main verification and guarded main synchronization required. Research Recorder run R-20261120T110410Z-8417ffa6-fa1b-4a4f-96c7-db7a6b99cb71.

# Handoff

Accepted main remains 18597c06f15c6ba5d50e055a88890a54f737fd52. The regular review of 8974560b75644d1417a8ea37c226d0f5f201cd1c failed. Its report and fix evidence are in spec/progress/evidence/LOOP1-JAVA-IM-001/. /root/fix1 addressed the findings on task/LOOP1-JAVA-IM-001 at the assigned Git root. The second regular review failed on 6fd25b03834a38fdb31af5e6517d5c0f8d32ce32. Its original report is preserved in 6fd25b0-regular-fail.md. /root/fix2 aligned message sender and Session lock acquisition and added a real overlapping login/send regression on this branch. See fix2.md. The third regular review of a7e85f34ccc0cf9cccf942d51cd42fc4654751a5 failed clean Control Acceptance because the current verification record combined two evidence paths. Its original report, including the live IM/Auth, TLS, Sync and Unicode results, is preserved in a7e85f3-regular-fail.md in the task evidence directory. /root/fix3 corrected the verification entry to point to fix2.md, the evidence for the recorded command. Recorder R-20261120T123149Z-38099785-19f4-4062-815c-0ce1d35ff61a. Both independent reviews must run on the new committed candidate. Error specialist, hosted CI, protected integration and main synchronization remain pending. S3 OPEN.

Fresh regular review PASS and different fresh specialist FAIL at 86ebf3510450013943c22311abb5d5a00c526457 are preserved under the task evidence directory. /root/fix4 corrected both committed-message fan-out findings and added regression coverage. See fix4.md for the per-path recovery, real verification results and Recorder run. The current replacement requires both fresh reviews and exact-head hosted acceptance. Accepted main remains 18597c06f15c6ba5d50e055a88890a54f737fd52.

The fresh regular review of 57b98c54c2da2d6bf4dcfedb8e9ff740c8981301 failed on an extended signed year. See 57b98c5-regular-fail.md and fix5.md. /root/fix5 corrected the Java committed ACK and event validators and verified the real Java/Go/Java fixtures. The separate UUID comparison found an unresolved cross-profile divergence for an uppercase message.send request ID. BLOCKED_BY_ARCHITECTURE pending the compatibility decision recorded in fix5.md. The task stays in review, Gate S3 OPEN. The final replacement has no independent reviews or hosted acceptance.

# Next Action

Human/Architect to decide whether to scope a separate Go change to enforce the existing machine verifier, or authorize a compatibility/contract decision for mixed-case UUID input. Resume fresh regular and separate specialist reviews and exact-head hosted acceptance only after resolution.

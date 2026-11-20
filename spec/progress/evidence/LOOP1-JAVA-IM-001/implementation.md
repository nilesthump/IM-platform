# Java IM implementation evidence

Branch task/LOOP1-JAVA-IM-001; accepted baseline 18597c06f15c6ba5d50e055a88890a54f737fd52. Product tree commit 54fa46a6351c82bc4ac1d8f44adc8ba7021aa487. Worktree H:/.codex/worktrees/java-im/IM-platform. Implementer /root/java_im. S1/S2 accepted, S3 OPEN. This is development evidence. Both final candidate reviews, hosted CI, protected integration, actual-main verification and guarded synchronization remain pending.

## Local checks

Python 3 used the bundled runtime with -Xutf8 -B. The Recorder has exact argv, command durations, exits and output hashes in R-20261120T110410Z-8417ffa6-fa1b-4a4f-96c7-db7a6b99cb71. The parent R-20261120T110043Z-4fb24ce5-1424-4121-ad3d-acac3369b6fc holds the original prompt, Auth and coordinator verification. Both runs mark incomplete pre-run startup reads.

| Command | Exit | Elapsed | Observation |
| --- | --- | --- | --- |
| mvn -B -f backend/java/pom.xml -Dim.build.dir=EXTERNAL package dependency:build-classpath -Dmdep.outputFile=EXTERNAL/classpath.txt | 0 | 5.813 s | Final host build with five Maven unit tests |
| python tools/verify_java_im.py --build-dir EXTERNAL | 0 | 73.468 s | Real migrated PostgreSQL 16/NATS, Java then Go then Java. 35 group exchanges and 8 transaction vectors per backend. Includes concurrent receipt/member identity, six failure points, before/after commit lost response, tuple scan, concurrent friend writes, 500-member GROUP, originating connection exclusion and same-user peer delivery, duplicate/reordered delivery and gap-free Sync. Cross-profile cursor/receipt/ACK replay and new member access to pre-join history passed both directions. |
| python tests/e2e/go_tls_messaging.py --profile java | 0 | 142.344 s | Independent Compose stack, validated CA/hostname, durable ACK, one logical Outbox, rollback at deferred commit, nonmember, local NATS fan-out and Session revocation. |
| python tools/verify_sync_runtime.py --profile java | 0 | 133.656 s | Disposable Compose, TLS, 208 metadata events, 205 messages, pagination through terminal, oversized integer coefficients and exponents, new post-terminal commit, membership/cursor checks and no DB writes by Sync. |
| python -m unittest discover -s tests/ci | 0 | 8.594 s | 41 methods, 4 environment skips reported; live IM suite executed separately. |
| python -m unittest discover -s tests/architecture | 0 | 22.187 s | 99 methods, 1 environment skip; source-all ran separately. |
| python contracts/websocket/verify.py | 0 | 0.203 s | 18 shared scenarios plus rejected schema/behavior mutations. |
| python contracts/http/verify-group.py | 0 | 0.515 s | 35 conforming exchange descriptions and 30 invalid descriptions. |
| python tools/verify_sync_transport.py | 0 | 0.234 s | Frozen HTTPS binding and paging validation. |
| pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1 | 0 | 5.985 s | Nine operations, positive/negative fixtures and mutation checks. |

Auth regression used the existing tools/verify_java_auth.py --profile java, --profile go and --profile-switch. The coordinator recorded the passing results after the test peer supported socket attributes. The only deferred runtime case is friend-add-authorization-denied under ADR-0004. Local build, TLS and fixture commands executed at the indicated stages of development. CI must independently build and run the final SHA.

Initial failures retained in the runs: prompt already bound to parent run (linked child by parent_run_id); GBK output encoding failed when displaying the source graph (reran using UTF-8); task path syntax and missing governance marker (fixed); GroupFixtures test compile (added checked exception propagation); timestamp comparison compared RFC3339 spellings (now compares instants); missing group receipt returns 502 via Go Gateway and 500 via Java (canonical verify-group.py accepts 5xx and requires no fabricated result); original exact path matrix changed with shared E2E test (updated only its new Java selection); Development recovery found missing evidence/entry/next action (updated current and Task Spec). Recovery and raw run outputs remain development evidence.

## Error handling inventory

Product blob hashes and responsibilities are in production-hashes.json. The final specialist must inspect actual source independently.

| Location | Retained handling and recovery |
| --- | --- |
| CoreAuth.body | Parse errors classify malformed client JSON. Size/object constraints project the established validation error. |
| CoreAuth.isGroupJson and group | Malformed Content-Type, malformed UTF-8 and duplicate/invalid JSON reject under the group contract. An IO failure reading the body propagates. |
| CoreAuth.message | Canonical ApiFailure maps known bind/session errors to permitted message.ack variants. Confirmed PostgreSQL P0001 rejection raises MESSAGE_COMMIT_FAILED after rollback; unrecognized SQL/transaction errors propagate as unconfirmed server failure. |
| Groups.mutate | Refresh the ordered set of locked users only when an overlapping membership addition enlarged the set during acquisition. No writes precede that rollback. Existing receipt/identity inconsistency fails immediately. |
| Social.friendship, Messages.send, Sync.cursor and Sync.userPage | Missing digest/HMAC provider, impossible event serialization and malformed durable metadata propagate with causes. No new identity, empty page or successful ACK is substituted. |
| Sync.read and position | Malformed JSON or base64 user cursor rejects. Authentication/user binding, positive position and durable cursor existence still apply. SyncInput preserves numeric integrality in bounded storage. |
| SessionOutbox | Disconnected NATS has a pending durable row. A flush timeout rolls back the entire publication batch for retry. Permanent closure fails the worker. Shutdown interrupt is expected only during close, unexpected interruption reasserts the flag and propagates. |
| Gateway notification workers | Interrupt consumed only during shutdown. IO/internal parse failures propagate to service-worker failure. During delivery, a failed individual socket is removed and closed; an open-socket invariant failure propagates. |
| Gateway close/revoke | Aggregate teardown failures retain suppressed causes. A disconnected socket or documented close race retires that peer; an unexpected IllegalStateException on an open socket propagates. |
| Gateway.Socket | Malformed envelope closes the peer, known token/session rejection issues the canonical bind response then retires it. The pre-ACK registration is removed in finally if bind did not complete. Private HTTP transport failure or unverifiable result cannot produce a confirmed ACK. |
| tools/verify_java_im.py and profile fixtures | Missing env/build or any failing fixture subprocess fails the command. The existing profile manager preserves body and cleanup exceptions. Tests only normalize equivalent RFC3339 instants and the explicit noncanonical 5xx transport class in missing-receipt cases. |


Post-handoff local frozen integrity, source-all and Development recovery checks passed. Recovery resolved the unique review entry among five queues and 42 Task Specs.

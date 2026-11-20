# Independent regular review — PASS

Reviewer /root/review_auth_coverage was dispatched in a fresh context and did not implement, fix, previously review or integrate this candidate. Independently reviewed entire e4aee5ce2c4327904990d5c651267ca5eaae389d..72f1a46e5031cfc9e7e675de1164796960069904 on task/LOOP1-JAVA-AUTH-001. Assigned committed worktree H:/.codex/worktrees/j/IM-platform matched its Git root. Status clean before and after testing, also verified by Control Acceptance. No unresolved blocking findings. No repository writes or publication by reviewer.

## Source and acceptance

The frozen Markdown and historical PDF matched the manifest. Core owns authoritative auth, the locked slot, refresh rotation and the transactional outbox. Gateway queries authoritative sessions on bind and reconnect, owns its connection registry, and only performs read-only DB access. The three roles have separate startup and shutdown paths. Approved JDBC, MVC/WebSocket, JDK crypto, BCrypt and Session-only JNATS uses trace to ADR-0014. Shared support holds credential primitives and configuration. No new contract or migration. The narrow Go complete-message change preserves the existing size limit and downstream ACK behavior. Spring JDBC is exempt only from unresolved namespace string classification; actual declarations still undergo ownership checks. The additional database and temporary synthetic test rows serve the concrete conflict between real credential issuance and canonical mismatched target ownership. They are fixture infrastructure. The build now copies specific Java/build inputs, and Compose places the default operator config outside the source checkout.

The common runner actually exercised the five positive, fifteen negative and eight WSS scenarios against each profile. Checked fixture preconditions, asserted bodies and effects against canonical files, output identity and corresponding test logic. The complete per-case table in committed fixture-fix.md agrees with the code and live outputs. Real WEB2 mismatch, WEB7/8 stale case, refresh digests and usable replacements, canonical session state snapshots, true independently owned target slot, unchanged official login tokens, credentials captured from the exact query spelling, request correlation, bound identity and zero writes around WSS were present. Both key-rotation cases exercised a genuine previous-key login. An unbound socket remained unbound after ping. Rejected bind cases closed and a replacement produced revocation before close. The 16 future-stage exclusions and ADR-0004 deferral remain excluded from PASS. The scope of disclosure verification is the captured HTTP and WSS responses and role logs. No independent trace collector was exercised.

Peer retirement removes the binding atomically, isolates known failed sends/closes and propagates open-transport invariant failure. The normal NATS probe verified continued delivery to another live peer and a subsequent Session, plus original failure propagation for an unexpected internal error. Outbox publication timeout really rolled back and the worker retried. A nonpublication failure reached the uncaught worker boundary. Both profile-switch directions worked against one target DB. Linux workflow independently provisions and migrates the target/issuer DBs, requires both live runs and switch, and retains the separate operator-configured deployment smoke. Coordinator's deployment smoke remains separate evidence, not independently rerun by this reviewer.

## Command evidence

checks.py defines the exact argument vectors and environment derivation without credential values. Each row below gives its index, command, real exit status and wall time in seconds. Full command records, raw-output hashes and timings are in research/runs/R-NOV18-COVERAGE/events.jsonl.

| Index | Check | Exit | Seconds |
| --- | --- | ---: | ---: |
| 0 | verify_frozen_architecture | 0 | 0.313 |
| 1 | check_architecture --scope all --json | 0 | 0.875 |
| 2 | unittest discover -s tests/architecture (99, one skipped) | 0 | 19.656 |
| 3 | unittest discover -s tests/ci (39, four skipped) | 0 | 7.407 |
| 4 | contracts/websocket/verify.py | 0 | 0.172 |
| 5 | contracts/http/verify-auth-user-friend.ps1 | 0 | 5.547 |
| 6 | verify-loop1-ctrl-002.ps1 -Mode Acceptance | 0 | 24.094 |
| 7 | Offline Maven verify and dependency:build-classpath (initial cache denial) | 1 | 3.515 |
| 7 | Approved offline retry, five tests passed | 0 | 5.828 |
| 8 | verify_java_auth --profile java, 28 real fixtures | 0 | 77.437 |
| 9 | verify_java_auth --profile go, 28 real fixtures | 0 | 10.547 |
| 10 | verify_java_auth --profile-switch, both directions | 0 | 39.750 |

External input-hashes.json inventories SHA-256 of all surviving changed files. Manifest SHA-256 de505ce7bf6ea3b77bd6ca56ddf4242906b06cd92462ba3d61ac809f671ae2b9. Recorder R-NOV18-COVERAGE validated 46 events, final event hash 2a9bcb5767eedaec344e4a23a9aeeaffd0352861407d5cd87288497da58f08db. Partial startup and supplementary manual source reads outside the recorder include an unsuccessful PowerShell section filter and file glob, followed by corrected reads. Prompt record is a coordinator assignment summary. Recorder recorded prospective_resume with pre-work marked. The review build subtree contains disposable private test material and must stay external.

Regular pre-CI review PASS applies only to the specified SHA. Different fresh error audit, exact-head hosted checks, protected integration, actual-main verification and safe synchronization remain pending. S3 remains OPEN.

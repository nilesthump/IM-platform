# Role shutdown and WebSocket rejection repair

Fix agent /root/auth_exit_fix worked on task/LOOP1-JAVA-AUTH-001 at H:/.codex/worktrees/j/IM-platform. The regular review passed 72f1a46e5031cfc9e7e675de1164796960069904, and a different independent specialist rejected it before publication. The original reports are regular-review5.md and error-review5.md, with the specialist's inventory under error-review5-inventory.json. The previous accepted main is e4aee5ce2c4327904990d5c651267ca5eaae389d.

The default JVM uncaught handler retains its redacted class-only diagnostic and initiates nonzero JVM exit on a separate non-daemon thread. Spring can join the terminated worker and complete ordinary shutdown. This also covers an uncaught Main startup failure after Spring creates the context. The shared rejection sender uses the WebSocket session in try-with-resources. A lone close error propagates and a second error is suppressed on the actual send failure. Unknown types that require close only still close immediately. No contract, schema, role responsibility, dependency or TLS change.

## Local verification

- Verified frozen Markdown, PDF and approved decision lineage. Ran ci/check_architecture.py --scope all --json, both tests/architecture and tests/ci unittest discovery, contracts/websocket/verify.py and contracts/http/verify-auth-user-friend.ps1. All returned 0. The existing architecture suite reported one platform-conditional skip. CI discovery reported four existing conditional skips.
- Offline Maven verify and dependency:build-classpath, external output, exited 0 in 7.39 s.
- tools/verify_java_auth.py --profile java exited 0 in 93.14 s. Each of the two production roles ran twice from the packaged Spring Boot jar, loading only the initiating test class externally. After real Main startup, normal JVM shutdown returned 0 and actual unexpected worker interruption returned 1 with the expected redacted class, within a 30 s subprocess deadline. The existing DB/NATS probes remained active. Both rejection paths verified original send error identity, attempted close and exact suppressed close error. All 28 Java scenarios passed.
- tools/verify_java_auth.py --profile go exited 0 in 12.56 s, all 28 scenarios. The sequential --profile-switch run verified credentials in both directions, exit 0 in 42.89 s. Fixture cleanup, captured logs and intentional disclosure controls passed.
- Coordinator ran the isolated workflow preparation, Docker image build and Java TLS smoke on these product bytes. See lifecycle-local-tls.json. Hosted runs remain pending.
- External trace at C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119/nov18-lifecycle-fix/research/runs/R-FIX5. Recorder started after read-only startup. System Python was 2.7 and the py launcher was absent, so the installed bundled Python 3 executed the recorder. The external trace records the final exact commit and postcommit clean Control verification separately.

The candidate is the commit containing this record. All task-owned edits are in the assigned worktree. Fresh independent regular and different specialist reviews, exact-head hosted verification, protected integration, actual-main verification and synchronization to H:/IM-platform are pending. S3 remains OPEN.

Original external artifact SHA-256 values, before repository line-ending normalization:

- regular-review5.md 2128739a4ac76d8be7aae0b0807c4d8a7c6badb84ba252be9e303e98cacfed48
- error-review5.md 8da371bed2844a295e57df7d4595d558d57b7ef07288da940ff42177a114529a
- error-review5-inventory.json 86ea3a1f2dd9aea16990ed5135cb07da8b6dc0f386dec1d9038d881e48c97f25
- lifecycle-local-tls.json 7baba5b3a3a4a341223645a55944c95f3bfca2803adf006e99814e5c2cced573

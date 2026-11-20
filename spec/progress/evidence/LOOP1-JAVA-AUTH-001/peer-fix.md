# Revocation delivery repair

Branch task/LOOP1-JAVA-AUTH-001, assigned root H:/.codex/worktrees/j/IM-platform. Fixer /root/auth_fix_transport received the clean, rejected candidate 3b8f79049e03f6934ba6b1f5b8056d761e3007ef from the independent reviewer. See regular-review3.md for the original P1. No publication or main synchronization has occurred. Accepted main remains e4aee5ce2c4327904990d5c651267ca5eaae389d.

Gateway atomically removes each matching binding once. Serialization occurs outside the socket-I/O catch. A failed write still closes the retiring socket. Only I/O at the transport boundary and a container state exception on an observed closed connection are recoverable. Unknown failures on an open socket propagate. The resource-close boundary preserves an unexpected primary exception if cleanup also throws. Other peers and later committed events continue on the existing notification worker.

The regression uses a real Gateway and real NATS subscription with controlled WebSocketSession send/close outcomes. It checks retirement, notification before close for the surviving binding, and another event on the same worker. An internal open-session exception must reach the thread's uncaught handler with original identity. Existing live canonical cases separately exercise actual WebSocket connections and database-backed binding.

Offline Maven verify plus dependency:build-classpath passed (five tests, zero skips). tools/verify_java_auth.py --profile java --build-dir BUILD passed all 28 canonical scenarios, the new peer controls twice, actual NATS/outbox recovery, reconnect, nondefault TTL and existing disclosure controls. Frozen verifier and source-all passed. The Coordinator separately verified the actual Java TLS smoke with committed CI preparation, exit 0. Receipt: auth-ci-prep-smoke-267b86a5/receipt.json under the external evidence root. No Go product change in this repair. Prior Go parity, profile switch and TLS runs remain recorded for their own candidates.

Research R-PEER-FIX, source-hashes.json and external Maven/live outputs are under C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119/java-auth-peer-fix. Direct startup inspections and edits are outside complete trace. Initial system Python was 2.7 and py launcher missing. Restricted Maven dependency access and a Recorder GBK rendering failure required a new UTF-8 recorded build. Initial architecture suite failed its temporary Go subprocess under default cache permissions. No failed observation counts as PASS. Never publish private temporary live config files.

Final SHA is the commit containing this record, discoverable from its parent and branch; the external Recorder records the exact committed SHA and clean Control verification. Both new independent reviews and exact-head hosted verification are pending. S3 OPEN.

Scoped source SHA-256:
- backend/java/gateway/auth/Gateway.java: d267c3c0e321b500369835a49d073d525776e842d60e4286b0476142850aa780
- backend/java/tests/auth/RevocationDeliveryProbe.java: 53cadfb2d0876c5b5ee7abfcff3cb68a55e9f69e8fb92171eb0ec7701ae44421
- tools/verify_java_auth.py: 0968a30ad3062ceb0d6f890fe62f2e55ae3e2cb4a669c2e9408003d79f95e152

Final controls: tests/architecture 99 tests, one platform skip; tests/ci 39 tests, four platform skips. Both exited zero. The durable regular-review3.md normalizes line endings; the original external report SHA256 is 56b8986c113401f85b8b359ea4074a26ec29aaee4fc504f22b429ea6325deb47. An initial recovery-metadata read used the Windows default encoding and failed; explicit UTF-8 fixed the read.

# Terminal Session relay and resource teardown

Fresh Fix /root/auth_nats_terminal started at clean parent a45e98e55df922c9a1be31ab3031ae0b220cfcea on task/LOOP1-JAVA-AUTH-001 in H:/.codex/worktrees/j/IM-platform. SHA of the commit containing this record identifies the candidate. Accepted main remains e4aee5ce2c4327904990d5c651267ca5eaae389d. The parent passed independent regular Review and failed a separate error audit. Original external reports V/nov18-expiry-regular/review.md and V/nov18-expiry-error/review.md were verified before archival as regular-review7.md and error-review6.md. The latter's hash-checked path inventory is error-review6-inventory.json. V is C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119.

Core reads the pinned connection state on each existing tick. Reconnection can resume on a later tick; permanent CLOSED fails the actual worker and reaches the existing uncaught process failure boundary. A real JNATS connection in terminal state starts the worker against a disposable migrated PostgreSQL containing an unpublished event. The probe observes the worker's exact uncaught failure and unchanged attempts and publication time. The previous direct publish rollback check and delayed-PONG recovery still run. Normal role shutdown joins the worker before closing its client. Gateway's pinned subscription already fails on inactivity.

Gateway shutdown attempts every bound socket, retaining the first failure and suppressing subsequent failures. Java resource scopes also close NATS after socket or join failure. A two-peer regression exercises the real destruction method with a failing closing handshake, verifies both peer closes and real NATS CLOSED, and checks an independent body assertion retains the cleanup exception. The verifier uses the same Java resource semantics for restoring the hash, writing the sensitive-value capture, removing fixture rows, restoring the uncaught handler, removing the failed-DB config and destroying the Gateway. The test relay collects background errors, closes owned sockets and joins threads when a close fails. Shutdown socket errors are discarded only within the transfer/read paths during intentional closure. Other I/O and cleanup failures reach the test.

Python fixture teardown records independent owned cleanup when resources are acquired. All actions run; a lone failure propagates and simultaneous failures form an ordered exception group with the body failure first. Host waits are bounded. A timeout preserves its error even after successful termination. Both opaque issuer files receive removal attempts. An injected Go nonzero exit and a Java role wait timeout each coincide with a body failure. Assertions check the primary and secondary causes and completion of log closure, seed cleanup and disclosure checking. The Java job runs this negative control before the live fixtures.

## Local results

The run used the bundled Python 3 interpreter after the system python resolved to 2.7 and py was unavailable. Recorder R-NOV18-TERMINAL-FIX used prospective_resume for the pre-capture startup. Exact argv, outputs, exit codes and timings are in V/nov18-terminal-fix/research/runs/R-NOV18-TERMINAL-FIX; V/nov18-terminal-fix/checks.py resolves the indexed commands. Local data uses two disposable migrated databases and a real NATS broker. Each profile covered 28 canonical scenarios, expired-peer isolation and actual logout. Packaged Core/Gateway normal and fatal exits were 0 and 1 respectively.

| Recorded command | Exit | Recorder seconds |
| --- | --- | --- |
| Frozen architecture hash and provenance | 0 | 0.359 |
| Architecture boundaries, all scopes | 0 | 0.984 |
| Architecture unit checks | 0 | 19.922 |
| CI unit checks | 0 | 7.282 |
| WebSocket contract verification | 0 | 0.313 |
| HTTP Auth contract verification | 0 | 6.250 |
| Clean rejected parent control Acceptance | 0 | 24.766 |
| Offline Maven verify and dependency classpath | 0 | 6.047 |
| Java live profile including terminal NATS and gateway teardown | 0 | 108.969 |
| Go live profile | 0 | 25.172 |
| Sequential credential switching, both directions | 0 | 43.782 |
| Go nonzero exit / Java wait timeout plus simultaneous fixture failure | 0 | 0.328 |

Coordinator's isolated Java deployment/TLS smoke passed, exit 0, for the same product sources and workflow preparation body. V/auth-ci-prep-smoke-38cc95d2/receipt.json SHA-256 7baba5b3a3a4a341223645a55944c95f3bfca2803adf006e99814e5c2cced573. A subsequent CI edit wires the teardown test into an existing Java step. Prior unchanged Go deployment smoke is recorded in peer-expiry-fix.md.

Final clean Control Acceptance is run against the committed SHA and recorded externally in the same Recorder run. Fresh regular and different fresh specialist reviews, candidate hosted CI, protected integration, actual-main CI and safe synchronization are pending. S1/S2 PASS retained, S3 OPEN. No unknown main changes were copied or overwritten.

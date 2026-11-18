# Peer credential expiry repair

Regular review of parent 7679f24a848cf167a214311b3fbb83a5511ffdd5 failed. Its complete independent report is regular-review6.md with line endings normalized. Original V/nov18-final-regular/review.md SHA-256 6c4f2ffeeb430d3642f2b74539c09e893e86de33ffebc93da361b52bfa8212cb. Human scope approval on 2026-11-18 was “本轮同时修复 Go 和 Java”. The assigned root H:/.codex/worktrees/j/IM-platform was clean at startup on task/LOOP1-JAVA-AUTH-001. The range under repair starts at that rejected parent. The accepted baseline/main SHA is e4aee5ce2c4327904990d5c651267ca5eaae389d.

The Java bound message path and post-bind authority recheck now retire the affected socket on credential expiry. The Go receive loop and periodic watcher also close only that peer. Persisted Session revocation or stale epoch and real NATS delivery retain Session-wide retirement. Two formerly conflicting Go test assertions now require observable closure without a Session event and reject timeout. The database outage and persisted-revocation cases remain covered.

The common runner executes the original 28 canonical scenarios separately against each live profile. In an additional ordinary case, the real Java login HTTP controller issues a 12-second credential on the same key and database. Its localhost context closes immediately and runs no relay. Go production tokens ordinarily last 900 seconds. The selected profile owns refresh, Gateway bindings, logout and the sole publisher. While the initial connection remains bound, two more connections bind the freshly rotated credential on the same Session and epoch. After the old credential expires, the Java receive path or Go idle watcher closes that socket without a revocation frame. Both refreshed sockets answer correlated pings, the database slot is unchanged, and authorized user lookup succeeds. Actual logout then delivers a LOGOUT event with the same Session ID followed by closure on each refreshed socket. The Java post-bind race path uses the same per-binding retirement and was inspected in source.

## Local verification

V denotes C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119. Exact per-check argv and environment derivation are in V/nov18-expired-peer/checks.py, with redacted captured output in V/nov18-expired-peer/research/runs/R-NOV18-EXPIRED-PEER. Verification used the existing offline Maven cache, migrated PostgreSQL and NATS, with a separate issuer database for the canonical mismatch fixture. The test controller for the short credential shares the application database deliberately. Startup/source inspection before Recorder is marked incomplete (prospective_resume). The default Python executable rejected Python 3 commands during startup; the bundled Python 3 interpreter ran the actual verification. No credentials are included here.

| Check | Exit | Elapsed seconds |
| --- | ---: | ---: |
| Frozen Architecture/PDF verification | 0 | 0.203 |
| All architecture source/dependency checks | 0 | 1.375 |
| Architecture unit checks (99, one existing platform skip) | 0 | 19.938 |
| CI unit checks (39, four existing platform skips) | 0 | 6.828 |
| WebSocket contract verification | 0 | 0.172 |
| HTTP contract verification | 0 | 5.921 |
| Clean parent Control Acceptance | 0 | 24.657 |
| Offline Maven verify and dependency classpath | 0 | 6.766 |
| Java live profile | 0 | 103.391 |
| Go live profile | 0 | 24.078 |
| Sequential Go→Java and Java→Go credential switching | 0 | 38.953 |
| Go vet ./... | 0 | 10.813 |
| Go test -count=1 ./... | 0 | 23.015 |
| Go test -race -count=1 ./... | 0 | 101.235 |

Coordinator independently ran both isolated Docker deployment smoke checks against the changed Gateway sources. Java passed, exit 0, in V/auth-ci-prep-smoke-cfc2bcff/receipt.json, SHA-256 7baba5b3a3a4a341223645a55944c95f3bfca2803adf006e99814e5c2cced573. Go passed, exit 0 in 20.875 seconds, with result in V/root-research/runs/R-AUTH-20261118/events.jsonl under command C-528b4006-d746-4d2c-aa46-43846978c21b.

Regular and separate error-handling reviews for the new commit are pending, as are mandatory exact-head hosted CI, protected integration, actual-main verification and synchronization. Only this task-owned repair has been staged for commit. Unknown main work remains untouched. S1/S2 PASS retained, S3 OPEN.

# Independent regular review of Java Auth and Session

Candidate 2b8bcad24b5dddb82495a3e72b69ef045f73e899 on task/LOOP1-JAVA-AUTH-001. Compared with accepted main e4aee5ce2c4327904990d5c651267ca5eaae389d and separately inspected the terminal-relay and teardown repair since a45e98e55df922c9a1be31ab3031ae0b220cfcea. Reviewer /root/regular_terminal is a fresh context independent of implementation, fixes and prior reviews. Clean committed checkout H:/.codex/worktrees/j/IM-platform, unique task in review. Review artifacts and build output are external. scope.json records checkout and committed blob SHA-256 for all 68 changed paths, including deletions. All paths match the task allowance. 53 entries match the previous regular review's checkout inventory.

Verified the frozen Markdown and historical PDF hashes, accepted Java technology decision and the narrow Go scope. Examined the actual production logic and import boundaries. Core owns the row locks, rotation, logout, and Session Outbox transaction. Gateway owns WSS registration, authoritative read-only bind checks and NATS revocation delivery. Shared code provides configuration, hashing, token and error primitives. Root assembles and shuts down independent roles, and plugin-host provides its authorized health endpoint. Reviewed the declared JDBC, Jackson, Spring MVC/WebSocket, PostgreSQL, BCrypt-only and Session-only JNATS uses against ADR-0014. No new architecture-sensitive dependency, business responsibility, migration, public contract or ACK change in the repair. The helper mechanisms added to the verifier have concrete simultaneous failure cases. Go exits just the expired connection on receive/watch. Java conditionally removes that peer on expired binding, while actual retirement notifications apply across the old Session. Direct checks confirmed the two refreshed sockets survive the old credential expiry, then both observe the genuine logout before closing.

The Core worker now checks terminal CLOSED independently of CONNECTED and temporary reconnect states. The live worker probe used a real closed client, verified its uncaught failure and checked that a pending database event remained unpublished. The delayed PONG exercise separately confirmed rollback and eventual publication. Both packaged roles exited 0 on normal shutdown and 1 after forced worker failure. Gateway now attempts every bound peer and the NATS close after joining its notification worker. A live connection plus two peer doubles exercised one failing close and observed that both peers received close attempts, NATS closed, and the original fixture exception retained the close failure. Java resource scopes and independent Python cleanup callbacks preserve first and secondary errors, including on timeout. The Python control injected Go nonzero exit and Java wait timeout and verified other processes, log closure, binding cleanup and disclosure inspection. The CI step invokes this control and the live profile runs; both disposable PostgreSQL databases must be migrated.

The independent live runs exercised 5 positive, 15 negative and 8 WSS fixtures per backend against the same runner plus the peer regression. Lost-revocation reconnects consulted PostgreSQL on both. The Friend denied case remains DEFERRED_BY_HUMAN and other future Friend/Message cases remain outside this task. The recorded disclosure checks cover generated and captured test values. The terminal failure probe exercises an already-CLOSED JNATS connection and a real worker; actual broker reconnect exhaustion was not separately timed out. TLS deployment smoke is attributable to the Coordinator and the earlier unrelated Go suite is attributable to the recorded Go run in peer-expiry-fix.md. Exact-head hosted CI, distinct error audit, integration, actual-main and safe main synchronization are separate pending requirements. S3 stays OPEN.

The initial Maven run failed to access the pinned local dependency cache. The approved retry built from the same offline dependencies. Startup authority inspection preceded Recorder capture and was marked prospective_resume. checks.py contains all indexed verification arguments and environment setup, including real disposable service configuration without exposing credentials. Local scope.py was corrected to handle prior inventory tombstones; its initial offline comparison failed with KeyError before producing a manifest. The successful comparison is recorded in scope.json.

## Verdict

PASS for the independent regular review of 2b8bcad24b5dddb82495a3e72b69ef045f73e899. No blocking findings. Sequential switching confirmed a Go-created account can sign in through Java and a Java-created account through Go. Final Git status clean at the same SHA. Recorder R-NOV18-TERMINAL-REGULAR validated 34 events, manifest 6c598a0cee610a3f4c95f8839e3da3ebadf0a5f25d09b915788f7b66335909d3. Coordinator may dispatch the different fresh pre-CI error-handling review of this exact commit.

| Command (indexed commands resolved in checks.py) | Exit | Recorder seconds |
|---|---:|---:|
| 0 Frozen architecture | 0 | 0.407 |
| 6 Clean control Acceptance | 0 | 24.469 |
| 7 Offline Maven verify and dependency classpath | 1 | 3.703 |
| 7 Offline Maven verify and dependency classpath | 0 | 6.125 |
| backend/java/tests/auth/test_profile_cleanup.py | 0 | 0.344 |
| 8 Live Java | 0 | 110.344 |
| 9 Live Go | 0 | 24.281 |
| 10 Bidirectional profile switching | 0 | 42.203 |
| 1 Source and dependency checks, all scopes | 0 | 1.032 |
| 2 Architecture tests | 0 | 20.282 |
| 3 CI tests | 0 | 8.422 |
| 4 WebSocket contracts | 0 | 0.297 |
| 5 HTTP contracts | 0 | 6.125 |
| C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119/nov18-terminal-regular/scope.py | 0 | 7.781 |
| --branch | 0 | 0.078 |

# Independent pre-CI error-handling review

**PASS** for candidate `2b8bcad24b5dddb82495a3e72b69ef045f73e899`, branch `task/LOOP1-JAVA-AUTH-001`, compared with accepted base `e4aee5ce2c4327904990d5c651267ca5eaae389d`. No open specialist findings.

Fresh reviewer /root/terminal_audit took no part in implementation, fixes, or the regular review. The same specialist resumed its interrupted Nov 18 review on Nov 20, verifying the assigned checkout H:/.codex/worktrees/j/IM-platform again at the identical SHA. The index and working tree were clean on initial and final inspection. All specialist builds and evidence stayed outside the tracked tree. Independently verified the final regular PASS report SHA-256 2b5065f4d36c388a83a282af6136d41baf40d29da68bf8dd582205e4bb2ac7e7.

## Prior findings and verified outcomes

1. SessionOutbox distinguishes recoverable reconnection from terminal CLOSED. The actual worker failed on a closed JNATS connection with the expected uncaught error; the PostgreSQL event retained a null publication time and zero attempts. A separate real delayed PONG caused rollback and later successful publication without restarting. An unavailable database produced an uncaught transaction failure. Packaged Core and Gateway exited 0 after ordinary shutdown and 1 after unexpected worker interruption. The CLOSED probe uses an actual closed connection; reconnect exhaustion itself was not timed.
2. Gateway attempts all registered peer closes after the worker join, preserves the first failure and suppresses secondary failures, then closes NATS. One injected peer-close failure during teardown produced the expected suppressed IOException while the primary fixture error survived; both peer close attempts were observed and real NATS reached CLOSED. The independent delivery test also verified genuine worker defects propagate, isolated disconnects leave subsequent notifications functional and rejection send/close double failures remain distinguishable.
3. Java resource scopes retain primary and secondary failures when restoring a corrupted fixture hash, writing captured values, deleting rows or temp config, resetting handlers, closing peers and joining the relay. Python teardown runs independently registered resource releases in reverse acquisition order. The two-case Python regression verified that a Go nonzero exit and a Java wait timeout both survive alongside the original failing fixture assertion, with log closure, seed cleanup and disclosure inspection still attempted. A standalone cleanup failure is rethrown directly. The typed handlers and verifier-local cleanup helper address these concrete requirements without a new product framework.
4. The ordinary login/refresh/expiry/logout probe ran separately against both real profiles. Only the original credential's peer closed at expiry; both refreshed peers remained live and each received the genuine logout notification before closure. Go's unchanged-since-parent receive/watch changes remain confined to local credential expiry versus session-wide revocation. Java makes the equivalent distinction for bound requests.

## Scope and authority

inventory.json SHA-256 f23fababdee373f0e0efbe405981543258e28fc6e652c31129b72810e8a012cc covers all 35 non-governance files in the full range, including the removed placeholder, plus 51 actual retained catch locations with trigger and disposition. File entries record committed and checkout byte hashes, responsibilities and inspection outcome. 26 have independently matched committed bytes in the prior specialist inventory (SHA-256 f44c4243e111b7b3c47236c4fdcd95f5904e0d812e8a610c0f0c9cee2e3f8a7b). The remaining nine are separately assessed against the final source. The final regular report and its scope.json bind the governance changes as well.

The frozen architecture hash is a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef. Examined Session ownership, transaction boundaries, concrete JDBC/JNATS usage, public Auth/WSS semantics, Java technology authority ADR-0014, the scoped ADR-0004 deferral and the repository error handling and minimality rules. The Core owns committed Session and pending-outbox state. Gateway registration and read-only validation distinguish a credential-local refusal from a committed Session invalidation. Known wire refusals retain contract meanings. Internal crypto, SQL, state and callback failures retain their failures. The repair adds no public contracts, migration, architecture-sensitive dependency or generic product fallback.

## Command evidence

Times below come from the specialist Recorder. checks.py resolves its command indices. live.py and Expire.java supply the exact routine live role and lifecycle invocation, including the candidate's own expiredPeer assertion. The externally stored Recorder command records retain argv, output hashes, exit codes and durations. Root, branch, SHA, clean state and the full diff scope are asserted by inventory.py. The broader canonical fixtures, HTTPS verification and hosted acceptance are separate from the specialist tests.

| Command | Exit | Seconds |
| --- | ---: | ---: |
| checks.py 0, frozen baseline | 0 | 0.391 |
| checks.py 7, offline Maven build | 1 then 0 | 3.734 / 6.234 |
| live.py, packaged exit, outbox, peer failure and both profile expiry checks | 1 then 0 | 0.812 / 63.156 |
| backend/java/tests/auth/test_profile_cleanup.py | 0 | 0.859 |
| checks.py 1, architecture all scopes | 0 | 3.641 |
| inventory.py, complete range | 1, 1 then 0 | 0.860 / 2.031 / 2.282 |
| git status --short --branch | 0 | 0.078 |

The two initial Java invocations could not access the pinned offline Maven cache; the approved reruns on the same source and cache passed. The inventory helper initially counted catches in a removed file and string literals in a Python checker. Its corrected final pass enumerated only executable catch sites retained in the candidate. All failed attempts remain in the log. The first interpreter lookup resolved to Python 2 and the py launcher was unavailable; the bundled Python 3 ran the Recorder.

Research run R-NOV18-TERMINAL-ERROR uses prospective_resume. Initial authority inspection preceded capture; prompt.txt records the delegated audit request in condensed form. The recorded successful live command completed on Nov 18. On resumption its actual persisted output was inspected; those live checks were not duplicated. This is pre-CI evidence. The coordinator retains ownership of hosted acceptance, protected integration, actual-main verification, safe synchronization and task closure.


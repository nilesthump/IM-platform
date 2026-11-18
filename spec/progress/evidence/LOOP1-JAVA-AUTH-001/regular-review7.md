# Independent regular review of Java Auth and Go/Java credential expiry

Candidate a45e98e55df922c9a1be31ab3031ae0b220cfcea on task/LOOP1-JAVA-AUTH-001. Reviewed range e4aee5ce2c4327904990d5c651267ca5eaae389d..a45e98e55df922c9a1be31ab3031ae0b220cfcea, assigned clean Git root H:/.codex/worktrees/j/IM-platform. Reviewer /root/auth_expiry_regular is a fresh context with no implementation, earlier review, fix or integration role. External review outputs reside beside this report.

The unique review task retains S1/S2 PASS and S3 OPEN. The changed-path manifest covers 63 paths with removed paths represented explicitly, SHA-256 e159d9e6b96cb58ea9c73296c5018a6d53b12a9e92b4ff44529fe19f9e67044d. Contracts, frozen sources, migrations, clients and accepted unrelated work are outside this diff. Verified canonical a52e871d and provenance PDF 546915f6. Current Human authorization covers the narrowly named Go receive/watch change and two obsolete expiry-frame expectations. The continued DB outage and persisted-revocation assertions and the complete-frame decoding path remain present.

Core owns row locking, same-slot rotation, refresh-hash rotation, logout and transactional Session-only Outbox. Committed events update Gateway registrations. Gateway revalidates new binds against PostgreSQL and has no Session writes. Root assembly starts role workers, plugin-host stays health-only, and shared code contains data-source, token and password primitives. I inspected runtime imports, Maven role dependencies against ADR-0014, Docker build inputs and source-boundary controls. No contract, schema, role, password format, external dependency or future-stage facility was introduced by the expiry correction. Existing source checks still detect a local Core type masquerading under the Spring JDBC namespace. The fixture harness compares wire and stored state and keeps the ADR-0004 deferred Friend case and later-stage cases outside its 28 applicable cases per profile.

In Go the receive loop leaves through its per-connection unregister/close defers. Its idle authority check broadcasts only for revoked Session or stale epoch and retains the genuine error path for database/transport failure. In Java a conditional removal of the exact socket and claims protects other registrations from either the bound receive path or the post-bind recheck. The latter uses Session-wide retirement only after the committed slot signals revocation or stale epoch. Real NATS logout/replacement continues to retire the entire old Session. No new timer or notification type was needed. Java checks access expiry on bound application traffic while Go also has its pre-existing idle watcher. Heartbeats are available to unauthenticated clients under frozen section 7.2.

The regression signs in through the real Java login controller with a short configured access lifetime, closes that localhost controller context before refresh and runs a single relay for the selected profile. It binds the initial socket and two additional sockets to the rotated credential, checks unchanged Session/epoch and stored refresh rotation, requires the old socket to close without an event, confirms two correlated pongs and authorized User lookup, and requires both remaining sockets to receive the matching LOGOUT event before close. Java post-bind revalidation was checked by source inspection, without forcing a race. Packaged worker exit, rejection cleanup and publication retry controls remain in the normal verifier.

Java workflow dispatch provisions PostgreSQL/NATS, migrates the two distinct databases, builds and executes Java and Go profile runs and bidirectional profile switching. The local deployment TLS smokes and Go vet/full race runs are implementation/coordinator evidence in peer-expiry-fix.md. This independent review exercised direct live profile checks against disposable infrastructure. Hosted CI, protected integration, actual-main verification, synchronization and the distinct error-handling audit are separate and pending.

## Verdict and exact-head verification

PASS, independent regular review. No blocking finding in the full candidate range. Both profiles passed the original 28 applicable fixtures and the additional ordinary peer-expiry/logout scenario. Both rejected rebind after a lost notification. The four packaged role exit checks observed normal exit 0 and failure exit 1.

Command arguments and environment setup are in the external checks.py (0 through 10) and go-check.py (11). Results below give process exit code and wall time in seconds.

| Index | Verification | Exit | Seconds |
|---|---|---:|---:|
|0|Frozen Markdown/PDF|0|0.219|
|1|All source and dependency checks|0|0.938|
|2|Architecture unit checks|0|19.843|
|3|CI unit checks|0|7.782|
|4|WSS contracts|0|0.156|
|5|HTTP contracts|0|5.750|
|6|Control Acceptance from clean candidate|0|24.250|
|7|Offline Maven verify and classpath, first cache access attempt|1|3.578|
|7|Same command after approved cache access|0|6.094|
|8|Real Java profile|0|103.984|
|9|Real Go profile|0|23.734|
|10|Both directions of same-database credential switching|0|39.500|
|11|Go credential expiry, PostgreSQL fallback and unavailable database closure|0|7.532|

Initial Recorder console encoding failed on the first all-source command (wrapper exit 2). A UTF-8 wrapper rerun produced a complete successful command record. Manual startup and initial source inspection preceded capture and were marked prospective_resume with incomplete earlier trace. Research run R-NOV18-EXPIRY-REGULAR finished and validated, with 31 events. The architecture unit suite has one existing platform skip and the CI unit suite has four. Clean Git status and exact HEAD were reconfirmed after all checks. Real acceptance remains pending.

# Java Auth implementation candidate

Base: accepted authority/main `e4aee5ce2c4327904990d5c651267ca5eaae389d`.
Assigned root: `H:/.codex/worktrees/j/IM-platform`; branch `task/LOOP1-JAVA-AUTH-001`.
Implementer: `/root/java_auth_impl`, sole repository writer. Candidate SHA is the commit containing this record; final independent reviews, exact-head CI, integration and safe main synchronization remain PENDING. S1/S2 remain PASS; S3 remains OPEN. No claim of Java IM/Friend/Sync completion.

## Current behavior and scope

Core owns register/login/refresh/logout/User queries, Session replacement and transactional Session Outbox/user-sync revocation records. Gateway owns Auth HTTP proxy, WSS bind and readonly Session verification, registry and Session-only NATS notifications. Shared contains configuration and crypto primitives; Main only assembles roles. Plugin-host remains health-only. The expired InfraPlaceholder is removed.

The approved stack is Spring Boot3.5.16, Spring MVC/WebSocket/JDBC, PostgreSQL JDBC, Jackson, BCrypt-only Spring Security Crypto and JNATS2.23.0. Java source target21 runs on JDK25. Local Maven3.9.15 output/cache are external. Direct spring-jdbc avoids an unused pool. JNATS' unused NKeys BouncyCastle provider is excluded; real plain-NATS startup, publication, subscription and closed-connection tests pass with that exclusion. No ORM/authentication framework or new public contract/schema was introduced.

Coordinator approved the test-only Go bootstrap path before editing: real exported Core/Gateway handlers and existing relay run on ephemeral listeners under explicit selector/environment. Normal Go test does not start an indefinite fixture host. The same Java runner executes all applicable canonical inputs/expected values against both profiles. The existing Go product remains unchanged.

## Local verification

- `mvn -B -f backend/java/pom.xml -Dim.build.dir=EXTERNAL verify dependency:build-classpath -Dmdep.outputFile=EXTERNAL/classpath.txt`: PASS, 5 unit tests; actual product JAR and test runner compiled.
- `python -B tools/verify_java_auth.py --build-dir EXTERNAL --profile java`: PASS 28 canonical Auth/User/WSS scenarios, explicit fixture expected/input mutations, concurrent slot epochs, credential rotation, logout persistence/notification, lost-notification reconnect, real JWT claim checks, persisted BCrypt corruption produces HTTP500, real closed-NATS publish leaves PostgreSQL Outbox pending.
- Same command `--profile go`: same 28 canonical cases and mutation controls; no product Go changes. Revoked-socket executes both canonical steps and verifies no new messages/message Outbox after attempted post-revoke send.
- `--profile-switch`: PASS sequential same-database Go-created credentials on Java and Java-created credentials on Go, including passwords longer than BCrypt's native input limit. Stored hashes are not rewritten.
- `python -B ci/check_architecture.py --scope all --json`: PASS.
- `python -B -m unittest discover -s tests/architecture`: PASS99, one platform symlink limitation skip; `tests/ci`: PASS38, four platform symlink limitation skips. These are not skipped live acceptance cases.
- Canonical HTTP verifier: PASS9paths/9operations,6positive/21negative and15mutations; WSS verifier PASS18scenarios/18schema+26behavior mutations; frozen authority verifier PASS.
- Actual Compose Java TLS smoke: Coordinator-run PASS, TLS1.3 HTTPS registration/login, WSS auth.bind and logout notification through Caddy, PostgreSQL migrations and actual Core/NATS roles. Direct HTTP tests alone are not deployment evidence.
- Preserved Go Compose transport regression: Coordinator-run PASS, PostgreSQL migration/Core NATS/HTTPS/WSS over TLS1.3; separate disposable project and configuration, no Go product changes.

Final clean Control Acceptance and fresh reviews bind the committed candidate; local checks never substitute for hosted CI.

## Failures retained and corrections

Initial managed-branch approval call failed with infrastructure Bad Request before execution; identical normal approval retry succeeded. Initial Maven sandbox JAR/cache denial required approved external-cache build escalation. Initial source suite encoding/Go-cache access failures were environmental, rerun explicitly; no false PASS.

Control Development initially found missing parseable verification fields/entry-point metadata, plus legacy Python2/default Go cache environment failures. Added the required task/current fields and used explicit Python3/external Go cache; Control Development PASS in review state. This is recovery verification, not independent acceptance.

Actual HTTP fixture found the missing-authentication public message mismatch; corrected to canonical data. Live WSS found wildcard MVC proxy shadowing the WebSocket handler; proxy mapping now names only current Auth/User/Friend-auth-boundary routes. No future message handler was added.

The source checker mistook approved `org.springframework.jdbc.core` for application Core. Coordinator approved the narrow unresolved-import correction after physical declaration ownership checks, with positive external JDBC and negative locally declared lookalike Core controls. Historical S0 tests now keep their standalone placeholder controls while recognizing the current first-business transition. The old S0 rejection checker itself is unchanged.

Two TLS smoke attempts failed at the PowerShell callback invoked on a background .NET thread with no Runspace. Actual HTTPS and manual WSS101 had passed. Replaced only that test callback with the existing .NET static validation delegate, confined to disposable local-CA smoke; no host trust change. Corrected smoke PASS.

Repeated Go/JDK terminal-observation timeouts were preserved, not accepted. A Go goroutine snapshot showed no remaining Gateway socket/watch goroutines while JDK input/output flags remained open after the revocation frame. The runner had omitted the canonical second revoked-socket input. It now performs that post-revoke send, requires positively observed terminal closure (close notification or I/O error with both JDK sides closed), and checks no new message/Outbox rows; unknown exceptions and timeouts still fail. Temporary Go diagnostic instrumentation was removed.

## Evidence location and instrumentation limitation

External root: `C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119`.
Implementation recorder: `java-auth-implementation/runs/R-JAVA-AUTH-PRODUCT`; earlier preparation runs and planning inventory retained separately. Capture is `prospective_resume`, with incomplete early/direct command trace explicitly disclosed. Final live commands are recorded with actual argv/exit/output hashes. External build/config directories contain disposable test credentials and MUST NOT be published wholesale. Product evidence is separate from Recorder validation.

Coordinator TLS receipt is in `root-research/R-JAVA-AUTH-COORD3-20261113` command history; isolated local service receipt `auth-services-ready.json` records independent canonical migration and resource ownership. Main preservation snapshot belongs to Coordinator; implementation never writes `H:/IM-platform`.

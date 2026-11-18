---
task_id: LOOP1-JAVA-AUTH-001
title: Java Auth and Session equivalence
status: review
owner: /root/auth_nats_terminal
stage: S3
gate: S3
---

# Goal

Implement Java register/login/refresh/logout, User lookup, three Session slots and Gateway auth.bind/revocation under the same canonical Auth/User/WSS fixtures as Go. Include only Session Outbox/NATS delivery required by canonical 搂7.3. Retain S1/S2 PASS; S3 remains OPEN.

# Inputs

Resolve/hash-check spec/architecture/README.md and baseline.md; read canonical 搂2.3, 搂3, 搂4.1, 搂6.1, 搂7, 搂10 SRC-01 through SRC-07, 搂11, 搂20 and Appendix B. Accepted ADR-0014 and its exact Human approvals, ADR-0004 scoped exception, execution-boundaries, minimality, independent-review, technology-selection, error-handling and research/README apply. Read spec/domain/auth-user-friend.md, spec/invariants/auth-user-friend.md, spec/acceptance/s0-auth-user-friend.md; contracts/http/auth-user-friend.openapi.json, contracts/errors/, contracts/websocket/, contracts/database/ and all applicable fixture documents. Go code supplies compatibility observations only, never overrides contracts or dictates Java layout.

# Technology Authorization

Accepted ADR-0014: Spring Boot MVC/WebSocket, Spring JDBC/PostgreSQL driver, Jackson, JDK crypto plus BCrypt-only Spring Security Crypto, JNATS only current Session notifications. No ORM/security auth framework. Pin compatible versions within this authority; standard tooling/test libraries do not add product frameworks. External im.build.dir keeps generated Maven output outside tracked source roots. One artifact selects physically separate roles; root Main only assembles dependencies and starts/stops role services.

# Dependencies

- LOOP1-S2-GATE-001
- LOOP1-JAVA-ARCH-001 (accepted and synchronized at e4aee5ce2c4327904990d5c651267ca5eaae389d)
- LOOP1-CONTRACT-001
- LOOP1-CONTRACT-002
- LOOP1-DB-001
- LOOP1-CI-001

# Allowed Paths

- spec/progress/checkpoints/2026-11-13-java-authority.md (one-time accepted prerequisite closure)

- spec/progress/evidence/LOOP1-JAVA-ARCH-001/acceptance.json (one-time accepted prerequisite closure)

- spec/tasks/review/LOOP1-JAVA-ARCH-001.md (one-time accepted prerequisite closure)

- spec/tasks/done/LOOP1-JAVA-ARCH-001.md (one-time accepted prerequisite closure)

- backend/java/Main.java
- backend/java/pom.xml
- backend/java/Dockerfile
- backend/java/config.example.json
- backend/java/README.md
- backend/java/InfraPlaceholder.java (remove on first business implementation)
- backend/java/core/auth/** (Auth/User/Session transactions and Session-only Outbox delivery)
- backend/java/gateway/auth/** (HTTP proxy, WSS bind, readonly Session validation, connection registry/NATS revocation)
- backend/java/shared/authsupport/** (config, connections, token/crypto/codecs only; no business workflows)
- backend/java/plugin-host/Health.java (retain non-business health role required by existing Compose; no plugin execution)
- backend/java/tests/auth/** (unit and same-fixture blackbox tests, JDBC state assertions and profile-switch credential checks)
- backend/go/tests/java_auth_profile_test.go (explicit opt-in real Go Core/Gateway ephemeral test listeners for the shared blackbox runner; Coordinator authorized before edit, no Go product changes in the fixture host)
- backend/go/gateway/gateway.go (Coordinator authorized Fix2 only: replace prefix-decoding ReadJSON with complete-message decoding at existing serve boundary; same canonical single JSON envelope, limits, frame handling and ACK semantics. Shared malformed-suffix failure is present evidence; no other Go product edits under Fix2. Human decision “本轮同时修复 Go 和 Java” on 2026-11-18 additionally authorizes the bound receive path and safety watcher to close only the connection whose access credential expired. Cover both profiles with ordinary login, refresh and logout.)
- backend/go/gateway/watch_failure_test.go (2026-11-18 authorized corresponding test: watcher expiry alone closes without a Session event)
- backend/go/tests/revocation_fallback_test.go (same decision: correct the old expiry-frame assertion, retain the independent database-unavailable case)
- tools/verify_java_auth.py (bounded build/start/test/stop orchestration; standard library, no secret output)
- .github/workflows/ci.yml (replace Java placeholder job with real build and mandatory migrated PostgreSQL/NATS tests; preserve existing jobs/gate)
- tests/ci/test_java_auth_job.py (negative control rejects missing live tests or restored placeholder-only Java job)
- tests/ci/test_s0_boundary.py (Coordinator authorized SRC-06 first-business transition in current-tree/workflow assertions only; historical rejection checker remains unchanged)
- ci/check_architecture.py (Coordinator authorized narrow unresolved Spring JDBC namespace false-positive correction; retain declaration ownership checks)
- tests/architecture/test_source_boundaries.py (real framework positive and lookalike locally-owned Core negative controls)
- deploy/compose.yaml (Java role config mounts/dependencies only, reuse existing TLS/PG/NATS/migration topology)
- tests/infrastructure/smoke.ps1 (only adapt Java health/transport smoke to current Auth role, preserve Go and TLS assertions)
- spec/tasks/backlog/LOOP1-JAVA-AUTH-001.md
- spec/tasks/ready/LOOP1-JAVA-AUTH-001.md
- spec/tasks/active/LOOP1-JAVA-AUTH-001.md
- spec/tasks/review/LOOP1-JAVA-AUTH-001.md
- spec/tasks/done/LOOP1-JAVA-AUTH-001.md
- spec/progress/current.md
- spec/progress/evidence/LOOP1-JAVA-AUTH-001/**
- spec/progress/checkpoints/*java-auth*.md

allowed_paths does not waive SRC-01..07. The old S0 checker may remain historical; remove its Java workflow invocation only when actual Java build/live tests replace it. Do not broaden that checker to disguise product as placeholder. Coordinator owns prior freeze closure; do not modify other tasks without explicit current scope.

# Acceptance

Execute the 5 Auth/User positive, 15 Auth/security negative and 8 Auth WSS canonical scenarios listed in spec/progress/evidence/LOOP1-JAVA-AUTH-001/fixture-coverage.json against live Java and the same blackbox runner against live Go. Normalize only generated IDs/timestamps/token values using stable bijections and actual token claims; preserve statuses/errors/body/header/state assertions. Required missing case fails; Friend/Message cases are explicitly NOT_APPLICABLE_YET, not PASS. friend-add-authorization-denied remains DEFERRED_BY_HUMAN per ADR-0004.

Verify at most one valid Session per slot, concurrent login atomic epoch replacement, other slots unaffected, refresh rotation and rejection of old refresh material, logout invalidates Session and socket, session.revoked arrives before close, rebind validates authoritative DB after lost NATS events. Session write and outbox effects are one transaction; failed publish leaves event pending and cannot fake success. Same DB Go-created user logs in through Java and Java-created user through Go, profiles run sequentially. Keep SHA256(UTF8("im-password-v1:"+password)) lowercase hex then BCrypt compatibility without rewriting stored hashes. Reject credentials in query; response/log capture does not expose test secrets.

No applicable runtime tests may be skipped due to unset variables. HTTPS/WSS entry smoke remains required for deployment; direct HTTP/WS isolated tests are not production-entry acceptance. Fresh regular and different fresh error audits of final SHA, actual selected hosted jobs, protected integration, actual-main verification, safe H:/IM-platform sync and evidence required before done.

# Forbidden

No contract/schema/migration/security/ACK change, no Friend/Message/Sync business, no generic/message outbox framework, no ORM/authframework/new core library, no early plugin implementation, no permanent placeholder exception or unknown-main overwrite. No self-acceptance.

The 2026-11-18 Human decision also permits only the Go expired-peer correction described above, under existing wire semantics.

Fix2 narrow Go product exception above corrects existing acceptance of malformed JSON suffixes; it does not change the public contract or compatibility rules. Verify shared malformed suffix/legal whitespace controls on both profiles, applicable Go tests, Go TLS smoke and source-all boundaries.

# Minimality

Use direct role startup and small concrete Auth/Session methods. Transaction boundaries and Session Outbox exist for present canonical obligations. Avoid repository/service/factory hierarchies without current consumers. Shared contains primitives only. Use one fixture normalizer/runner for both profiles; retain existing Go tests except the two explicitly authorized obsolete expiry-frame assertions above.

# Error Handling Review

Unknown internal defects propagate and make request/test/process fail. Known invalid credential/schema/authorization failures project only canonical errors; SQL rollback, publish failure and socket cleanup keep real failure outcomes. No blanket exception-to-auth-invalid fallback. Record every retained catch/retry reason and file inventory; final SHA needs independent regular Review then different fresh specialist before CI, repeated after fixes.

# Verification

Recovery entry point: `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` from the clean committed candidate. Live entry point: `tools/verify_java_auth.py` with the concrete arguments below.

Existing baseline: python -Xutf8 -B tools/verify_frozen_architecture.py; python -Xutf8 -B ci/check_architecture.py --scope all --json; python -Xutf8 -B -m unittest discover -s tests/architecture; clean Control Acceptance.

Planned commands must exist before Review. Available local checks must pass. Local live tests unavailable due to Docker must remain explicitly PENDING, not PASS; informed code Review may precede mandatory hosted real PostgreSQL/NATS execution. No acceptance before all applicable hosted live checks PASS. Commands are not yet executable evidence:
- mvn -B -f backend/java/pom.xml -Dim.build.dir=ABSOLUTE_EXTERNAL_BUILD_DIR verify
- python -Xutf8 -B tools/verify_java_auth.py --build-dir ABSOLUTE_EXTERNAL_BUILD_DIR --profile java
- python -Xutf8 -B tools/verify_java_auth.py --build-dir ABSOLUTE_EXTERNAL_BUILD_DIR --profile go
- python -Xutf8 -B tools/verify_java_auth.py --build-dir ABSOLUTE_EXTERNAL_BUILD_DIR --profile-switch
- python -Xutf8 -B -m unittest discover -s tests/ci
- python -Xutf8 -B contracts/websocket/verify.py
- pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1
- pwsh -NoProfile -File tests/infrastructure/smoke.ps1 -Profile java; preserve -Profile go regression

Live prerequisites: two migrated disposable PostgreSQL16 databases (target PGDATABASE and distinct JAVA_AUTH_ISSUER_DATABASE), NATS2.10, operator-owned credential/config files, Go toolchain for sequential comparison, Java/Maven, external writable build directory. Existing PGHOST/PGPORT/PGUSER/PGDATABASE/PGSSLMODE/PGPASSWORD and NATS_URL wire the harness; DB_TEST_ENABLE=1 selects existing Go suites but absence must fail the new Java acceptance command. Secrets never appear in argv/logs. Run independent migration component before app startup. Local Docker became available after the user handled its startup prompt; isolated PostgreSQL/NATS tests now execute. Hosted Java job independently provisions real PG/NATS and must actually execute all live assertions.

# Evidence

Record exact branch/SHA/range, commands/exits/timings, fixture IDs/results/exclusions, environmental failures, independent review evidence, hosted actual job/step conclusions, integration/main sync and Recorder path. Research PASS is not Task PASS or S3 PASS.

# Handoff

Candidate a45e98e55df922c9a1be31ab3031ae0b220cfcea passed regular review and failed the separate error audit. The repair distinguishes terminal NATS closure from transient reconnection and preserves primary and secondary failures across role and verifier cleanup. Durable evidence, local commands, results and source of the independent findings are in spec/progress/evidence/LOOP1-JAVA-AUTH-001/terminal-cleanup-fix.md. Production sources, tests, Java CI wiring and scoped records are owned by /root/auth_nats_terminal. Branch task/LOOP1-JAVA-AUTH-001 remains in review. Last accepted main e4aee5ce2c4327904990d5c651267ca5eaae389d retains S1/S2 PASS. S3 remains OPEN.

# Next Action

Coordinator delegates fresh regular review of the commit containing this handoff followed by a different fresh error specialist on the same SHA. Both are pending. Exact-head hosted CI, protected integration, actual-main verification, and safe synchronization to H:/IM-platform are pending. Retain review state until independent acceptance and synchronization complete.

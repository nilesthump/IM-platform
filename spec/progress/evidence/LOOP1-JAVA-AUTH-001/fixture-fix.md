# Fixture and packaging repair

Fixer /root/auth_fixture_fix, branch task/LOOP1-JAVA-AUTH-001, managed root H:/.codex/worktrees/j/IM-platform. Parent candidate 82a68477b0e380c847bacd8b1cce7fc4167371f9 was rejected by fresh regular review. Original report SHA-256 1d9625bee2d666d3e73b00f1b730a51a44f9047d0af0c6647d86a61b6ded9a3d, normalized copy regular-review4.md. Last accepted main e4aee5ce2c4327904990d5c651267ca5eaae389d. Final repair SHA is the commit containing this record, recorded by the external clean Control/Recorder. No hosted verification, protected integration or main sync yet.

## Local coverage

The same runner exercised the following cases against actual Java and Go roles on migrated PostgreSQL and NATS. Every HTTP response and WSS fixture frame is compared to canonical expected data. Generated values use stable mappings. This table describes the specific observations underlying the local result.

| Canonical case | Evidence on each profile |
| --- | --- |
| registration-and-authorized-user-search | Fresh mixed-case registration, matching normalized lookup for the issued account and uppercase search. |
| same-slot-login-replaces-only-that-slot | WEB1, DESKTOP1, WEB2. Both current slots read successfully, two active rows, immediate WEB1 rejection. |
| native-refresh-rotates-current-session-credential | MOBILE4 identity unchanged, replacement digest is unique and retired digest absent. An ordinary subsequent refresh with the new credential succeeds. The dedicated old-native negative also rejects. |
| web-refresh-rotates-secure-cookie | WEB5 identity unchanged. Secure cookie replaced, former digest absent, current digest identifies this slot, and a subsequent ordinary refresh with the new cookie succeeds. Old-cookie retirement is verified in storage. No old-cookie HTTP replay was performed. |
| logout-revokes-session-refresh-and-connection | Authenticated desktop socket receives LOGOUT before close. Persisted slot revoked with null refresh hash, old access denied. |
| invalid-credentials | Canonical wrong-password error. Full target user slot snapshots before/after match. |
| token-in-query-rejected | Canonical access_token query name with a generated opaque value, required 400 body, inventory membership and captured response/header/role log checks. Literal example value coincides with a word in the required error message. |
| invalid-client-type | Unsupported TABLET rejected and full slot snapshot unchanged, including row count. |
| refresh-client-type-mismatch | WEB2 cookie credential on the MOBILE refresh fixture. Required 401 plus identical full slot snapshot. |
| unsupported-protocol-version | Unsupported protocol response and 426. Full prior slot rows preserved. |
| missing-authentication | No Authorization material, canonical 401 body, no user or other data. |
| authorization-binding-mismatch | An unchanged ordinary test login from a distinct migrated issuer database. Before target startup two fresh synthetic target accounts and their WEB1 slots are inserted in one transaction. The token subject has its own different slot ID and the ID in the token belongs to the other target fixture account. An explicit DB check confirms both. Ordinary /me returns exact 401 without profile. Both fixture rows/accounts cleaned after role shutdown. Separate missing-ID rejection retained. |
| invalid-access-token | Ordinary issued token from before disposable signing-key rotation, unchanged bytes. Exact 401 with no data. |
| expired-access-token | Expired claim on the correct session, exact 401 and no data. |
| revoked-session-token | Actual logged-out DESKTOP token rejected with the specified body. |
| username-already-exists | Case-normalized duplicate 409. Exactly one original ID and display name remain. |
| web-refresh-missing-cookie | WEB refresh without Cookie gets canonical rejection and no token response. |
| native-refresh-missing-token | Native refresh without refresh token gets canonical rejection and no token response. |
| stale-session-epoch-rejected | Real WEB7 token immediately after successful WEB8 login. Both numeric epochs checked and zero disclosed data. |
| revoked-refresh-token-rejected | Actual retired MOBILE refresh after rotation, exact rejection and no newly issued token. |
| bind-valid-session | ACK identity matches the presented validated claims. Counts for all messages and all outbox rows unchanged. |
| ping-before-bind | Correlated pong followed by the canonical rejected send on the same socket, establishing it remained unbound. |
| unauthenticated-send | Expected rejected ACK and terminal socket. Both total message and total outbox counts unchanged. |
| stale-epoch-bind | Actual earlier WEB token, canonical rejected ACK followed by terminal close. Message/outbox counts unchanged. |
| expired-token-bind | Expired token, canonical rejected ACK followed by terminal close. Message/outbox counts unchanged. |
| wrong-client-type-bind | Mismatched client claim, canonical rejected ACK followed by terminal close. Message/outbox counts unchanged. |
| invalid-signature-bind | Well-formed credential issued before disposable signing-key rotation. Rejected ACK, terminal close and unchanged counts. Independent malformed WSS-only fixture checks disclosure inventory. |
| revoked-socket | Actual replacement event matched prior identity and required reason. Terminal closure/no successful send, total messages/outbox unchanged. |

Captured HTTP bodies/headers, WSS traffic and role logs underwent disclosure checks. No distributed trace collector was present. The 16 future-stage scenarios and the single ADR-0004 deferral remain distinct from these results. Controls mutate the fixture expectation/input and insert synthetic disclosure strings into captured-output checks.

## Deployment and scope

The Java image copies only Maven metadata, the entry point and Java sources in the required directories. Compose selects a default operator configuration directory beside the checkout. The Java README documents migration of the former in-tree default. A trial root .dockerignore was rejected by the exact source ownership guard and removed. The final change preserves the architecture checker. No contract, migration, product auth handler or product dependency changed.

The second disposable database is required to test an independently issued ordinary Session against divergent synthetic fixture rows without modifying existing target users or forging a credential. The Go/Java profile-switch still shares one database. Canonical migrations are run by the independent bootstrap before either profile. The fixture setup never updates existing rows. Both local profile runs confirmed transactional setup and scoped cleanup.

## Verification and remaining gates

External evidence root C:/Users/21441/.codex/visualizations/2026/11/13/01a1d469-fb95-7d83-bf4b-53bd8ba2b119/nov18-auth-fixture-fix contains checks.py and Research Recorder R-FIX4. Its numbered recorded commands contain actual arguments, output hashes, return codes and timings. Private build directories and role logs must stay external. Startup used direct reads before capture, system Python 2 and missing py launcher failed before bundled Python 3 was located. Coordinator dispatch summary retained. Edits and some reads were direct. An intermediate Maven name collision and a deliberate incomplete-coverage run failed and remain observable.

- Offline Maven verify plus dependency:build-classpath exited 0, 5 tests. Java live profile exited 0 (77.438s), Go live profile exited 0 (11.360s). Both checks completed all 28 scenarios. Fresh profile-switch exited 0 in both directions.
- Frozen verifier, source-all, tests/architecture, tests/ci and HTTP/WSS contract verifiers run through checks.py. Final exit codes recorded in the Recorder. Clean Control Acceptance follows commit.
- Coordinator executed actual CI configuration preparation and final Java Docker/TLS smoke, exit 0, external auth-ci-prep-smoke-a4fd5e14/receipt.json. Initial Docker testCompile failure on the earlier intermediate source is superseded.
- S1/S2 retain accepted PASS. S3 is OPEN. Fresh independent regular review, different independent error audit, exact-head hosted acceptance, protected integration, actual-main verification and safe synchronization all pending.

# Independent regular review — FAIL

Reviewed by /root/auth_regular_final, fresh independent context. No participation in implementation, fixes, or prior reviews. Clean assigned worktree H:/.codex/worktrees/j/IM-platform, branch task/LOOP1-JAVA-AUTH-001, entire range e4aee5ce2c4327904990d5c651267ca5eaae389d..82a68477b0e380c847bacd8b1cce7fc4167371f9. Commit and cleanliness confirmed before and after testing. Remain in review; S3 OPEN.

## Correction required

1. The common live runner does not instantiate some canonical conditions or test their required effects. AuthFixtureRunner.java lines 125–130 and 211–224, plus callHeaders around line 76. Detailed 28-case disposition follows. The upgraded fixture coverage must work through both real profiles. Preserve existing literal malformed credential/disclosure controls where useful. No new product contract or response semantics are required.
2. Java Dockerfile COPY of the entire source directory includes the default operator config directory selected by deploy/compose.yaml within that very build context. There is no ignore file at the Java context root. An operator using that provided default sends the JWT/PG files to the builder and makes them part of the first-stage COPY layer. Final stage copies just the JAR. Restrict copied inputs or require operator config outside the build context. This is a static packaging finding. No credential discovery or image extraction was performed.

## Canonical fixture audit

The following compares each current canonical precondition, state expectation and visible response with the common runner on both profiles. Independent static examination found no implementation bypass or observed data disclosure. A correctly shaped wire error alone does not establish which input condition produced it. Where durable DB uniqueness and an authorized HTTP read already establish an outcome, no separate test mechanism is prescribed.

| Canonical ID | Observed implementation and outstanding evidence |
| --- | --- |
| registration-and-authorized-user-search | Fresh account, canonical lowercase response, authorized uppercase search and unique user schema present. Negative duplicate case supplies conflict. Role logs scanned for submitted password/tokens. |
| same-slot-login-replaces-only-that-slot | WEB1, DESKTOP1, WEB2 replacement, accepted WEB2 and DESKTOP1 and two active rows checked. WSS suite separately observes old WEB event/close. Old epoch rejection is tested later when the current epoch has advanced further. Tie the old-epoch rejection to immediate post-replacement state where claiming that exact timing. |
| native-refresh-rotates-current-session-credential | Actual MOBILE4 setup and successful replacement material; old credential is rejected by the later native negative case. Explicitly compare pre-/post-refresh Session identity (currently first appearance of its normalized session ID is after refresh); ensure newly issued credential is usable. |
| web-refresh-rotates-secure-cookie | Actual WEB5, secure cookie attributes and different cookie value checked. Missing observation that old cookie is invalid, and that the same Session identity survives rotation. Java nondefault TTL path separately uses new cookie. |
| logout-revokes-session-refresh-and-connection | Authenticated desktop socket, logout, LOGOUT event, terminal close, persisted REVOKED/null refresh hash, rejection of old access token observed. No client-storage code changed. |
| invalid-credentials | Existing account, rejected code, exact body and log checks executed. No before/after Session assertion, so an erroneous replacement alongside a rejection could pass. |
| token-in-query-rejected | Actual GET with access_token yields validation error before missing-auth error. Collector recognizes token/accessToken/refreshToken/password but misses the canonical access_token spelling. No role log/response/trace check actually tracks that specific query credential. Assess only captured surfaces. |
| invalid-client-type | TABLET input rejected, canonical schema prohibits fourth slot. Runtime fixture does not compare existing slots or check absent TABLET row. |
| refresh-client-type-mismatch | The fixture states WEB epoch 2, presented to MOBILE. Runner injects DESKTOP refresh and runs after WEB5. No before/after observation of the required unchanged WEB slot. |
| unsupported-protocol-version | Unsupported request, 426 and canonical body checked. DB state before/after missing for no Session creation/replacement. |
| missing-authentication | Uncredentialed friends request, canonical 401 and exact no-data body verified. |
| authorization-binding-mismatch | Uses random unowned Session UUID. Canonical requires token subject A and an actual binding owned by another user B; no B account/Session exists in this setup. Expected error matches regardless. |
| invalid-access-token | HTTP case changes a real token signature by appending one character, producing different-length signature bytes. Canonical invalid-token error and no-data body checked. A normal-length mismatched signature can establish signature-specific behavior unambiguously in both transports. |
| expired-access-token | Expired, signed claims using actual Session; HTTP error, no data and disclosure verified. |
| revoked-session-token | Access token for actual logged-out desktop slot produces canonical error and no data. |
| username-already-exists | Existing canonical identity and 409 plus password disclosure checks observed. Database unique username constrains duplicate creation; runner does not count users or verify retained original account immediately after failed registration. |
| web-refresh-missing-cookie | Actual cookie absence, canonical HTTP error, exact no-token body verified. |
| native-refresh-missing-token | Actual body omits refresh material, canonical error and exact no-token body verified. |
| stale-session-epoch-rejected | Actual stale token, but runner uses WEB1 versus current5. Canonical precondition fixes current8 versus old7 (epoch is not a generated ID/timestamp/token normalization). |
| revoked-refresh-token-rejected | Actual revoked old MOBILE credential, canonical status/body, no issued token. |
| bind-valid-session | Valid token, full bound ACK and subsequent routed revocation observed. Normalize maps first-seen user/session identifiers to arbitrary valid UUIDs rather than the actual presented Session claims. Compare bound identity with login claims. Zero message/outbox effects not sampled around this case. |
| ping-before-bind | Pong and exact correlation checked. New socket starts unbound; runner closes it after pong without observing that it remained unbound. |
| unauthenticated-send | New unauthenticated socket, rejected ACK/code checked. No before/after DB comparison for required zero message/outbox effects. |
| stale-epoch-bind | Real stale token and canonical rejection. No check of required zero messages, nor follow-up observation of failed admission or terminal close; runner itself closes the socket. |
| expired-token-bind | Real expired token and canonical rejection. Same missing zero messages/failed-admission observation. |
| wrong-client-type-bind | Signed DESKTOP claim for WEB session; canonical rejection. Same missing zero messages/failed-admission observation. |
| invalid-signature-bind | Input "not-a-valid-JWT" fails token structure before any signature check. Canonical given explicitly requires invalid signature. The unit-level Java key check does not supply shared live evidence. Same zero messages/failed-admission gaps. |
| revoked-socket | Real bound session/replacement event, correct reason and echoed normalized prior session, post-revocation send, terminal closure and no message or message-outbox increase checked. |

The concurrent-login check at lines 247–251 requires four HTTP 200 responses through login(), four distinct reported epochs and one WEB row. It does not independently compare consecutive epochs or the winning active credential to the final persisted slot. This is an evidence-strength observation, not an independent request to expand scope. The canonical DEFERRED_BY_HUMAN and 16 future-stage exclusions remain distinct from execution.

## Source, scope and prior repair

Core owns authoritative User/Auth writes, session upsert+revocation/outbox within one Spring transaction. Gateway is read-only against session DB. Root starts dedicated roles and shared utilities hold configuration/token/password primitives. JDBC/PG, Spring Web/MVC/WS, Jackson, JDK crypto, BCrypt-only Security Crypto and Session-only JNATS trace to canonical sections 2.3/3.2/7 and accepted ADR-0014. Plugin host remains health-only. Go's complete-message decoding delta preserves length, handler and ACK responsibilities; actual declarations still undergo the architectural ownership check after the bounded JDBC namespace change. No migration or contract file changed. No speculative product frameworks identified. Common blackbox client, probes and the narrow resource-close scope have concrete current consumers.

Prior peer-disconnect P1 has been corrected. Atomic binding removal, serialized send and guaranteed cleanup isolate observed closed-peer outcomes; open-socket internal state failure propagates with identity preserved, and outbound serialization is outside the recoverable I/O catch. Fresh normal probe actually ran on real NATS, observed another binding's notification before close, and processed a second independent notification on the same worker. Fresh Java and Go fixture suites and cross-profile account compatibility completed. Existing CI guarantees Maven build, migration, PG/NATS and both profile runs plus profile switch; the current test omissions also affect what that CI can establish. Deployment TLS smoke requires origin configured through the committed CI step. This review did not independently rerun TLS; separate coordinator smoke evidence remains distinct.

## Independent command evidence

External directory nov18-auth-regular; checks.py records exact argv for each check index. Recorder research/runs/R-NOV18-JAVA-REGULAR/events.jsonl records commands, real exit codes/durations and stdout/stderr hashes. The role fixture setup reads a credential file without printing it. Do not publish the runtime build/ subfolders containing private disposable credentials.

- Frozen verifier 0, source-all 0. Architecture 99 tests (one platform skip), CI 39 tests (four platform skips), HTTP and WSS contract verifiers, and Control Acceptance all exit 0.
- Fresh offline Maven verify plus dependency:build-classpath exit 0 (five tests). Initial restricted JVM dependency-cache access exited 1 and was retained; approved offline retry succeeded.
- Normal Java, Go and sequential Go→Java/Java→Go credential test commands exit 0. Source deficiencies above limit the meaning of the 28 printed PASS labels.
- Startup research attempts used system Python 2 and a missing py launcher before the installed Python 3 was located. Initial startup reads and supplementary direct source reads were outside complete trace. External Recorder uses prospective_resume with explicit pre-work and a coordinator-sourced summary. No repo edits or pushes, no specialist/hosted/integration verdict.

Fresh fix, fresh regular review and then distinct fresh error review are required on the new final SHA. Current candidate must not advance.

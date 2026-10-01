# S0 Auth, User, and Friend Contract Checks

These checks are executable requirements for the future canonical contract runner. They define observable cases and assertions, not endpoint paths, wire fields, classes, or storage schema.

| Rule ID | Executable contract check | Source |
| --- | --- | --- |
| AUF-A-001 | Given one valid Session in a login slot, when the same user logs in again for that client type, the fixture runner MUST assert that the old epoch can no longer authenticate and the new Session can; the same test MUST assert that other client types remain valid. | Architecture Baseline v1.0, chapters 4.1, 7.2, and 7.3, and appendix B (Session). |
| AUF-A-002 | Given an unauthenticated WSS connection, the negative fixture runner MUST reject every operation other than auth.bind and ping/pong; after valid binding it MUST assert the authenticated state is bound to user, Session, and client type. | Architecture Baseline v1.0, chapter 7.2. |
| AUF-A-003 | Given an active same-slot connection, when a replacement login commits, the fixture runner MUST observe session.revoked followed by closure and MUST reject reconnect with the old token. | Architecture Baseline v1.0, chapters 7.2 and 7.3. |
| AUF-A-004 | Given users A and B, adding A-to-B and then B-to-A MUST converge to one normalized friendship and one DIRECT Conversation; fixtures MUST reject a second distinct relationship for the same unordered pair. | Architecture Baseline v1.0, chapter 4.2 and appendix B (Friend). |
| AUF-A-005 | The friend-add contract fixture MUST demonstrate immediate bidirectional success and MUST NOT expose a pending approval state. | Architecture Baseline v1.0, chapter 4.2. |
| AUF-A-006 | Logout fixtures MUST assert Session and Refresh Token revocation plus WSS closure, while making no assertion that local client history is deleted. | Architecture Baseline v1.0, chapter 7.1. |
| AUF-A-007 | Security fixtures MUST reject tokens in URL query input and MUST assert that responses and captured structured logs contain no token or password material. | Architecture Baseline v1.0, chapter 7.4. |
| AUF-A-008 | Both backend profiles MUST run the same positive and negative fixtures and normalize to the same observable auth, friendship, error, and transaction outcomes. | Architecture Baseline v1.0, chapter 11.2 and chapter 11.3. |

## Current implementation acceptance overlay

Source labels above preserve original S0 semantic input provenance, not selection of an old active baseline. Current implementation resolves/hash-checks spec/architecture/README.md/baseline.md and applies canonical §3/§10 SRC-01 through SRC-07/§11 plus spec/governance/execution-boundaries.md. Unchanged behavioral cases require applicable source ownership/import checks and fresh Review using spec/governance/independent-review.md. allowed_paths and behavioral parity never waive structure.

Stage-three effective checkers are bounded accepted at2afeac8/run36726926394; execute ci/check_architecture.py --scope all --json and tests/architecture with evidence003/hosted-acceptance.md. Go remediation product candidate d0ae52f5615320790ae7039cb48831873de6f486 is independently reviewed and accepted by hosted run36744072690; evidence004/final-hosted-acceptance.md. Historical stage003 source_go/Gate FAIL was expected before migration and remains preserved. Applicable source/dependency checks remain mandatory; no grandfather exception. Administrative closure candidate still requires a new independent Review and exact-head hosted verification; S1 product Gate remains OPEN. No follow-on business is activated by this discovery update. Check each backend stage: Java placeholder now and full Java boundaries at first business implementation. Record actual integration enable conditions/services/skips; unexecuted integration is not PASS. Verify hosted head/required jobs; historical S0/Auth acceptance does not cover new rules.

## Human-approved Loop1 exception: friend403

ADR-0004-loop1-friend-403-exception.md and contracts/fixtures/auth-user-friend/loop1-exceptions.json exempt only friend-add-authorization-denied from Loop1 implementation/runtime acceptance. OpenAPI403 placeholder and full future golden expectation remain unchanged. Report DEFERRED_BY_HUMAN separately; never count it PASS or claim every canonical case executed. AUF-A-008 profile equivalence applies to required stage cases; all other applicable checks remain required. FRIEND-AUTHORIZATION-403 remains a later-iteration TODO requiring approved credential/permission context, exact403/noeffects tests and fresh independent Review/CI. This scope decision does not waive401/422, membership/plugin authorization or transaction invariants.

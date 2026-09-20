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

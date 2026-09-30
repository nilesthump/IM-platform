# S0 Messaging Contract Checks

These checks are executable requirements for the future canonical contract runner. They define observable cases and assertions, not wire fields, classes, or storage schema.

| Rule ID | Executable contract check | Source |
| --- | --- | --- |
| MSG-A-001 | Given an authorized member send, the runner MUST withhold success ACK until a fault-injection probe confirms durable Message and Outbox commit; rollback before commit MUST produce no success ACK. | Architecture Baseline v1.0, chapters 2 (F-04) and 5.1, and appendix B (Message). |
| MSG-A-002 | Given repeated sends with the same sender, Conversation, and client request identity, the runner MUST assert one logical Message, one Conversation sequence, and a stable successful outcome. | Architecture Baseline v1.0, chapters 4.4, 5.1, and 11.3. |
| MSG-A-003 | Given the same client request identity in different Conversations, the runner MUST treat each Conversation-scoped request independently while preserving globally unique server Message identity. | Architecture Baseline v1.0, chapter 4.4. |
| MSG-A-004 | Given a sender who is not a Conversation member, the negative fixture MUST assert rejection, no Message, no Outbox event, and no success ACK. | Architecture Baseline v1.0, chapter 5.1. |
| MSG-A-005 | Given duplicate and out-of-order NATS delivery, the runner MUST assert idempotent consumer behavior, no duplicate logical Message, and eventual completeness through Sync. | Architecture Baseline v1.0, chapter 5.2 and appendix B (Outbox). |
| MSG-A-006 | Given a GROUP send, the runner MUST assert one logical Message and one Outbox event regardless of member count, with local online fan-out treated separately from persistence. | Architecture Baseline v1.0, chapter 5.3. |
| MSG-A-007 | Correctness fixtures MUST assert zero lost committed Messages, zero duplicate logical Messages, zero wrong-Conversation deliveries, zero permanent sequence gaps, and zero ACK-before-commit cases. | Architecture Baseline v1.0, chapter 5.3 (message correctness red lines). |
| MSG-A-008 | Both backend profiles MUST consume identical fixtures and normalize to the same ACK, idempotency, authorization, ordering, error, and transaction outcomes. | Architecture Baseline v1.0, chapter 11.2 and chapter 11.3. |

## Current implementation acceptance overlay

Source labels above preserve original S0 semantic input provenance, not selection of an old active baseline. Current implementation resolves/hash-checks spec/architecture/README.md/baseline.md and applies canonical §3/§10 SRC-01 through SRC-07/§11 plus spec/governance/execution-boundaries.md. Unchanged behavioral cases require applicable source ownership/import checks and fresh Review using spec/governance/independent-review.md. allowed_paths and behavioral parity never waive structure.

Stage-three effective checkers are bounded accepted at2afeac8/run36726926394; execute ci/check_architecture.py --scope all --json and tests/architecture with evidence003/hosted-acceptance.md. Go remediation product candidate d0ae52f5615320790ae7039cb48831873de6f486 is independently reviewed and accepted by hosted run36744072690; evidence004/final-hosted-acceptance.md. Historical stage003 source_go/Gate FAIL was expected before migration and remains preserved. Applicable source/dependency checks remain mandatory; no grandfather exception. Administrative closure candidate still requires a new independent Review and exact-head hosted verification; S1 product Gate remains OPEN. No follow-on business is activated by this discovery update. Check each backend stage: Java placeholder now and full Java boundaries at first business implementation. Record actual integration enable conditions/services/skips; unexecuted integration is not PASS. Verify hosted head/required jobs; historical S0/Auth acceptance does not cover new rules.

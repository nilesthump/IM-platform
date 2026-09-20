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

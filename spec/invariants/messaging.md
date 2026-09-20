# Messaging Invariants

These invariants constrain future contracts without prescribing wire shape or persistence schema. Machine-verifiable public authority remains exclusively under `contracts/`.

| Rule ID | Invariant | Source |
| --- | --- | --- |
| MSG-I-001 | Repeating a send with the same server idempotency identity MUST converge on the same logical Message and MUST NOT allocate another Conversation sequence. | Architecture Baseline v1.0, chapters 4.4 and 5.1. |
| MSG-I-002 | A successful message ACK MUST NOT be observable before the Message and matching Outbox event are durably committed. | Architecture Baseline v1.0, chapters 2 (F-04) and 5.1, and appendix B (Message). |
| MSG-I-003 | Every committed logical Message MUST have exactly one logical Outbox event, even when publication delivery is retried. | Architecture Baseline v1.0, chapters 4 (Figure 4-1), 5.1, and 5.2. |
| MSG-I-004 | No recipient MUST receive a Message for the wrong Conversation, and no permanent sequence gap may remain after Sync convergence. | Architecture Baseline v1.0, chapter 5.3 (message correctness red lines). |
| MSG-I-005 | Duplicate NATS delivery MUST NOT create a duplicate logical Message or duplicate client materialization. | Architecture Baseline v1.0, chapter 5.2 and appendix B (Outbox). |
| MSG-I-006 | A send by a non-member MUST be rejected before persistence and before a success ACK. | Architecture Baseline v1.0, chapter 5.1. |
| MSG-I-007 | GROUP fan-out MUST remain an online delivery concern and MUST NOT alter the single-Message, single-Outbox persistence outcome. | Architecture Baseline v1.0, chapter 5.3. |

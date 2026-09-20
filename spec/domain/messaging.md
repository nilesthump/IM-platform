# Messaging Domain Input

This document supplies semantic input to `LOOP1-CONTRACT-002`. Names used below identify domain concepts only; they do not define public wire fields, implementation classes, or database tables.

| Rule ID | Domain statement | Source |
| --- | --- | --- |
| MSG-D-001 | A client request identity MUST be unique within a Conversation and is the identity reused by retry and local convergence. | Architecture Baseline v1.0, chapter 4.4. |
| MSG-D-002 | The server idempotency identity MUST include sender, Conversation, and client request identity; the server message identity MUST be globally unique. | Architecture Baseline v1.0, chapter 4.4 and appendix B (Message). |
| MSG-D-003 | Conversation sequence numbers MUST be unique and monotonically increasing within each Conversation. | Architecture Baseline v1.0, chapter 4.4 and appendix B (Message). |
| MSG-D-004 | Message send MUST authorize the sender as a Conversation member before persistence. | Architecture Baseline v1.0, chapter 5.1. |
| MSG-D-005 | Sequence allocation, Message persistence, and the matching Outbox event MUST commit atomically; a successful ACK MUST mean that durable commit has completed. | Architecture Baseline v1.0, chapters 2 (F-04) and 5.1, and appendix B (Message, Outbox). |
| MSG-D-006 | Outbox delivery and NATS delivery MAY repeat or be briefly missed; consumers MUST be idempotent and Sync MUST provide eventual completeness. | Architecture Baseline v1.0, chapter 5.2 and appendix B (Outbox). |
| MSG-D-007 | Gateway MUST fan out only to locally active connections and MUST NOT own friendship, membership, persistence, or plugin business rules. | Architecture Baseline v1.0, chapters 2 (F-05) and 5.2. |
| MSG-D-008 | A GROUP send MUST create one logical Message and one Outbox event; it MUST NOT create one persistent message record per member. | Architecture Baseline v1.0, chapter 5.3. |
| MSG-D-009 | Loop 1 MUST NOT treat NATS JetStream as the message source of truth. | Architecture Baseline v1.0, chapters 2 (F-03) and 5.2. |

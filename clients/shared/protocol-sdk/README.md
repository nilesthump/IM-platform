# Shared storage Repository

Current scope: Desktop TypeScript models, per-account SQLite schema/migrations and transaction intents. Canonical authority is contracts/ plus Frozen Architecture §6 and accepted ADR-0005. Network orchestration and plugin runtime are later tasks.

Repository accepts local send, committed ACK, realtime payload and Sync messages. Realtime payload has no original send requestId under the canonical envelope; its temporary row has a NULL request_id. ACK/Sync atomically merge it with the matching local row after verifying sender/content and every durable identity. Conflicting data rejects and rolls back; SENT is terminal. Request identity is scoped to conversation, server identity is global within the account database, and sequence identity is scoped to conversation.

Statement tuples are private adapter instructions, not a public wire contract. Every intent is one real native transaction including row-count assertions, data materialization and contiguous/cursor changes. User cursor comparisons are opaque string equality against the caller's expected previous cursor; revisions cannot regress. Message events never enter user cursor materialization. No Repository/schema/business logic lives in Rust.

Build: npm --prefix clients/shared/protocol-sdk ci --ignore-scripts; npm --prefix clients/shared/protocol-sdk run build.
Actual behavior: python -B tools/verify_client_sqlite.py --scope desktop.
The shared job compiles TypeScript; Desktop and Android jobs execute the same canonical storage fixtures. Host mocks cannot establish Android acceptance.

Internal schema v1 is a retained migration test fixture, not a previously released client. v2 adds user materialization/cursor in one transaction. tests/clients/sqlite/v1.sql is the independent old-layout fixture; do not silently regenerate it when changing the current schema. Unsupported schema versions fail without destructive fallback.

Sequence/revision inputs use safe `number` or exact built-in `bigint`; larger integers require `bigint` to avoid already-rounded JS values. SQLite adapter binds decimal strings and `contiguous()` returns `bigint`. Current signed64 SQLite capacity is checked locally; this does not add a public protocol maximum or implement a wire parser. Native Rust receives only string parameters, no BigInt serialization change.

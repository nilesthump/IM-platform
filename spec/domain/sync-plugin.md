# Sync and Plugin Domain Input

This document supplies semantic input to `LOOP1-CONTRACT-003`. Names used below identify domain concepts only; they do not define public wire fields, implementation classes, or database tables.

| Rule ID | Domain statement | Source |
| --- | --- | --- |
| SP-D-001 | Web MUST remain memory-only and MUST NOT claim offline history; Desktop and Mobile MUST use per-account local materialized views and render local state before background Sync. | Architecture Baseline v1.0, chapters 2 (F-07) and 6.1, and appendix B (Web). |
| SP-D-002 | A local optimistic send MUST create one client request identity, persist SENDING before transmission, converge to SENT after ACK, and reuse the same request identity when retrying FAILED. | Architecture Baseline v1.0, chapter 6.2. |
| SP-D-003 | SENT MUST be terminal and MUST NOT regress to FAILED; FAILED means only that the current attempt lacks success confirmation. | Architecture Baseline v1.0, chapter 6.2 and appendix B (SQLite). |
| SP-D-004 | User Sync cursor MUST cover only low-frequency user-level state; message state MUST use per-Conversation sequence and contiguous sequence tracking. | Architecture Baseline v1.0, chapters 2 (F-06) and 6.4, and appendix B (Sync). |
| SP-D-005 | Sync MUST advance a per-Conversation contiguous sequence only across a gap-free prefix; duplicate and out-of-order input MUST converge without skipping a gap. | Architecture Baseline v1.0, chapter 6.4 and appendix B (Sync). |
| SP-D-006 | All local send, ACK, realtime, and Sync write paths MUST converge through transactional upsert; data and cursor advancement MUST commit together. | Architecture Baseline v1.0, chapter 6.3. |
| SP-D-007 | Plugin API v1 MUST expose Events, Queries, Actions, and UI Host surfaces, each constrained by declared capability and permission. | Architecture Baseline v1.0, chapters 2 (F-08) and 8.1. |
| SP-D-008 | Queries MUST be read-only, paginated, and limited; Actions MUST be re-authorized, rate-limited, and audited; plugins MUST NOT call Core internals or databases directly. | Architecture Baseline v1.0, chapter 8.1. |
| SP-D-009 | A custom renderer MUST pass package hash, signature, manifest-schema, API-compatibility, permission, resource-size, CSP, and import checks before loading, and MUST run in the stated UI sandbox. | Architecture Baseline v1.0, chapter 8.2. |
| SP-D-010 | A plugin artifact identified by plugin and version MUST be immutable; backend and renderer MUST remain version-bound, and history MUST retain the renderer needed by referenced messages plus fallback text. | Architecture Baseline v1.0, chapter 8.2 and appendix B (Plugin). |
| SP-D-011 | WASM execution MUST default-deny database, server-file, arbitrary-network, and other-plugin-memory access and MUST enforce CPU/time, memory, concurrency, storage, and network limits. | Architecture Baseline v1.0, chapter 8.3 and appendix B (Plugin). |
| SP-D-012 | Plugin artifact lifecycle and Conversation-scoped instance lifecycle MUST remain distinct; upgrade MUST keep the old version serving until snapshot, migration, paired health checks, and atomic switch succeed, and MUST roll back on failure. | Architecture Baseline v1.0, chapters 9.1 and 9.2. |
| SP-D-013 | DISABLE MUST preserve data, UNINSTALL MUST default to RETAINED, and PURGE MUST require an explicit irreversible operation with elevated permission, audit, and a confirmed retention policy. | Architecture Baseline v1.0, chapter 9.3. |


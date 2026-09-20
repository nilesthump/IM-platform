# Sync and Plugin Invariants

These invariants constrain future contracts without prescribing wire shape or persistence schema. Machine-verifiable public authority remains exclusively under `contracts/`.

| Rule ID | Invariant | Source |
| --- | --- | --- |
| SP-I-001 | Duplicate or out-of-order Sync input MUST be idempotent, and contiguous sequence MUST NOT advance across a missing sequence. | Architecture Baseline v1.0, chapters 6.3 and 6.4, and appendix B (Sync). |
| SP-I-002 | When Sync observes a server Message matching a locally FAILED send identity, it MUST converge that local item to SENT rather than create another item. | Architecture Baseline v1.0, chapter 6.2. |
| SP-I-003 | Local materialized data and its corresponding cursor or contiguous-sequence advance MUST commit atomically. | Architecture Baseline v1.0, chapter 6.3. |
| SP-I-004 | User-level cursor input MUST NOT contain Message events. | Architecture Baseline v1.0, chapter 6.4. |
| SP-I-005 | Plugin capability or permission denial MUST prevent the Event subscription, Query, Action, or UI behavior without granting an alternate direct access path. | Architecture Baseline v1.0, chapters 2 (F-08) and 8.1. |
| SP-I-006 | Query operations MUST NOT mutate state; Action authorization and rate limits MUST be reevaluated at execution and the Action MUST be auditable. | Architecture Baseline v1.0, chapter 8.1. |
| SP-I-007 | A changed package, backend, or renderer hash under an existing plugin version MUST be rejected. | Architecture Baseline v1.0, chapter 8.2 and appendix B (Plugin). |
| SP-I-008 | WASM and custom-renderer execution MUST remain sandboxed with least privilege and MUST NOT directly reach host-sensitive resources. | Architecture Baseline v1.0, chapters 8.2 and 8.3, and appendix B (Plugin). |
| SP-I-009 | Upgrade MUST NOT split backend and renderer versions and MUST leave the previous version serviceable until atomic switch; any failed step MUST restore the snapshot and continue the old version. | Architecture Baseline v1.0, chapter 9.2. |
| SP-I-010 | DISABLE and UNINSTALL MUST NOT purge retained data; PURGE MUST NOT occur implicitly. | Architecture Baseline v1.0, chapter 9.3. |

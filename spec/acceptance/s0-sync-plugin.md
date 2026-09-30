# S0 Sync and Plugin Contract Checks

These checks are executable requirements for the future canonical contract runner. They define observable cases and assertions, not wire fields, classes, or storage schema.

| Rule ID | Executable contract check | Source |
| --- | --- | --- |
| SP-A-001 | Given duplicate and out-of-order per-Conversation inputs with a gap, the runner MUST assert idempotent materialization and that contiguous sequence stops before the gap; after the missing input arrives it MUST advance across the now-complete prefix. | Architecture Baseline v1.0, chapters 6.3 and 6.4, and appendix B (Sync). |
| SP-A-002 | Given a locally FAILED item and a matching server Message, the runner MUST assert convergence to SENT without an additional local item; SENT MUST remain terminal under later timeout input. | Architecture Baseline v1.0, chapter 6.2 and appendix B (SQLite). |
| SP-A-003 | Fault injection between local materialization and cursor advancement MUST roll back both effects; retry MUST converge by transactional upsert. | Architecture Baseline v1.0, chapter 6.3. |
| SP-A-004 | A user-cursor fixture containing a Message event MUST be rejected; low-frequency friend, Conversation, membership, and plugin state fixtures MUST advance only the user cursor. | Architecture Baseline v1.0, chapter 6.4. |
| SP-A-005 | Permission-negative fixtures MUST deny undeclared Event subscriptions, unauthorized Queries, unauthorized Actions, and unavailable UI capabilities, with no direct Core or database bypass. | Architecture Baseline v1.0, chapters 2 (F-08) and 8.1. |
| SP-A-006 | Query fixtures MUST assert read-only, paginated, limited behavior; Action fixtures MUST assert execution-time re-authorization, idempotent outcomes, and audit evidence. | Architecture Baseline v1.0, chapter 8.1. |
| SP-A-007 | Artifact fixtures MUST reject a changed package, backend, or renderer hash for an existing plugin/version identity and MUST reject backend-renderer version splitting. | Architecture Baseline v1.0, chapter 8.2 and appendix B (Plugin). |
| SP-A-008 | Renderer-negative fixtures MUST reject failures of hash, signature, manifest schema, API compatibility, permission, resource-size, CSP, or entry-point checks; runtime probes MUST verify the declared UI sandbox boundary. | Architecture Baseline v1.0, chapter 8.2. |
| SP-A-009 | WASM-negative fixtures MUST verify default denial of database, server-file, arbitrary-network, and other-plugin-memory access plus enforcement of resource limits and AUTO_DISABLED threshold behavior. | Architecture Baseline v1.0, chapter 8.3. |
| SP-A-010 | Upgrade fixtures MUST keep the old version serving until snapshot, migration, paired health checks, and atomic switch succeed; failure at each step MUST restore the snapshot and continue the old version. | Architecture Baseline v1.0, chapter 9.2. |
| SP-A-011 | Lifecycle fixtures MUST assert that DISABLE preserves data, UNINSTALL defaults to RETAINED, and PURGE requires an explicit elevated, audited, retention-confirmed operation. | Architecture Baseline v1.0, chapter 9.3. |
| SP-A-012 | Golden fixtures MUST include duplicate, out-of-order, gap, and permission-denial cases and MUST normalize to identical Sync and Plugin outcomes across both backend profiles. | Architecture Baseline v1.0, chapter 11.2 and chapter 11.3. |
| SP-A-013 | Given repeated execution of the same Action, the runner MUST assert one idempotent observable outcome with no duplicate side effect and MUST retain audit evidence for every execution attempt. | Architecture Baseline v1.0, chapter 8.1. |

## Current implementation acceptance overlay

Source labels above preserve original S0 semantic input provenance, not selection of an old active baseline. Current implementation resolves/hash-checks spec/architecture/README.md/baseline.md and applies canonical §3/§10 SRC-01 through SRC-07/§11 plus spec/governance/execution-boundaries.md. Unchanged behavioral cases require applicable source ownership/import checks and fresh Review using spec/governance/independent-review.md. allowed_paths and behavioral parity never waive structure.

Stage-three effective checkers are pending; bind independently accepted exact commands before business activation. Existing Go compliance is unproven until stage four. Check each backend stage: Java placeholder now and full Java boundaries at first business implementation. Record actual integration enable conditions/services/skips; unexecuted integration is not PASS. Verify hosted head/required jobs; historical S0/Auth acceptance does not cover new rules.

---
batch_id: LOOP1-S1
loop: Loop 1
stage: S1
execution: dependency-driven
writer_concurrency: 1
independent_review_required: true
ci_acceptance_required: true
---

# LOOP1-S1 Execution Manifest

S0 Gate PASS and LOOP1-ARCH-REMEDIATION final batch PASS are current entry conditions. Historical Auth remains valid under old checks; Social/Message/E2E stay suspended until remediation finishes. Execute these architecture-listed tasks in dependency order:

1. `LOOP1-GO-AUTH-001`
2. `LOOP1-GO-SOCIAL-001`
3. `LOOP1-GO-MSG-001`
4. `LOOP1-E2E-001`

Each task enters `ready` only after its listed dependencies and inputs are present, then `active` in a single writer context. A fresh independent reviewer and applicable real CI are required before `done`.

The S1 Gate passes only when the Go Auth -> Friend -> Direct -> Message chain works through the real TLS entrypoint with durable ACK, Outbox and NATS; contract, integration and end-to-end checks pass; all four tasks are `done`; recovery state and a stable checkpoint are current. S2 stays inactive until then.

Business tasks read canonical §3/§10 SRC-01 through SRC-07/§11 and the execution/review guides, narrow paths by responsibility and require accepted source/import checks alongside behavior. Future Java task creation follows canonical §20 and TASK_TEMPLATE.md, never Go layout.

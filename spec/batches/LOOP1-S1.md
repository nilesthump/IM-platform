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

S0 Gate PASS is the entry condition. Execute these architecture-listed tasks in dependency order:

1. `LOOP1-GO-AUTH-001`
2. `LOOP1-GO-SOCIAL-001`
3. `LOOP1-GO-MSG-001`
4. `LOOP1-E2E-001`

Each task enters `ready` only after its listed dependencies and inputs are present, then `active` in a single writer context. A fresh independent reviewer and applicable real CI are required before `done`.

The S1 Gate passes only when the Go Auth -> Friend -> Direct -> Message chain works through the real TLS entrypoint with durable ACK, Outbox and NATS; contract, integration and end-to-end checks pass; all four tasks are `done`; recovery state and a stable checkpoint are current. S2 stays inactive until then.

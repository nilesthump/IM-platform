---
batch_id: LOOP1-S0
loop: Loop 1
stage: S0
execution: dependency-driven
writer_concurrency: 1
independent_review_required: true
bootstrap_ci_exception: active until LOOP1-CI-001 is DONE
---

# LOOP1-S0 Execution Manifest

## Required Tasks

Dependency order, not filename order, controls execution:

1. `LOOP1-CTRL-001`
2. `LOOP1-CTRL-002`
3. `LOOP1-SPEC-001`
4. `LOOP1-CONTRACT-001`
5. `LOOP1-CONTRACT-002`
6. `LOOP1-CONTRACT-003`
7. `LOOP1-DB-001`
8. `LOOP1-INFRA-001`
9. `LOOP1-CI-001`

`LOOP1-SPEC-001` is the minimum missing producer for repository-native domain, invariant, and acceptance inputs required by the three Contract tasks. It may materialize only already-approved Frozen Architecture semantics.

## Completion

The batch completes only when every required task is `done`, the actual S0 Gate Checklist passes, no blocker remains, `spec/progress/current.md` is current, a Last Known Good Commit and stable checkpoint exist, the Frozen Architecture resolves from the repository index and verified manifest, and real CI is operational. Task filenames or local self-reported PASS results do not establish Stage PASS. S1 must not activate during this batch.

## Current historical status

Original bootstrap condition above is retained as history. LOOP1-CI-001 is operational and done, so ADR-0001 is expired and cannot substitute current hosted acceptance. Preserve historical S0 PASS; current remediation/later applicable tasks use exact-head hosted CI and fresh Review. S1 business waits for remediation batch PASS.

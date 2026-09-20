---
task_id: LOOP1-SPEC-001
title: Materialize S0 domain, invariant, and acceptance inputs
status: active
owner: loop1-spec-implementation-agent
stage: S0
gate: S0
---

# Goal

Materialize the minimum repository-native domain, invariant, and executable acceptance inputs required before the three S0 Contract tasks, strictly from already-approved Frozen Architecture semantics.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4 through 9, 11, 19 and appendices A-B, resolved through `spec/architecture/README.md`.
- Approved ADRs in `spec/architecture/decisions/`.
- `spec/batches/LOOP1-S0.md`.

# Dependencies

- LOOP1-CTRL-002 done.

# Allowed Paths

- `spec/domain/**`
- `spec/invariants/**`
- `spec/acceptance/**`
- `spec/tasks/**/LOOP1-SPEC-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-SPEC-001/**`

# Acceptance

- Repository-native inputs exist for Auth/User/Friend, Messaging, and Sync/Plugin in each of `spec/domain/`, `spec/invariants/`, and `spec/acceptance/`.
- Each statement is traceable to the Frozen Architecture or an approved ADR and introduces no new semantics.
- Acceptance documents define executable S0 contract checks without selecting implementation-language classes or concrete database tables.

# Forbidden

- Invent or change architecture, public contract semantics, ACK/security/compatibility rules, persistence truth, or plugin sandbox rules.
- Define implementation-specific classes or prematurely define the canonical database schema.
- Implement product behavior or machine-verifiable public contracts.

# Verification

- While editing, run `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`; run `& .\tools\verify-loop1-ctrl-002.ps1` only from a clean committed review checkout.
- Run `& .\spec\acceptance\verify-s0-spec-materialization.ps1`; it deterministically requires all nine area/layer inputs, unique rule identifiers, a normative keyword and exact baseline citation on every rule, and absence of implementation/schema leakage patterns.

# Evidence

- Dependency `LOOP1-CTRL-002` was independently accepted at `d86bf1727b46b6b4f782d1ec7ad156ba35d8b2e7` under ADR-0001 and moved to `done`.
- Required inputs resolve through `spec/architecture/README.md`, the verified baseline manifest and immutable PDF, approved `ADR-0001`, and `spec/batches/LOOP1-S0.md`.
- Baseline SHA-256 was revalidated as `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` before activation.
- Baseline development verification on `main` passed: `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`, exit `0`, elapsed `453.618 ms`.
- S0 remains NOT YET PASSED.

# Handoff

- Activated on `task/LOOP1-SPEC-001` by fresh Implementation Agent `/root/spec001_impl`; repository-native specification work is in progress.
- Activation transition changes are owned by `loop1-spec-implementation-agent`. Last known good accepted commit: `d86bf1727b46b6b4f782d1ec7ad156ba35d8b2e7`. Latest accepted checkpoint: `spec/progress/checkpoints/2026-09-20-loop1-ctrl-002-accepted.md`. Architecture conflict: none.

# Next Action

- Read the exact Frozen Architecture inputs and materialize the minimum domain, invariant, acceptance, and deterministic traceability verification artifacts within `allowed_paths`.

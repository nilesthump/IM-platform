---
task_id: LOOP1-SPEC-001
title: Materialize S0 domain, invariant, and acceptance inputs
status: backlog
owner: unassigned
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

- Run the repository control-plane verifier in development mode while editing and acceptance mode only from a clean committed review checkout.
- Run a traceability check that every materialized rule cites the baseline chapter or approved ADR source.

# Evidence

- Pending.

# Handoff

- Created as the minimum missing S0 producer during architect-authorized CTRL-002 dependency repair; no domain or contract semantics were materialized by CTRL-002.

# Next Action

- Promote only after LOOP1-CTRL-002 is independently accepted and moved to `done`.

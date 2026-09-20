---
task_id: LOOP1-SPEC-001
title: Materialize S0 domain, invariant, and acceptance inputs
status: review
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
- Implementation content commit: `8dbe190e2137833fca9dfda3e54e3530a75f2f0e`.
- Clean implementation verification: `& .\spec\acceptance\verify-s0-spec-materialization.ps1`, exit `0`, elapsed `108.4403 ms`; 9 files and 83 unique, cited rules verified.
- Clean recovery verification: `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`, exit `0`, elapsed `367.5828 ms`; explicitly development evidence, not acceptance.
- Durable development evidence: `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-development-8dbe190-pass.md`.
- Fresh independent Review Agent `/root/spec001_review2` reviewed `74134bd306cbf0a1546f500bc46c45a1217b2d58` from a clean detached isolated worktree and returned FAIL. Permanent evidence: `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-independent-review-74134bd-fail.md`.
- The FAIL identified invented Plugin Action rate limiting, missing Action idempotency/repeated-Action coverage, `import checks` instead of chapter 8.2 `entry-point checks`, and EOF whitespace in all three domain plus all three acceptance inputs.
- Fresh Fix Agent `/root/spec001_fix` repaired those findings at content commit `10aaba0750bc38031589fc2821c6b6cec567a7e6`: chapter 8.1 Action semantics are now re-authorization, idempotency, and audit; `SP-A-013` checks repeated-Action idempotent convergence without defining wire fields; Renderer validation uses `entry-point checks`; and all reported EOF whitespace is removed.
- Fix verification: `& .\spec\acceptance\verify-s0-spec-materialization.ps1`, exit `0`, elapsed `128.4595 ms`; 9 files and 84 unique cited rules verified.
- Recovery verification: `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`, exit `0`, elapsed `465.0543 ms`; explicitly non-acceptance development output.
- Whitespace verification: `git diff --check e324e74b028ecb08f019ab2dccc2c377ea72f7d6`, exit `0`, elapsed `42.7957 ms`.
- Durable fix evidence: `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-fix-development-10aaba0-pass.md`.
- Fresh independent Review Agent `/root/spec001_review3` reviewed `85069032c137cce6e526e0e329b6e93178515274` from a clean detached disposable clone and returned FAIL because changing chapter 8.2 `entry-point checks` to `import checks` still passed the verifier; all other review areas passed.
- Permanent review evidence: `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-independent-review-8506903-fail.md`.
- Fresh Fix Agent `/root/spec001_fix2` strengthened the verifier at content commit `3cecd6ffd1dbfdeb57adee53b8aef60597f7aeb0`: `SP-D-009` and `SP-A-008` are now checked by exact rule ID and required renderer-validation semantics, `import checks` are explicitly rejected, and all prior Action guards remain in force.
- Fix verification on clean content commit `3cecd6ffd1dbfdeb57adee53b8aef60597f7aeb0`: materialization verifier PASS, exit `0`, elapsed `141.9375 ms`; CTRL-002 Development PASS, exit `0`, elapsed `487.6677 ms`; baseline diff check PASS, exit `0`, elapsed `45.6821 ms`.
- Regression mutations of `SP-D-009` and `SP-A-008` from `entry-point checks` to `import checks` were independently rejected with exit `1`; the Action-to-rate-limiting mutation also remained rejected with exit `1`.
- Durable fix evidence: `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-fix-development-3cecd6f-pass.md`.
- S0 remains NOT YET PASSED.

# Handoff

- Fresh Implementation Agent `/root/spec001_impl` materialized the original inputs; fresh Fix Agents `/root/spec001_fix` and `/root/spec001_fix2` repaired successive independent review findings. None has self-accepted the task.
- The task remains in `review` and is ready for a new fresh independent Review Agent under ADR-0001. Last known good accepted commit remains `e324e74b028ecb08f019ab2dccc2c377ea72f7d6`; latest accepted checkpoint remains `spec/progress/checkpoints/2026-09-20-loop1-ctrl-002-accepted.md`. Architecture conflict: none.

# Next Action

- Delegate a new fresh independent Review Agent to review the final committed `3cecd6ffd1dbfdeb57adee53b8aef60597f7aeb0` repair handoff from a clean isolated checkout, recheck both permanent FAIL findings, run `& .\spec\acceptance\verify-s0-spec-materialization.ps1`, `& .\tools\verify-loop1-ctrl-002.ps1`, the entry-point-to-import negative controls, and `git diff --check e324e74b028ecb08f019ab2dccc2c377ea72f7d6`, and record ADR-0001 evidence as PASS or FAIL.

# LOOP1-SPEC-001 Fix Development Evidence (`3cecd6f`)

- Fix Agent: `/root/spec001_fix2`; this agent is not an independent reviewer and cannot accept its own work
- Failed reviewed commit: `85069032c137cce6e526e0e329b6e93178515274`
- Fix content commit: `3cecd6ffd1dbfdeb57adee53b8aef60597f7aeb0`
- Baseline commit: `e324e74b028ecb08f019ab2dccc2c377ea72f7d6`
- Branch: `task/LOOP1-SPEC-001`
- Runtime: PowerShell `7.6.5` Core on Windows `10.0.26200.0`; Git `2.52.0.windows.1`
- Result: development verification PASS; this is not independent acceptance evidence

## Repair

- Preserved the permanent `/root/spec001_review3` FAIL record for `85069032c137cce6e526e0e329b6e93178515274`.
- Strengthened `spec/acceptance/verify-s0-spec-materialization.ps1` to locate `SP-D-009` and `SP-A-008` by exact rule identifier and require the chapter 8.2 renderer validation semantics, including entry-point validation and the UI sandbox boundary.
- Explicitly rejected `import checks` in Sync/Plugin materialization inputs.
- Preserved the existing Action re-authorization, idempotency, audit, repeated-execution, and invented-rate-limiting guards.

## Clean-Commit Positive Verification

1. Command: `& .\spec\acceptance\verify-s0-spec-materialization.ps1`
   - Exit code: `0`
   - Elapsed: `141.9375 ms`
   - Result: PASS; 9 files and 84 unique cited rules verified.
2. Command: `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`
   - Exit code: `0`
   - Elapsed: `487.6677 ms`
   - Result: PASS for task `LOOP1-SPEC-001` in `review`; explicitly non-acceptance development output.
3. Command: `git diff --check e324e74b028ecb08f019ab2dccc2c377ea72f7d6..3cecd6ffd1dbfdeb57adee53b8aef60597f7aeb0`
   - Exit code: `0`
   - Elapsed: `45.6821 ms`
   - Result: PASS.
4. Command: `git status --short --branch`
   - Result: clean `task/LOOP1-SPEC-001` branch at the content commit.

## Regression Negative Controls

Each mutation was applied only for the named run, checked with `pwsh -NoProfile -File .\spec\acceptance\verify-s0-spec-materialization.ps1`, and then restored before the content commit.

1. Changed `SP-D-009` from `entry-point checks` to `import checks`.
   - Exit code: `1`
   - Elapsed: `1905.1142 ms`
   - Result: expected rejection; the verifier reported the explicit import-check violation.
2. Changed `SP-A-008` from `entry-point checks` to `import checks`.
   - Exit code: `1`
   - Elapsed: `1885.7515 ms`
   - Result: expected rejection; the verifier reported the explicit import-check violation.
3. Replaced the `SP-D-008` Action re-authorization/idempotency/audit semantics with invented rate limiting.
   - Exit code: `1`
   - Elapsed: `1892.9639 ms`
   - Result: expected rejection; the pre-existing Action semantic guard remains effective.

## State

- Frozen Architecture PDF hash remains `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- No public contract, migration, product code, workflow, architecture decision, or frozen artifact changed.
- `LOOP1-SPEC-001` remains in `review`; S0 remains NOT YET PASSED.
- A new fresh independent Review Agent must review the final committed handoff from a clean isolated checkout under ADR-0001.

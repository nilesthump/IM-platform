# LOOP1-SPEC-001 Independent Review - FAIL (`8506903`)

- Reviewer: fresh independent Review Agent `/root/spec001_review3`; not the implementer or a fixer for the reviewed commit
- Reviewed commit: `85069032c137cce6e526e0e329b6e93178515274`
- Baseline commit: `e324e74b028ecb08f019ab2dccc2c377ea72f7d6`
- Source branch: `task/LOOP1-SPEC-001`
- Reviewed diff: `e324e74b028ecb08f019ab2dccc2c377ea72f7d6...85069032c137cce6e526e0e329b6e93178515274`
- Reviewed diff scope: 16 changed paths, all within the Task Spec's `allowed_paths`
- Isolated checkout: disposable clone at `H:\.codex\worktrees\spec001-independent-review-2\IM-platform`
- Clean-state method: detached checkout at the reviewed commit; porcelain was empty before and after review
- Runtime: PowerShell `7.6.5` Core on Windows `10.0.26200.0`; Git `2.52.0.windows.1`
- Final Git state: detached reviewed commit with empty porcelain output
- Result: **FAIL**; this permanent record is not acceptance evidence

## Positive Verification

1. Command: `& .\spec\acceptance\verify-s0-spec-materialization.ps1`
   - Exit code: `0`
   - Elapsed: `119.9111 ms`
   - Result: PASS; 9 files and 84 unique cited rules verified.
2. Command: `& .\tools\verify-loop1-ctrl-002.ps1`
   - Exit code: `0`
   - Elapsed: `400.7244 ms`
   - Result: PASS in default Acceptance mode from the clean detached checkout.
3. Command: `git diff --check e324e74b028ecb08f019ab2dccc2c377ea72f7d6..85069032c137cce6e526e0e329b6e93178515274`
   - Exit code: `0`
   - Elapsed: `38.5254 ms`
   - Result: PASS.

## Negative Controls

Each specification mutation was made only in a disposable clone and checked with `& .\spec\acceptance\verify-s0-spec-materialization.ps1`. The dirty-checkout control used `& .\tools\verify-loop1-ctrl-002.ps1` in default Acceptance mode.

1. Missing required file
   - Exit code: `1`
   - Elapsed: `372.3341 ms`
   - Result: expected rejection.
2. Rule without an exact baseline citation
   - Exit code: `1`
   - Elapsed: `340.4992 ms`
   - Result: expected rejection.
3. Duplicate rule identifier
   - Exit code: `1`
   - Elapsed: `335.1537 ms`
   - Result: expected rejection.
4. Added schema leakage
   - Exit code: `1`
   - Elapsed: `333.0298 ms`
   - Result: expected rejection.
5. Action idempotency replaced with invented rate limiting
   - Exit code: `1`
   - Elapsed: `334.1618 ms`
   - Result: expected rejection.
6. Dirty Acceptance checkout
   - Exit code: `1`
   - Elapsed: `774.7124 ms`
   - Result: expected rejection.
7. Chapter 8.2 `entry-point checks` changed to `import checks`
   - Exit code: `0`
   - Elapsed: `313.8304 ms`
   - Result: **unexpected PASS**; the verifier did not protect the required renderer validation semantics.

## Frozen Architecture Facts

- The sole tracked PDF was `scalable-distributed-im-architecture.pdf`; it was readable, unencrypted, contained 28 pages, and the relevant chapters and appendices were visually reviewed.
- SHA-256: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Git blob at HEAD and baseline: `17f7883b20dc75077f7491d2cb91049c9a53a75b`.
- The review checkout remained unchanged and the disposable clone and rendered pages were removed.

## Finding

1. **P1 - The verifier does not enforce the chapter 8.2 renderer entry-point validation semantics.** `spec/acceptance/verify-s0-spec-materialization.ps1` allowed `SP-D-009` to change from the required `entry-point checks` to `import checks` while still returning exit `0`. The verifier must deterministically require the chapter 8.2 entry-point-check semantics in both `SP-D-009` and `SP-A-008` and explicitly reject `import checks`.

All other review areas passed, including Action re-authorization/idempotency/audit semantics, the repeated-Action outcome, architecture fidelity, scope, whitespace, and clean-state acceptance recovery.

## Required Repair

Keep `LOOP1-SPEC-001` in `review` and S0 NOT YET PASSED. Strengthen only the allowed-path verifier, preserve Action checks, add and execute the entry-point-to-import regression mutation, run development verification, commit a clean fix handoff, and delegate a new fresh independent reviewer. The fixer must not self-accept.

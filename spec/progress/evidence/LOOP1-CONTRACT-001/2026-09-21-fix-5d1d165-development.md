# LOOP1-CONTRACT-001 OpenAPI Schema-Lint Fix - Development Evidence

## Identity and scope

- Task: `LOOP1-CONTRACT-001`
- Role: fresh Fix Agent `/root/contract001_schema_fix`; this is development evidence, not independent acceptance.
- Source independent FAIL closure: `95750c372fe47af169a87c2e62dcb16817eccf67`.
- Rejected candidate repaired: `12c566f71da9b038764ecb7a5303b116e77ca32f`.
- Fix candidate: `5d1d16561d7671ce54d6456741a51c21f5d3dadc`.
- Recorder prompt: `P-0b38bad2-5670-4d05-aa0d-17e855ad67d5`.
- Recorder run: `R-20260921T083334Z-f24d9caf-e49d-4678-a2d8-f05c6481190b`.
- Prospective trace start: `2026-09-21T08:33:34.262345Z`; `capture_mode=prospective`, `pre_recorder_work=false`, `pre_recorder_trace_complete=true`, `experiment_group=full_governance`.
- Parent review run: `R-20260921T080248Z-b5e568c3-afdd-4f81-8ef7-5c3d236e16f4`.

## Repair

- Added repository-contained JSON Schema `contracts/http/auth-user-friend.openapi.structure.schema.json` for deterministic OpenAPI 3.1 structural lint.
- Integrated the structural schema into `contracts/http/verify-auth-user-friend.ps1` before semantic and fixture checks.
- Added a built-in mutation regression that removes required `info.title` and fails unless schema lint rejects it.
- The canonical OpenAPI document, shared error schema, and all golden fixtures are byte-for-byte unchanged from the rejected candidate.
- No product implementation, WSS/Sync/Plugin contract, database migration, ACK behavior, frozen architecture, or compatibility rule changed.
- The paused Agent-owned untracked `contracts/http/schema-lint/` tree was not read, copied, modified, staged, claimed, or used.

## Recorded verification

All commands below were executed through Recorder run `R-20260921T083334Z-f24d9caf-e49d-4678-a2d8-f05c6481190b` after candidate commit `5d1d16561d7671ce54d6456741a51c21f5d3dadc`.

1. `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`
   - Recorder command: `C-faf3d82c-bfeb-43a2-9915-53e69f6374ae`
   - Exit `0`; `5858.7081 ms`; PASS.
   - Result: 9 paths, 9 operations, 15 error codes, 6 positive and 21 negative scenarios, Go/Java parity, OpenAPI 3.1 schema lint, and 7 mutation regressions.
2. Focused in-memory negative control: remove `info.title` and validate the mutated document against `contracts/http/auth-user-friend.openapi.structure.schema.json`.
   - Recorder command: `C-6637b1eb-5e49-4e6e-8aa7-7cf7fe0a47aa`
   - Exit `0`; `602.8583 ms`; PASS: the mutation was rejected.
3. `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`
   - Recorder command: `C-447d4671-6fa2-47b1-8207-a24fbe075a7d`
   - Exit `0`; `907.3632 ms`; PASS in explicitly non-acceptance Development mode.
4. Repair-only diff check, full candidate diff check excluding immutable Recorder raw patch payloads, public-contract/fixture unchanged check, and changed-path listing.
   - Recorder command: `C-0918ab2e-fe0a-41ad-bfad-0b6e38024603`
   - Exit `0`; `680.9781 ms`; PASS.
   - Repair scope is exactly the new structural schema and the modified verifier.
   - `contracts/http/auth-user-friend.openapi.json`, `contracts/errors/**`, and `contracts/fixtures/**` have no diff from `12c566f71da9b038764ecb7a5303b116e77ca32f`.

An earlier broad `git diff --check 12c566f..HEAD` in this run returned exit `2` only for already accepted trailing spaces inside immutable `research/runs/R-LOOP1-RESEARCH-001-BOOTSTRAP-PARTIAL/diff.patch`. The corrected checks retain that raw evidence file unchanged, exclude only `research/runs/**/diff.patch`, and pass; the repair-only range itself also passes without exclusions.

## Result and handoff

Development result: **PASS**. This Fix Agent does not accept its own work. `LOOP1-CONTRACT-001` remains in `review`; a new fresh independent Review Agent must review committed candidate `5d1d16561d7671ce54d6456741a51c21f5d3dadc` from a clean isolated checkout, rerun the verifier and governance acceptance mechanism, and repeat the missing-`info.title` negative control.

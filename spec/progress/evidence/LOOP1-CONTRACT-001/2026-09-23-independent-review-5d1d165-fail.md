# LOOP1-CONTRACT-001 Fresh Independent Review — FAIL

- Task: `LOOP1-CONTRACT-001`
- Result: **FAIL**
- Independent reviewer: `/root/contract001_schema_rereview`
- Reviewer independence: fresh review context; not the implementer or Fix Agent for the reviewed candidate
- Fix candidate: `5d1d16561d7671ce54d6456741a51c21f5d3dadc`
- Reviewed handoff closure: `9290139b918e76a0f0310b646ec7a9c6433c91a1`
- Baseline / reviewed diff range: `e5482b135a2ab7451c24c29c7517e1a8f19ce420...9290139b918e76a0f0310b646ec7a9c6433c91a1`
- Repository branch at delegation: `task/LOOP1-CONTRACT-001`
- Clean-state method: detached isolated Git worktree at `H:\.codex\worktrees\contract001-independent-review-schema-61a82ea3\IM-platform`
- Clean-state result: `git status --short --branch` returned only `## HEAD (no branch)` before and after verification; HEAD resolved to `9290139b918e76a0f0310b646ec7a9c6433c91a1`.
- Prior-agent isolation: the isolated checkout did not contain `contracts/http/schema-lint/`; the review did not read, copy, modify, claim, stage, or depend on the original untracked tree.
- Recorder prompt: `P-3031f02c-67f1-49c7-b890-295c85627dba`
- Recorder run: `R-20260921T085657Z-61a82ea3-f63b-4315-87b2-d090f3f48905`
- Prospective trace start: `2026-09-21T08:56:57.582531Z`
- Parent Fix run: `R-20260921T083334Z-f24d9caf-e49d-4678-a2d8-f05c6481190b`
- Recorder completion: finished with result `FAIL`, 71 events, final event hash `a439fc0d0626b6ef3d9f68db9ac188b2e545a2043dce698eaf0a941cfe632b68`, manifest hash `08419a0cee245fd87b24ab8b9ff548ddc85809968daf1886bf7ba9071ea2eb2c`
- Recorder validation: PASS; `validate-run` returned `status=finished`, `event_count=71`

## Authority and scope checks

- Frozen Architecture SHA-256 was independently recomputed as `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`, matching `spec/architecture/baseline.md`.
- Frozen Architecture chapters 2, 4, 7, 11, 19, and appendix B; ADR-0001; the Task Spec; and the referenced domain, invariant, and acceptance inputs were inspected.
- The fixed-point commit list, full three-dot name/status diff, and detailed schema/verifier repair diff were captured by Recorder.
- `git diff --exit-code 12c566f71da9b038764ecb7a5303b116e77ca32f..5d1d16561d7671ce54d6456741a51c21f5d3dadc -- contracts/http/auth-user-friend.openapi.json contracts/errors/http-errors.schema.json contracts/fixtures/auth-user-friend`
  - Exit `0`, elapsed `30.0828 ms`: canonical OpenAPI, shared errors, and all fixtures are unchanged by the schema-lint fix.
- `git diff --name-status 5d1d16561d7671ce54d6456741a51c21f5d3dadc^..5d1d16561d7671ce54d6456741a51c21f5d3dadc`
  - Exit `0`, elapsed `29.9384 ms`: the Fix commit adds only `contracts/http/auth-user-friend.openapi.structure.schema.json` and modifies only `contracts/http/verify-auth-user-friend.ps1`.
- `git diff --check e5482b135a2ab7451c24c29c7517e1a8f19ce420..HEAD -- . ':(exclude)research/runs/**'`
  - Exit `0`, elapsed `42.7535 ms`.
  - An earlier broader check excluding only `diff.patch` returned exit `2` solely for trailing whitespace preserved in a committed Recorder stdout blob; no product, contract, Task, or progress source was implicated.

## Verification

All commands below were executed through the accepted Recorder command wrapper.

1. `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`
   - Exit `0`, elapsed `5915.9704 ms`.
   - Output: `PASS: Auth/User/Friend contracts verified paths=9 operations=9 error_codes=15 positive=6 negative=21 profiles=go,java schema_lint=OpenAPI-3.1 mutation_regressions=7.`
2. `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance`
   - Exit `0`, elapsed `959.8039 ms`.
   - Output confirmed `task=LOOP1-CONTRACT-001 state=review`, five queues, ten Task Specs, detached HEAD, and zero status/diff entries.
3. Disposable missing-`info.title` control at candidate `5d1d16561d7671ce54d6456741a51c21f5d3dadc`
   - The disposable checkout changed only `contracts/http/auth-user-friend.openapi.json` by one deletion.
   - The contract verifier returned exit `1`, elapsed `638.5647 ms`, with `Required properties ["title"] are not present at '/info'`.
   - The invalid document was correctly rejected; the disposable worktree was then removed.
4. Broader in-memory OpenAPI structural negative controls
   - Command mutated no repository file.
   - Exit `1`, elapsed `623.0664 ms`, because the claimed structural schema unexpectedly accepted all three invalid shapes:
     - unknown top-level member: `True`;
     - unknown `Info` member: `True`;
     - scalar `42` used as the login `200` Response Object: `True`.

## Findings

### Spec axis — FAIL

**P1: The schema-lint acceptance requirement remains only partially implemented.**

`spec/tasks/review/LOOP1-CONTRACT-001.md` requires schema lint. The new `contracts/http/auth-user-friend.openapi.structure.schema.json` is a narrow bespoke subset: top-level and `Info` objects remain open, `components` is constrained only to an object, and operation `responses` is constrained only to a nonempty object without validating response keys or Response Objects. `contracts/http/verify-auth-user-friend.ps1` applies that subset and its committed structural regression tests only missing `info.title`. The independently recorded controls prove the lint can certify structurally invalid OpenAPI 3.1 documents. A complete repository-contained OpenAPI 3.1 schema/linter, or a materially complete equivalent with broader structural negative regressions, is required.

No additional canonical Auth/User/Friend semantic, error-code, fixture-completeness, or scope-creep defect was found. The canonical OpenAPI, errors, and fixtures are byte-identical to the previously reviewed repaired semantics.

### Standards axis — FAIL

1. The same incomplete structural lint is a hard standards violation against the Task acceptance and Frozen Architecture chapter 19 (`schema lint; positive/negative complete`).
2. The axis also identified a governance inconsistency: commit `9290139b918e76a0f0310b646ec7a9c6433c91a1` commits CONTRACT Fix-run artifacts under `research/prompts/**` and `research/runs/**`, while the Task Spec's hard `allowed_paths` does not list `research/**`. The repository-wide Recorder mandate requires those artifacts but states no explicit write-boundary exception. The next cycle must obtain an explicit path authorization or amend the Task boundary through the proper authority before committing further Task-linked Recorder artifacts.

## Decision and handoff

- Review result: **FAIL**.
- The successful normal verifier and missing-`info.title` regression do not override the broader structural negative-control failure.
- `LOOP1-CONTRACT-001` remains in `review`; it MUST NOT move to `done`.
- No accepted checkpoint was created.
- Next action: delegate a fresh Fix Agent to replace or materially complete the OpenAPI 3.1 structural lint and add broader invalid-structure regressions. Before that Fix run commits Recorder artifacts, resolve the `research/**` write-boundary inconsistency explicitly. After the fix, delegate a new fresh independent Review Agent.

## Instrumentation limitation

The first attempt to register the visible delegation prompt used `recorder.ps1 --stdin-base64`; PowerShell did not bind pipeline stdin and Recorder created an empty prompt artifact `P-6d2dcdca-d1e2-400f-b4d8-f180f46d8e23`. That artifact was not associated with this run and was not rewritten. The exact visible prompt was then registered successfully as `P-3031f02c-67f1-49c7-b890-295c85627dba`, and the limitation was recorded as an `instrumentation_warning`. Prospective capture from the successful `start-run` at `2026-09-21T08:56:57.582531Z` through `finish-run` is complete; no command/test result was reconstructed or backfilled.

# LOOP1-RESEARCH-001 Independent Review — FAIL

Date: 2026-09-21

## Review identity and isolation

- Reviewer: `/root/recorder_review`, a fresh independent Review Agent with no implementation or fix participation.
- Reviewed commit: `96fc13d5e953a8a926a9295dd82847789ed222fc`.
- Baseline and reviewed diff: `1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc..96fc13d5e953a8a926a9295dd82847789ed222fc`.
- Clean-state method: detached isolated worktree `H:\.codex\worktrees\research-recorder-review\IM-platform` checked out at the reviewed commit. `git status --short --branch` initially reported only `## HEAD (no branch)`.
- Review closure branch: `review/LOOP1-RESEARCH-001-fail`, created only after the clean-candidate review established FAIL.
- Frozen Architecture SHA-256 independently matched the manifest: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- ADR-0001 was the applicable temporary acceptance mechanism. Because the candidate failed, no Instrumentation Epoch or accepted checkpoint was created.

## Deterministic verification

1. Command:

   `& 'C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests/research -v`

   Result: exit `0`; 17 tests passed; unittest elapsed `12.078s`. The read-only sandbox initially prevented temporary-directory creation; the recorded result is the fresh rerun with isolated temporary writes permitted. The tests created only reviewer-owned `__pycache__` directories in the review worktree; those exact directories were removed before clean-checkout verification.

2. Command:

   `& .\tools\research\recorder.ps1 validate-repository`

   Result: exit `2`; FAIL in approximately `2.4s`:

   `R-LOOP1-RESEARCH-001-BOOTSTRAP-PARTIAL: finished run manifest hash mismatch`

3. Command, after removing only reviewer-generated `tests/research/__pycache__/` and `tools/research/__pycache__/` and re-confirming a clean worktree:

   `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance`

   Result: exit `0`; PASS in approximately `1.3s`; task `LOOP1-RESEARCH-001`, state `review`, five queues, ten task specs, zero status entries and zero diff lines.

4. Command:

   `git diff --check 1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc..HEAD -- . ':(exclude)research/runs/**/diff.patch'`

   Result: exit `0`; PASS in approximately `0.8s`.

5. Scope inspection:

   `git diff --name-status 1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc..96fc13d5e953a8a926a9295dd82847789ed222fc`

   Result: changes were confined to the Task Spec's allowed research and governance paths. No product implementation, contract, Frozen Architecture, domain, invariant, acceptance, ACK, plugin-boundary, or `.github/workflows/**` path changed. `LOOP1-CONTRACT-001` remained in `review` with owner `unassigned-independent-review-agent`; the original `H:\IM-platform` worktree and its untracked `contracts/http/schema-lint/` were not read, modified, moved, stashed, cleaned, or claimed.

## Blocking findings

### F1 — Committed finished run fails the repository's own integrity validator

The required default repository validation rejects the committed bootstrap run with `finished run manifest hash mismatch`. Thus the delivered repository is not self-validating, and the finished-run integrity/immutability acceptance criterion is not met even though the 17 isolated unit tests pass. The tests create fresh runs but do not validate the exact committed artifact.

### F2 — Secret-like values survive structured-event and quoted-prompt recording

The redaction implementation recursively visits values but does not treat sensitive dictionary keys as sensitive. A synthetic negative control using `password`, `api_key`, and `token` keys returned `changed=False` and retained each synthetic value. Real entry-point checks then showed:

- `record-event` exited `0` and stored all synthetic secret-like values in `events.jsonl`;
- `register-prompt` accepted `{"password":"SYNTHETIC_HUNTER2","api_key":"SYNTHETIC_API_VALUE","token":"SYNTHETIC_TOKEN_VALUE"}` as `prompt_capture=full`, `secret_redaction_applied=false`, and persisted the values verbatim.

This violates the Human Secret Handling requirement and requirement K. The positive test covers only unquoted `API_KEY=value` / `password=value` text and misses structured JSON/key-aware cases.

### F3 — CI ingestion accepts and persists unvalidated secret-bearing extra fields

A synthetic CI evidence object containing all required fields plus `password` and `raw_auth_headers` was accepted. `ingest-ci` copied those extra fields verbatim into a `ci_finished` event, including the synthetic secret-like values. The runtime checks only a required subset and result enum; the CI schema also does not prohibit additional properties, and the ingestion path does not redact the object. This violates Secret Handling and the requirement that CI ingestion be a constrained observation interface rather than an arbitrary durable payload sink.

### F4 — Committed prompt content hash does not match prompt metadata

For `P-LOOP1-RESEARCH-001-HUMAN-AUTH-V1`, the committed `prompt.txt` SHA-256 observed in the clean checkout was `8632aad762e1e6015b22af13f366550c765ecd4b42a77e69ebf5bc07c56f94f3`, while `metadata.json` records `ae27c414cddd31fb0a12659d93fc0f859fb0b87cd6fb213e7d76d6bee4c543a6`. The current `associated_run_id` cross-link is correctly `R-LOOP1-RESEARCH-001-BOOTSTRAP-PARTIAL`, but repository validation does not validate prompt hashes or prompt/run cross-references. Consequently the Prompt Registry does not currently provide stable, auditable content-addressing for the committed bootstrap prompt.

## Other observations

- The committed prompt and run metadata now cross-reference one another, and `system_prompt_capture` remains `unavailable`; no platform-internal prompt is claimed.
- A scan of committed bootstrap prompt/run blobs found no apparent real credential. The only secret-pattern match was the redaction regex source embedded in the archived diff.
- The bootstrap run is labeled `capture_mode=bootstrap_partial` and final metadata has `pre_recorder_trace_complete=false`. Raw event 1 contains the earlier contradictory `true`, followed by an append-only `instrumentation_warning`; the raw event was not rewritten.
- Backfills mark `collection_mode=retrospective_backfill`, `backfilled=true`, and unavailable facts as `unavailable`. The prospective-resume fixtures mark `pre_recorder_work=true` and incomplete prior trace.
- No CI PASS, reviewer independence, Human Decision, hidden chain-of-thought, token use, cost, or pre-Recorder trace was manufactured by this review.

## Verdict and next action

Verdict: **FAIL**. `LOOP1-RESEARCH-001` remains unfinished in `review`; Recorder schema version `1.0.0` is not accepted, no Instrumentation Epoch exists, and the paused product Agent must not resume under this Recorder candidate.

Next action: delegate a fresh Fix Agent to repair F1 through F4 within the existing allowed paths, add negative regression tests for structured secret keys, quoted JSON prompts, CI extra-field rejection/redaction, committed prompt hash/cross-link validation, and exact committed-run repository validation, then commit a new candidate and delegate a new fresh independent Review Agent.

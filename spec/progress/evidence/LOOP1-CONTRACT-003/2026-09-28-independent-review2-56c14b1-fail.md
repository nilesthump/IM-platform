# LOOP1-CONTRACT-003 independent review 2 — FAIL

- Reviewer: fresh `/root/contract003_review2`, independent of implementation, Fix 1, and Review 1. I changed no product contract or runtime file.
- Reviewed candidate: `56c14b18a3378ebaade1b4ad4fe85e26aa2f474b`; branch `task/LOOP1-CONTRACT-003`; accepted base `eb9ebea6dd6852acf80d7686d4592d1b98025ae4`; product/recovery diff range `eb9ebea..56c14b1`; Fix 1 range `09d3065..56c14b1`.
- Clean-state method: separate detached checkout `H:\.codex\worktrees\contract003-review2-accept\IM-platform` at exact candidate. `git status --short --branch` was only `## HEAD (no branch)` before and after CTRL-002 Acceptance, with zero changed or untracked paths. The assigned review worktree was clean at candidate before my task-linked prompt, probe, Recorder, and evidence writes.
- Result: **FAIL**. Task remains `review`; S0 Gate remains NOT YET PASSED. Seven Review 1 invalid mutations now reject, but two additional acceptance gaps remain.

## Findings

1. **[P1] SP-A-002 convergence starts from no observed FAILED state.** `failed-to-sent-terminal` asserts final `SENT`, but removing its initial `local.failed` step leaves the expected result unchanged. The remaining `sync.message` creates a SENT item, and the later `local.failed` checks only terminality. The fixture therefore cannot prove that a matching server Message converges an *existing locally FAILED item* to SENT. The independent probe accepts this invalid mutation. See `contracts/fixtures/sync-plugin/generate.py` case `failed-to-sent-terminal`, `contracts/plugin-api/verify.py` `local.failed`/`sync.message`, and `review2-negative-probe.py`.
2. **[P1] SP-A-006 Query pagination has no verifiable response.** `contracts/plugin-api/v1.schema.json` `$defs.Query` defines only the request (`pageSize`, `pageToken`) and no Query result/page, returned item limit, or next-page token. The `query-read-only-paginated` fixture checks `last=ALLOWED` and `sideEffects=0`; it observes no returned page. A simulated million-item response added to the fixture step leaves the expected result unchanged because the runner never models responses. The request cap and read-only denial are checked, but paginated, limited Query *outcomes* are not. This falls short of the Task's machine-verifiable Query contract and SP-A-006's paginated behavior assertion. See the schema, `contracts/plugin-api/verify.py` `plugin.call`, and the independent probe.

### SP-A-012 acceptance interpretation

`go.json` and `java.json` are distinct, complete, static normalized vector artifacts and the verifier rejects divergence from canonical expectations. They were initialized from those expectations; neither is a Go or Java backend-produced result. Frozen Architecture §11.3 describes fixture execution through Go and Java profiles with outputs A/B, while the Stage table places the contract freeze in S0 and dual-profile Golden Test PASS in S3; this Task forbids runtime implementation. Static vectors establish planned equal expected outcomes at S0, but cannot establish observed backend parity. The narrow unresolved decision is: **For this S0 Task, does SP-A-012 require only frozen, separately stored profile expected vectors, with backend-produced A/B evidence deferred to S3/S4, or actual profile execution now?** Neither static artifact should be described as backend conformance evidence. This ambiguity is separate from the two concrete FAIL findings.

## Checks

Commands used the bundled Python at `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` and were captured by review Recorder run `R-20260928T124947Z-fcdac40d-4b7d-406d-ba60-f61ae57ed4a8` unless specified. Elapsed times are Recorder `duration_ms`.

| Check | Exact command after Recorder `run-command --run-id R-20260928T124947Z-fcdac40d-4b7d-406d-ba60-f61ae57ed4a8 --` | Exit / elapsed | Result |
| --- | --- | --- | --- |
| Schema and fixtures | `python.exe contracts/plugin-api/verify.py` | 0 / 63 ms | Baseline PASS: 79 cases, 22 positive, 57 negative, SP-A-001..013 labels, 11 controls. |
| Permanent Review 1 probe | `python.exe spec/progress/evidence/LOOP1-CONTRACT-003/review1-negative-probe.py` | 0 / 62 ms | 0/7 invalid mutations accepted; prior findings repaired. |
| Independent Review 2 probe | `python.exe spec/progress/evidence/LOOP1-CONTRACT-003/review2-negative-probe.py` | 1 / 63 ms | Review FAIL: 2/2 invalid mutations accepted. Exit 1 is intentional for this negative audit. |
| Independent control-plane Acceptance | `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 / 1141 ms | PASS in the separate clean detached candidate checkout, with Recorder `--repo` pointing there and `--research-root` to the review worktree. |
| Candidate path scope | `git diff --name-only eb9ebea6dd6852acf80d7686d4592d1b98025ae4..56c14b18a3378ebaade1b4ad4fe85e26aa2f474b` | 0 / 47 ms | Task-owned contract, fixture, recovery, evidence, and Recorder paths only. |
| Fix product whitespace | `git diff --check 09d306596176212302efd2110d858a0247e20ed9..56c14b18a3378ebaade1b4ad4fe85e26aa2f474b -- contracts/plugin-api contracts/fixtures/sync-plugin` | 0 / 31 ms | PASS. |
| Fix Recorder integrity | `python.exe tools/research/recorder.py validate-run --run-id R-20260928T114841Z-4641b577-7645-4011-be22-1baaa30290e5` | 0 / 79 ms | Finished, 18 events; Recorder integrity only. |
| Frozen Architecture hashes | `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 / 750 ms | Markdown `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`; PDF `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`, matching manifest. |

Recorder prompt `P-820a014e-77e7-4d02-bd59-53719e9519dc` and run above are `prospective_resume`: startup inspection and the first direct baseline invocation preceded run start and are marked incomplete pre-Recorder trace. Research Recorder validation does not supply product acceptance. The original `H:\IM-platform\contracts\http\schema-lint` was untouched.

The review Recorder was finished with result `FAIL`; `validate-run` exited 0 and reported `status=finished`, `event_count=20`.

## Handoff

Keep task `review`. Delegate a fresh Fix Agent for the two concrete findings, then a different fresh reviewer. Resolve the SP-A-012 S0 interpretation before PASS. No product file was changed in this review. The detached Acceptance checkout remains clean at candidate.

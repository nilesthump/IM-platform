# LOOP1-CI-001 independent Review 2: FAIL

- Reviewer: fresh `/root/ci001_review2`, independent of Implementation `/root/ci001_impl`, Fix 1 `/root/ci001_fix1`, Review 1 `/root/ci001_review1`, and Coordinator `/root`. No CI product code was edited or self-accepted.
- Reviewed exact candidate: `f508750e9a0da6a9f449ec2cc202077fdb8bb135` on `task/LOOP1-CI-001`; marker fix `ba0bbe7`; product diff range `10406be70bf66482836164400cd5b8be07709c58..f508750e9a0da6a9f449ec2cc202077fdb8bb135`.
- Clean-state method: new detached checkout `H:\.codex\worktrees\ci001-review2-clean` at exact candidate. Before and after verification, `git status --short --branch` showed only `## HEAD (no branch)`; `git rev-parse HEAD` matched the candidate. Python bytecode generation was disabled and no cleanup was needed. The Review 1 blocker is repaired: `spec/tasks/backlog/.gitkeep` is tracked and CTRL-002 Acceptance sees all five queues.
- Prompt `P-94e1e917-f50e-4ffa-9226-3b223b018982`; review Recorder `R-20260928T205355Z-d9e2feba-fa5d-431a-ab08-dd4d405a67af` uses `prospective_resume` because mandatory reads preceded registration. Exact argv and command IDs are in the run events. All commands below ran with the clean checkout as the Recorder command `--repo`; the linked Recorder artifacts are stored in the task branch.

| Exact command in clean checkout | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests/ci -v` | 0 | 489.8354 ms | 11 classifier/gate tests PASS |
| `pwsh -NoProfile -File ./tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1049.7966 ms | Five queues and clean recovery PASS |
| `pwsh -NoProfile -File ./tools/verify-frozen-architecture.ps1` | 0 | 671.0433 ms | Markdown and historical PDF hashes PASS |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B H:\.codex\worktrees\loop1-s0-contracts\IM-platform\spec\progress\evidence\LOOP1-CI-001\review2-negative-probe.py` | 1 | 452.66 ms | Expected independent negative-control failure: shared rename bypasses matrix |
| `pwsh -NoProfile -File ./tools/research/recorder.ps1 validate-run --run-id R-20260928T194702Z-28ed6ab3-9f1c-4240-9d1f-6e217d7265d4` | 0 | 638.2721 ms | Implementation Recorder valid, 22 events |
| `pwsh -NoProfile -File ./tools/research/recorder.ps1 validate-run --run-id R-20260928T204018Z-fa44f3d6-9105-4273-b08b-e5f61aa5088b` | 0 | 641.8074 ms | Fix Recorder valid, 25 events |
| `pwsh -NoProfile -File ./tools/research/recorder.ps1 validate-repository` | 0 | 770.6046 ms | Committed Recorder repository PASS |

## Finding

`ci/classify.py::diff_paths` calls `git diff --name-only -z` with Git's default rename detection. In an independent disposable Git repository, renaming `contracts/wire.json` to `docs/wire.json` yielded only `['docs/wire.json']`. `classify` selected no jobs, although removal of a shared contract must fan out to Go, Java, every client, and the compatibility matrix. The durable probe also checked 24 selected failure/cancel/skip combinations across every gate job, an unexpected success for an unselected job, and the ordinary shared/deploy mappings; these passed before the rename assertion failed. A direct deletion is covered by the existing 11 tests, but a rename-away is effectively a deletion of shared authority and is silently missed. The smallest repair is to classify both old and new paths for a rename, such as by disabling rename detection for this name-only diff, and add a regression case.

Static inspection of the workflow graph confirms classifier recovery precedes selection; selected Go/Java/client/shared/compatibility/deploy jobs feed the always-running gate, and the gate rejects failed, cancelled, or skipped selected jobs. Existing client jobs fail closed when future source arrives without its CI command. The committed CI product files and backlog marker are within the authorized paths; no product behavior, contract, migration, or Frozen Architecture file changed. No speculative dependency, service, or framework was added under the Minimality Contract. These findings do not overcome the shared rename failure. No actual GitHub workflow run has occurred; operational CI remains separate and pending.

- Review result: **FAIL**. Keep `LOOP1-CI-001` in `review`; S0 Gate NOT YET PASSED.
- Next: Coordinator delegate a fresh Fix Agent for rename-aware diff classification and its regression, then a different fresh independent reviewer. An actual GitHub workflow run remains required before CI becomes operational.
- Last known good independently accepted main: `10406be70bf66482836164400cd5b8be07709c58`.
- Reviewer owns only this FAIL evidence/probe, task/current recovery edits, prompt, and linked Recorder artifacts until committed. Detached checkout remains clean. Original `H:\IM-platform\contracts\http\schema-lint` was untouched under another Agent's ownership.

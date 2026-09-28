# LOOP1-CI-001 Fix 1 development evidence

- Fresh Fix Agent: `/root/ci001_fix1`; Review 1 failure: `2026-09-29-independent-review1-97db67e-fail.md`.
- Base and branch: `585ba81` on `task/LOOP1-CI-001`; reviewed marker commit: `ba0bbe7990ce81c534bb141ba1018ced4ecac860`.
- Product diff: exactly `spec/tasks/backlog/.gitkeep` added at 0 bytes under prospective Coordinator authorization. No CI product, contract, schema, or Frozen Architecture file changed.
- Clean-state method: new detached Git worktree at `H:\.codex\worktrees\ci001-fix-clean` checked out at `ba0bbe7`; `git status --short --branch` showed only `## HEAD (no branch)` after verification. Diff range for this fix: `585ba81..ba0bbe7`.
- Research Recorder: prompt `P-bf60a719-b3dc-47c0-9460-33d9a9ec26d2`; run `R-20260928T204018Z-fa44f3d6-9105-4273-b08b-e5f61aa5088b` linked to Review 1. Startup reading and baseline checks preceded registration, so capture mode is `prospective_resume`, with pre-Recorder trace explicitly incomplete. An initial attempt to pass a `.ps1` directly to `run-command` failed with WinError 193 before a command event was recorded; subsequent PowerShell invocations were recorded normally.
- Recorder run finished `PASS` and `validate-run` passed with 25 events. The temporary prompt source file was removed after registration; only the registered prompt artifact remains.

## Verification in new clean committed checkout

| Exact command after `Set-Location 'H:\.codex\worktrees\ci001-fix-clean'` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `./tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1.121 s | All five queues, 12 task specs, clean Git state; prior missing backlog failure repaired |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest discover -s tests/ci -v` | 0 | 0.957 s | 11 path-classifier and selected-job gate tests pass |
| `./tools/verify-frozen-architecture.ps1` | 0 | 0.690 s | Canonical Markdown and historical PDF hashes match manifest |
| `git status --short --branch` | 0 | 0.621 s | `## HEAD (no branch)`; no changes |
| `./tools/research/recorder.ps1 validate-repository` | 0 | 0.794 s | Committed Recorder repository artifacts valid |

`./tools/verify-loop1-ctrl-002.ps1 -Mode Development` also exited 0 in the writer checkout (1.021 s) after the marker was created. This is development evidence only. The candidate remains in `review`; a different fresh Review Agent must independently verify and accept it. The actual GitHub workflow has not yet run, so operational CI and S0 Gate remain unaccepted. Last known good independently accepted main is `10406be70bf66482836164400cd5b8be07709c58`. No architecture conflict is known.

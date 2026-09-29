# LOOP1-CI-001 Fix 4: portable historical Recorder checkout

## Cause and bounded repair

Hosted run [36521060867](https://github.com/nilesthump/IM-platform/actions/runs/36521060867) reported 17 modified historical Recorder stdout blobs directly after `actions/checkout@v4`. The repository's `research/.gitattributes` requests LF conversion, while those committed stdout blobs contain CRLF. A machine-local `H:/IM-platform/.git/info/attributes` exception for the two run directories hid this on local worktrees. The fresh GitHub checkout had no such exception.

The Coordinator prospectively added exactly two transport metadata paths to this Task Spec. Commit `21c10e3` adds `*.txt -text -eol` to each affected run's `blobs/.gitattributes`, matching an established older Recorder run. It changes no historical Recorder blob, public contract, architecture, verifier, or CI gate. The earlier local Git info overrides remain machine-local and were not copied into either test clone.

## Development verification

| Verification | Result |
| --- | --- |
| `python.exe -m unittest discover -s tests/ci -v` through Fix 4 Recorder | Exit 0; 12 tests pass. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` through Recorder | Exit 0; development recovery only. |
| `git clone --no-local --branch task/LOOP1-CI-001 --single-branch` into `H:\.codex\worktrees\ci001-fix4-portable-lf` | Exit 0; independent `.git`, no `info/attributes`, effective `core.autocrlf=true`. |
| `git clone --no-local --branch task/LOOP1-CI-001 --single-branch -c core.autocrlf=false` into `H:\.codex\worktrees\ci001-fix4-portable-noautocrlf` | Exit 0; independent `.git`, no `info/attributes`, effective `core.autocrlf=false`. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` through Recorder from each clone | Exit 0 in both; `status_entries=0`, `diff_lines=0`; task remains `review`. This is Fix Agent evidence, not independent acceptance. |
| `git ls-tree -r 1d9ec9f` versus `21c10e3` for both historical `blobs/` directories, excluding the two new attribute files | All 42 original Git blob entries and object IDs identical. |
| `git hash-object --no-filters` on all 42 historical blob working files in each clone versus their recorded Git object IDs | Zero byte mismatches in either clone. |
| `recorder.ps1 validate-run` for the two historical runs | Exit 0; 20 and 30 events, both finished. |

The Fix 4 Recorder prompt is `P-49450b77-dcfc-42ea-92de-2d3c48044b8a`; run `R-20260929T043656Z-cdc8ce0f-06f4-460c-989b-c2f3603ee365` captures baseline tests and both isolated Acceptance runs. The PowerShell Recorder wrapper rejected one nested `run-command` argument form before any command ran; invoking the same Python Recorder CLI directly succeeded. This instrumentation error is disclosed, not used as acceptance evidence.

## Handoff

Branch `task/LOOP1-CI-001`; repair base `1d9ec9f`; exact transport repair commit `21c10e3`. The final handoff commit also includes only this task's development evidence, Task Spec/current recovery, and linked Recorder artifacts. Last independently accepted local `main` is `10406be70bf66482836164400cd5b8be07709c58`. S0 Gate remains NOT YET PASSED. A fresh independent Review Agent must inspect the final clean candidate and then the Coordinator must obtain a passing actual GitHub workflow run before task closure.

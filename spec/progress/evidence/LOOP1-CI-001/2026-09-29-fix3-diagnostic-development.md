# LOOP1-CI-001 Fix 3: hosted checkout diagnostic

## Observed failure and diagnosis limit

- GitHub Actions run [36515716353](https://github.com/nilesthump/IM-platform/actions/runs/36515716353) at reviewed `f07e353334b5afa07cf03a564c5f7ca349639b10` checked out the requested SHA, then `classify` failed `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` with `Acceptance mode requires a clean worktree and index.` The gate rejected the failure.
- `gh run view 36515716353 -R nilesthump/IM-platform --log-failed` exited 0 and exposed only that generic failure. The checkout log shows `actions/checkout@v4` finished, but neither step printed Git porcelain entries. The exact dirty path or output remains unavailable.
- A clean local checkout at accepted `main` `10406be70bf66482836164400cd5b8be07709c58` returned zero entries from the verifier's equivalent `git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all` call under PowerShell 7.6.5. The suspected empty-output array behavior was not reproduced locally. This does not establish hosted cleanliness.

## Task-scoped change

- `.github/workflows/ci.yml` prints `checkout_status_entries` and each raw porcelain entry immediately after `actions/checkout@v4` and before unchanged CTRL-002 Acceptance. It exits if Git status itself fails. No clean-state criterion, selected-job gate, product contract, or frozen authority changed.
- This candidate adds observability; it does not claim the hosted failure is fixed. A new hosted run is necessary before deciding the root repair.

## Development verification

| Command | Result |
| --- | --- |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` through Recorder | exit 0; five queues and current `review` task resolved. Development only. |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests/ci -v` through Recorder | exit 0; 12 path classifier and gate tests passed. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` through Recorder | exit 0; canonical Markdown and retained PDF hashes match manifest. |
| `git diff --check` through Recorder before staging | exit 0 for the task working diff. |

Recorder prompt `P-66187f43-d320-43c6-b9d7-3e209070aaf5`; run `R-20260929T032745Z-2c2aaba9-5225-46c0-9bab-6a6e44e31d22` finished PASS for diagnostic development and `validate-run` passed with 15 events. Ten staged output blobs match raw bytes under the run-local `blobs/.gitattributes` transport rule. The recorded `diff.patch` contains literal diff-added blank lines, so its trailing-whitespace diagnostics are retained as raw evidence; `git diff --cached --check` passes for all task source/handoff files. An initial `--stdin-base64` registration attempt produced empty prompt artifact `P-f8cce6f7-5834-4b11-ba20-1781467c6b3a` because the PowerShell wrapper did not accept piped input. It is retained and excluded from this run; the subsequent file-based registration captured the actual delegated task. No Recorder evidence was edited to hide the failed attempt.

## Handoff

- Branch: `task/LOOP1-CI-001`; base for this fix: `f32e0b9` (prior hosted FAIL evidence). Reviewed diff range for the next independent reviewer: `f32e0b9..HEAD` after candidate commit.
- Last independently accepted local `main`: `10406be70bf66482836164400cd5b8be07709c58`. S0 Gate NOT YET PASSED. The task remains `review`.
- Next exact action: fresh independent review of the clean diagnostic candidate, then a new hosted run to inspect exact status entries. A new Fix/Review cycle repairs the identified cause; only a passing actual CI run can support operational acceptance.

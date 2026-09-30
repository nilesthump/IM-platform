# LOOP1-GO-AUTH-001 hosted CI context repair: independent local review PASS

- Reviewer: fresh `/root/go_auth_ci_review`, separate from the Go Auth implementation, CI Fix Agent, and previous reviewers. Candidate: `8eed78bb1d5763edec349358fb538d32549ad187` on `task/LOOP1-GO-AUTH-001`; reviewed diff `8321deff76e37dfb3eea0f448d346e46953286f7..8eed78bb1d5763edec349358fb538d32549ad187`.
- Clean method: separate local clone `H:\.codex\worktrees\go-auth-ci-review\IM-platform`, detached at exact candidate. Strict `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` passed before and after the mutation, with zero status entries/diff lines. The temporary workflow mutation was restored byte-for-byte. Original `H:\IM-platform` unknown files were untouched.
- Scope: the only executable changes are `.github/workflows/ci.yml` and `tests/ci/test_workflow_context.py`. Other changed files are task-authorized recovery and Recorder evidence. No Go product, Compose, contract, architecture, migration, Java, client, classifier, selected-job gate, or other job changed. The workflow diff removes invalid job-level `${{ runner.temp }}`, sets it in the permitted preparation step `env`, and exports the resolved directory via `GITHUB_ENV` for the later Compose/smoke steps. Disposable credentials stay outside the checkout; the existing read-only mounts are unchanged. This is the smallest repair for the observed no-job workflow failure.
- Negative control: in the detached review clone, reintroduced the old `deploy.env.IM_GO_CONFIG_DIR: ${{ runner.temp }}/im-go-config` assignment. `python -m unittest discover -s tests/ci -p test_workflow_context.py -q` exited 1 as expected: `test_runner_context_is_absent_from_job_env` identified line 214, and the setup-shape assertion also failed. Restored original bytes exactly and strict Acceptance passed again. This demonstrates the committed regression is effective against the prior failure.

## Verification

| Exact command or check | Exit / elapsed | Result |
| --- | --- | --- |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` in detached clone, before and after probe | 0 / about 7.5 s and 6.6 s | PASS, clean exact candidate |
| Bundled Python 3 `-m unittest discover -s tests/ci -q` | 0 / 7.7 s | 21 tests pass; four Windows real-symlink subcases skipped for privilege |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 / under 1 s | Canonical Markdown and historical PDF hashes match |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` | 0 / about 6 s | PASS, nine operations and positive/negative artifacts |
| Bundled Python 3 `contracts/websocket/verify.py` | 0 / under 1 s | PASS, 8 positive and 10 negative golden scenarios |
| `git diff --check 8321def..8eed78b -- .github/workflows/ci.yml tests/ci/test_workflow_context.py spec/tasks/review/LOOP1-GO-AUTH-001.md spec/progress/current.md spec/progress/evidence/LOOP1-GO-AUTH-001` | 0 / under 1 s | PASS for editable paths |
| Bundled Python 3 `tools/research/recorder.py validate-run --run-id R-20260929T164238Z-6215f0a2-b090-4e45-8137-32eb19fa60e7` | 0 / under 1 s | Fix development Recorder finished, integrity-valid, 20 events |
| Independent negative-control mutation and focused test, then exact byte restoration | expected test exit 1 / 9.5 s | PASS: old invalid assignment detected; review clone restored clean |

The first CI suite attempt in the restricted sandbox exited 1 because Python could not create any temporary directory. An authorized rerun exited 0. `actionlint` is unavailable locally; the corrected workflow still needs an actual hosted run. This local PASS is independent review evidence, not CI acceptance or S1 Gate PASS. The previous hosted run `36598098200` had zero jobs and remains a FAIL. A new hosted CI run at the review closure commit is the next acceptance action.

Review Recorder: `R-20260929T165256Z-44fbe90d-37de-44dc-9d92-f9150c8968c3`, linked to Fix run `R-20260929T164238Z-6215f0a2-b090-4e45-8137-32eb19fa60e7`. It uses `prospective_resume` because mandatory startup inspection and baseline verification preceded registration; pre-run activity is not claimed as a complete prospective trace. Recorder integrity is separate from task acceptance.

Task remains `review`; S1 Gate remains NOT YET PASSED. Last independently accepted base remains S0 `main` `09cec968f64faf0db319aea8d9c21d4fffe8ec49`. Reviewer owns only this task-linked evidence, Task Spec/current recovery, and linked Recorder artifacts until the clean review closure commit.

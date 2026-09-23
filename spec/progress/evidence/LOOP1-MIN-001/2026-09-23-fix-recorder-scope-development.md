# LOOP1-MIN-001 Recorder scope Fix: development evidence

- Fix Agent: `/root/min001_fix2`; branch `fix/LOOP1-MIN-001-recorder-scope`; isolated worktree `H:\.codex\worktrees\loop1-min-001-fix2\IM-platform`.
- Base: committed independent FAIL closure `eb5aa7a84454c7417acd20f27b6808e6afcc8f53`; finding: `2026-09-23-independent-review-03c3286-fail.md`.
- Coordinator prospectively authorized exactly one Fix prompt and one Fix run before Recorder writes. Prompt `P-3938e88c-ea8d-4dfa-94f4-edd7c4b17812` contains the exact visible Fix delegation. Prospective `role=fix`, `experiment_group=full_governance` run: `R-20260923T021826Z-679d5d5a-4016-4481-bf0f-6ea135fa78bd`.
- Change: `tools/verify-loop1-min-001.ps1` checks only recognized Recorder prompt/run files and requires metadata `task_id=LOOP1-MIN-001` plus an ID matching the directory. No fixed ID list, product change, architecture change, or public-contract change.

## Development verification

All verifier commands below ran through Recorder `run-command`. These results are development evidence, not independent acceptance.

| Command / condition | Exit | Result |
| --- | ---: | --- |
| `pwsh -NoProfile -File tools/verify-loop1-min-001.ps1` in Fix worktree | 0 | PASS, including existing policy contradiction and necessary-complexity controls |
| Same verifier in disposable checkout with new task-owned independent-review Recorder artifacts | 0 | PASS; future task-owned IDs no longer require verifier updates |
| Same disposable checkout with synthetic prompt metadata owned by `OTHER-TASK` | 1 | Expected rejection of `research/prompts/P-00000000-0000-0000-0000-000000000001/metadata.json` |
| Same disposable checkout with `research/unknown.txt` | 1 | Expected out-of-scope rejection |
| Same disposable checkout with `extra.txt` inside a valid task-owned prompt directory | 1 | Expected out-of-scope rejection |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | PASS; current `LOOP1-CONTRACT-001` remains `review` |
| `git diff --check` | 0 | PASS |

The disposable mutations were confined to `H:\.codex\worktrees\loop1-min-001-fix2-negative\IM-platform`; no synthetic fixture is acceptance evidence or a Human Decision. Frozen Architecture PDF SHA-256 remains `546915F639F30CD294F11390DA3ADE2CE6A85B620BF55727C2A90CA6017D7510`. The diff from accepted Recorder baseline `1c274bcbf92ebcc05c1bc208386c5976437d8221` contains no `contracts/`, `backend/`, `clients/`, `plugins/`, `spec/architecture/`, `spec/domain/`, `spec/invariants/`, `spec/acceptance/`, or `LOOP1-CONTRACT-001` Task Spec change.

The prospective Fix run finished with observed Development PASS and validated: `validate-run --run-id R-20260923T021826Z-679d5d5a-4016-4481-bf0f-6ea135fa78bd` exited `0`, status `finished`, 22 events. The final clean candidate SHA is recorded at handoff. Fresh independent review remains required. Local `main` is `e5482b135a2ab7451c24c29c7517e1a8f19ce420`; a direct fast-forward from this branch would import unfinished `LOOP1-CONTRACT-001` ancestors and is not authorized.

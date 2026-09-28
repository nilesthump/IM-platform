# LOOP1-CONTRACT-002 auth.bind fix: development evidence

- Actor: fresh Fix Agent `/root/contract002_fix2`, distinct from implementation and both independent reviewers. This is not independent acceptance.
- Base: clean review closure `a68cad2cb72fb606932428df2c03edb5802da76a` on branch `task/LOOP1-CONTRACT-002`; reviewed product candidate `102b0ef8cd045ab628618cb541ed36a72d2b0db6`. Fix scope: `contracts/websocket/verify.py` and task-linked recovery/evidence/Recorder paths. The original `H:\IM-platform` untracked HTTP schema-lint directory was not accessed.
- Recorder prompt `P-792b920d-8209-4b7e-9168-40c82eb8ae18`; run `R-20260928T024701Z-63b628c9-0944-46da-b52b-c2f97020a7ee` uses `prospective_resume`. Mandatory recovery, baseline verification and architecture inspection before run start are explicitly not claimed as a complete prospective trace.

## Change

`check_scenario` now requires `bind-valid-session` to start unauthenticated, emit exactly one successful `auth.ack`, and expect an authenticated socket. Every rejected auth.bind vector must retain an unauthenticated socket. Three new permanent in-memory mutations cover the exact independent findings. The nine earlier behavior controls remain. No canonical envelope schema, golden fixture, error contract, HTTP contract, Frozen Architecture, or product implementation changed.

## Recorded verification

| Exact command through bundled Python `tools/research/recorder.py run-command --run-id R-20260928T024701Z-63b628c9-0944-46da-b52b-c2f97020a7ee -- ...` | Command ID | Exit | Elapsed | Result |
| --- | --- | ---: | ---: | --- |
| Bundled Python 3 `contracts/websocket/verify.py` | `C-4cc067d9-760f-4e96-9591-6257d1357cbc` | 0 | 93 ms | PASS: 8 positive, 10 negative shared Go/Java scenarios; 11 schema and 12 behavior mutations rejected. |
| Bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | `C-02fa1d46-3ef1-41cc-bdd1-9ca5e76825ed` | 0 | 94 ms | PASS: all 12 invalid mutations rejected, including the three prior auth.bind failures. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | `C-0e44d421-b491-416b-bec8-162cc56925a6` | 0 | 1641 ms | PASS: task recovery in review; explicitly non-acceptance Development mode. |

Source-path `git diff --check` and canonical path diff checks passed locally. The Recorder run finished as development PASS with 10 events and `validate-run` passed. A run-local `blobs/.gitattributes` preserves raw output bytes during Git staging; after re-indexing, all six output blobs and the registered prompt matched their recorded SHA-256 in both local files and staged Git blobs (7/7). Whole-commit whitespace checking reports CRLF in immutable Recorder output blobs and blank context lines in its `diff.patch` snapshot; those bytes are retained for Recorder integrity and excluded from source whitespace checks. No Gate PASS or task `done` transition is claimed. A different fresh independent Review Agent must inspect the clean committed candidate and run clean-checkout Acceptance verification.

# LOOP1-CONTRACT-002 systemic fixture assertion fix: development evidence

- Fresh Fix Agent: `/root/contract002_fix3`, distinct from implementation and all three independent reviewers. Branch `task/LOOP1-CONTRACT-002`; base `1dda0a3bd6609c45510d61253c8a29a6519f16c5` was clean. Full task diff starts at accepted `main` baseline `7484901b3915535f60941a01116b730a845bd47d`. This is local development evidence, not independent acceptance.
- Recorder prompt `P-0372bc01-e14d-4326-9e28-c0a8068b3078`; run `R-20260928T033910Z-c8f7568a-2fe1-4c9a-aec5-e50bf28cb4b2`, `prospective_resume`. Mandatory startup, authority inspection, and initial baseline preceded the run and are not claimed as fully prospective. An initial broad probe rejected 23/24 because the stable but wrong retry Message ID still escaped; the final explicit committed-vector identity assertion repaired that gap. This failed intermediate command is preserved in the run.
- `contracts/websocket/verify.py` now has independent named-case outcomes and transaction timelines, plus direct checks on response type/count, request binding, auth identity and epoch, durable ACK and created-event identity/sequence, retry and cross-Conversation identity, GROUP persistence, fan-out, Sync convergence flags, heartbeat, rejection code, and revocation. The table is separate from generated fixture bytes. Canonical WSS schema, README, and golden fixture bytes were not changed. No dependency, service, framework, or product implementation was added.

## Final development verification

Commands below were executed through bundled Python 3 `tools/research/recorder.py run-command --run-id R-20260928T033910Z-c8f7568a-2fe1-4c9a-aec5-e50bf28cb4b2 -- <command>`. Durations are Recorder values. The exact bundled executable is recorded in each command-start event.

| Command after `--` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| Bundled Python 3 `contracts/websocket/verify.py` | 0 | 63 ms | PASS: 8 positive, 10 negative shared Go/Java scenarios; 11 wire and 12 behavior mutations rejected. |
| Bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 63 ms | PASS: prior 12/12 invalid outcomes rejected. |
| Bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 63 ms | PASS: broad 24/24 invalid outcomes rejected. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 1062 ms | PASS after recovery edits: repository recovery, five queues, current `review` task. Development mode explicitly is not acceptance. |

- `git diff --check` passed. The task product diff changes only `contracts/websocket/verify.py`. The original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed. No architecture conflict or contract semantic change arose.
- Recorder finished `PASS` with 22 events; `validate-run` returned exit 0. All 18 staged Recorder output blobs match working bytes exactly; the staged prompt SHA-256 matches its registry metadata. `git diff --cached --check` passed for source/governance/evidence after excluding immutable raw Recorder output and `diff.patch`, whose captured CRLF/trailing spaces must remain unchanged. The clean candidate SHA and status are confirmed after commit.

## Handoff

The next action is fresh independent review of the committed candidate from a clean isolated checkout. Review must repeat the broad adversarial probe and CTRL-002 Acceptance. Keep task in `review` and S0 Gate NOT YET PASSED until independent acceptance.

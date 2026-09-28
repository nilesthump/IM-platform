# LOOP1-CONTRACT-003 Fix 1 development evidence

- Actor: fresh Fix Agent `/root/contract003_fix1`; branch `task/LOOP1-CONTRACT-003`; base and independent FAIL closure `09d306596176212302efd2110d858a0247e20ed9`. This is development evidence, not independent acceptance.
- Scope: `contracts/plugin-api/verify.py` and README, `contracts/fixtures/sync-plugin/generate.py`, golden vectors, separately stored Go/Java normalized outcome vectors, and task-linked recovery/evidence/Recorder files. No Frozen Architecture, public schema, HTTP/WSS ACK, or product runtime file changed.
- The oracle stages user state and Message materialization before the fault point, records unchanged local data and cursor/contiguous sequence on rollback, and records retry commit. The gap case records all intermediate sequence states. Full Message payload consistency rejects conflicting duplicates and reused identity at a second sequence. Action fixtures expose every attempt's execution-time authorization, outcome, and side effect. Upgrade fixtures expose ordered stages, old-version service, and rollback at each failure point.
- Profile `go.json` and `java.json` are **static contract test vectors**, separately stored and compared to canonical expectations. They were initially populated from the canonical fixtures. They are not outputs of Go and Java backends, which do not exist in this task. The smallest remaining acceptance interpretation question is whether SP-A-012 requires live backend-produced outcomes at S0 contract-freeze time or permits static profile conformance vectors pending implementation. The verifier no longer runs one Python oracle twice under profile labels and rejects divergence in either profile artifact.

## Verification

All commands below ran through Research Recorder run `R-20260928T114841Z-4641b577-7645-4011-be22-1baaa30290e5` in `prospective_resume` mode. The startup inspection and first baseline invocation predate this run and are marked incomplete pre-Recorder trace.

| Command after `run-command --run-id ... --` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe contracts/fixtures/sync-plugin/generate.py` | 0 | 53.4112 ms | 79 golden cases regenerated. |
| Same Python `contracts/plugin-api/verify.py` (final pass) | 0 | 72.4403 ms | 79 cases; 22 positive, 57 negative; SP-A-001..013; 11 permanent mutation controls, including seven review findings and both profile divergences. |
| Same Python `spec/progress/evidence/LOOP1-CONTRACT-003/review1-negative-probe.py` (final pass) | 0 | 59.2498 ms | 0/7 invalid mutations accepted. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 1083.8057 ms | Recovery PASS; explicitly non-acceptance Development mode. |

The pre-edit baseline verifier exited 0 on the rejected candidate. A local `git diff --check` exited 0 after the fix. A separate fresh reviewer must inspect the clean committed candidate, decide the profile evidence interpretation, run deterministic verification and clean detached CTRL-002 Acceptance, and only then consider task acceptance. S0 Gate remains NOT YET PASSED.

Recorder `finish-run --result PASS` exited 0 with 18 events. `validate-run` exited 0 and reported `status=finished`, `event_count=18`. The full development result remains non-acceptance evidence.

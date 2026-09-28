# LOOP1-CONTRACT-002 precondition fix: development evidence

- Fix Agent: `/root/contract002_fix4`, fresh context after independent Review 4 FAIL. This is development evidence, not independent acceptance.
- Base: clean `ff35aa7c985a819944e9830a86789a787c76a79d`, branch `task/LOOP1-CONTRACT-002`; review range for the candidate is `7484901b3915535f60941a01116b730a845bd47d..HEAD`.
- Scope: `contracts/websocket/verify.py` plus task-authorized evidence, Task Spec, current progress, and Recorder artifacts. No canonical wire schema, golden fixture, HTTP/error contract, architecture, or implementation change.
- Canonical Markdown SHA-256 `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and historical PDF SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` matched `spec/architecture/baseline.md` at startup. The Task Spec, messaging domain/invariants/acceptance, approved ADRs, Minimality Contract, and four independent FAIL reports were inspected.
- Prompt `P-a7441ba7-453d-4815-881b-7f196e0ef45c`; run `R-20260928T042440Z-2abf26e1-ad46-4d62-b224-42f747519427`, `prospective_resume`. Mandatory startup and first baseline preceded the run and are not claimed as a complete prospective trace.

## Repair

The verifier now has an independent `GIVEN` table covering the exact required fields and values of all 18 named scenarios. `check_declared_behavior` rejects a scenario whose declared socket state, membership, token condition, transaction premise, Conversation type, fan-out premise, or revocation premise differs from that table. This binds each already asserted output/state/timeline to its starting premise. Twelve permanent in-memory premise mutations include Review 4's nine failures plus changed foreign Conversation, removed replacement-session premise, and an added unverified field. No generator byte comparison is used for this assertion.

## Verification

The commands below ran through `tools/research/recorder.py run-command --run-id R-20260928T042440Z-2abf26e1-ad46-4d62-b224-42f747519427 -- <command>`. Python is the bundled runtime at `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Durations are Recorder `duration_ms`.

| Exact command after `--` | Command ID | Exit | Elapsed | Result |
| --- | --- | ---: | ---: | --- |
| Python `contracts/websocket/verify.py` | `C-eee90948-3551-4a76-9851-db35baeca628` | 0 | 78 ms | PASS: 8 positive/10 negative; 11 schema/24 behavior controls rejected. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | `C-6117b434-415f-4199-a226-80b29b235e1c` | 0 | 63 ms | PASS: 12/12 invalid mutations rejected. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | `C-4e52eb43-1943-4813-9ea3-f8a89c56ff9a` | 0 | 47 ms | PASS: 24/24 invalid mutations rejected. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | `C-1b63b2e6-9ecf-4032-b1cd-999a3d192aa9` | 0 | 63 ms | PASS: 9/9 invalid preconditions rejected. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | `C-3cbe07ed-19ec-4d5f-82ee-2cd7f089960a` | 0 | 1078 ms | PASS: review task recovery; non-acceptance Development mode. |
| `git diff --check` | `C-6f35a59e-e06e-4cd2-85d0-55c6d924c7b8` | 0 | 31 ms | PASS. |
| `git diff --exit-code ff35aa7 -- contracts/websocket/envelope.schema.json contracts/fixtures/websocket/golden.json contracts/errors contracts/http spec/architecture` | `C-37719904-20a1-462b-93ef-fa0f773946a3` | 0 | 31 ms | PASS: canonical inputs unchanged. |

The minimal pre-run baseline command, Python `contracts/websocket/verify.py`, exited 0 and reported 8 positive, 10 negative, 11 schema, and 12 behavior controls. Independent review must repeat the probes on the exact clean candidate and use the clean-checkout Acceptance mechanism. S0 Gate remains NOT YET PASSED; no architecture conflict was found.

## Next action

Hand the clean committed candidate to a different fresh independent Reviewer. The original `H:\IM-platform` untracked `contracts/http/schema-lint/` remains under its prior owner's control and was not accessed.

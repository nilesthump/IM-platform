# LOOP1-CONTRACT-002 independent fourth review: FAIL

- Fresh reviewer: `/root/contract002_review4`, distinct from the implementer, three fixers, and three prior reviewers. No product contract file was edited.
- Exact candidate: `cb24c4ca2727e344ee8c40dcbdce1ae5b540b12f`, branch `task/LOOP1-CONTRACT-002`; reviewed diff `7484901b3915535f60941a01116b730a845bd47d..cb24c4ca2727e344ee8c40dcbdce1ae5b540b12f`.
- Candidate had empty `git status --porcelain=v1` before review artifacts. Separate clean detached Acceptance checkout: `H:\.codex\worktrees\contract002-review4-clean\IM-platform`, at the exact candidate SHA, status empty before and after Acceptance.
- Frozen Markdown and historical PDF SHA-256 values match `spec/architecture/baseline.md`: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Approved ADRs, messaging domain/invariants/acceptance, HTTP/error authority, Minimality Contract, exact Task Spec, full task diff, focused fix, and prior FAIL reports were inspected.
- Review Recorder prompt `P-a6760d2f-5f60-4e31-b3d5-24073780b9fe`; run `R-20260928T040555Z-46762043-e185-4e47-b77a-8402f787f573`, `prospective_resume`. Mandatory startup and architecture inspection preceded registration; those activities are not claimed as a complete prospective trace.

## Verification

All commands in this table ran through `tools/research/recorder.py run-command --run-id R-20260928T040555Z-46762043-e185-4e47-b77a-8402f787f573 -- <command>`. Python means bundled Python 3 at `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Elapsed values are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| Python `contracts/websocket/verify.py` | 0 | 78 ms | Baseline PASS: 8 positive, 10 negative; 11 schema and 12 behavior controls rejected. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 63 ms | Prior 12/12 invalid mutations rejected. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 78 ms | Prior broad 24/24 invalid mutations rejected. |
| `pwsh -NoProfile -Command "Set-Location -LiteralPath 'H:\.codex\worktrees\contract002-review4-clean\IM-platform'; & '.\tools\verify-loop1-ctrl-002.ps1' -Mode Acceptance"` | 0 | 1219 ms | Clean detached recovery PASS; this does not establish Contract acceptance. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 687 ms | Both frozen hashes PASS. |
| Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 1 | 47 ms | Blocking: 0/9 invalid scenario preconditions rejected. |

The committed Fix Recorder run `R-20260928T033910Z-c8f7568a-2fe1-4c9a-aec5-e50bf28cb4b2` validated finished with 22 events. `git diff --check 7484901..cb24c4c -- contracts/websocket contracts/fixtures/websocket` exited 0. Product changes remain within the Task's allowed paths: WSS schema, verifier, README, and golden fixtures. The focused fix changes only `contracts/websocket/verify.py`; canonical schema and fixture bytes remain unchanged. No speculative dependency or implementation layer was added.

The Review Recorder run finished `FAIL` and `validate-run` returned exit 0 with 16 events. Its 12 staged raw output blobs match recorded SHA-256 values byte-for-byte after a run-local `blobs/.gitattributes` preserves transport bytes; the staged prompt hash also matches registry metadata. Staged source/governance/evidence `git diff --check` passed, excluding immutable raw Recorder output and `diff.patch`.

## Blocking finding

`contracts/websocket/verify.py::check_declared_behavior` asserts named `expect` outputs and timelines but does not bind most `given` preconditions to the outcome. The independent in-memory probe copies generated scenarios, changes one precondition at a time, and invokes `check_scenario` without editing the checked-in fixture or generator. All nine invalid cases were accepted:

- `durable-send-and-created` still returned committed ACK and `message.created` when the declared socket became `UNAUTHENTICATED`, membership became false, or the declared transaction became a rollback.
- `idempotent-retry` still returned successful ACKs with an unauthenticated socket; `same-request-different-conversation` still returned two committed ACKs when both declared transactions rolled back; `group-single-message` still committed for a declared nonmember.
- `unauthenticated-send` still reported `AUTH_REQUIRED` after its socket precondition became `AUTHENTICATED`; `rollback-before-ack` still reported a commit failure when the declared transaction became committed; `bind-valid-session` still bound a declared invalid-signature token.

The prior 12/24 mutation probes cover output/state/timeline edits and therefore pass, but they do not cover these input premises. A generated fixture byte comparison protects the currently checked-in serialization; it does not independently validate a generator or fixture whose premises have drifted. The accepted contradictions violate the machine-verifiable authentication, membership, durable-commit ACK, and negative-case semantics in Frozen Architecture chapters 5 and 7 and MSG-D-004/005, MSG-I-002/006, MSG-A-001/004/007. The cross-Conversation case has no transaction timeline, making its rollback contradiction especially easy to miss. The negative precondition probe is retained beside this report for regression.

Go and Java currently share one fixture, with no backend implementation runners at this stage; this is a stated contract-only limitation rather than a separate finding. No architecture conflict was found.

## Disposition

**FAIL** for `cb24c4c`. Keep `LOOP1-CONTRACT-002` in `review` and S0 Gate NOT YET PASSED. A fresh Fix Agent should bind each scenario's material authentication, membership, token, and transaction preconditions to its asserted outcome, add permanent adversarial controls, and then hand off to a different fresh independent Reviewer. Do not transition to `done`, merge, or push. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed.

# LOOP1-CONTRACT-002 independent third review: FAIL

- Fresh reviewer: `/root/contract002_review3`, distinct from implementer, both fixers, and both prior reviewers. No product contract file was edited.
- Exact reviewed commit: `1da1b4020658006f01e8c73675126c47af21a0fd` on `task/LOOP1-CONTRACT-002`. Full task diff: `7484901b3915535f60941a01116b730a845bd47d..1da1b4020658006f01e8c73675126c47af21a0fd`.
- Candidate checkout was clean before this review. Independent detached Acceptance checkout: `H:\.codex\worktrees\contract002-review3-clean\IM-platform`, at the exact candidate SHA with empty `git status --porcelain=v1` before and after Acceptance. Review evidence and Recorder artifacts are task-owned uncommitted additions until this FAIL closure commit.
- Canonical Frozen Architecture Markdown SHA-256 `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and historical PDF SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` match the manifest. Approved ADRs, messaging domain/invariants/acceptance, shared HTTP/errors, Minimality Contract, and exact Task Spec were inspected. No architecture conflict was found.
- Review Recorder prompt `P-b6a7bd6a-db97-49d3-8b95-abb44c946329`, run `R-20260928T031404Z-1b954968-1e74-47a2-925b-65c3188f4559`, mode `prospective_resume`. Mandatory startup and first baseline check preceded the run and are not claimed as a complete prospective trace.

## Verification

All commands below ran through `tools/research/recorder.py run-command --run-id R-20260928T031404Z-1b954968-1e74-47a2-925b-65c3188f4559 -- <command>`. Elapsed values are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| Bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 62 ms | Prior 12/12 invalid mutations rejected. |
| Bundled Python 3 `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 1 | 62 ms | Only 3/24 independent invalid mutations rejected; 21 invalid outcomes accepted. This is the blocking review result. |
| `pwsh -NoProfile -Command "Set-Location -LiteralPath 'H:\.codex\worktrees\contract002-review3-clean\IM-platform'; & '.\tools\verify-loop1-ctrl-002.ps1' -Mode Acceptance"` | 0 | 1094 ms | Clean detached candidate recovery PASS; not Task acceptance. |
| Bundled Python 3 `contracts/websocket/verify.py` | 0 | 62 ms | Baseline PASS: 8 positive, 10 negative Go/Java shared scenarios; 11 schema and 12 behavior mutations rejected. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 687 ms | Canonical Markdown and historical PDF hashes PASS. |

`git diff --check 7484901..1da1b40 -- contracts/websocket contracts/fixtures/websocket` exited 0. Product files in the full task diff are only `contracts/websocket/{README.md,envelope.schema.json,verify.py}` and `contracts/fixtures/websocket/golden.json`, all within allowed paths. The Fix Agent Recorder run `R-20260928T024701Z-63b628c9-0944-46da-b52b-c2f97020a7ee` validated as finished; its seven committed output blobs matched `git show HEAD:<path>` byte-for-byte. No new dependency, service, framework, or speculative layer was found.

## Blocking finding

`contracts/websocket/verify.py::check_scenario` checks selected timing/count relations and three previous auth.bind regressions, but leaves much of each named fixture's declared output, state, and timeline unasserted. The review probe copies generator scenarios in memory, changes one invalid outcome at a time, and calls `check_scenario` without touching fixture bytes. It found these accepted violations:

- `bind-valid-session`: wrong bound user ID or session epoch.
- `durable-send-and-created`: missing `message.created`, wrong ACK sequence, mismatched created message ID, zero persisted Messages/Outbox, or omitted sequence allocation despite a successful ACK.
- `idempotent-retry`: stable but wrong message identity, or two expected persisted Messages/Outbox events and sequences.
- `same-request-different-conversation`: ACK names a third Conversation, unrelated to the request.
- `group-single-message`: two expected logical Messages/Outbox events.
- `duplicate-fanout` and `out-of-order-fanout`: double client materialization or a permanent sequence gap.
- `ping-before-bind`: socket becomes authenticated or no pong is emitted.
- `unauthenticated-send` and `non-member-send`: wrong rejection codes.
- `rollback-before-ack`: expected persisted Message/Outbox despite rollback.
- `conflicting-retry`: `secondSuccessAck` becomes true.
- `wrong-conversation-fanout`: expected wrong-Conversation delivery becomes true.
- `revoked-socket`: expected persisted Message/Outbox despite closure.

The three changed auth rejection codes for expired token, wrong client type, and invalid signature were rejected. Thus the prior 12-case probe passes, but coverage of the broader MSG-A-001 through MSG-A-008 fixture expectations remains insufficient. Generated fixture byte equality protects the current checked-in bytes against drift; it does not independently verify these semantics if generator expectations or scenario logic change. This is especially consequential for durable ACK, single logical persistence, authorization errors, fan-out, and eventual completeness. The schema validates individual frame shape but cannot supply transaction/state cross-checks. The task's required machine-verifiable message/auth behavior is not established.

Go and Java are listed as two profiles sharing one canonical fixture; no backend profile implementation or profile-specific runner exists yet. That is a current-stage limitation, not a separate blocker for this contract-only task. WSS v1 TEXT-only content remains the documented dependent Plugin-contract extension and is likewise not a new finding.

## Disposition

**FAIL** for `1da1b40`. Keep `LOOP1-CONTRACT-002` in `review`, with S0 Gate NOT YET PASSED. Delegate a fresh Fix Agent to add independent assertions and permanent adversarial regressions for the declared scenario outcomes, then a different fresh Review Agent. No product fix, `done` transition, merge, or push is part of this review. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed.

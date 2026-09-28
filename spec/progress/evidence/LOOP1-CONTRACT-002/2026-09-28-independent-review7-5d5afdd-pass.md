# LOOP1-CONTRACT-002 independent seventh review: PASS

- Fresh independent Reviewer `/root/contract002_review7` did not implement or fix this task and is distinct from the six Fix Agents and six earlier Review Agents. No product contract was edited during this review.
- Exact reviewed candidate: `5d5afddfc5c5099029daf6ecd6c653cd9fecff4b`, branch `task/LOOP1-CONTRACT-002`, diff range `7484901b3915535f60941a01116b730a845bd47d..5d5afddfc5c5099029daf6ecd6c653cd9fecff4b`. The candidate had no tracked or untracked changes before this review. A separate managed worktree at `H:\.codex\worktrees\contract002-review7-accept\IM-platform` checked out exactly that commit detached; `git status --porcelain=v1` was empty before and after CTRL-002 Acceptance.
- Canonical Frozen Architecture Markdown SHA-256 `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and historical PDF SHA-256 `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510` matched the baseline manifest. I inspected the referenced frozen chapters, approved ADRs, messaging domain/invariants/acceptance, shared HTTP/error authority, Minimality Contract, WSS schema/verifier/fixtures, prior FAIL reports, and Fix 6 diff.
- Recorder prompt `P-95d93bba-8928-45a0-8c4e-b0967d372fbe`, run `R-20260928T062353Z-39bc4b6e-2cc6-4610-940b-1e93949d211b`, capture mode `prospective_resume`. Mandatory startup and a direct smallest WSS baseline PASS preceded run start and are excluded from a complete prospective trace. First prompt registration was denied by the read-only sandbox; its authorized retry succeeded. The run finished PASS and `validate-run` passed with 32 events.
- After staging, the independent integrity script confirmed all 28/28 Review 7 raw output blobs match their Recorder event SHA-256 and staged Git bytes. `git diff --cached --check -- . ':(exclude)research/runs/**/blobs/*.txt' ':(exclude)research/runs/**/diff.patch'` exited 0. Raw Recorder output blobs are excluded from whitespace lint because their exact bytes are evidence; the run-local `blobs/.gitattributes` preserves them through Git.

## Verification

Each command below was executed by bundled Python `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools/research/recorder.py run-command --run-id R-20260928T062353Z-39bc4b6e-2cc6-4610-940b-1e93949d211b -- <command>`. Durations are Recorder `duration_ms`. `PY` in the table is exactly `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

| Exact command after `--` | Exit | Elapsed ms | Result |
| --- | ---: | ---: | --- |
| `PY contracts/websocket/verify.py` | 0 | 78 | PASS: 8 positive and 10 negative shared Go/Java vectors; 18 schema and 26 behavior controls rejected. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 63 | 12/12 invalid behavior changes rejected. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 63 | 24/24 outcome/state/timeline changes rejected. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 0 | 62 | 9/9 premise changes rejected. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | 0 | 63 | Cross-Conversation sequence-gap case rejected. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review6-mutations.py` | 0 | 47 | Duplicate sender/Conversation/request identity and malformed schema type both rejected. |
| `pwsh -NoProfile -File H:\.codex\worktrees\contract002-review7-accept\IM-platform\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1141 | PASS: detached clean recovery, task in review. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review7-controls.py` | 0 | 47 | 10/10 focused malformed-keyword, duplicate Message ID, gap, and timeline controls rejected. |
| `PY tools/research/recorder.py validate-run --run-id R-20260928T060018Z-0daae2f5-d6ee-4d1a-a688-39bb16513878` | 0 | 78 | Fix 6 run structurally valid. |
| `PY spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review7-integrity.py` | 0 | 609 | All 18 Fix 6 raw output blobs matched event SHA-256 and committed Git bytes. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 703 | Both frozen provenance hashes match. |
| `git -C H:\.codex\worktrees\contract002-review7-accept\IM-platform status --porcelain=v1` | 0 | 46 | Empty after Acceptance. |
| `git diff --check 7484901b3915535f60941a01116b730a845bd47d..5d5afddfc5c5099029daf6ecd6c653cd9fecff4b -- contracts/websocket contracts/fixtures/websocket spec/tasks spec/progress/current.md spec/progress/evidence/LOOP1-CONTRACT-002` | 0 | 31 | PASS. |
| `git diff --exit-code 7484901b3915535f60941a01116b730a845bd47d..5d5afddfc5c5099029daf6ecd6c653cd9fecff4b -- contracts/http contracts/errors spec/architecture spec/domain spec/invariants spec/acceptance` | 0 | 32 | Protected authority files unchanged. |

## Review decision and limits

The canonical WSS v1 schema contains the required envelope and auth/message/revocation frames. The verifier applies every JSON Schema keyword used by this schema and now rejects malformed values for its supported keywords. The generator's golden fixture bytes match, while independent named-case assertions and probes enforce durable ACK, authorization, idempotent retry, one Message/Outbox event, per-Conversation sequencing, Sync convergence, and revoked-session behavior. Fix 6 directly closes both Review 6 findings. No additional abstraction or dependency lacks a current responsibility under the Minimality Contract; the changed product code is confined to `contracts/websocket/verify.py` after the prior review.

The fixtures are contract vectors for future Go and Java profiles; this review does not claim running backend implementations. The local linter intentionally supports the schema keywords in this WSS contract rather than the entire JSON Schema vocabulary. Recorder PASS and local task review PASS are distinct from Stage Gate PASS. The original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed.

**PASS** for exact candidate `5d5afddfc5c5099029daf6ecd6c653cd9fecff4b` under ADR-0001's clean-checkout independent mechanism. The Coordinator owns the task transition, merge, and post-merge verification; S0 Gate remains NOT YET PASSED at this review closure.

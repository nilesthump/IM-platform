# LOOP1-CONTRACT-002 independent sixth review: FAIL

- Fresh independent reviewer: `/root/contract002_review6`, distinct from implementation, all five fix agents, and five earlier reviewers. No product contract was edited.
- Exact reviewed candidate: `dfc31e542316184724d2a8206a9874a0d2ab5cc8`, branch `task/LOOP1-CONTRACT-002`, full diff `7484901b3915535f60941a01116b730a845bd47d..dfc31e542316184724d2a8206a9874a0d2ab5cc8`. Candidate was clean before the review. Separate detached checkout `H:\.codex\worktrees\contract002-review6-accept` was created at that SHA and had empty `git status --porcelain=v1` before and after Acceptance.
- Frozen canonical Markdown and historical PDF hashes matched the manifest (`ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`, `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`). Task Spec, ADRs, messaging domain/invariants/acceptance, Minimality Contract, shared HTTP/error contract, WSS schema/verifier/golden fixture, five prior FAIL reports, and focused Fix 5 were inspected. No architecture or scope change was found.
- Recorder prompt `P-1ae662cb-11d4-442c-b656-6c066c82cc41`; review run `R-20260928T053447Z-5aa0c014-0381-4fba-9457-7acb7cf3da9a` uses `prospective_resume`. Mandatory startup, authority inspection, and clean candidate confirmation preceded run start and are excluded from its complete prospective trace. One initial `start-run` call failed argument parsing without creating a run; the corrected call succeeded.

## Verification

Commands below ran as `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools/research/recorder.py run-command --run-id R-20260928T053447Z-5aa0c014-0381-4fba-9457-7acb7cf3da9a -- <command>`. Durations are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed ms | Result |
| --- | ---: | ---: | --- |
| Bundled Python `contracts/websocket/verify.py` | 0 | 78 | PASS: 8 positive, 10 negative; 11 schema and 25 behavior controls rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 63 | Prior 12/12 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 62 | Prior 24/24 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 0 | 63 | Prior 9/9 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | 0 | 63 | Cross-Conversation invalid case rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review6-mutations.py` | 1 | 63 | New invalid same-Conversation request identity and malformed schema type accepted. An earlier one-control version also exited 1 in 63 ms. |
| `pwsh -NoProfile -File H:\.codex\worktrees\contract002-review6-accept\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1266 | PASS: detached clean recovery, task remains review. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 704 | PASS: Markdown/PDF hashes. |
| `git -C H:\.codex\worktrees\contract002-review6-accept status --porcelain=v1` | 0 | 47 | Empty after Acceptance. |
| `git diff --check 7484901b3915535f60941a01116b730a845bd47d..dfc31e542316184724d2a8206a9874a0d2ab5cc8 -- contracts/websocket contracts/fixtures/websocket spec/tasks spec/progress/current.md spec/progress/evidence/LOOP1-CONTRACT-002` | 0 | 47 | PASS. |
| Bundled Python `tools/research/recorder.py validate-run --run-id R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb` | 0 | 78 | Fix 5 run structurally valid. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review6-integrity.py` | 0 | 547 | 16/16 Fix 5 raw output blobs match event hashes and committed bytes. |

## Blocking finding

The in-memory probe changes the seq-1 `out-of-order-fanout` input `message.created` and matching output to reuse the seq-2 frame's `requestId`. Both events retain the same sender and Conversation; they retain distinct `messageId` and seq 2/1. The frame schema remains valid and the declared premises, timeline, and expected outcomes are unchanged. `check_scenario` accepts both logical Messages under one `(senderId, conversationId, requestId)` identity. This violates Frozen chapter 4.4, MSG-D-001/002, and MSG-I-001: retry identity must converge to one logical Message and must not allocate a second sequence. The baseline checks and generator-to-golden byte comparison cannot establish that invariant when a generator and fixture share this defect. The smallest fix is to assert distinct request identities for the two distinct messages in this named case, with a permanent negative control.

The same probe also demonstrates that `lint_schema` accepts a `MessageSend.payload.type` value that is not a JSON Schema type. This is a separate schema-validity gap in the contract verifier; it should be addressed with a direct type-keyword structural check or a valid offline metaschema mechanism. The committed schema itself has `type: object`; the probe changes only an in-memory copy. The idempotency finding independently requires FAIL.

Fix 5's same-Conversation repair correctly rejects the prior cross-Conversation probe. Go and Java consume the same checked-in golden fixture; runtime implementation equivalence is future work. The WSS-specific message error codes remain within the WSS schema, with no change to the shared HTTP error envelope. No speculative abstraction was found.

## Disposition

**FAIL** for `dfc31e5`. Keep `LOOP1-CONTRACT-002` in `review`; S0 Gate remains NOT YET PASSED. Delegate a fresh Fix Agent and then a different fresh independent Reviewer. Do not transition to done, merge, or push. The original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed.

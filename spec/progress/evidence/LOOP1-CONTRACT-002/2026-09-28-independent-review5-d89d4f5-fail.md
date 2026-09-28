# LOOP1-CONTRACT-002 independent fifth review: FAIL

- Fresh independent reviewer: `/root/contract002_review5`, distinct from the implementer, four fixers, and four earlier reviewers. No product contract was edited.
- Exact reviewed candidate: `d89d4f5c5e78c38d8a25c0739227ddccd34fb8c9`, branch `task/LOOP1-CONTRACT-002`, full diff `7484901b3915535f60941a01116b730a845bd47d..d89d4f5c5e78c38d8a25c0739227ddccd34fb8c9`. Candidate branch was clean before review artifacts. Separate detached checkout `H:\.codex\worktrees\contract002-review5-accept` remained at that SHA with empty `git status --porcelain=v1` before and after Acceptance.
- Canonical Markdown and historical PDF SHA-256 matched `spec/architecture/baseline.md`: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Approved ADRs, domain, invariants, S0 messaging acceptance, shared HTTP/error contracts, Minimality Contract, full WSS schema/verifier/fixture, and prior four FAIL reports/probes were inspected. No architecture conflict or speculative complexity was found.
- Review Recorder prompt `P-f1ac8e70-0def-4193-8e84-09595934a7b8`, run `R-20260928T044144Z-c2f35c2f-7072-4b31-bd49-5b84dd1c4654`. Mandatory startup and authority inspection preceded the run; these steps are outside its prospective trace. The PowerShell Recorder wrapper rejected one `run-command` invocation before executing the baseline, so the Python entry point was used. This limitation is disclosed rather than treated as captured work.

## Verification

Commands below ran through `python tools/research/recorder.py run-command --run-id R-20260928T044144Z-c2f35c2f-7072-4b31-bd49-5b84dd1c4654 -- <command>`. Elapsed values are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `python contracts/websocket/verify.py` | 0 | 108 ms | Baseline PASS: 8 positive, 10 negative shared Go/Java scenarios; 11 schema and 24 behavior controls rejected. |
| `python spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 102 ms | Prior 12/12 invalid mutations rejected. |
| `python spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 78 ms | Prior 24/24 invalid mutations rejected. |
| `python spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 0 | 70 ms | Prior 9/9 invalid precondition mutations rejected. |
| `python spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | 1 | 74 ms | New cross-Conversation out-of-order mutation unexpectedly accepted. Exit 1 is the intended probe failure signal. |
| `pwsh -NoProfile -File H:\.codex\worktrees\contract002-review5-accept\tools\verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | 1111 ms | Clean detached recovery PASS; task remains review. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 703 ms | Frozen hashes PASS. |
| `git -C H:\.codex\worktrees\contract002-review5-accept status --porcelain=v1` | 0 | 43 ms | Empty, clean after Acceptance. |
| `git diff --check 7484901..d89d4f5 -- contracts/websocket contracts/fixtures/websocket spec/tasks spec/progress/current.md spec/progress/evidence/LOOP1-CONTRACT-002` | 0 | 38 ms | Source/recovery whitespace PASS. |
| `python spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-integrity.py` | 0 | 456 ms | Fix 4 Recorder output blobs match event hashes and committed bytes, 14/14. |
| `python tools/research/recorder.py validate-run --run-id R-20260928T042440Z-2abf26e1-ad46-4d62-b224-42f747519427` | 0 | 83 ms | Fix 4 run structurally valid, finished with 18 events. |

## Blocking finding

The `out-of-order-fanout` fixture claims `contiguousSeqAfterSync: 2` and `permanentSeqGap: false` for a Conversation. The verifier checks that its two event sequence numbers are `[2, 1]` and message IDs differ, but does not require the events to belong to the same Conversation. The retained in-memory probe changes only the seq-1 event's `conversationId` and matching output to `C2`, leaving the seq-2 event in `C1`. Frame schema remains valid, all `given`, `timeline`, and `expect` fields remain unchanged, and `check_scenario` accepts it. C1 still lacks seq 1, while C2 has only seq 1; neither has a contiguous sequence through 2. Thus the contract runner can accept a false eventual completeness claim, contrary to MSG-I-004 and MSG-A-005/007 and Frozen chapter 5.2/5.3. Generator-to-fixture byte equality cannot catch a jointly changed generator and golden fixture. The smallest fix is a direct same-Conversation assertion for the two events and a permanent negative control; a fresh reviewer should repeat this probe.

The other 17 named scenarios' premises, input frames, outputs, timelines, and declared expectations were inspected for mutual consistency. Positive/negative auth, committed ACK order, rollback, idempotent retry and conflict, group single persistence, wrong-Conversation suppression, and revocation were covered by the baseline plus prior probes. WSS v1 uses one shared Go/Java fixture; profile implementations are future work. The WSS-only `MESSAGE_*` codes are in the canonical WSS schema and do not alter the approved HTTP error envelope. No additional blocking finding was identified.

Review Recorder finished `FAIL` and `validate-run` passed with 26 events. Its 22 staged command output blobs match working bytes and event SHA-256 exactly after a run-local Git transport rule; the retained integrity script also verifies the prior Fix 4 blobs 14/14. Recorder integrity does not change the Task FAIL result.

## Disposition

**FAIL** for `d89d4f5`. Keep `LOOP1-CONTRACT-002` in `review` and S0 Gate NOT YET PASSED. Delegate a fresh Fix Agent and then a different fresh independent Reviewer. Do not transition to `done`, merge, or push. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` remained untouched.
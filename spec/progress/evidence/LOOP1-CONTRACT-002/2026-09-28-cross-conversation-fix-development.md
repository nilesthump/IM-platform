# LOOP1-CONTRACT-002 cross-Conversation fix: development evidence

- Fix Agent: `/root/contract002_fix5`, fresh context after independent Review 5 FAIL. This is development evidence, not independent acceptance.
- Base: clean `f81c1b4a07ddd71189d8803e1e3b1fdeb3afc8db`, branch `task/LOOP1-CONTRACT-002`; full candidate diff range `7484901b3915535f60941a01116b730a845bd47d..HEAD`.
- Canonical Markdown and historical PDF hashes matched the manifest: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Task Spec, architecture, ADRs, domain, invariants, S0 acceptance, Minimality Contract, and Review 5 probe were inspected.
- Prompt `P-0f5a6035-96d4-4ed9-914c-c293abdeac2f`; Recorder run `R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb`, `prospective_resume`. Mandatory startup and baseline preceded run start and are outside its complete prospective trace. The first prompt registration attempt was denied by the read-only sandbox; the authorized retry succeeded.

## Repair

`check_declared_behavior` now requires both out-of-order `message.created` events to carry the same `conversationId`. Its existing sequence assertion `[2, 1]` and fixture outcome then establish that the seq-1 event fills the gap for that Conversation. A permanent behavior mutation moves the seq-1 input event and matching output to C2, precisely reproducing Review 5's failure. No generated schema, golden fixture, HTTP/error contract, frozen authority, or implementation file changed.

## Verification

All commands below ran through the bundled Python `tools/research/recorder.py run-command --run-id R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb -- <command>`. Bundled Python path: `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Durations are Recorder `duration_ms`.

| Exact command after `--` | Command ID | Exit | Elapsed | Result |
| --- | --- | ---: | ---: | --- |
| Bundled Python `contracts/websocket/verify.py` | `C-6451b0a0-fd0e-4583-9c8d-eccec5d7006b` | 0 | 110 ms | PASS: 8 positive/10 negative; 11 schema/25 behavior mutations rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | `C-d166b824-6dcb-4c50-addf-4ce5ef904568` | 0 | 62 ms | PASS: 12/12 invalid mutations rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | `C-ebe24da7-03db-4cba-9038-c544fccc0933` | 0 | 63 ms | PASS: 24/24 invalid mutations rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | `C-8aeca201-c015-487c-b3c5-dcd0edab88f5` | 0 | 47 ms | PASS: 9/9 invalid preconditions rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | `C-2b4d0834-89bf-4240-b6ff-ff221c38bbbc` | 0 | 63 ms | PASS: cross-Conversation out-of-order mutation rejected. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | `C-798b8c46-fcb9-4623-841f-fc8396da8704` | 0 | 1109 ms | PASS: recovery recognizes task in review; non-acceptance mode. |
| `git diff --check` | `C-4916ca31-4878-4686-8e59-aaf763af7d31` | 0 | 47 ms | PASS: source whitespace. |
| `git diff --exit-code f81c1b4 -- contracts/websocket/envelope.schema.json contracts/fixtures/websocket/golden.json contracts/errors contracts/http spec/architecture` | `C-be0998c3-c657-4cb0-a79e-46a06a9a2a29` | 0 | 46 ms | PASS: canonical product inputs unchanged. |

The pre-run minimal baseline passed 8 positive/10 negative, 11 schema/24 behavior controls. A system Python alias was too old to parse the verifier; the bundled Python runtime above was used for all valid checks. Fresh independent review must repeat the cross-Conversation probe and the clean-checkout Acceptance mechanism. S0 Gate remains NOT YET PASSED. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` remained untouched.

The Recorder run finished `PASS` with 20 events; `validate-run` exited 0. An exact run-local Git transport rule under `.git/info/attributes` preserved its raw output blobs. After staging, all 16/16 command-output blobs matched event SHA-256, working bytes, and staged Git bytes. Full `git diff --cached --check` reports embedded whitespace in immutable Recorder `diff.patch` and raw CRLF output blobs; source checks exclude the Recorder run. Recorder integrity is not task acceptance.

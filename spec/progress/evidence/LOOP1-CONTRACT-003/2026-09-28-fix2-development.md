# LOOP1-CONTRACT-003 Fix 2 development evidence

- Fresh Fix Agent: `/root/contract003_fix2`; branch `task/LOOP1-CONTRACT-003`; predecessor `3fa33bba3053ef30293498aedf55ce8710b6cbaf`. This is development evidence only. Task remains `review`; S0 Gate remains NOT YET PASSED.
- Product changes: the FAILED send fixture now observes a single local item at FAILED, then SENT after a matching `(conversationId, requestId)` server Message, then terminal SENT after a later failure signal. The Query schema defines a `query.page` response capped at 100 items and an at-most-100 request; fixture pages link continuation tokens, compare returned count to requested size, and assert zero side effects. Denied Queries return no page. Both static Go and Java contract vectors were updated for the changed outcomes.
- Recorder prompt `P-aee6d189-546e-42e9-b5be-0399cbecd199`; run `R-20260928T132300Z-2ceed8fb-fea6-4ab2-9320-73547e743d4c`, mode `prospective_resume`. Startup inspection and initial direct baseline verification preceded Recorder start; they are incomplete pre-Recorder trace, not backfilled as full observation.

## Recorded checks

All commands below used `tools/research/recorder.py run-command --run-id R-20260928T132300Z-2ceed8fb-fea6-4ab2-9320-73547e743d4c --` with the bundled `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` where `python.exe` appears. Elapsed times are Recorder `duration_ms`.

| Command after `--` | Exit / elapsed | Result |
| --- | --- | --- |
| `python.exe contracts/plugin-api/verify.py` | 0 / 172 ms, then 0 / 109 ms after adding three further controls | PASS: 79 cases, 22 positive, 57 negative, SP-A-001..013, now 16 mutation controls. Earlier development failures while repairing fixtures are retained in the Recorder. |
| `python.exe spec/progress/evidence/LOOP1-CONTRACT-003/review1-negative-probe.py` | 0 / 125 ms | PASS: 0/7 prior invalid mutations accepted. |
| `python.exe spec/progress/evidence/LOOP1-CONTRACT-003/review2-negative-probe.py` | 0 / 109 ms | PASS: 0/2 Review 2 invalid mutations accepted. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 / 2344 ms | PASS, explicitly non-acceptance Development mode. |

`git diff --check` exited 0. The frozen Markdown and historical PDF SHA-256 values matched the manifest during startup inspection. The Recorder finished with result `PASS`, 30 events, and `validate-run` exited 0; this verifies research artifact integrity only. No Frozen Architecture, ACK, security, or HTTP schema-lint path was edited.

## Remaining interpretation

SP-A-012 profile artifacts are separately stored static normalized **contract vectors** initialized from canonical fixtures; they are not Go or Java backend output. The Task forbids runtime implementation, while the frozen Stage schedule places dual-profile Golden Test PASS in S3. The smallest acceptance question remains: at S0 contract freeze, are distinct static expected vectors sufficient, with actual backend-produced A/B evidence deferred to S3, or is live profile execution required for this Task? A fresh independent reviewer or Architect must resolve this before Task PASS.

## Handoff

The fresh independent reviewer should inspect this committed candidate, rerun the baseline verifier and both permanent probes, validate Recorder integrity, and perform CTRL-002 Acceptance only in a clean committed checkout. The Fix Agent does not self-accept or move the task to `done`.

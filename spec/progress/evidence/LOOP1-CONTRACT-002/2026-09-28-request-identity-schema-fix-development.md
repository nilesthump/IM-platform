# LOOP1-CONTRACT-002 Review 6 fix: development evidence

- Fresh Fix Agent `/root/contract002_fix6`; base was clean `5e68af0433dcc726519deced98b09fb290c6391c` on `task/LOOP1-CONTRACT-002`. This is development evidence, not independent acceptance.
- Canonical Markdown and historical PDF hashes matched their manifest values `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Prompt `P-8c4f0e33-9c8d-4a95-ba64-547d848fa419`; Recorder run `R-20260928T060018Z-0daae2f5-d6ee-4d1a-a688-39bb16513878`, `prospective_resume`. Startup, authority inspection, and baseline preceded the run and are outside a complete prospective trace. The first prompt-registration attempt was denied by the read-only sandbox; the authorized retry succeeded.

## Repair

`check_declared_behavior` requires the two distinct out-of-order Messages in one Conversation to have distinct `requestId`s. A permanent mutation gives the seq-1 event the seq-2 request identity and verifies rejection. `lint_schema` now checks the shapes of the JSON Schema keywords used by the WSS contract, including supported `type` values and nested schema containers. Seven permanent malformed-keyword mutations cover invalid and unsupported type values, malformed `required`, `properties`, `allOf`, `additionalProperties`, and `minLength`. The linter intentionally rejects valid but unsupported JSON Schema type unions because the local validator does not implement them. Canonical schema and golden fixtures remain unchanged.

## Verification

Commands below ran through bundled Python `tools/research/recorder.py run-command --run-id R-20260928T060018Z-0daae2f5-d6ee-4d1a-a688-39bb16513878 -- <command>`. Bundled Python is `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Durations are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed ms | Result |
| --- | ---: | ---: | --- |
| Bundled Python `contracts/websocket/verify.py` | 0 | 78 | PASS: 8 positive/10 negative; 18 schema and 26 behavior mutations rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 78 | Prior 12/12 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 63 | Prior 24/24 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 0 | 62 | Prior 9/9 rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | 0 | 63 | Cross-Conversation invalid case rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review6-mutations.py` | 0 | 47 | Both Review 6 invalid cases rejected. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 1172 | PASS: task recovered in `review`; non-acceptance mode. |
| `git diff --check` | 0 | 31 | PASS. |
| `git diff --exit-code 5e68af0 -- contracts/websocket/envelope.schema.json contracts/fixtures/websocket/golden.json contracts/errors contracts/http spec/architecture` | 0 | 31 | PASS: canonical contract and frozen authority files unchanged. |

Review must verify the clean candidate independently, including CTRL-002 Acceptance. S0 Gate remains NOT YET PASSED. Original `H:\IM-platform` untracked `contracts/http/schema-lint/` was not accessed.

Recorder run finished `PASS` with 22 events; `validate-run` exited 0. A run-local `blobs/.gitattributes` preserves raw output bytes through Git. All 18/18 command-output blobs matched event SHA-256, working bytes, and staged Git bytes. Focused staged diff whitespace check passed. Recorder integrity is separate from task acceptance.

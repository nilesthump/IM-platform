# LOOP1-CONTRACT-002 checkout portability fix: development evidence

- Fresh Fix Agent: `/root/contract002_portability_fix`; branch `task/LOOP1-CONTRACT-002`; clean base `9b5210f7b3042be477ce826a36333356faa4ffe6`. This is development evidence, not independent acceptance.
- The original integration failure remains recorded in `2026-09-28-post-main-merge-fail.md`. On clean local `main` with `core.autocrlf=true`, Git changed the generated golden fixture's working bytes while reporting a clean status. The WSS verifier compares exact deterministic bytes, so it rejected that checkout. The committed fixture blob is `b7c23c4c300ed2acbcffaa9183f8889a5772f4f3`.
- Repair commit `59bc411be40dd33744f59b12055f5eb0931c96a5` adds only `contracts/fixtures/websocket/.gitattributes` and the disposable-worktree regression script. The fixture-local `golden.json -text` attribute leaves the exact committed JSON bytes intact under both checkout settings. Exact byte comparison remains valuable because it catches generator drift; canonicalized JSON comparison would hide byte changes in the shared golden artifact. No WSS schema, generator, fixture, wire semantics, ACK, authentication, or authorization changed.
- The regression `verify-checkout-portability.ps1` created separate detached clean worktrees from the committed fix, one with `core.autocrlf=true` and one with `false`. Each had empty `git status --porcelain=v1`, working-file hash equal to the committed `golden.json` blob, and a passing WSS generator/verifier. Both disposable worktrees were removed. This reproduces the integration condition rather than relying on the original task checkout.
- Canonical Markdown and retained PDF SHA-256 matched the manifest: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91` and `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`.
- Recorder prompt `P-1e0f7ed9-541e-4fe6-b5de-89e8a3485513`; run `R-20260928T083213Z-9aaad4eb-0bfa-4998-9604-000a450420e6`, `prospective_resume`. Startup and baseline preceded the run and are not claimed as a complete prospective trace. An initial PowerShell prompt piping attempt created an empty, unlinked prompt registration; that task-local artifact was removed before the run. The valid registered prompt and run are retained.

## Recorded verification

Commands below were run through `tools/research/recorder.ps1 run-command --run-id R-20260928T083213Z-9aaad4eb-0bfa-4998-9604-000a450420e6 -- ...`; the Python executable was `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Times are Recorder `duration_ms`.

| Exact command after `--` | Exit | Elapsed ms | Result |
| --- | ---: | ---: | --- |
| `pwsh -NoProfile -File spec/progress/evidence/LOOP1-CONTRACT-002/verify-checkout-portability.ps1` | 0 | 9846.3483 | PASS in clean `true` and `false` checkouts; both fixture hashes `b7c23c4c300ed2acbcffaa9183f8889a5772f4f3`; both WSS verifiers PASS. |
| Bundled Python `contracts/websocket/verify.py` | 0 | 80.3047 | PASS: 8 positive, 10 negative shared Go/Java scenarios; 18 schema and 26 behavior mutations rejected. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-rereview-mutations.py` | 0 | 71.958 | Rejected 12/12 invalid mutations. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review3-mutations.py` | 0 | 71.7144 | Rejected 24/24 invalid mutations. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review4-mutations.py` | 0 | 61.6957 | Rejected 9/9 invalid premises. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review5-mutations.py` | 0 | 59.5088 | Rejected cross-Conversation mutation. |
| Bundled Python `spec/progress/evidence/LOOP1-CONTRACT-002/2026-09-28-independent-review6-mutations.py` | 0 | 64.1034 | Rejected both duplicate-identity and malformed-schema mutations. |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 663.1409 | PASS: both frozen provenance hashes. |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | 1060.2969 | PASS: exact current task recovered in `review`; development mode only. |

The first Recorder-wrapped CTRL-002 Development run also passed, exit 0 in 1295.6278 ms. Focused `git diff --exit-code 9b5210f -- contracts/websocket contracts/errors contracts/http contracts/fixtures/websocket/golden.json spec/architecture spec/domain spec/invariants spec/acceptance` exited 0, showing protected product and authority files unchanged from base. `git check-attr -a -- contracts/fixtures/websocket/golden.json` exited 0 and reports `text: unset`. Recorder run finished `PASS` with 32 events and `validate-run` exited 0. Its 28/28 command-output blobs have matching event SHA-256, working bytes, and staged Git bytes; the staged prompt hash also matches its metadata and Git blob. The run-local `blobs/.gitattributes` preserves raw output bytes. Focused staged diff whitespace check passed outside immutable output blobs and the captured `diff.patch`.

## Handoff

The task remains `review`, and S0 Gate remains NOT YET PASSED. A different fresh independent Review Agent must verify the clean final candidate, including checkout portability and CTRL-002 Acceptance. The Coordinator must then repeat local-main integration checks before closure. `origin/main` is still at `7484901`; this Fix Agent neither merged nor pushed. The original `H:\IM-platform` untracked HTTP schema-lint directory was not touched.

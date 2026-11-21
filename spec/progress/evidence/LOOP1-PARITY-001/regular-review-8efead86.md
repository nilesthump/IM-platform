# Independent regular review of LOOP1-PARITY-001

Verdict FAIL. Reviewed by /root/review1, a fresh delegated agent with no implementation or fix involvement. Task branch task/LOOP1-PARITY-001. Range 3a5a54abff6410762d2039c4acf880abbe3269a5..8efead861e5f7524f05d477abb904b3cd569c33d. App-created detached worktree H:/.codex/worktrees/pr1/IM-platform. Git verified the assigned root and exact HEAD. Porcelain status empty before and after review. No candidate files modified.

1. Recovery contract fails on this clean candidate. Current progress omits the required Current Blockers, Verification and Changed Files or Migrations headings and its verifier cannot identify the exact command, result or durable evidence. The task combines Evidence and Handoff, omits Next Action and exposes no discoverable tools/ verifier. Restore required sections and include the working Control Acceptance command.
2. ci/classify.py selects the new Java parity job on Compose YAML changes but misses deploy/Caddyfile and deploy/migrate.Dockerfile consumed directly by those same deployments. The classifier reproduces deploy=true and java=false for these inputs. Deployment smoke only exercises Go's full TLS product flows. Include both inputs and regression assertions to preserve Java/Web verification on deployment changes.

The diff is confined to the task paths. The existing Web npm-locked build helper is reused, the same output tree is hashed and passed into each real profile, and the compiled production WebClient owns protocol operations after account setup. The unchanged TLS fixture checks durable outcomes, replay, authorization and revocation. Existing Auth and Group fixtures and TLS Sync jobs exercise both profiles. No new runtime, browser UI, protocol implementation or dependency enters the product. Frozen Markdown SHA-256 a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef. ADR-0004's single deferred case was reported on both profiles. Sections 11, 15 and 20 require the canonical vectors, S3 backend equivalence and unchanged client, with live plugin runtime responsibilities in S4.

| Exact command (python denotes the bundled Python 3) | Exit | Elapsed | Observation |
|---|---:|---:|---|
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 2.000s | PASS |
| python -Xutf8 -B -m unittest discover -s tests/ci -q | 0 | 10.687s | 41 tests, four skipped |
| pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance | 1 | 43.750s | 10 candidate defects above with Python 3 first on PATH. Initial run used Python 2.7 and reported one additional environment failure in 44.719s. |
| python -Xutf8 -B ci/classify.py --base 3a5a54ab --head HEAD | 0 | 0.844s | All 14 classifier flags true on actual candidate |
| python -Xutf8 -B ci/classify.py --paths deploy/Caddyfile deploy/migrate.Dockerfile | 0 | 0.360s | Only deploy true |
| python -Xutf8 -B tests/e2e/parity.py | 0 | 120.718s | Two clean TLS deployments, same SHA-256 58bc0ef831639eecea2a71fec77db588a5b32a93e13efe05b96aebcb6b017577, both owned projects cleaned. Initial sandboxed invocation failed in 2.578s on npm cache permissions. |
| git diff --check 3a5a54ab HEAD | 0 | unavailable | Clean |

External Recorder R-20261121T072804Z-769262af-7323-4088-af03-9e86a731a19d, linked to coordinator R-20261121T070901Z-3e845e2e-3f89-4a05-8fb2-99ef8644a952, finished FAIL and validated with 20 events. Initial register-prompt via base64 stdin rejected line ending. Retried successfully with the UTF-8 prompt file before review commands. Fresh fix, new independent regular review and then different fresh specialist review required before candidate push. S3 remains OPEN.

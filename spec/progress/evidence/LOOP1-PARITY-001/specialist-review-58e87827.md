# Independent pre-CI error-handling review • FAIL

Task LOOP1-PARITY-001. Reviewer /root/specialist, a fresh delegated context with no implementation, fix or regular-review participation. The coordinator supplied regular PASS at this same commit before dispatch. Detached clean app checkout H:/.codex/worktrees/pr2/IM-platform, task branch task/LOOP1-PARITY-001, exact range 3a5a54abff6410762d2039c4acf880abbe3269a5..58e878271b94e4aee96e347718156104ba112aa9. Start and end porcelain empty. Neither the candidate nor any remote refs were changed. Canonical Markdown a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef and historical PDF 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 match the manifest.

## Blocking findings and deterministic fault probes

1. tests/e2e/parity.mjs:80-83, new runner. A failed registration and a failing first disposal produce only the disposal exception. Bob.dispose never runs. The external Node fixture exercised the actual committed runner and emitted only "dispose 1" and "first client cleanup fault"; "original registration fault" disappeared. Attempt both disposals and preserve both primary and teardown causes, surfacing one original cause when only one fails. Emit the overall PASS only after successful teardown.
2. tests/e2e/go_tls_messaging.py:195-201, 214-222. The extracted run_profile now drives parity on each profile. All docker cp errors become missing-CA readiness and all health OSErrors become waiting for Gateway. Fault injection reproduced a Docker permission error and a TLS certificate verification failure independently. Each consumed all 60 attempts and ended with only generic unavailability, both __cause__ and __context__ None. Limit readiness handling to actual CA-not-created and documented transient startup failures. Propagate other errors with their diagnostic and retain the last transient cause on deadline. Keep certificate verification and time bounds.
3. tests/e2e/go_tls_messaging.py:406-409. The first socket close exception stops all future teardown, including Compose removal. socket_cleanup.py exercised the committed function with an operation failure and two registered resources. The call trace ended after close 1, with no second close or invocation of the Compose teardown. Python preserved the operation as exception context, but the resources were skipped. Attempt every owned socket and the existing ownership-checked project cleanup even when an earlier release fails; surface failures with their causes.

The probes use controlled faults in external adapters to exercise failure branches without modifying candidate files. Review gates require explicit failure, truthful classification, retained original causes and actual teardown. The CLI printed the initial Windows path import error on the first Node probe; using a file URL ran the intended reproduction. No hosted CI or live Docker rerun claimed. Architecture baseline exited zero. Product and contract trees are byte-identical throughout the candidate diff.

## Catch and fallback audit

- Web verify.py CLI catches recognized validation, OS, parser/key and subprocess errors and prints a nonzero FAIL. build_web raises for missing npm/output; checked npm install/build failures propagate. Existing pre-product skeleton recognition requires exact proof and runs boundary checks, product verification cannot fall back to the marker. Local compared_base uses committed HEAD per verifier authority; new branch uses empty tree, unsupported events fail. No new product runtime or dependency.
- parity.py has no exception handler; hash/read/build/profile/temporary-directory errors propagate. Hash mismatch raises. The selected optional artifact argument preserves the standalone established TLS entry point; parity passes it on both profiles.
- parity.mjs register asserts HTTP status; failed JSON, promises, predicates and assertion failures escape the body. until bounds asynchronous observation; Promise.all login/logout rejection fails; subprocess timeout is enforced by its parent. The two finally disposals are finding 1.
- go_tls_messaging.py:51,54 distinguish fixture UUID/timestamp placeholders from literals; actual invalid identity/time and literal mismatches fail. :115 quiet requires a bounded silent window; returned frames fail. :125 read EOF/close is expected only for a required revocation close. :198,:219 readiness handlers are finding 2. :227 checks untrusted-authority probe, :252 demands hostname mismatch, neither allows a successful invalid handshake. :256 reinstates and verifies exact Caddy configuration; :382 drops only the injected test trigger/function. :406 teardown is finding 3. docker() nonzero includes stderr, SQL uses ON_ERROR_STOP, subprocess timeout and child nonzero are fatal. Optional absence of client artifact only serves the original standalone entry. ADR-0004 defers one named input explicitly.
- Workflow selected Java branch runs both parities and Sync steps without a continue-on-error. Classifier adds applicable Java paths. CI tests check the routing and workflow commands with assertions. Administrative records contain no runtime catches. No production Java/native/Go/Web imports, contracts or protocol logic changed. Narrow harness corrections suffice.

## Candidate file inventory

SHA-256 values below cover the exact checked-out files at the reviewed commit. Roles in the inventory distinguish the actual functional and administrative review surfaces.

.github/workflows/ci.yml | db77da35df2726b5838c4fc45f94de21b38f8c80021afba27e78be3a5725a811 | hosted steps propagate nonzero
ci/classify.py | 18361f728bbaeca5a4dc1084cd1fec9a53bafc038399e496b63f411aba48afec | adds parity inputs, no exception translation
spec/progress/current.md | 7c07c0400a6be05b33f190a4ed7650fca701df36d163f1b3f3931a1a6ca41f20 | task recovery only
spec/progress/evidence/LOOP1-PARITY-001/implementation.md | d22176cc0fe516402db291052ba77a0489f0d3a5a9bbb32f82064ff0687d5929 | local evidence
spec/progress/evidence/LOOP1-PARITY-001/regular-review-8efead86.md | 89d003b59c8874c0b9b98f691ef1a3f4c06e3f449bfbb081401d68e5d93b3507 | earlier immutable regular FAIL
spec/tasks/review/LOOP1-PARITY-001.md | 89128e63ffbda45b1995d4e92bcb8513f1889eb21fd2a07b8d1eb364155ee735 | task scope and gate
tests/ci/test_classify.py | 5315693de6a80735a490b780ebae43d8cbaea606f3b329035c5be6b947fe6344 | path expectations and assertions
tests/ci/test_java_im_job.py | 10ed46c89d165cf4bbd7b53ff90e826117be6b615334f887ac03a56f92c60769 | live job routing and command assertions
tests/clients/web/verify.py | 783434ebffe6df13d9a49b2eb8b0821a0c0150108ea0ec529b9484084294f4c1 | actual locked build, fail-closed
tests/e2e/go_tls_messaging.py | 45677f390521e23c929c39c819426b6f337fe250670402f7c0f6280d9c524543 | TLS fixture, findings 2 and 3
tests/e2e/parity.mjs | 59dbd8dd46fcd25ed5fc6bb9b5d548d6fc34c2f30ded967aec79e9c28b8bded8 | Web parity fixture, finding 1
tests/e2e/parity.py | f9f03f273a60c4fba31101990c70580c7d4fad96c64d0733d58e760f4e56d771 | single build and identical digest, no catch

## Recorded command, exit and elapsed time

git rev-parse --show-toplevel | 0 | 47 ms
git rev-parse HEAD | 0 | 31 ms
git status --porcelain=v1 -b | 0 | 93 ms
git diff 3a5a54abff6410762d2039c4acf880abbe3269a5 HEAD --name-status | 0 | 31 ms
git log -3 --oneline | 0 | 47 ms
C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1015 ms
node --import C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/fail-fetch.mjs tests/e2e/parity.mjs C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/fixture https://localhost | 1 | 62 ms
node --import file:///C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/fail-fetch.mjs tests/e2e/parity.mjs C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/fixture https://localhost | 1 | 78 ms
C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/readiness.py | 0 | 406 ms
C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B C:/Users/21441/.codex/visualizations/2026/11/21/01a1fced-3275-7091-a51c-3a6c9028d457/parity-specialist-58e87827/socket_cleanup.py | 0 | 437 ms
git status --porcelain=v1 -b | 0 | 78 ms

Recorder R-20261121T074502Z-d23747c3-36c8-4db9-a07c-00853b3d92b5 finished FAIL and validated, 26 events. Parent R-20261121T070901Z-3e845e2e-3f89-4a05-8fb2-99ef8644a952. Probe inputs and command output hashes reside alongside this report. Routine discovery before initial recording included startup instructions, authority resolution and finding Python. Next action is fresh Fix, fresh regular review and different fresh specialist on the resulting candidate before any CI-triggering push or PR. S3 remains open.

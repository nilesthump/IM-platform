# Independent error-handling review of LOOP1-PARITY-001

PASS on d990c0459f93576ba0d9951abaab9a5f2fa18f26, task/LOOP1-PARITY-001, base 3a5a54abff6410762d2039c4acf880abbe3269a5. Fresh delegated /root/specialist2 participated in neither implementation, repair nor regular review. Fresh /root/review3 regular PASS was confirmed on this SHA before the specialist verdict. Initial and final Git porcelain empty in the assigned, detached H:/.codex/worktrees/pr2/IM-platform. Canonical a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef and historical PDF 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 matched manifest. Reviewed candidate changes within harness, CI and governance records. Product code and contracts retain their base bytes.

## Error and recovery paths

- parity.mjs body catch records the actual failure, including synchronous construction, registration, rejected application calls, deadline and assertion failures. Each constructed client is registered before constructing the next. Each dispose catch preserves its own error and continues disposal. Single failures rethrow the same value. Multiple failures throw AggregateError containing all original exceptions. Success prints only after disposal. Sequential login/logout avoid unfinished sibling operations. Product dispose is synchronous. Registration JSON/status, UUID and wait predicates have no default success.
- go_tls_messaging.py wait_for_startup retries missing generated CA only when the command reports the expected file and container, and retries verified-gateway startup only for refused/reset/timeout or 502/503. Other Docker, certificate, HTTP or internal failures propagate immediately. The retry deadline raises from the final failure. Unexpected readiness response/role fails. Fault injection confirmed single attempt for permission, certificate and HTTP 403, bounded retries with last cause for the generated CA and refused connection, and recovery through refused/502 to success.
- go_tls_messaging.py run_profile registers ownership-checked Compose teardown first, then a close per constructed socket before sending bind. ExitStack attempts all registered actions in reverse acquisition order, preserving exception context. Test independently exercised simultaneous body, two close and down errors. Original socket close on stale token remains idempotent. Failed ownership verification or down is fatal. Optional artifact argument serves the existing standalone TLS suite. Dual-profile entry supplies the artifact on both calls. Nonzero or timeout from Node and Docker propagate. SQL uses ON_ERROR_STOP.
- Oracle.check catches ValueError only to distinguish canonical UUID/timestamp placeholder from exact string literal. Malformed actual values or mismatched fields fail. WS.quiet accepts only socket timeout in the expected silence interval and restores timeout. WS.closed accepts expected EOF or WebSocket close and rejects unexpected delivery. Untrusted-CA and wrong-host probes verify reason and fail on successful invalid handshake. Caddy negative test restores and verifies original config in finally. SQL finally removes the injected trigger/function. Call's empty-body {} permits the pre-existing empty logout response; required response fields/shapes are asserted at their use. ADR-0004's single deferred Friend case is reported explicitly.
- parity.py propagates build, profile, temporary directory, file-read and digest failures. Both profiles share the one build. tests/clients/web/verify.py uses checked npm invocations, tests required outputs, and fails on missing input/tooling. Its existing CLI turns recognized validation/OS/subprocess exceptions into status 1. Exact prerelease skeleton marker is an explicitly separate verified prerequisite state. The parity build has no marker fallback. Previously approved local/empty-branch Git base rules have no product impact.
- CI classifier adds applicable Java inputs. Selected workflow runs parity failure checks, both live profiles and both Sync suites; each command must succeed. CI tests assert path routing and job commands. test_parity_failures.py explicitly asserts exceptions and child exit codes. Administrative records carry no executable catch/fallback. No new dependency, production runtime, shared handler, replacement fixture contract or speculative recovery mechanism.

## Verification

Four failure tests passed against real Node runner and injected Python boundaries. The regression assertions cover all three previous blocking findings. Architecture baseline succeeded. CI unit suite ran 41 tests with four pre-existing environment skips. The separate fresh regular review ran real profiles on this commit. Specialist scope here was deterministic fault verification and logic inspection. Git rejected the Windows device NUL as an excludes file during a final status probe. Repeating with the repository info/exclude yielded empty porcelain, exit 0. An initial authority-discovery query printed rg help from -h; subsequent reads inspected the selected inputs. Bootstrap discovery predates instrumentation and is declared in prospective_resume.

Recorder R-20261121T080914Z-deac87be-c27e-4fe4-9ccc-2cd46072673b, parent R-20261121T070901Z-3e845e2e-3f89-4a05-8fb2-99ef8644a952. No candidate edit or push. Next action is exact-head hosted acceptance, protected integration and actual-main verification/synchronization. S3 OPEN.

## Changed file SHA-256

.github/workflows/ci.yml  e91c0f2c072d8986d4034a3e999e6c822d100b8f622f0f3d12b26f100fd3bde8
ci/classify.py  499afd673c62999b8c87e12aec34dfb40806e755f19f1e7e919c853edc629127
spec/progress/current.md  4917694c8b21732d21052c79c1a7008d20446aef631958470e458b8a5a9d1930
spec/progress/evidence/LOOP1-PARITY-001/fix-58e87827.md  28b0028c1feaef2c1aca4eb06d7555538794f61988e226f34365228c68eb33b6
spec/progress/evidence/LOOP1-PARITY-001/implementation.md  d22176cc0fe516402db291052ba77a0489f0d3a5a9bbb32f82064ff0687d5929
spec/progress/evidence/LOOP1-PARITY-001/regular-review-58e87827.md  38b6d613043658382ebbb0c2470e6f73a4c7486ef6514105810a465b89b4e0f3
spec/progress/evidence/LOOP1-PARITY-001/regular-review-8efead86.md  89d003b59c8874c0b9b98f691ef1a3f4c06e3f449bfbb081401d68e5d93b3507
spec/progress/evidence/LOOP1-PARITY-001/specialist-review-58e87827.md  364a7da3bfdd02516af49825a30c1f787a4a6e4daf7fc69de24d3139c6ffc605
spec/tasks/review/LOOP1-PARITY-001.md  eed8629b8545877558bba11643db93774e3b01652fdffa139a7fe13087fe334b
tests/ci/test_classify.py  23468eecd507eaf2f0e2cfb6aba25d615652186f987529dc095bb50d9112a119
tests/ci/test_java_im_job.py  10ed46c89d165cf4bbd7b53ff90e826117be6b615334f887ac03a56f92c60769
tests/clients/web/verify.py  783434ebffe6df13d9a49b2eb8b0821a0c0150108ea0ec529b9484084294f4c1
tests/e2e/go_tls_messaging.py  403ac33b2e60d7ac252bf524f1794ce06c26dea733e94a957f856cd52fb6c5ef
tests/e2e/parity.mjs  cb557ff85f0c3b30940056667b343fcdbf71cd3970e586d7edc75b5932ba620b
tests/e2e/parity.py  f9f03f273a60c4fba31101990c70580c7d4fad96c64d0733d58e760f4e56d771
tests/e2e/test_parity_failures.py  633d3f70a85ec8581a05a47fdb594e35c67a08b4e4277ec1c476ec5b33ae558d

## Recorded commands, exit and duration in milliseconds

pwsh -NoProfile -Command rg -n "^#{1,4} (2\.3|3\.|6\.1|10\.|11\.|12\.|15\.|20\.)|SRC-0|S3.*[Pp]arity" spec/architecture/frozen-architecture.md; rg -ih "parity|回滚|cleanup|rollback|拒绝|retry|失败" spec/architecture/decisions/ADR-00{04,07,08,13,14}*; Get-Content AGENTS.md | Measure-Object -Line | 0 | 437
git rev-parse --show-toplevel | 0 | 31
git rev-parse HEAD | 0 | 32
git status --porcelain=v1 | 0 | 62
git diff | 0 | 62
git diff --stat 3a5a54ab HEAD | 0 | 47
git log -3 --oneline | 0 | 47
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1203
git diff 3a5a54ab HEAD -- tests/e2e/go_tls_messaging.py tests/clients/web/verify.py | 0 | 62
git show HEAD:tests/e2e/parity.mjs | 0 | 47
git show HEAD:tests/e2e/parity.py | 0 | 47
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tests/e2e/test_parity_failures.py | 0 | 563
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/ci -q | 0 | 10312
git -c core.excludesFile=NUL status --porcelain=v1 --untracked-files=all | 128 | 63
git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 78

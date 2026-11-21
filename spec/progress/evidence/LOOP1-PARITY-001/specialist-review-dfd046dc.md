# Independent error-handling review of LOOP1-PARITY-001

PASS. Fresh delegated specialist /root/s4 inspected task/LOOP1-PARITY-001 from 3a5a54abff6410762d2039c4acf880abbe3269a5 to dfd046dc29e16bf8531723539e5652b34d9e5f65 on clean, detached H:/.codex/worktrees/pr1/IM-platform. I did not implement, fix or perform regular review. I checked the exact-candidate regular PASS report by /root/r4. The root and initial/final clean status matched. Architecture Markdown and historical PDF matched manifest SHA-256 a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef and 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510. No product, public contract, schema, technology or runtime responsibility changed.

## Findings

No blocking finding. The current shared ledger test locates the actual run_profile function, exact docker/compose/sql helpers and unique canonical migration assertion. Missing structure, different SQL, malformed native output or a changed response fails. Its ten cases accept only the two ordered exact migration IDs. Concatenated/newline-containing rows, comma data, empty/missing/extra/duplicate/reordered/case-changed rows fail. Native exit 37 must surface the stderr sentinel. Both CLI and parity paths reach run_profile. The shared job runs the entire group test suite, independent single-file classification tests cover both the ledger regression and its source runner, and all fourteen candidate flags were selected. Workflow parity and Sync steps propagate native failures. Tests/CI command checks and task recovery/evidence records do not provide a catch or skip path.

## Retained exception boundaries

- tests/e2e/parity.mjs records the body rejection and every dispose failure individually, attempting every registered client. One failure throws the original and multiple failures retain all causes in AggregateError. The success message follows disposal. Registration, assertions, waits and application calls fail normally. Sequential awaits avoid an outstanding sibling login/logout.
- tests/e2e/go_tls_messaging.py wait_for_startup catches RuntimeError/OSError only when the predicate identifies a known startup condition. For CA copying only the missing generated file on this exact container qualifies. For gateway readiness only refusal/reset/timeout or HTTP 502/503 qualifies. Unexpected TLS errors, permission failures, wrong role and other responses propagate. Sixty exhausted attempts retain the final causal error. ExitStack attempts every registered socket close and then ownership-checked Compose teardown even with multiple failures. The Python exception chain preserves body, close and teardown errors. Node nonzero/timeout, Docker nonzero and SQL errors fail the operation.
- Oracle.check handles expected fixture UUID parse failure by testing timestamp format, then literal equality. Invalid actual UUID/time fails. WS.quiet accepts only socket timeout for a required silence window and restores the read timeout. WS.closed accepts EOF/close for revocation. TLS negative probes check untrusted peer and name-mismatch verification failures, and fail if a forbidden handshake succeeds. The temporary Caddy policy is restored and checked in finally. The rollback injection's finally drops the injected database trigger/function. An empty HTTP body is allowed at logout. Other required fields are asserted at consumption. Standalone optional artifact argument preserves the existing messaging-only runner while parity always supplies the build. ADR-0004 retains the one explicit Friend deferral.
- tests/e2e/parity.py propagates build/read/hash/profile errors and compares the actual artifact after each profile. tests/clients/web/verify.py raises on npm absence, nonzero builds and missing artifacts. Existing CLI validation/OS/subprocess catches exit nonzero. The historical exact empty marker and local/new branch comparison rules remain confined to existing verifier paths. tests/e2e/test_parity_failures.py checks specific fault outcomes and process exit. The four fault tests exercised the three previous review findings. No compensating product layer or added runtime dependency.

## Verification and scope

All 29 shared group tests, four runner fault tests, 19 classify tests and two Java-job tests passed. Architecture checker returned no violations. /root/r4 independently ran live Go and Java on this exact head. This specialist verified faults and CI selection. Local review is complete. Exact-head hosted push/PR, protected integration, actual-main and main synchronization remain coordinator work. S3 OPEN. No candidate writes or push.

External Recorder R-20261121T103134Z-a327a795-1a13-4411-a041-d906293502ea related to R-20261121T100440Z-803fce8c-4506-44dd-9a70-6f7944795344 finished and validated. Startup reads preceded recording and are marked prospective_resume. An initial start-run invocation incorrectly passed prompt registration JSON. Retrying with its prompt_id succeeded. Initial Git status warned about an unreadable user ignore file. Both explicit exclude-file checks returned clean.

## Recorded commands, exit and elapsed milliseconds
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1204
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tests/e2e/test_parity_failures.py | 0 | 562
git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 109
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/contract/group -p test_*.py -v | 0 | 65969
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/classify.py --base 3a5a54ab --head HEAD | 0 | 1672
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/ci -p test_classify.py -q | 0 | 3063
C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/ci -p test_java_im_job.py -q | 0 | 265
git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 78

## Changed file SHA-256
.github/workflows/ci.yml  e91c0f2c072d8986d4034a3e999e6c822d100b8f622f0f3d12b26f100fd3bde8
ci/classify.py  76f25ffa7854e44a5effa7ecef6b52f466b8c71b6e38d42411621d912fb0df9a
spec/progress/current.md  f81f88d5699b310c22727422ba6b92169ba384e1f8dd0c313433ba25d8303a6b
spec/progress/evidence/LOOP1-PARITY-001/fix-58e87827.md  28b0028c1feaef2c1aca4eb06d7555538794f61988e226f34365228c68eb33b6
spec/progress/evidence/LOOP1-PARITY-001/hosted-fix-d990c045.md  c3dae10a362035a8434f5a511b408c993aaa8ae81ed7d5e4db402d0649b6cbed
spec/progress/evidence/LOOP1-PARITY-001/implementation.md  d22176cc0fe516402db291052ba77a0489f0d3a5a9bbb32f82064ff0687d5929
spec/progress/evidence/LOOP1-PARITY-001/regular-review-58e87827.md  38b6d613043658382ebbb0c2470e6f73a4c7486ef6514105810a465b89b4e0f3
spec/progress/evidence/LOOP1-PARITY-001/regular-review-8efead86.md  89d003b59c8874c0b9b98f691ef1a3f4c06e3f449bfbb081401d68e5d93b3507
spec/progress/evidence/LOOP1-PARITY-001/regular-review-d990c045.md  864b0b84d608bf25a6942ab754a84f7002ffaa23a3d28da81b58bb1cbab6e987
spec/progress/evidence/LOOP1-PARITY-001/specialist-review-58e87827.md  364a7da3bfdd02516af49825a30c1f787a4a6e4daf7fc69de24d3139c6ffc605
spec/progress/evidence/LOOP1-PARITY-001/specialist-review-d990c045.md  326bea2f4b3553c4d28238b1391a2ad138f5f32745993a016967b0b5f2c9bbd6
spec/tasks/review/LOOP1-PARITY-001.md  ba6658e79d9f0041c6699d9976cb455ecce3aa1a264726dd69b61380be29f772
tests/ci/test_classify.py  21177c03948b4393424e744f219b28ac5eaff1640da036429fcab15593d7eb9a
tests/ci/test_java_im_job.py  10ed46c89d165cf4bbd7b53ff90e826117be6b615334f887ac03a56f92c60769
tests/clients/web/verify.py  783434ebffe6df13d9a49b2eb8b0821a0c0150108ea0ec529b9484084294f4c1
tests/contract/group/test_verification_failures.py  591a0a84c00726e155d95947318586f2457c985053a40bc16f753860b308241d
tests/e2e/go_tls_messaging.py  403ac33b2e60d7ac252bf524f1794ce06c26dea733e94a957f856cd52fb6c5ef
tests/e2e/parity.mjs  cb557ff85f0c3b30940056667b343fcdbf71cd3970e586d7edc75b5932ba620b
tests/e2e/parity.py  f9f03f273a60c4fba31101990c70580c7d4fad96c64d0733d58e760f4e56d771
tests/e2e/test_parity_failures.py  633d3f70a85ec8581a05a47fdb594e35c67a08b4e4277ec1c476ec5b33ae558d

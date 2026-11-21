# Independent regular review of LOOP1-PARITY-001

Fresh reviewer /root/r4 had no implementation, fix or prior review role. Reviewed task/LOOP1-PARITY-001, range 3a5a54abff6410762d2039c4acf880abbe3269a5..dfd046dc29e16bf8531723539e5652b34d9e5f65. Verified managed H:/.codex/worktrees/pr1/IM-platform clean before switching the detached HEAD, and verified clean status on the exact candidate. The unique task remains in review, with accepted Java Auth and IM prerequisites and S3 OPEN. Review made no candidate edits.

Frozen Markdown and historical PDF match a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef and 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510. Reviewed sections 2.3, 3, 6.1, 10–12, 15, 20, named ADRs, governance, contract families and domain acceptance. All 20 diff paths are permitted. Production Web/SDK/service code, migrations, dependencies and contracts are unchanged. No additional product technology or future-stage mechanism. Existing canonical fixture suites drive both services. The Web build uses the existing npm lock and builds once. The Node driver imports compiled product WebClient, registers only its disposable accounts by HTTP, and uses the product for subsequent HTTPS/WSS operations. The test does not claim browser rendering.

Previously reported defects were independently examined. Control Acceptance now resolves all recovery fields; Compose, Caddy and migrate Dockerfile inputs select Java. Client failures preserve all disposal errors, ExitStack unwinds sockets and project teardown, documented startup failures have bounded retries with causes and unexpected exceptions propagate. The four dedicated runner fault tests passed. Previous PR109 shared failure arose because extraction looked for migrated helpers in main. In this candidate both entry points call run_profile; the regression compiles the actual docker/compose/sql helpers and ledger assertion there. Its unchanged ten transcripts accept the exact ordered two rows and reject ambiguous, missing, extra, duplicate, reordered and case-altered versions as well as native status 37. The latter must preserve its stderr sentinel. The complete group suite passed all 29. The updated path tests exercise each shared trigger on its own. The full candidate selects all fourteen job flags.

CI and architecture suites ran 41 and 99 tests, with four and one conditional skips respectively. Auth/group/Sync fixture CI steps are wired for both profiles, including explicit Sync runtime checks for Go and Java. ADR-0004's single friend-add authorization deferral remains visible. S4 owns live plugin permission tests. Regular review is distinct from the required separate error review, exact-head hosted runs, protected integration, actual-main verification and main synchronization.

External Research Recorder R-20261121T102347Z-52f26800-5fba-4e30-af1c-5f7f792c0928 is linked to parent R-20261121T100440Z-803fce8c-4506-44dd-9a70-6f7944795344. The registered prompt conveys the coordinator delegation and human authorization. Bootstrapping Git root selection and inspection preceded recording. Bundled Python 3 first on PATH, PYTHONDONTWRITEBYTECODE=1, UTF-8.


Independent live Go and Java reruns passed TLS peer controls, durable ACK/one Outbox, retry/conflict/nonmember and commit rollback, session revocation, Web login, DIRECT and GROUP exchanges, Sync and logout. Both owned Compose projects verified cleanup. The locked Web artifact was 58bc0ef831639eecea2a71fec77db588a5b32a93e13efe05b96aebcb6b017577 on both profiles. Final porcelain empty. Verdict PASS for independent regular review at dfd046dc. Recorder finished and validated.

| Command | Exit | Elapsed ms |
|---|---:|---:|
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0 | 1391 |
| pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance | 0 | 23282 |
| python -Xutf8 -B -m unittest discover -s tests/contract/group -p test_*.py -v | 0 | 70422 |
| python -Xutf8 -B tests/e2e/test_parity_failures.py | 0 | 531 |
| python -Xutf8 -B -m unittest discover -s tests/ci -q | 0 | 7703 |
| python -Xutf8 -B -m unittest discover -s tests/architecture -q | 0 | 27407 |
| python -Xutf8 -B ci/classify.py --base 3a5a54ab --head HEAD | 0 | 250 |
| python -Xutf8 -B tests/e2e/parity.py | 0 | 119844 |
| git -c core.whitespace=cr-at-eol diff --check 3a5a54ab HEAD | 0 | 63 |
| git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all | 0 | 63 |

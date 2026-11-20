# Fresh independent regular Review of LOOP1-JAVA-IM-001

PASS for 7ff6d1ed68dd30ec033b3e6f7f11c608cb216728, task/LOOP1-JAVA-IM-001. Base and range 18597c06f15c6ba5d50e055a88890a54f737fd52..7ff6d1ed68dd30ec033b3e6f7f11c608cb216728. Independently dispatched reviewer /root/regular6 did no implementation, fixes or prior review. Inspected managed detached checkout H:/.codex/worktrees/jir/IM-platform. The detached HEAD and task branch matched. The checkout had empty initial and final status. The control verifier independently resolved precisely one current review task and a clean candidate. No checkout writes or hosted submission.

Human-approved Go scope is respected. Core requires a lowercase request UUID before it can return an ACK, validates the conversation UUID before starting the transaction, and stores precisely the validated values. The Gateway correlation change runs only for message.send or its forwarded response. Unrelated social, login, ping and binding code retained its existing behavior. Both real TLS profiles passed the same uppercase-request close, uppercase-conversation rejection plus no durable effects, then authenticated lowercase success with identical correlation, first sequence, single message and Outbox plus recipient delivery, retry and conflict controls.

Reviewed the earlier failed reports and repairs, canonical hash, source rules, domain and contract inputs, actual imports, Core transactions, group receipts, actor-scoped Sync, Session/epoch locking, Outbox dispatch and Gateway delivery, CI selection and build inputs. Comparison against the independently inspected 57b98c54 proved all tracked inputs outside the listed final product/tests/task-record changes byte-identical. The current final-HEAD Java/Go/Java live fixture covered message and group transactions, rollback/unknown outcome and recovery, actor access and fan-out, profile continuity, delayed delivery and broken-peer isolation. The schema-backed date probes now exercise the previously failing signed extended year on committed ACK and event. Calendar date and clock/timezone syntax are checked before serializing or visiting any peer. No authority, dependency, migration or speculative mechanism introduced. Older Auth and standalone Sync runs remain historical evidence on unchanged runner/logic, see the prior reports. ADR-0004's one restricted friend scenario remains DEFERRED_BY_HUMAN.

Exact-head Control Acceptance, structural checks (99 architecture tests, one skip), canonical WSS verifier, external Maven build, live IM and both independent Compose TLS jobs passed. The classifier selects all 14 jobs. Remaining acceptance requires a different fresh error-handling specialist, hosted CI and protected integration/actual-main synchronization. S3 remains OPEN.

Advisories: default Windows git diff --check flags CR line endings and some trailing blank EOF lines. With cr-at-eol enabled just five EOF findings remain. These are formatting observations outside required acceptance. The first sandbox Maven testCompile could not resolve the external compiled classes; host-access rerun passed. Git reported an inaccessible existing user global ignore file while explicit status including all untracked entries was empty. Startup reads, direct inspections and initial Python/CLI selection/parsing errors were outside recorder commands. Recorder was finished and validated, 38 events.

## Exact commands and results

- Exit 0, 31 ms: git rev-parse HEAD refs/heads/task/LOOP1-JAVA-IM-001
- Exit 0, 125 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- Exit 0, 1344 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- Exit 0, 20531 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- Exit 0, 22750 ms: pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
- Exit 0, 93 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 125 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/classify.py --base 18597c06 --head HEAD
- Exit 1, 3375 ms: mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp/im-review6-7ff6d1e/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp/im-review6-7ff6d1e/build/classpath.txt
- Exit 0, 5516 ms: mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp/im-review6-7ff6d1e/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp/im-review6-7ff6d1e/build/classpath.txt
- Exit 0, 36015 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tests/e2e/go_tls_messaging.py --profile go
- Exit 0, 83953 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_java_im.py --build-dir C:\Users\21441\AppData\Local\Temp/im-review6-7ff6d1e/build
- Exit 0, 36406 ms: C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tests/e2e/go_tls_messaging.py --profile java
- Exit 0, 47 ms: git diff --exit-code 57b98c54 HEAD . :(exclude)backend/go/core/message.go :(exclude)backend/go/gateway/gateway.go :(exclude)backend/java/core/im/Messages.java :(exclude)backend/java/gateway/auth/Gateway.java :(exclude)backend/java/tests/im/MessageDeliveryProbe.java :(exclude)backend/java/tests/im/MessageOutcomeProbe.java :(exclude)tools/verify_java_im.py :(exclude)tests/e2e/go_tls_messaging.py :(exclude)spec/progress/current.md :(exclude)spec/progress/evidence/LOOP1-JAVA-IM-001/* :(exclude)spec/tasks/review/LOOP1-JAVA-IM-001.md
- Exit 2, 47 ms: git diff --check 18597c06..HEAD
- Exit 0, 31 ms: gofmt -l backend/go/core/message.go backend/go/gateway/gateway.go
- Exit 0, 94 ms: git status --porcelain=v1 --untracked-files=all
- Exit 0, 78 ms: git status --porcelain=v1 --untracked-files=all
Recorder R-20261120T133231Z-9c51b70a-defc-4be9-b962-235f0f1a41b5


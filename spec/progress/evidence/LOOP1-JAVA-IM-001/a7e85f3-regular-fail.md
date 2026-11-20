# Independent regular review of a7e85f34

FAIL. Fresh independent reviewer /root/regular3 took no part in implementation, fixing or prior reviews. Reviewed LOOP1-JAVA-IM-001 on branch task/LOOP1-JAVA-IM-001 against accepted main 18597c06f15c6ba5d50e055a88890a54f737fd52, range 18597c06f15c6ba5d50e055a88890a54f737fd52..a7e85f34ccc0cf9cccf942d51cd42fc4654751a5. Managed detached checkout H:/.codex/worktrees/jir/IM-platform resolved to that exact candidate, clean before review. All builds, evidence and additional positive-boundary probes were external.

## Required correction

The required clean Control Acceptance command exits 1 with "current.md Verification is missing a durable evidence path." In spec/progress/current.md the Evidence line combines two existing paths. tools/verify-loop1-ctrl-002.ps1 requires an Evidence line containing exactly one backticked path. Put each existing file on its own Evidence line, then rerun clean Acceptance. No change to product code, verifier or frozen authority is needed for this finding.

## Behavior and scope

Verified Frozen Architecture hashes/provenance, scoped ADR-0004/0008/0013/0014, approved technical stack, core/gateway dependencies, actual handlers, fixture and workflow enablement, minimality, diff paths and unique review queue. Core owns social/group/sequence transactions, receipts, Session authorization, Sync reads and Outbox. Gateway does transport, local session validation/watch and delivery. No new runtime dependency, migration, public contract, client, or Go product edit. The earlier sender/session lock-order finding is addressed by acquiring the user FK lock before the Session. Concurrent ADD/send use the same conversation/member order. IM live tests passed for missed Session retirement, lost/invalid private confirmation, durable original-identity retry, same-slot login overlapping public send, group transactions and both profile-switch directions. A lost confirmation leaves the outcome unconfirmed. No architecture decision is required.

ADR-0004 friend-add-authorization-denied remains DEFERRED_BY_HUMAN. The canonical WSS text maximum also passed a separate positive check against each real Gateway with 4,096 ASCII and 4,096 supplementary-plane characters per message. Gateway.afterConnectionEstablished sets the socket limit to 65536, overriding Tomcat's default.

## Evidence

Recorder R-20261120T122252Z-ea564419-09a7-40e7-82d0-ff3c24e70aaf. Initial startup reads, an invocation selecting Python 2, an absent py launcher and an incorrectly placed CLI flag preceded capture. Corrected to bundled Python 3, a registered prompt and prospective_resume. Additional read-only source inspections were direct. Commands below used a dedicated external Maven build and the coordinator's disposable PostgreSQL/NATS fixture; Docker checks use their own Compose projects. Hosted CI, specialist review and main integration are subsequent stages.

Final status was clean at the exact SHA. Real Java/Go Auth fixtures, credential switching, Java Compose TLS messaging and bulk Sync passed. An ordinary escaped serialization of the 4,096 supplementary characters (49,354 wire characters) also committed on both profiles. Architecture unit suite passed 99 tests with one skip. CI unit suite passed 41 tests with four environment skips. Exact command outcomes follow.

 - exit 0, 125 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_frozen_architecture.py
 - exit 0, 4859 ms, H:\apache-maven-3.9.15\bin\mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build/classpath.txt
 - exit 0, 75078 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_java_im.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build
 - exit 0, 1516 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
 - exit 0, 29250 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/architecture
 - exit 1, 30328 ms, pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
 - exit 0, 7157 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/ci
 - exit 0, 96360 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_java_auth.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build --profile java
 - exit 0, 109 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B contracts/websocket/verify.py
 - exit 0, 453 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B contracts/http/verify-group.py
 - exit 0, 188 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_sync_transport.py
 - exit 0, 6171 ms, pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1
 - exit 0, 23906 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_java_auth.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build --profile go
 - exit 0, 139219 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tests/e2e/go_tls_messaging.py --profile java
 - exit 0, 36406 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_java_auth.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/build --profile-switch
 - exit 0, 19563 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/contract_text.py
 - exit 0, 20703 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\im-review3-a7e85f3/contract_text.py
 - exit 0, 35515 ms, C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_sync_runtime.py --profile java
 - exit 0, 79 ms, git status --short --branch
 - exit 0, 47 ms, git rev-parse HEAD

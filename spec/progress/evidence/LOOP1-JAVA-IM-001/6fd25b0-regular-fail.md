# Independent regular review of Java IM

**FAIL** at 6fd25b03834a38fdb31af5e6517d5c0f8d32ce32. Task LOOP1-JAVA-IM-001, branch task/LOOP1-JAVA-IM-001, range 18597c06f15c6ba5d50e055a88890a54f737fd52..6fd25b03834a38fdb31af5e6517d5c0f8d32ce32. A fresh independent regular reviewer /root/regular2 inspected the full change and had no part in implementation, fixes, or the prior regular review. Managed detached checkout at H:/.codex/worktrees/jir/IM-platform matched the assigned root and candidate. Both initial and final status were clean. The unique task is in review. S3 remains OPEN.

## Blocking finding

Concurrent message send and same-slot login can deadlock across the Session and its user. Messages.send calls checkSession before inserting the Message (backend/java/core/im/Messages.java, lines 28 and 44). CoreAuth.sessionCheck takes FOR SHARE on the Session (line 85). The Message INSERT references users through its sender_id foreign key (contracts/database/migrations/0001_initial.up.sql line 125), acquiring KEY SHARE on that user. In the opposite order, CoreAuth.login locks the user FOR UPDATE (line 206), then updates the same Session (line 210). Each transaction can therefore hold a conflicting lock needed by the other. PostgreSQL can abort a legitimate login or return an unconfirmed failure for the send, beyond the intended ordered outcomes of send-before-retirement or rejection after retirement. This finding comes from static inspection. Ensure consistent lock ordering for the sender user and Session before Message persistence, retaining Session validation and existing conversation/member order. Cover the overlapping public operations with a deterministic concurrency regression.

## Review coverage

Verified the canonical Markdown and historical PDF hashes against the resolver, ADR-0004/0008/0013/0014, current authority and implementation responsibilities. The diff follows allowed paths. Core owns the transactions, receipts, membership authorization, user/conversation Sync and durable Outbox. Gateway reads Sessions, forwards private requests and fans out to local bound connections. Actual imports stay within the approved Spring/JDBC, Jackson, JDK and JNATS stack and role boundaries. No product Go, client, public contract or migration delta. No speculative production layer identified. The streaming Sync numeric handling serves the unbounded external JSON integer contract. Workflow selects the real Java fixture, TLS messaging and bulk Sync commands.

All three findings from 8974560b were addressed in this candidate. The fixture passed idle retirement after missed notification, consistent ADD/send lock ordering, commit reply loss/malformed reply rejection with original-identity retry and schema verification. The independent real IM runner exercised both profiles, group vectors, immediate friendship, real durability/rollback, fan-out, cursor/receipt and ACK continuity in both directions. ADR-0004 remains the sole deferred friend scenario.

Frozen/source-all, architecture tests (99, one skipped), clean Control Acceptance, CI tests (41, four skipped), external Maven build, and official HTTP/Group/WSS/Sync contract checkers passed. Separate full Java Auth, Compose TLS and bulk Sync suites were not independently rerun on this failed review. No specialist result, hosted acceptance, external submission or integration occurred. Historical implementation runs remain separately attributed.

## Command evidence

The external Recorder run R-20261120T120700Z-c72507f2-3da0-4acd-91a5-ca698805d1cc finished FAIL and validated. The early stand-alone startup reads and failed Python 2, py launcher and misplaced Recorder option invocations preceded capture and are reported as prospective_resume. The sandbox Maven build could not resolve the temporary compiled classes at testCompile. The approved external rerun succeeded in the same directory. An additional direct git diff --check reported CRLF/trailing whitespace/blank EOF issues. Raw command/output hashes are in the adjacent research/runs directory.

- exit 0, 187 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- exit 0, 1704 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- exit 0, 27328 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- exit 0, 32281 ms, pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
- exit 1, 4406 ms, H:\apache-maven-3.9.15\bin\mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\im-review2-6fd25b0/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\im-review2-6fd25b0/build/classpath.txt
- exit 0, 6578 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/ci
- exit 0, 5922 ms, H:\apache-maven-3.9.15\bin\mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\im-review2-6fd25b0/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\im-review2-6fd25b0/build/classpath.txt
- exit 0, 76860 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -Xutf8 -B tools/verify_java_im.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review2-6fd25b0/build
- exit 0, 188 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -B contracts/websocket/verify.py
- exit 0, 687 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -B contracts/http/verify-group.py
- exit 0, 156 ms, C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe -B tools/verify_sync_transport.py
- exit 0, 5954 ms, pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1
- exit 0, 62 ms, git status --short --branch

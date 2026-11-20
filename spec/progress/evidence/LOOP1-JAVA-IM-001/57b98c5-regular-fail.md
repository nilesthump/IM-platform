# Independent regular review — FAIL

Candidate 57b98c54c2da2d6bf4dcfedb8e9ff740c8981301, task/LOOP1-JAVA-IM-001, from accepted base 18597c06f15c6ba5d50e055a88890a54f737fd52. Reviewer /root/regular5 was independently dispatched and participated in no implementation, fix, or earlier review. The detached candidate and task branch resolved to that exact SHA. Initial and final status were clean in H:/.codex/worktrees/jir/IM-platform. Startup recovery found the sole current task under review, S3 OPEN. The workspace remained read-only.

## Blocking finding

Gateway.java checkCommittedMessage accepts an invalid public createdAt timestamp. An independent external probe called the exact compiled validation method on a complete, otherwise valid message.created frame with createdAt "+02026-01-01T00:00:00Z". The call returned normally because OffsetDateTime accepts extended signed years. The machine verifier in contracts/websocket/verify.py rejected the same frame and accepted it when just createdAt changed to "2026-01-01T00:00:00Z". Gateway.deliver serializes and forwards the unchanged event immediately after validation. Thus malformed internal committed data can still escape on a public WSS connection. The probe exercises the internal boundary directly; ordinary Core-generated timestamps from the current clock passed the live suite. Use a public date-time-compatible check, preserve valid Go/Java timestamps, and extend the malformed-event regression for extended years and other syntax admitted only by the Java parser. Keep the fix at the validation boundary and retain failure-before-peer-operation behavior. The previous serializer-catch finding is resolved: Jackson now runs once before the socket catch, and the live regression verifies cause propagation and preservation of the healthy binding.

## Scope and verification

Authority hash/provenance and architecture checks passed. Reviewed role imports, JDBC Core social/group/message/sync operations, transaction/receipt and sequence allocation, repeatable replay outcomes, JNATS publication, session checks, Gateway forwarding and local transport, deployment inputs and job classification. The changes stay within task-owned paths. No new dependency, public contract, migration or speculative mechanism was identified. ADR-0004's single deferred friend case remains deferred. The previous regular/specialist reports and independent product evidence for a7e85f3 explain authorization, TLS, Auth fixtures, login/send overlap, pagination, profile switching and failure probes. Compared to 86ebf351, all tracked material outside the enumerated task records, Gateway and two message tests is identical. The live IM suite was rerun on the actual candidate, including real PostgreSQL/NATS, Java/Go/Java continuity, serialization isolation, malformed messages and disconnected peer behavior. Maven verified the candidate with external build output, Control Acceptance passed on the clean checkout, and the classifier selects all fourteen jobs. Earlier Auth/TLS/Sync execution is historical evidence. A failed regular review precludes pre-CI specialist submission for this SHA. Fresh fix plus both fresh reviews on the replacement are required.

## Provenance

External Recorder R-20261120T130341Z-5d8cb2a7-d3e0-4651-82ec-67df63a0cbde finished FAIL and validated, 42 events. Setup reads and shell/CLI selection errors (Python 2, absent py launcher, misplaced recorder arguments and PowerShell syntax) and direct inspection were outside the recorded verification sequence. An initial probe wrapper mistakenly expected the canonical oneOf rejection message to contain a field path. The corrected probe independently verified the identical frame with only the timestamp corrected. Initial sandboxed Maven testCompile failed to resolve its external build classes. The host-access retry passed. Git reported the existing unavailable global ignore file; final explicit status including all untracked files was empty. External probes, input, build and Recorder files are in the same temporary directory as this report. The recorded command results below are local; hosted acceptance and integration are pending.

## Recorded verification commands

- Exit 0, 78 ms, git status --short --branch
- Exit 0, 63 ms, git diff HEAD
- Exit 0, 47 ms, git log -5 --oneline
- Exit 0, 47 ms, git diff --name-status 18597c06 HEAD
- Exit 0, 47 ms, git diff --name-status 86ebf351 HEAD
- Exit 0, 31 ms, git rev-parse HEAD task/LOOP1-JAVA-IM-001
- Exit 0, 109 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- Exit 0, 969 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- Exit 0, 20032 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- Exit 0, 21938 ms, pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance
- Exit 1, 2984 ms, mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\im-review5-57b98/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\im-review5-57b98/build/classpath.txt
- Exit 0, 4953 ms, mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\im-review5-57b98/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\im-review5-57b98/build/classpath.txt
- Exit 0, 76985 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_java_im.py --build-dir C:\Users\21441\AppData\Local\Temp\im-review5-57b98/build
- Exit 0, 1343 ms, java @C:\Users\21441\AppData\Local\Temp\im-review5-57b98/java.args
- Exit 0, 172 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\im-review5-57b98/contract.py C:\Users\21441\AppData\Local\Temp\im-review5-57b98/timestamp.json
- Exit 0, 140 ms, git diff --exit-code 86ebf351 HEAD . :(exclude)backend/java/gateway/auth/Gateway.java :(exclude)backend/java/tests/im/MessageDeliveryProbe.java :(exclude)backend/java/tests/im/MessageOutcomeProbe.java :(exclude)spec/progress/current.md :(exclude)spec/progress/evidence/LOOP1-JAVA-IM-001/* :(exclude)spec/tasks/review/LOOP1-JAVA-IM-001.md
- Exit 0, 343 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B contracts/websocket/verify.py
- Exit 0, 218 ms, C:\Users\21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/classify.py --base 18597c06 --head HEAD
- Exit 0, 203 ms, git status --porcelain=v1 --untracked-files=all

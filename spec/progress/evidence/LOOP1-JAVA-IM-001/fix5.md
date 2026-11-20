# Java committed-frame fix and UUID interoperability decision

Fresh regular review failed on 57b98c54c2da2d6bf4dcfedb8e9ff740c8981301, from accepted base 18597c06f15c6ba5d50e055a88890a54f737fd52. The original independent report is 57b98c5-regular-fail.md, SHA-256 efcb238587690aef7861f21106bea93b7b971f75ab3b53ca5aef8a97246d610c. Fix owner /root/fix5 used the assigned H:/.codex/worktrees/java-im/IM-platform and branch task/LOOP1-JAVA-IM-001.

Gateway validates both committed timestamps before delivery. Its wire grammar requires a four-digit positive calendar year, a valid calendar date, time with seconds, optional decimal fraction and a numeric hour/minute offset or Z. Calendar faults propagate. Tests derive the expectations for eight samples from the frozen WSS verifier and exercise both the real Core confirmation relay and the bound notification peer. Cases cover signed extended years, year zero, leap and non-leap dates, hour/second overflow, lowercase z, and a ten-digit fractional second with a negative offset.

Reviewed full envelope and payload shapes, required fields, extras, scalar types, canonical identifiers, correlation, positive integer sequence, message content kind and Unicode code-point length. Both exits now require canonical lowercase UUIDs. Java closes message.send with an unrepresentable request ID before forwarding, Core checks canonical conversation and request IDs before writes, and committed ACKs must match the sent conversation exactly. No new production catch, fallback, schema, dependency or Go change. The test harness catches only expected contract validation or timestamp/calendar failures for the negative cases.

## Disconnected behavior between profiles

An ordinary authenticated member sent the same two request IDs against separate freshly started Java and Go profiles, each with its own seeded conversation in the disposable PostgreSQL/NATS fixture. Both requests had valid membership, conversation and TEXT content. The lowercase control used a distinct identity so its counts cannot be affected by replay. Each count is filtered by that conversation and request ID. The outbox count joins the persisted message ID to message.created rows. Full requests, replies and counts are in uuid-case-observations.json. The Python oracle was contracts/websocket/verify.py validate(frame, SCHEMA).

| Profile | request ID spelling | Input oracle | Reply | Reply oracle | Messages / Outbox |
| --- | --- | --- | --- | --- | --- |
| Java | ABCDEFAB-0000-4000-8000-000000000001 | invalid | socket close 1007 | no frame | 0 / 0 |
| Go | ABCDEFAB-0000-4000-8000-000000000001 | invalid | committed ACK echoed uppercase | invalid | 1 / 1 |
| Java and Go individually | abcdefab-0000-4000-8000-000000000002 | valid | committed ACK echoed lowercase | valid | 1 / 1 each |

BLOCKED_BY_ARCHITECTURE on cross-profile compatibility. The current Java task forbids Go product and compatibility changes. Should a separately scoped Go change bring message.send UUID handling into agreement with the current machine verifier, or should acceptance of mixed-case UUIDs go through an approved compatibility/contract decision? Keep the task in review until a Human/Architect resolves this question. No hosted submission, protected integration, actual-main synchronization or Gate acceptance.

## Local verification

Research Recorder R-20261120T131112Z-50e7ee21-4d99-492f-9802-1e4963e4e1f4, parent R-20261120T110043Z-4fb24ce5-1424-4121-ad3d-acac3369b6fc. Startup inspection and an initial invocation of the system Python 2 preceded registration. The bundled Python 3 ran subsequent commands. Research files and temporary compiled artifacts are under %TEMP%/im-fix5-crosscheck. The temporary UUID probe is uuid_probe.py with UuidBoundary.java beside it. Comparison exit 0 means observations were collected, including the divergence.

| Command | Result |
| --- | --- |
| python -Xutf8 -B tools/verify_frozen_architecture.py | 0 |
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0 before and after changes |
| python -Xutf8 -B -m unittest discover -s tests/architecture | 0 |
| python -Xutf8 -B -m unittest discover -s tests/ci | 0, 41 tests, 4 skips |
| python -Xutf8 -B contracts/websocket/verify.py | 0, 18 shared scenarios, 44 mutations |
| mvn -B -f backend/java/pom.xml -Dim.build.dir=EXTERNAL verify dependency:build-classpath -Dmdep.outputFile=EXTERNAL/classpath.txt | 0, final build 6.125 s |
| python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL | 0, final build and real Java/Go/Java fixtures 72.422 s |
| python -Xutf8 -B EXTERNAL/uuid_probe.py | 0, live comparison 19.625 s |

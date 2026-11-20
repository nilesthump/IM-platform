# Independent pre-CI error-handling review — FAIL

Reviewer /root/specialist is a fresh independent context. I did not implement, fix or perform the regular review. The coordinator reported fresh regular PASS before dispatch. I reviewed detached HEAD 86ebf3510450013943c22311abb5d5a00c526457 in H:/.codex/worktrees/jir/IM-platform, task/LOOP1-JAVA-IM-001 from 18597c06f15c6ba5d50e055a88890a54f737fd52. Git status before/after showed only detached-HEAD status, with a host global ignore-file access warning. No task-tree writes. The sole queue entry is review. Frozen integrity and PDF provenance passed. S3 remains OPEN.

## Findings with observations

1. Gateway.java:127–145. The receive path checks version/type then extracts sender/conversation/request for filtering. A syntactically valid internal JSON envelope lacking seq, messageId, createdAt and content still becomes a public message.created. The exact-head probe invoked production delivery with an independently constructed JsonNode and an open bound test peer and observed sendMessage with those four fields missing. This violates the existing MessageCreated schema and hides an upstream invariant failure. Check the committed frame against its existing required envelope/payload shape before delivery or peer retirement. A regression should verify the failure is observable, with no outgoing frame or peer removal. No new public field or schema is needed.
2. Gateway.java:118–120 and 140–146. The peer-disconnect catch encloses send(socket,event), which serializes the event before writing. JsonProcessingException is an IOException. The exact-head probe injected a serializer defect through a test-only POJO node whose getter threw; deliver returned normally, called close on a healthy peer, and removed the binding. This injection isolates the exception boundary; the ordinary NATS decoder produces JSON data nodes, not injected Java POJOs. Move serialization outside the socket-write catch, preserving its cause via the existing worker boundary. Catch transport errors only around the actual write. Retain peer-local disconnection/closed-socket handling, assert genuine write failure still retires only that peer, and verify internal failure reaches the caller with its cause.

The external probe uses the production Gateway and a real local disposable NATS connection. Its assertions describe the two observed defective results; exit 0 reproduces the failures. It did not manufacture an accepted durable commit or attempt to change the public contract. Prior live regression commands, including lost response, invalid private ACK, concurrent login/send, missed revocation, cross-profile continuity, TLS and real Sync, are independently documented in spec/progress/evidence/LOOP1-JAVA-IM-001/a7e85f3-regular-fail.md. Only its product evidence is reused: git diff verified byte-identical backend, contract, tool, test and CI paths at this SHA; its Control Acceptance failed on a subsequently repaired record. The fresh regular review and final specialist are distinct. This result blocks CI submission until a fresh fix and both new final-SHA reviews.

## Production coverage and retained recovery

- CoreAuth.java:30 uses a client correlation ID if validated, otherwise generates a request correlation, never a data result. Lines 40,105,116 classify malformed client JSON, malformed media type and invalid UTF-8/duplicate or malformed group JSON respectively. Stream read failures propagate. Line 149 translates an explicit ApiFailure to the frozen rejection vocabulary; other runtime errors propagate. Line 152 handles PostgreSQL P0001 as a confirmed failed database transaction; rethrows unrecognized JDBC and transaction exceptions unchanged. No committed ACK until the transaction wrapper returns.
- SessionOutbox.java:30 after the publication timeout transaction rolled back, so the next tick can retry. At 34 shutdown interrupt ends the worker, unexpected interruption restores the flag and fails. At 52 a flush timeout escapes through rollback with its cause, and at 53 interruption restores the flag and fails with cause. A disconnected NATS connection leaves rows pending. A permanently closed connection fails the worker. Main's uncaught handler exits the process. Publication is at least once.
- Groups.java has no catch. Retry sentinel only on membership set expansion after lock acquisition and before mutation; rollback, reacquire the full ordered set. Existing committed receipt binds exact normalized targets, absent create receipt with an existing identity fails. Empty add-set is a genuine no-op. Page-limit default/terminal cursor are contract defaults. Database failure aborts the operation.
- Messages.java:53 impossible event serialization raises with cause inside the transaction. Explicit rejects cover input, membership and content conflict; idempotent replay uses original committed identity. Unknown database, locking or timestamp exceptions escape.
- Social.java:24 absent SHA-256 provider raises with cause. Correctly distinguishes a missing target, canonical DIRECT conflict and replay; existing known pair conversation can be reused and pair membership subsequently validated. Transaction failure propagates.
- Sync.java:30 malformed external JSON is a validation failure; 56 HMAC provider/key failure propagates with cause; 63 corrupt external base64 becomes validation failure; 76 malformed durable JSON raises with cause, with additional explicit payload invariant checks. Cursor 0 is initial position; empty page/terminal cursor comes from a real query. Gapped histories fail and all database failures propagate.
- SyncInput.java has no catch. Read I/O propagates, malformed/beyond-bound input is rejected, coefficient/exponent saturation is used solely for allowed pagination semantics and does not populate a missing durable result.
- Gateway.java:55/70 handle interrupted waits only at shutdown, otherwise reinterrupt and throw; 56/72 wrap checked I/O with cause so service worker failure is visible. At 88 attempt all peer closes, retaining subsequent failures as suppressed. At 141/144 FAIL above; closed-socket races can still retire only their peer and open-socket IllegalStateException must propagate. At 155 known bound-session invalidation reads the durable reason, using generic REVOKED for an inactive session with no reason row; a persisted unknown reason fails. At 178/181 a revocation write that lost the peer retires it via close in try-with-resources, while open-peer internal errors propagate. At 192/195 closing an already retired connection can fail at transport level or race actual close; unexpected open-peer state errors propagate. At 244 malformed external JSON closes with BAD_DATA. At 262/271 known token/session failures reject and retire, with finally removing unacknowledged registration. Unconfirmed Core transport, unparseable/unrelated/impossible ACK raises without success. No new dependency or cross-service business import.
- Dockerfile adds the necessary core/im copy. Build errors stop the image. Main.java was examined (unchanged), exits on uncaught worker errors; its shutdown adapter preserves interruption. There is no gateway/im source file in the candidate; the responsible code is in Gateway.java.
- tools/verify_java_im.py fails on absent inputs and nonzero/timeout subprocesses, and uses the existing profile context manager for cleanup. Java fixture checks use explicit failure assertions including rollback/replay, preserve causes on unexpected exceptions, and restore transport/transaction manager and database fences. TLS/Sync runner changes select the real profile; checked role identity and live query assertions remain active. Classifier and workflow select real checks. No evidence that these normal regressions exercise the two flagged outgoing notification paths.

## Input SHA-256 (working file bytes from clean exact checkout)
.github/workflows/ci.yml  cf6e0fad77a7d83185a7a459036d5c229a058385b172f7d025a95a9b08b8b4a8
backend/java/Dockerfile  b31abea61833f74e60673cf9f900b3efd30055f49e8137558dfde2378d8523f9
backend/java/core/auth/CoreAuth.java  d13f54a82ed086bf98814b70da272e3e8d666c1fc23ab68b739cf975a6bb7723
backend/java/core/auth/SessionOutbox.java  7b7e66747ab32f48813e8b7655fddb840e9a20267b360d1ef53c980249081d4e
backend/java/core/im/Groups.java  bb8f6c84c11eb48fda385dfbd69d52552c3060dd3be7f7e9773def46f03ada4a
backend/java/core/im/Messages.java  a734cad8ea7081f2ce5364c4ff1b0dd089f13fa993aac361c2eaf7066ae5c908
backend/java/core/im/Social.java  5d3d1360248e2490a8cdeed9f5d3ea7195764a9ad32212f312c151161b47ce98
backend/java/core/im/Sync.java  3dda6224284171cd4a87e1a3c5b9985c780914b435faec03ae3c5ead2b982cfe
backend/java/core/im/SyncInput.java  613ca2e307702f8fba6cb4f44d61a5d24ea8d92bb37e29bc1cdb7616b256af5d
backend/java/gateway/auth/Gateway.java  66c5cc0fd9ecfffe850bcf06270d5c216fa09e11b2e53e5296879b1f1006a381
backend/java/tests/auth/RevocationDeliveryProbe.java  48d69bc1c81a9a5276784120939e8bcb76e5719787e00e4cfe4d0c7b70155770
backend/java/tests/im/GroupFixtures.java  57e951bd1b3967e6f0aecfc02c4cd59e1be8cca8e7ffd8712b8ed556781a4e50
backend/java/tests/im/GroupTransactions.java  49196205b06a96815c5eee151dbeff4a36bd3f3d7058d00256ad11135b981896
backend/java/tests/im/MessageFixtures.java  a6a6ef6c9c264f64b5e063904ce0afbe8a8cc5645184c83400cdc82e2889d787
backend/java/tests/im/MessageOutcomeProbe.java  ffb99f46000194be653bd74131e612f79e447295232afa5834771073c6141e09
backend/java/tests/im/ProfileContinuity.java  b22e88b5dbb03e016a8e7ce854704f8564146049418cb7e3ef7c08beaf4fbb24
ci/classify.py  17b6469afd3b1aa3687eb5ec045ca932454b4a801a4d6b56ea0924382e2f5f25
tests/ci/test_classify.py  a09cd092e9cb0f9f58ef2fc80e75309e953edec242e5dd03b27f6d05ac734fd7
tests/ci/test_java_im_job.py  315a5ef3aa7e0961e5a8049a61266b4bfe37c094fbee52e787defd6fc167c9e8
tests/e2e/go_tls_messaging.py  8d297d5c7e47ded4797e942498ec55fcf4c13dedd64592a08ff8eef941eaa86f
tools/verify_java_im.py  62f4eabaf51bdf18ad14a3e79aada4a0bff3b6329f874cb49b9869e021c23b71
tools/verify_sync_runtime.py  0808e314a5c01dc9a99eb139e2e89367cbcd1e27c2afebcb098dcaf5351a24f7
backend/java/Main.java  a826489d92f0d69d142f16846d154376dd63c4169cb19be0e57085a7baac214a

## Commands and evidence

Recorder R-20261120T124328Z-05ee6b5d-63e4-42f5-8e00-6011669ee45a; external research-root, validated with result FAIL. Startup reads, misselected Python 2/unavailable py launcher, misordered CLI flags and a mistyped run ID preceded or bypassed successful capture. The run uses prospective_resume. Its original immutable events contain exact argv, duration, stdout/stderr digests and output. An initial sandboxed Maven compile and sandboxed probe failed classpath access; the same exact-head build and targeted probe succeeded with host access. Setup failures were not treated as product findings.

- C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B tools/verify_frozen_architecture.py | exit 0 | 141 ms
- C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B ci/check_architecture.py --scope all --json | exit 0 | 906 ms
- C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B -m unittest discover -s tests/architecture | exit 0 | 19938 ms
- git rev-parse --show-toplevel | exit 0 | 47 ms
- git rev-parse HEAD | exit 0 | 47 ms
- git status --short --branch | exit 0 | 94 ms
- H:/apache-maven-3.9.15/bin/mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\jim-special-86ebf351/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\jim-special-86ebf351/build/classpath.txt | exit 1 | 3375 ms
- H:/apache-maven-3.9.15/bin/mvn.cmd -B -f backend/java/pom.xml -Dim.build.dir=C:\Users\21441\AppData\Local\Temp\jim-special-86ebf351/build verify dependency:build-classpath -Dmdep.outputFile=C:\Users\21441\AppData\Local\Temp\jim-special-86ebf351/build/classpath.txt | exit 0 | 6110 ms
- Java source probe with full classpath (see command C-46f768a7-ee03-4444-9ae6-70f30ec1fae8) | exit 1 | 750 ms
- C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\jim-special-86ebf351/probe.py | exit 0 | 2516 ms
- git diff --exit-code a7e85f34 HEAD backend tests ci contracts tools .github | exit 0 | 47 ms
- C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -Xutf8 -B contracts/websocket/verify.py | exit 0 | 109 ms
- git status --short --branch | exit 0 | 94 ms
FanoutProbe.java SHA256 547c1ed7428d5e8e26d23bf5aff2bf6d1f2eb37c3f0ce3dd15afc0f5c3894015
probe.py SHA256 7f99222ec092f36ca88a3cf49a45d27dd67e6ca60fdbb6cc9590f57d3e87d053

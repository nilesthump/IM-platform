# Independent error-handling specialist review

PASS for task/LOOP1-JAVA-IM-001 at 17471665fdbf7c5c5820c150c84823ee37e7398b. Full review range 18597c06f15c6ba5d50e055a88890a54f737fd52..17471665fdbf7c5c5820c150c84823ee37e7398b. Fresh /root/specialist3 was dispatched after regular7 PASS. I had no implementation, repair or regular review role. I inspected the clean detached checkout H:/.codex/worktrees/jir/IM-platform, whose HEAD matched the task branch. Initial and final status were clean. S3 OPEN. No push or repository writes.

The unique current queue entry is review. Verified frozen Markdown and historical PDF hashes, consulted the designated task authorities, and compared the changes since 7ff6d1ed68dd30ec033b3e6f7f11c608cb216728. Only executable changes are the WSS verifier and live runner. SHA-256 checked all 26 entries of the previous file inventory against the current checkout. The runner is the only changed entry. The production catch/fallback inventory below is incorporated from the hash-verified earlier report after cross-checking the current catch sites, responsibilities, both Go blobs, startup and the entire production tree. There are no new production catch or fallback sites.

## Verifier and live runner annex

- contracts/websocket/verify.py (SHA-256 1a2d867228470d50dc606aff2e1940217ea5576baf58966dd8a9054c7fa4b086). Line 95 treats Invalid as a rejected oneOf branch and requires exactly one match. Line 127 reports malformed/noncanonical UUID with cause. Lines 129–142 reject timezone-free or unparsable wire input and the original hour 24 after CPython normalizes it. Exposed Invalid preserves the ValueError cause. The source-hour test uses a fixed pattern. It neither substitutes a timestamp nor rewrites a message. Internal runtime exceptions propagate. Lines 494, 537 and 554 accept only the deliberately rejected behavior, frame or malformed-schema control. Otherwise the control fails. At 587 expected format, data and I/O errors print failure and return exit 1. Other internal exceptions fail the process. Positive hour 00/23 controls validate during ACK construction. Invalid controls mutate an already-valid ACK before running the validator. No existing checks were removed.
- tools/verify_java_im.py (SHA-256 173f22fc600297297bb75b29072825c1f5c737e7947def9008f9c613de3f5249). Line 48 records False only on the verifier's typed Invalid. A successful return is recorded as True. Missing dependencies, filesystem, subprocess, timeout and internal errors escape. The Java probe consumes the table for both remote ACK and notification behavior. The driver's extension adds an accepted final hour and rejected hour-24 offset cases. It introduces no recovery branch or new dependency.
- Compared with the earlier exact-SHA review, the immutable product inventory and unchanged schemas and fixtures do not require a second runtime implementation. The current independent probe executed 1,404 canonical-format boundary cases with explicit expected results per interpreter on CPython 3.12.14 and 3.14.3. A synthetic internal RuntimeError at the matcher propagated intact on both. The WSS executable passed its 8 positive/10 negative scenarios and 23 schema/26 behavior mutations on each. Local architecture suite ran 99 tests with one skip. The current regular review independently ran Control Acceptance. I did not rerun live DB/NATS fixtures in this specialist run. The fixer's live run is separately identified in hosted-hour-fix.md.

## Product catch and fallback inventory

Source of reproduced inventory is spec/progress/evidence/LOOP1-JAVA-IM-001/7ff6d1e-specialist-pass.md (verified SHA-256 edb7084713b9432e66aa3bcd9ffcd7b90d068592e68bc50749971ab85ace269c). Per-file SHA-256 and inherited catch locations below are current, except the old runner hash is superseded by the annex above.


- backend/go/core/message.go owns the private adapter and message transaction. New lowercase matcher precedes any database work. An unrepresentable request ID returns private HTTP 400 without an ACK. Invalid conversation UUID with valid correlation returns VALIDATION_FAILED. Only canonical values reach storage. No added catch, retry or normalization fallback. Prior transactional behavior inspected in context: missing session or membership gives a typed rejection, absent stored message is the only insert branch, database failures leave the transaction, confirmed failed writes project the existing rejection and unknown commit confirmation returns 503 without an ACK. Replay returns stored identity. Deferred rollback frees unfinished transactions.
- backend/go/gateway/gateway.go owns frame routing, exact private-response correlation and peer-local I/O. An unrepresentable message.send request ID ends that peer's read loop before forwarding. Decode failure, non-200 response, unexpected response version/type/ID or malformed status cannot establish the outcome and emit no ACK. A rejected new send removes its provisional origin, losing a transport response retains origin for retry/Sync. Exact comparison replaces case folding only for the forwarded message ACK. No introduced catch or added generic fallback. Other pre-existing Go routes are outside the Human-authorized change.
- backend/java/core/auth/CoreAuth.java owns HTTP and private send routing and session checks. Line 30 generates a correlation identifier only where client correlation is unavailable. At 40 malformed request JSON gives validation rejection. At 105 an invalid media type fails the JSON predicate. At 116 malformed UTF-8 or malformed/duplicate group JSON gives group validation rejection. Body read I/O escapes those parse handlers. At 149 a typed business rejection maps to the approved ACK code. At 152 an explicit PostgreSQL P0001 rejection can establish failed transaction. Every other transaction/data access failure is rethrown unchanged, leaving unknown commits unconfirmed. Transaction must return before successful reply.
- backend/java/core/auth/SessionOutbox.java owns durable delivery. Line 30 catches only the publication timeout after rollback and retries at the next existing tick. At 34 stop interrupt ends the loop, other interrupts reinterrupt and fail the worker. At 52 NATS flush timeout carries the cause out through transaction rollback. At 53 unexpected interruption restores the flag and fails with cause. Disconnected leaves rows pending, permanently closed fails the worker. Publish before flush and mark in the transaction; duplicates are permitted. Process handler in Main observes unexpected failure.
- backend/java/core/im/Groups.java has no catch. Membership growth between reads invalidates the locked user set before writes, marks rollback-only and reacquires in order. Missing target/member/friend rejects. Missing create receipt for an existing create identity fails, conflicting normalized targets reject, matching receipt returns the original result. Existing members contribute no new events. Snapshot defaults and terminal cursor come from the bounded page protocol. Query failure escapes.
- backend/java/core/im/Messages.java owns message write, Outbox and replay. At 53 impossible internal JSON serialization raises with cause inside the transaction. Invalid payload/IDs, absent membership and replay-content conflict reject explicitly. A matching committed row supplies the original identity. Failures in locks, inserts, sequence allocation and Session checks escape the write scope.
- backend/java/core/im/Social.java owns immediate friendship and DIRECT. At 24 absent SHA-256 provider fails with cause. Missing target and self-add give typed failures. Existing canonical pair/receipt is reused only after consistency checks. Incompatible DIRECT membership rejects. In-transaction database failures propagate.
- backend/java/core/im/Sync.java at 30 rejects malformed external JSON. At 56 HMAC provider/key failure raises with cause. At 63 invalid external cursor encoding is rejected. At 76 malformed durable event JSON raises with cause, also checking stored identity/revision. Initial cursor is zero, empty/terminal page derives from the query and a sequence gap fails the operation. Unexpected storage failures propagate.
- backend/java/core/im/SyncInput.java has no catch. The parser rejects malformed input. Numeric bounding preserves pagination semantics for oversized inputs. Input stream failure propagates. No substitute persisted data.
- backend/java/gateway/auth/Gateway.java at 55/70 only shutdown interrupts end the subscription workers normally; other interrupts restore status and fail. At 56/72 checked I/O is rethrown with cause to uncaught worker handling. At 88 every peer gets a cleanup attempt and subsequent failures are suppressed onto the first. At 171 only the actual peer write is caught for IOException, removing/closing that peer. At 174 a closed-peer race removes the binding; an open-peer IllegalStateException propagates. At 185 Session invalidation initiates a persisted-reason lookup; fallback REVOKED applies only to an inactive binding with no reason row, and unexpected persisted reason fails. At 208 a failed revoke write retires the affected peer via resource cleanup. At 211 a real close race completes retirement and open-peer failures propagate. At 222 a disconnection during close ends retirement of an already removed binding. At 225 an observed closed peer ends cleanup; open-peer errors propagate. At 271 malformed incoming JSON closes with BAD_DATA. At 290 token validation ApiFailure rejects the bind. At 299 actual Session rejection retires the unacknowledged binding, and 308 finally removes incomplete registration. Unknown transport outcomes, invalid ACKs/committed notifications and internal serialization never produce a success. Public origin defaults are existing desktop transport policy. No new infrastructure.
- backend/java/Dockerfile copies Core IM sources; build command failures propagate. backend/java/Main.java (unchanged) owns role startup/worker lifecycle: at 24 shutdown interruption preserves status and cause, and unexpected uncaught worker errors terminate the process. Port default is existing deployment config. No gateway/im file in final tree.


## Per-file SHA-256

cf6e0fad77a7d83185a7a459036d5c229a058385b172f7d025a95a9b08b8b4a8  .github/workflows/ci.yml
6d9543b64d2957413ce6f48d2eb73d621c2502207d3b77fba6f029ffd9271daa  backend/go/core/message.go
af22276c6ac942d42c57c65d179fccca62688b8fbbbde95708ff5647410d7f17  backend/go/gateway/gateway.go
b31abea61833f74e60673cf9f900b3efd30055f49e8137558dfde2378d8523f9  backend/java/Dockerfile
d13f54a82ed086bf98814b70da272e3e8d666c1fc23ab68b739cf975a6bb7723  backend/java/core/auth/CoreAuth.java
7b7e66747ab32f48813e8b7655fddb840e9a20267b360d1ef53c980249081d4e  backend/java/core/auth/SessionOutbox.java
bb8f6c84c11eb48fda385dfbd69d52552c3060dd3be7f7e9773def46f03ada4a  backend/java/core/im/Groups.java
343c63b87a637df6073c6c38c62f9d9a0bfc7691e615b3630e33fecf079d5039  backend/java/core/im/Messages.java
5d3d1360248e2490a8cdeed9f5d3ea7195764a9ad32212f312c151161b47ce98  backend/java/core/im/Social.java
3dda6224284171cd4a87e1a3c5b9985c780914b435faec03ae3c5ead2b982cfe  backend/java/core/im/Sync.java
613ca2e307702f8fba6cb4f44d61a5d24ea8d92bb37e29bc1cdb7616b256af5d  backend/java/core/im/SyncInput.java
7c853d8a0671966d9a72bda40d964228255bca346b0adbba2a097ad1d1d629d4  backend/java/gateway/auth/Gateway.java
48d69bc1c81a9a5276784120939e8bcb76e5719787e00e4cfe4d0c7b70155770  backend/java/tests/auth/RevocationDeliveryProbe.java
57e951bd1b3967e6f0aecfc02c4cd59e1be8cca8e7ffd8712b8ed556781a4e50  backend/java/tests/im/GroupFixtures.java
49196205b06a96815c5eee151dbeff4a36bd3f3d7058d00256ad11135b981896  backend/java/tests/im/GroupTransactions.java
700c93ac5eeff5767eed757baf7d26132ccbba6ae5c3291fdd3dd71fe292f616  backend/java/tests/im/MessageDeliveryProbe.java
a6a6ef6c9c264f64b5e063904ce0afbe8a8cc5645184c83400cdc82e2889d787  backend/java/tests/im/MessageFixtures.java
a9d7a759353a2102718c14e6a7b3f1f082718c5ec3893b26cda3ca0dba8d2c15  backend/java/tests/im/MessageOutcomeProbe.java
b22e88b5dbb03e016a8e7ce854704f8564146049418cb7e3ef7c08beaf4fbb24  backend/java/tests/im/ProfileContinuity.java
17b6469afd3b1aa3687eb5ec045ca932454b4a801a4d6b56ea0924382e2f5f25  ci/classify.py
a09cd092e9cb0f9f58ef2fc80e75309e953edec242e5dd03b27f6d05ac734fd7  tests/ci/test_classify.py
315a5ef3aa7e0961e5a8049a61266b4bfe37c094fbee52e787defd6fc167c9e8  tests/ci/test_java_im_job.py
7e7758138b6b9ec130baa44f16a83fc209bb730156582268e65518888d80c502  tests/e2e/go_tls_messaging.py
173f22fc600297297bb75b29072825c1f5c737e7947def9008f9c613de3f5249  tools/verify_java_im.py
0808e314a5c01dc9a99eb139e2e89367cbcd1e27c2afebcb098dcaf5351a24f7  tools/verify_sync_runtime.py
a826489d92f0d69d142f16846d154376dd63c4169cb19be0e57085a7baac214a  backend/java/Main.java


## Commands

Run R-20261120T141949Z-7987ba89-0e7c-4c45-8ff0-38d4d68e4135, validated 32 events, manifest bdf2711af5906b726ba6c9a9e94190889fd089631c9d833c8343547b5a7cdc0e. Initial ordered reads, resolving Python 2 on PATH and correcting Recorder subcommand option placement preceded capture, recorded as prospective_resume with incomplete prehistory. Additional direct reads and an exploratory malformed week-date parse (ValueError on both interpreters) were outside the command recorder. The sandbox warned of unreadable global Git ignore file. The status check included all untracked paths.

- exit 0, 94 ms, git status --porcelain=v1 --branch
- exit 0, 93 ms, git diff --stat
- exit 0, 63 ms, git diff --stat 18597c06 HEAD
- exit 0, 46 ms, git log -5 --oneline
- exit 0, 32 ms, git rev-parse --show-toplevel HEAD refs/heads/task/LOOP1-JAVA-IM-001
- exit 0, 125 ms, C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B tools/verify_frozen_architecture.py
- exit 0, 1032 ms, C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B ci/check_architecture.py --scope all --json
- exit 0, 22484 ms, C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B -m unittest discover -s tests/architecture
- exit 0, 93 ms, C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B contracts/websocket/verify.py
- exit 0, 172 ms, C:\Users\21441\AppData\Local\Temp\im-java-hour-runtimes\cpython-3.14.3-windows-x86_64-none\python.exe -Xutf8 -B contracts/websocket/verify.py
- exit 0, 47 ms, git diff --exit-code 7ff6d1ed HEAD -- backend .github ci tests contracts/http contracts/websocket/envelope.schema.json contracts/websocket/sync-v1.schema.json contracts/fixtures
- exit 0, 266 ms, C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\im-17471665-specialist3\verify-specialist.py
- exit 0, 406 ms, C:\Users\21441\AppData\Local\Temp\im-java-hour-runtimes\cpython-3.14.3-windows-x86_64-none\python.exe -Xutf8 -B C:\Users\21441\AppData\Local\Temp\im-17471665-specialist3\verify-specialist.py
- exit 0, 94 ms, git status --porcelain=v1 --untracked-files=all
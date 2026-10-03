# LOOP1-CLIENT-SEND-001 implementation evidence

This is local implementation evidence, not independent Review, hosted acceptance, Task PASS, or S2 Gate PASS. The implementer does not accept this candidate.

## Identity and boundaries

- Assigned managed Git root: H:/.codex/worktrees/client-mvp-planning/IM-platform, verified by git rev-parse before writes.
- Branch: task/LOOP1-CLIENT-SEND-001. Implementation base: 8b33571990241f91a676e15069b07b065697317a. Accepted main: 10b77b22386234c98409ca41b3622ad6d25f3884. Root-owned activation/accepted UIARCH closure metadata between those commits is separate from this implementation.
- Canonical v1.1 hash16e9c7b488e00dd39c7c2b5da7286c22be6ac67c163f0e89733bbe00297d0a3c and historical PDF546915 are unchanged. Authority: canonical sections2.3/3/6/10SRC01-07/11/19/20 and accepted ADR0005/0006/0007.
- Product scope: Desktop TypeScript application, minimal shared TypeScript wire codec; Android Kotlin ViewModel/StateFlow and standard-platform TLS/WSS adapter. Existing Repository, SQLite schema, native SQLx/Tauri adapters, backend and contracts are unchanged. No GUI, Web implementation, HTTP send route, full Sync fetch runner, new network library or additional frozen decision.
- TypeScript uses the built-in WebSocket. Android uses standard java/javax TLS sockets, JSON output and narrowly required RFC6455 text/control framing, with default platform trust and HTTPS hostname verification. Lifecycle/coroutines dependencies are explicitly authorized by canonical6.1/6.5+ADR0006. The account factories use the bound user identity for existing per-account storage.

## Behavior and minimality

One application/ViewModel belongs to one account/session. Intents produce an immutable request ID. Existing Repository localSend commits before observable SENDING and transmission. ACK only materializes through committedAck; original-ID message.created and authoritative Sync input converge through existing syncMessages. Rejected/offline/timed-out attempts persist FAILED; retry/restart reload the exact persisted ID/content. SENT remains terminal. Socket generations reject stale callbacks; per-attempt identity rejects obsolete timers; account retirement clears observations and networking. Transaction errors cannot cause a send before local persistence or publish SENT before ACK persistence.

The strict object decoder follows canonical envelope/schema fields, rejects unknown/duplicate keys and wrong versions/types/IDs/date-time/error shapes, and preserves integers beyond2^53 including mathematically integral decimal/exponent forms. Signed64 materialization bounds belong to existing SQLite Repository; wire decoding does not pretend that storage bounds are canonical wire limits. Transport parsers apply finite local resource budgets, not a new public protocol. Credentials are only transmitted in auth.bind.payload; endpoint query/userinfo are rejected, errors are generic, and credentials do not appear in state/logs/process arguments. Android credential toString is redacted.

The Socket seam exists for the currently required callback/attempt/commit-failure race tests, not future transports. The Android narrow WSS implementation avoids an unauthorized network dependency and is exercised through actual verified TLS. The explicit Gradle SEND instrumentation selector is necessary because AGP rewrites instrumentation names; the default remains StorageInstrumentation, and CI executes original storage checks before SEND. The ineffective extra androidTest Manifest was removed; the generated runner entrypoint is selected explicitly for SEND verification.

## Actual local verification

All commands use the bundled Python3 `-X utf8 -B`, never the machine's default Python2.7. Exact argv, exit codes, duration, raw-output hashes, stdout/stderr gzip and historical failures are indexed in commands.json and outputs/. Environment identifiers are recorded below, never credentials.

- `python -B tools/verify_client_send.py --scope desktop`: PASS; actual current SQLx adapter and built-in WSS through verified fixture TLS. Offline/timeout/rejected, same-ID restart retry, late ACK, original-ID realtime/Sync convergence, terminal SENT, malformed frame/wrong session, transaction rollback-before-send, failed ACK persistence, stale callback, replaced-attempt timer, and account isolation.
- `python -B tools/verify_client_send.py --scope mobile --serial emulator-5590`: PASS; actual fully booted/unlocked API34 Google APIs x86_64 Android emulator, SDK SQLite Repository, ViewModel/StateFlow and standard TLS WSS. 40 assertions, including closed-Repository async timer liveness and session revocation. Includes default trust rejection of fixture CA. SEND runner explicitly selected by its Gradle property; original storage runner is preserved.
- `python -B tools/verify_client_sqlite.py --scope desktop`: PASS;13 canonical cases/141 assertions, existing native atomic/read-only-query regression.
- `python -B tools/verify_client_sqlite.py --scope mobile --serial emulator-5590`: PASS;13 canonical cases/137 assertions in both install and application-data-clear phases; actual API34 SQLite3.39.2.
- `python -B tools/verify_client_send.py --scope shared`: PASS independent entrypoint, also executed within Desktop SEND. Strict mutations plus canonical golden server outputs.
- `python -B tests/clients/send/go_smoke.py H:/.codex/toolchains/client-sqlite/target-final/debug/storage_probe.exe`: PASS; actual Desktop TS application+SQLx -> actual accepted Go TLS/WSS -> PostgreSQL. Offline saved intent resumed by a new application using the same ID. Client SENT checked against one exact Message, one Outbox event and nextSeq2; only inspected task-owned Compose resources removed.
- `python -B ci/check_architecture.py --scope all --json`: PASS after removing only this task's verified generated build directories.
- `python -B -m unittest discover -s tests/architecture -v`: PASS53, no skips.
- `python -B -m unittest discover -s tests/ci -v`: PASS33; four pre-existing native Windows symlink-privilege cases are explicitly unexecuted, while existing simulated link controls execute. New SEND positive/deleted-fixture controls pass. Hosted Linux remains the independent judge for all actual applicable jobs.

Controlled TLS fixtures prove actual client behavior, not Go/PostgreSQL durability. The separately identified real-Go smoke verifies current committed rows; required original Go E2E in hosted CI still verifies broader rollback-before-ACK, idempotency, membership and real durability. No fixture result is promoted to product acceptance.

## Failures preserved and remaining acceptance

Initial missing desktop tsc install and callback-type mismatches were repaired; Gradle invocation at recorded repository cwd and default cache/DNS failures were repaired using explicit project path and existing H:/gradle cache. Android's first Manifest runner registration failed at the actual emulator and was repaired using the explicit SEND property while retaining default Storage. Test-only fake socket capture and real-Go HTTP request/response shape mistakes were repaired against canonical inputs. One invalid singular architecture scope invocation and generated-tree sourceall failure are retained; effective sourceall PASS follows validated cleanup. A final Android invalid-event test race was repaired by waiting for the completed FAILED/protocol observation, rather than the earlier connection-offline notification. Repeated failed Android runs now delete only their reserved fixture account database at setup, preventing previous failed-run sequence rows from colliding with a fresh controlled TLS server. Closed-Repository tests wait beyond the live attempt timer before the liveness/assertion marker, proving async failure stays observable without crashing. No failed trace is overwritten or removed.

Fresh independent Review, exact candidate hosted CI with all selected required jobs/actual SEND steps, protected integration/actual-main verification and synchronization back to H:/IM-platform remain mandatory. No push, PR, merge, main write, done transition or subsequent SYNC/GUI/WEB activation was performed by this implementer. Main synchronization is PENDING; accepted main SHA above remains the last known good product state.

## Toolchains and Recorder

Node H:/node.js; Rust existing cargo/rustup and external target-final with one build job; JDK17 H:/.jdks/jdk17; Gradle8.9 H:/gradle and existing dependency cache; AndroidSDK H:/Android; task-owned API34 emulator5590 in assigned Git metadata send-runtime, hidden background; public fixture TLS certs ephemeral. Final APK byte counts/hashes are in android-artifacts.json, with actual bytes privately preserved in send-runtime/artifacts before generated-source cleanup.

Recorder run R-CLIENT-SEND-IMPLEMENTATION-20261003 lives in H:/IM-platform/.git/worktrees/IM-platform4/send-implementation-research. Visible prompt P-CLIENT-SEND-IMPLEMENTATION-20261003 registered; prospective_resume explicitly marks earlier read-only startup as incomplete pre-Recorder activity. Commands/tests are recorded with actual exit codes and raw hashes. Final finish/validate occurs after the clean candidate commit; Coordinator can archive that immutable finished run when producing independent acceptance evidence. Recorder PASS is neither Task PASS nor Stage Gate PASS. The previously finished Coordinator run is untouched.

Final sourceall PASS after final build cleanup; Recovery Development PASS using bundled PowerShell7 (its frozen verifier/architecture negative controls included). Earlier Windows PowerShell5 Get-FileHash module failure is preserved; runtime corrected without changing verifier. Candidate clean Recovery Acceptance and full10b77b2..HEAD diffcheck follow commit, recorded privately for immutable final archive.

Committed implementation/product evidence SHA: `4d6e800ac32b328faacbe18d2e867e732efa0097`. Subsequent handoff-only commit records this identity; review final branch HEAD and full accepted-main diff. Sync result PENDING; main SHA remains10b77b22386234c98409ca41b3622ad6d25f3884.

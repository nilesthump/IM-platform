---
task_id: LOOP1-CLIENT-SQLITE-001
title: Authorized TypeScript Desktop and Kotlin Android SQLite materialized Repository
status: review
owner: Fresh Fix Agent (sole writer until clean release)
stage: S2
gate: S2
---

# Goal

Implement the bounded per-account SQLite schema, migration fixture and transactional Repository foundation for Desktop and Mobile. Local send, committed ACK, realtime and Sync materialization converge to one logical item through transactional UPSERT; data and cursor/contiguous-sequence changes are atomic. This is the storage slice, not network send/retry orchestration, Sync fetching, Web UI or S2 Gate closure.

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> current canonical `spec/architecture/frozen-architecture.md` SHA256aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c, unchanged historical PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510; canonical sections2.3,3,4.4,6,7,10 SRC-01..07,11,12-15,19,21,AppendixA/B.
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md` independently accepted e7c80c7/closureb1d3e91/actualmaina287529, with bounded Human GString waiver only. Historical ADR0001expired/0002/0003/0004 immutable; read actual indexed files.
- `spec/governance/minimality.md`, `spec/governance/execution-boundaries.md`, `spec/governance/independent-review.md`, `spec/governance/technology-selection.md`.
- `spec/domain/messaging.md`, `spec/invariants/messaging.md`, `spec/domain/sync-plugin.md`, `spec/invariants/sync-plugin.md`, `spec/acceptance/s0-messaging.md`, `spec/acceptance/s0-sync-plugin.md`; original provenance labels remain historical, current authority controls.
- `contracts/websocket/envelope.schema.json`, `contracts/websocket/sync-v1.schema.json`, `contracts/fixtures/websocket/golden.json`, `contracts/fixtures/sync-plugin/golden.json` and their current verifiers. Machine public wire/schema/fixtures authority remains contracts; no reverse authoring.
- `spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/readiness.md` and accepted dependency archive/manifest. No PR7 product or acceptance reuse.

# Technology Authorization

Canonical2.3/6.1 and accepted ADR0005 authorize the following choices only. TypeScript owns shared Desktop models/Repository/SQL migration and transaction intent; Rust supplies native connections/query/one atomic transaction adapter only. Mobile Kotlin equivalent Repository/models/adapters follow the same canonical fixtures, built-in Android SDK SQLite and real Android Studio emulator.
client_language: TypeScript
client_language: Kotlin
client_language: Rust
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android
client_dependency: typescript
client_dependency: tauri
client_dependency: tauri-build
client_dependency: sqlx

Necessary approved Android SDK/Gradle/Kotlin/Compose compiler/UI/activity bindings are canonical policy identifiers, not authority for Room/ORM/network/test frameworks or any arbitrary native package. Use standard SDK test instrumentation/standard-library tooling when possible. New direct sensitive dependencies, product runtimes or unapproved build identifiers require authority before edits. No multiple independent execute calls may simulate transactions.

# Dependencies

- LOOP1-CLIENT-ARCH-CLARIFICATION-001 done: independent e7/b1 Review and exact hosted CI; PR9 merged actualmaina28752967ddd471cd281aece7ea9b343521356e8, independent actualmain Review/run36884545395 all13required jobs/every stepSUCCESS.
- LOOP1-E2E-001 done; S1 PASS, accepted pre-PR7 product preserved.
- LOOP1-CI-001 done/operational; LOOP1-RESEARCH-001 done/Instrumentation Epoch accepted.

# Allowed Paths

- `clients/shared/protocol-sdk/.gitignore`, `clients/desktop/.gitignore`, `clients/desktop/src-tauri/.gitignore`, `clients/mobile/.gitignore` (only necessary local dependency/build caches, SDK local.properties and native build outputs).

- `clients/shared/protocol-sdk/package.json`, `clients/shared/protocol-sdk/package-lock.json`, `clients/shared/protocol-sdk/tsconfig.json`, `clients/shared/protocol-sdk/README.md`.
- `clients/shared/protocol-sdk/src/storage/**` (TypeScript models/schema/Repository/native transaction intent; no networking/plugin lifecycle).
- `clients/shared/protocol-sdk/tests/storage/**` (canonical fixture-driven storage tests).
- `clients/desktop/package.json`, `clients/desktop/package-lock.json`, `clients/desktop/tsconfig.json`, `clients/desktop/README.md`.
- `clients/desktop/src/storage/**` (TypeScript Tauri adapter wiring only).
- `clients/desktop/src-tauri/icons/icon.ico`, `clients/desktop/src-tauri/icons/icon.png` (Coordinator scope clarification: required neutral 32px Windows/Linux Tauri build resources).
- `clients/desktop/src-tauri/Cargo.toml`, `clients/desktop/src-tauri/Cargo.lock`, `clients/desktop/src-tauri/build.rs`, `clients/desktop/src-tauri/tauri.conf.json`.
- `clients/desktop/src-tauri/src/lib.rs`, `clients/desktop/src-tauri/src/main.rs`, `clients/desktop/src-tauri/src/database.rs`, `clients/desktop/src-tauri/src/bin/storage_probe.rs`, `clients/desktop/src-tauri/tests/storage.rs` (native connection/query/atomic adapter and necessary bounded actual-SQLx test transport only; no Repository/business/schema authority in Rust).
- `clients/mobile/settings.gradle.kts`, `clients/mobile/build.gradle.kts`, `clients/mobile/gradle.properties`, `clients/mobile/gradlew`, `clients/mobile/gradlew.bat`, `clients/mobile/gradle/wrapper/**`, `clients/mobile/README.md`.
- `clients/mobile/app/build.gradle.kts`, `clients/mobile/app/src/main/AndroidManifest.xml`, `clients/mobile/app/src/main/kotlin/im/platform/client/MainActivity.kt` (minimal approved Compose host for actual Android storage validation, not complete send/Sync UI).
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/**` (Kotlin equivalent models/schema/Repository/SDK SQLite).
- `clients/mobile/app/src/androidTest/AndroidManifest.xml`, `clients/mobile/app/src/androidTest/kotlin/im/platform/client/storage/**`, `clients/mobile/app/src/androidTest/assets/**` (same canonical fixture inputs and built-in Android instrumentation).
- `tests/clients/sqlite/**` (cross-implementation storage/migration/rollback fixtures and runner; no new public contract).
- `tools/verify-client-sqlite.ps1`, `tools/verify_client_sqlite.py` (only this slice's actual TS/native/Android validation, no skip-as-PASS).
- `.github/workflows/ci.yml` (replace selected Desktop/Mobile/shared S0 placeholder storage checks with current actual slice verification; preserve all existing other required checks and exact-head enforcement).
- `ci/classify.py`, `tests/ci/test_classify.py`, `tests/ci/test_workflow_context.py`, `tests/ci/test_s0_boundary.py` (only positive/deleted new storage test/tool/native/Android trigger and honest first-implementation placeholder expiry).
- `spec/tasks/**/LOOP1-CLIENT-SQLITE-001.md`, `spec/progress/current.md`, `spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/**`, `spec/progress/checkpoints/*client-sqlite*.md`.
- `research/prompts/**`, `research/runs/**` only own new research traces; external Recorder preferred.

Paths do not waive authority. No edits to canonical body/hash/ADRs/old tasks/evidence/contracts/backend/deploy/Web/plugin runtime. Build outputs/dependency caches stay ignored or external; do not commit credentials/private data/toolchains.

# Acceptance

- Desktop and Android each use per-account real SQLite, preserve isolation and existing history across reopen; a forward migration and old-schema fixture are verified with failure rollback/data preservation. Internal SQLite layout conforms to present canonical semantics without creating a second public contract.
- UNIQUE(conversation_id,request_id), globally unique non-null server_message_id and per-conversation non-null server_seq. All four storage write entrypoints converge under duplicate/crossed inputs. Same request identity in distinct conversations stays distinct. Conflict input cannot silently lose/overwrite durable identity/content.
- Committed ACK/realtime/Sync converge an existing local item to SENT; SENT never regresses under late FAILED/timeout writes. Storage exposes necessary transaction operations for later send/retry without implementing network orchestration.
- Fault injection between materialization and cursor/contiguous advance rolls back both; one actual native transaction encloses all operations. Contiguous sequence never crosses a gap. Test duplicate/out-of-order/gap closure, restart, account isolation and real uniqueness failures; no separate independent execute pseudo-transactions.
- TS owns Desktop shared Repository/models/migration/transaction intent; Rust only generic database adapter. Kotlin equivalent behavior consumes same canonical fixture cases. Reviewer inspects real responsibilities/imports/native command graph, not directory names or mocked behavior alone.
- Real SQLx SQLite adapter verification and real Android emulator SQLite/migration/instrumentation are required for this slice. Host/mock tests supplement, never replace Android acceptance. Exact actual environments/commands/skips/toolchain versions recorded. No full Desktop/Android network/UI/S2 Gate claim from this storage slice.
- Existing source/authority/client technology/classifier/Gate controls remain effective. First client storage implementation cannot be accepted solely by .gitkeep/S0 skeleton jobs. New selected hosted checks execute current real slice; no lowering/deleting prior checks or hidden skips.
- Fresh independent Review of clean committed full task candidate plus all actual applicable exact-head hosted selected jobs SUCCESS. Task PASS does not establish S2 Gate PASS.

# Forbidden

No architecture/public contracts/security/ACK/Sync/compatibility/server schema changes; no PR7 restore; no Dart/Flutter/Mobile TS/JS bridge/codegen/shared native rewrite; no Room/ORM/third-party network/runtime/native SQLite other than SQLxDesktop and built-in Android SDK. No S3Java/S4plugin/Loop2, Web history database, network send/retry/fetch engine, OS token-storage redesign or speculative repository framework.

# Minimality

Use direct existing SQLite semantics, one real atomic adapter and small present storage Repository APIs. A new interface must serve the actual TypeScript/native boundary or current equivalent fixture runner; no generic future strategy/ORM/parser/framework. Native test transport exists only to prove the current TS intents execute atomically in actual SQLx, not a new product IPC contract.

# Verification

Existing pre-edit baseline:
- `tools/verify-loop1-ctrl-002.ps1` Development while metadata editing, clean committed Acceptance for independent review.
- `tools/verify-frozen-architecture.ps1`; bundledPython -B ci/check_architecture.py --scope all --json; bundledPython -B contracts/websocket/verify.py; existing Sync/plugin fixture verifier; existing tests/architecture and tests/ci.
Bind exact independently accepted current checker commands before business edits. Recorded sourceall0/frozen53 are architecture evidence only, no future runtime claim.
After implementation, add exact available TS compile/test, actual SQLx adapter, actual Android build/emulator/instrumentation and migration/rollback commands to this Task and README. New slice runner paths above are planned until written/executed; they are not baseline or acceptance evidence yet. Provision only approved stack's necessary tooling in owned external locations, disclose availability failures; no unapproved dependency selection to make build easier. Run git diff--check with CR-aware mode only for documented retained raw-byte evidence and normal scoped changes. Actual selected Linux hosted CI covers known local Windows privilege controls.

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/readiness.md`; byte-preserved accepted architecture dependency archive/manifest; new Coordinator Recorder external H:/.codex/evidence/s2-sqlite-20261001/research/runs/R-S2-SQLITE-COORDINATOR-20261001. Finished prior traces immutable.

# Handoff

Coordinator owns only task readiness/progress/checkpoint/evidence until clean activation commit and sole-writer release; fresh Implementation Agent owns bounded source afterward. Accepted lastgood maina28752967ddd471cd281aece7ea9b343521356e8; S1PASS/S2OPEN. Original744unknownfiles and withdrawn historical task branch/worktree preserved. No product services/code started by Coordinator. Local Rust/TS/Android build tooling must be verified/provisioned explicitly by implementation; no runtime PASS presumed.

# Implementation Verification / Recovery

Completed actual bounded TS/native/Kotlin SQLite storage slice; see `spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/implementation.md` and immutable local-command-history/raw logs. Desktop actual SQLx13cases/98assertions + real native unit PASS; Android actual emulator13cases/97assertions/build/install PASS; source-only local all0/frozen53/architecture53 PASS, CI31PASS4Windowsprivilegeskips; WSS/SyncPlugin PASS. Live build-cache source checker FAIL and wrapper download failure preserved; clean committed independent/hosted rerun required. No Task/S2 Gate acceptance claim. Last independently accepted maina287529; initialTask2338667. Product/review-state e67953a clean detached local recovery Development PASS23specs/status0, sourceall0 PASS; final metadata closure candidate follows unchanged product. Own Recorder finishes/validates after candidate commit, reported separately with external trace.

# Next Action

Fresh independent Review of exact full clean committed candidate; actual selected exact-head hosted CI before administrative done. Coordinator handles push/PR authorization. Implementation Agent owns all bounded source/currentTask/evidence changes until clean commit and writer release; no unknown work overwritten. Original H:/IM-platform/historical GString FAIL/waiver preserved.

# Independent FAIL / Fresh Fix / Human Stop Recovery

Independent ee82 Review FAIL (minSDK26 unsupportedUPSERT and UTF16 text lengths) remains byte-preserved under fix1/independent-failed-review.zip. Fresh Fix aligns minSDK/config/CI/verifier34 and counts canonical4096codepoints with actual boundary/durable tests. ActualSQLx13cases106assertions/unit1PASS; stable minimumAPI34 SDKSQLite3.39.2 first install13cases105assertionsPASS and pm-clear13/105PASS. Command: bundledPython -B tools/verify_client_sqlite.py --scope desktop / --scope mobile --serial emulator-5584 via external fix1/tool.py actual environment. Full evidence: spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/fix1/fix-report.md and checks.md. Task remains uniquely review; NEW independent Review full finalSHA plus actual selected exactHEAD hosted CI required. Local/Recorder PASS is not Task or S2PASS. Prior FAIL/wrapper/cache/GString records preserved.

Latest Human exact instruction: LOOP1-CLIENT-SQLITE-001完成后立即按顺序执行以下操作：发起pr并合并、同步H:/IM-platform、记录当前进度、中止下一步实现. Coordinator closes current Task, authorized PR/merge, safely syncs original preserving unknown files, records progress, then STOP before SEND/SYNC/WEB. This supersedes earlier next-S2 continuation. Fresh Fix owns scoped work until clean candidate/release; independently accepted lastgood maina287529. FinalSHA/finishedvalidatedRecorder returned separately, never selfaccept.

# Independent Review2 FAIL / Fresh Fix2

Review2 exact6dc FAIL Cursor256 UTF16 mismatch preserved in fix2/independent-failed-review2.zip plus manifest. Actual hosted36905605691 FAIL Mobile retired tools package/Gate preserved,11otherjobsSUCCESS not TaskPASS. Fresh Fix2 directly counts cursor codepoints in TS/Kotlin and specifies setup-android v3 packages platform-tools; contracts/nativeSQLx adapter unchanged. Command: bundledPython -B tools/verify_client_sqlite.py --scope desktop / --scope mobile --serial emulator-5588 via disclosed external fix2 helpers. ActualSQLx13/118/nativeunit1PASS; actual minimumAPI34 SDKSQLite3.39.2 firstinstall/pmclear each13/116PASS. Evidence fix2/fix-report.md/local-command-history.json. Livecache/tooling failures retained, clean committed Recovery/authority/source/contracts checks follow. Current Task remains review, independent acceptance pending; NEW fresh Review3/exactHEAD hostedCI, then Coordinator performs authorizedPR/merge/safe original sync/progress/STOP before next implementation. S1PASS/S2OPEN. Original744files/GStringFAIL/waiver immutable; no Fix egress.

Fix2 clean committed a8c0cd0c183dae6145f60641b8273adb9f09df3a Recovery Acceptance23specs/sourceall0/frozen53/architecture53/CI31(4Windows privilege skips)/WSS/SyncPlugin/diffcheck/status0 PASS. Exact checks.md/clean-checks.json. Candidate remains review; fresh independent Review3 plus exactHEAD hosted actual checks required. Owned emulator stopped; no egress; final evidence-only candidate returned separately.

# Additional independently confirmed current integer repair

Fresh readonly assessment exact6dc and realSQLx precision/MAX promotion proof bytepreserved under fix2/independent-integer-assessment.zip+manifest. Canonical models/history/contiguous and current contracts/database bigint require exact concrete signed64 subset, no JSsafe authority. TS internal safe number|bigint input/decimal SQLbinding/contiguous bigint; unsafe JSnumber explicitly rejected, actual largevalue requiresbigint. Both CTEs maxguard preventsSQL REAL overflow; KotlinLong remains exact. No publicmaximum/wireparser/newlibrary/nativebusiness/schema change. ActualSQLx13/141/nativeunit1PASS, minimumAPI34 SDKSQLite3.39.2 firstinstall/pmclear each13/137PASS. Newclean committedchecks follow, freshReview3/applicable exactHEAD hosted mandatory. Taskreview/S1PASS/S2OPEN; Coordinator authorizedcurrentPR/merge/safe original sync/progress/STOP. No implementation of next task.

FinalFix2 integer product 6e62a30087ab316b784daf50dbde10eb4a0b4a03 clean committed RecoveryAcceptance23specs10.125s/allsource0/frozen53/architecture53/CI31(4Windowsprivilegeskips)/WSS/SyncPlugin/diff/status0 PASS locally; exact fix2/integer-clean-checks.json/rawgz. Final evidence-only SHA returned by gitHEAD, sourceequalproduct verified before writer release. NEWfreshReview3/actualexactHEADhostedbeforeTaskdone; HumanSTOPafterSQLitePRmerge/safeoriginalsync/progress still applies.

# Coordinator Review3 PASS / Exact Hosted Pending

Latest authoritative recovery: fresh independent /root/s2_sqlite_review3 PASS exact9a86d3b641ca60b526c65abcc7a9aeee0b48d082/full a287529..candidate in clean H:/isv3-sqlite. Actual SQLx13/141/nativeunit1 and AndroidAPI34/SQLite3.39.2 first-install/pm-clear each13/137 PASS; clean Recovery23/source0/frozen53/architecture53/CI31(4Winprivilege limits)/WSS/SyncPlugin PASS. Report external review3/review-report.md; finished validated40events manifest74feeaa81e270ef8d7adaac04a48161adb0d6c15400ce5c1bbd8b307a6be728e. All capabilities/owned emulators released; Coordinator owns subsequent recovery metadata. Prior implementation/fix ownership and next-action sections above describe historical phases.

Exact provider36910351172/9a86d3b remains in_progress:11completed jobsSUCCESS, Mobile running/Gate pending. No Taskdone or S2PASS. Official running-job logs404/browser os-error3 limitations retained. New admin candidate requires NEW independent Review and exactHEAD selected CI; no old/locally mocked acceptance. Required final order: complete SQLite, authorized PR/create/update/merge, independently verify actualmain, safely sync H:/IM-platform, record progress, STOP. No SEND/SYNC/WEB activation. Latest Human instruction: “LOOP1-CLIENT-SQLITE-001完成后立即按顺序执行以下操作：发起pr并合并、同步H:/IM-platform、记录当前进度、中止下一步实现”。 This explicit UTF8 text is authoritative; previously retained garbled rendering is historical provenance, not a new instruction. Original744files unchanged/local-only byte backup never sent; historical GStringFAIL/WAIVED_BY_HUMAN unchanged.

# Fresh Fix3 / Hosted KVM failure recovery

Exact9a run36910351172 completed FAIL:11jobsSUCCESS, Mobile second instrumentation timeout180s/GateFAIL. Official clean wrapper/build62tasks and first13cases137assertions PASS are retained; denied /dev/kvm and -accel off establish current hosted environment defect. Fix3 only enables disposable hosted Linux KVM permissions, checks read/write and emulator acceleration, explicitly disables software fallback configuration. Product clients/tests/tools remain byte-identical to9a. Full evidence under fix3/; Review3 PASS archive immutable. Task remains review/S1PASS/S2OPEN. NEW independent Review and actual exact-head all13jobs/two real Android phases required; then Coordinator authorizedPR/merge/actualmain/safeoriginalsync/progress/STOP. No next implementation or Groovy waiver repair. Fix3 inherited Coordinator metadata preserved; no original files changed.

Fix3 clean committed51f00b3 local checks PASS: RecoveryAcceptance23specs8.828s/status0/sourceall0/frozen53/architecture53/CI31(4Windowsprivilegeskips)/WSS/SyncPlugin/diffcheck; product clients/tests/verifier0diff from9a. Commands/results/rawgzip hashes in fix3/clean-checks.json; no repeated unchanged local runtimes. Final evidence-only SHA returned separately; NEW independent Review4 and exact hostedall13jobs/two actual137-assertion phases required.

# Fresh Fix4 / Review4 and current hosted FAIL

Fresh Fix4 corrects only hosted /dev/kvm permission preparation. Task review, S1 PASS / S2 OPEN. Existing character device is required, current runner identity and before/after stat are printed, sudo chown to runner owner/group and synchronous chmod0600 followed by explicit read/write check. No fake device/kernel/runner change/fallback/ignored error. Current acceleration enabled/prelaunch accel-check, API34, official wrapper, 180-second instrumentation and both full13cases137assertion rounds unchanged. Actual current hosted acceptance remains pending. Source clients/tests/SQLite verifiers remain identical to reviewed9a86d3b641ca60b526c65abcc7a9aeee0b48d082; prior Review3 actual13/141/nativeunit1 and Android13/137 first/clear are PRIOR evidence, not repeated here.

Review4 FAIL exactcdbcbc51fe42618e445b0bcef6eaff0b0e97242a is byte-archived with its in_progress provider snapshot under independent-failed-review4.zip,92members+verifiedmanifest. Separately completed run36916339328 FAIL has11jobsSUCCESS/Mobile and GateFAIL; seven current provider files byte-preserved under fix4/, completed-ci-manifest.json. Full raw1443442bytes SHA256ec0fdd96eec605d3215f52fdf0cb139a3c3b32d0672ad1665a9d0e1c41903687; gzip SHA256f4eed5111308d8aa8c3fea9e444ba4d52585e91d22b861eb97d2c77b2b2af045. Permission prerequisite failed before emulator; absent device/asynchronous race/other concrete cause is UNKNOWN, not inferred. Current direct permissions remove asynchronous whole-rule reliance without claiming that was proven cause.

Initial live H:/ica recovery baseline FAIL on ignored node_modules inspected by effective guard, preserved in Recorder; clean detached H:/if4-sqlite Acceptance baseline PASS23specs/status0. No cache deletion/checker weakening. Clean committed checks follow; known4Windowsprivilege limits require actual hostedLinux. Startup/passive reads outside Recorder explicitly incomplete prospective_resume. One metadata helper draft failed functions JS parsing before any process/write, corrected without hidden mutation.

No Frozen/contracts/ADRs/other Task/original files changed; GStringFAIL remains WAIVED_BY_HUMAN, not PASS. NEW independent Review and all actual exact-head13selected hosted jobs/every required stepSUCCESS plus usableKVM/two fullAndroid rounds required. Then independent administrative closure/CI, authorizedTaskPR/merge/actualmainverify/protectedoriginalsync/progress/STOP beforeSEND/SYNC/WEB. Original744unknownfiles and LOCALONLY backup excluded from all payloads.

Fix4 clean committed 0c2af19 Recovery Acceptance23specs7.344s/status0/sourceall0/frozen53/architecture53/CI31(4knownWindowsprivilegeskips)/WSS/SyncPlugin/diffcheck PASS. Product clients/tests/verifier0diff from9a PASS. Actual argv/rawbytes/durations/gzipSHA in fix4/clean-checks.json; no repeated unchanged native/Android runtimes, no hostedPASS. Final evidence-onlycandidate returned separately, NEWindependentReview5/currentexactHEADall13/KVM/twoAndroidrounds required.

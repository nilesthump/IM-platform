---
task_id: LOOP1-CLIENT-I18N-001
title: 三端国际化拆包
status: done
owner: fresh Implementation Agent
stage: S2
gate: S2
client_supplement_phase: i18n_product
---

# Goal

依赖任务二完成，提取三端现有用户可见文案，建立英语、简体中文和日语的独立语言资源。

1. 统一语言标识 en、zh-CN、ja-JP，以及跨端文案语义和占位参数。Web/Desktop 使用 TypeScript 侧纯数据语言资源，Android 使用现有 Kotlin/Compose 技术栈下的等价资源映射。

2. 覆盖页面文本、按钮、输入提示、校验与错误提示、连接及同步状态、无障碍标签，以及已有系统通知和托盘文案。将状态逻辑使用的稳定标识与翻译后的显示文本分离。

3. Settings 增加固定入口“Language / 语言 / 言語”，使用固定顺序的滚动选择列表：
   English → 简体中文 → 日本語。
   选项名称保持各自语言，切换后即时更新当前界面，本地保存并恢复语言选择。

4. 将语言选择的本地持久化范围、存储位置、字段和校验规则纳入三端偏好适配器的明确架构授权，保证现有外观配置继续有效，主题、字号、间距和语言独立保持。

5. 建立语言键完整性、占位参数一致性和英文回退验证；覆盖切换后的页面状态、消息状态、布局可读性及本地偏好恢复，完成三种语言的适用截图和 Architect 验收。


# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md` §2.3/§3/§6.1～6.6/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A。
- `spec/architecture/decisions/ADR-0012-client-supplement-planning.md`；ADR-0005/0006/0007/0008/0009/0010/0011及对应已接受证据；`spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`；`contracts/websocket/envelope.schema.json`、`contracts/websocket/sync-v1.schema.json`、`contracts/http/auth-user-friend.openapi.json`、`contracts/http/sync.openapi.json`、`contracts/database/`与对应golden fixtures。
- `spec/acceptance/client-gui.md`、`spec/acceptance/client-supplement.md`基线表与本任务全部强制验收；激活时重新读取前项实际接受树/截图/证据。

# Technology Authorization

canonical§6.1/§6.5与accepted ADR5/6/9/11；ADR12正式接受后§6.6窄补充。Web/Desktop/shared TypeScript、React，Desktop Tauri+SQLx必要Rustnative；Mobile Android Kotlin/Compose等价contracts/fixtures、SDKSQLite，真实Android Studio emulator。无新runtime/i18n/network/state/ORM库。
client_language: TypeScript
client_language: Kotlin
client_language: Rust
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

语言偏好为设备/宿主应用范围，跨账号保持、无云同步，独立于credential、账号SQLite、消息和Sync cursor。默认 en；只允许大小写精确的 en、zh-CN、ja-JP，不trim、不接受系统locale猜测或任意别名。缺失/非法/超长/存储不可用回退内存en，写失败诚实显示且不覆盖其他偏好或清除其他key。固定三端位置：Web仅新增 src/ui/language.ts 以原生 localStorage固定key plugworldim.language.v1读取/写入raw UTF-8 enum（最长5bytes），不改plugworldim.appearance.v1三字段；Desktop TypeScript native.ts持有language意图，desktop_capabilities.rs仅窄language_load/save字符串枚举校验及app_data/language.txt读写raw UTF-8（最多5bytes、无BOM/换行），appearance.json三项tuple原字节继续可读；Android Preferences.kt在既有MODE_PRIVATE appearance SharedPreferences只增String key language（最多5UTF-8bytes），保留theme/fontSize/density键和值。theme仅cold/warm；Web fontSize14/16/18/20、density compact/comfortable/spacious；Desktop/Android既有fontSize14..22、density0.8/1.0/1.2及默认cold/16/1继续有效。四标量语义各自独立，但Web/Desktop外观record仍三项，不合并为四字段记录。当前三字段appearance守卫不得提前放宽；只有I18N依赖独立接受+集成同步且任务active/review/done、client_supplement_phase: i18n_product才可实现语言adapter及对应窄源码guard。STATE/UI-REF和本规划不获得语言持久化产品许可。

# Dependencies

- LOOP1-CLIENT-UI-REF-001；须独立接受、protected integration/actual-main验证及H:/IM-platform同步全部完成，status done才可激活本项，不只是本地commit。

# Allowed Paths

- `tools/build_language_packs.py`

- `clients/web/src/ui/main.tsx`
- `clients/web/src/ui/style.css`
- `clients/web/src/ui/components/**`
- `clients/web/src/ui/i18n/**`
- `clients/web/src/ui/language.ts`
- `clients/web/src/application/client.ts`
- `clients/desktop/src/ui/main.tsx`
- `clients/desktop/src/ui/style.css`
- `clients/desktop/src/ui/components/**`
- `clients/desktop/src/ui/i18n/**`
- `clients/desktop/src/application/ui/workspace.ts`
- `clients/desktop/src/application/ui/native.ts`
- `clients/desktop/src/application/ui/auth.ts`
- `clients/desktop/src-tauri/src/desktop_capabilities.rs`
- `clients/desktop/src-tauri/src/lib.rs`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/i18n/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Preferences.kt`
- `tests/clients/i18n/**`
- `tests/clients/web/behavior.mjs`
- `tests/clients/web/browser.mjs`
- `tests/clients/gui/desktop_render.mjs`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/**`
- `ci/check_architecture.py`
- `tests/architecture/test_client_technology.py`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-I18N-001/**`
- `spec/progress/checkpoints/*loop1-client-i18n-001*.md`
- `spec/tasks/backlog/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/active/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/review/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/done/LOOP1-CLIENT-I18N-001.md`

当前实际源码职责如client-supplement基线表；本项列出的新增组件/测试/资源目录仅承载本Task已明确职责，不授权整个clients/backend通配或跨职责搬迁。激活时以最新前项树核对，路径不足先登记scope修订并遵守authority；allowed_paths不是架构豁免。I18N守卫改动仅正式i18n_product期、窄语言adapter和negative controls，不放宽appearance/business持久化。

# Acceptance

## Final Human scope clarification (2026-10-11)

Accepted ADR-0012 remains authoritative: en default/fallback; en/zh-CN/ja-JP remain built in across all three clients. Frozen canonical/manifest, ADR-0012 original and accepted records are unchanged; no ADR-0013 is introduced. The intermediate single-zh-CN/download proposal was superseded before an authority draft or product implementation.

Additional current acceptance: reproducibly generate separate en.json and ja-JP.json artifacts from the existing independent pure-data built-in resources using tools/build_language_packs.py. Verify cross-platform keys/placeholders, body equivalence, deterministic bytes and recorded sizes/SHA256. Artifacts are NOT_PUBLISHED and contain no fabricated download URL. Existing TS/Kotlin data remain current product resource authority; complete unified JSON migration is deferred.

Publication to a real project-controlled static HTTPS endpoint, catalog/download/installation/deletion management and offline pack persistence are deferred to GitHub issue #37 created by the parent Coordinator; issue https://github.com/nilesthump/IM-platform/issues/37 (enhancement, needs-info). No pack storage/download UI/network changes are authorized by this clarification. Existing raw locale preference and appearance three-field boundaries remain unchanged.

Verification: python -Xutf8 -B tools/build_language_packs.py --verify; python -Xutf8 -B -m unittest discover -s tests/clients/i18n -p test_language_packs.py. Default build writes only owned tests/clients/i18n/.runtime/language-packs; parent may explicitly choose an owned external artifact output. No publish/deploy command. Runtime/Architect/independent Review/hosted/integration/main sync remain required; old local PASS is not new acceptance.

Goal全部条目与spec/acceptance/client-supplement.md本任务段是强制验收，既有client-gui截图/Architect/独立Review/CI/main链共同生效。独立Reviewer核对真实请求/存储/状态/渲染或完整性/语言证据和实际import/minimality；不得以基线PASS代替新增场景。done前须Completion Metadata真实绑定独立接受/受保护集成/main同步，且相关证据文件可核对。前项接受树是本项baseline，不复用旧候选接受认定新SHA。

## Explicit current Human acceptance scope (2026-10-12)

Human: “继续验收，补充：此任务验收不需要实现issue #37”. Issue37 implementation/publication/download management is NOT a prerequisite or completion criterion for this task. Retain the current three builtins, ADR12 default/fallback and unpublished standalone artifacts; all current three-end runtime, Architect, independent Review, hosted/integration/main-sync requirements remain.

# Forbidden

不改变contracts/schema/ACK/security/兼容、技术边界或未来AI/plugin/runtime/Java功能；Web不新增聊天DB/离线历史/全量初始回填。不覆盖未知main work、不删除真实用户数据库/偏好/凭据，不自动跑StageGate。本规划endpoint不授权激活本Task。

# Minimality

使用既有Repository收敛/Send/Sync/UI与三端授权栈，直接满足本项要求；新抽象必须有现要求付租证明。无generic framework/事件总线/新库/未来migration机制。行为/视觉基线优先，语言仅纯数据与固定单标量adapter。

# Verification

- Minimum baseline: `python -Xutf8 -B ci/check_architecture.py --scope all --json`；`python -Xutf8 -B tools/verify_frozen_architecture.py`；`python -Xutf8 -B ci/check_s2_planning.py`；`tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed候选 `-Mode Acceptance`。
- `python -Xutf8 -B tools/verify_client_sqlite.py --scope shared`；`python -Xutf8 -B tools/verify_client_send.py --scope shared`及`--scope desktop`；`python -Xutf8 -B tools/verify_client_sync.py --scope shared`及`--scope desktop`；已接受checker命令是可执行基线，不把planned harness当PASS。
- Android `python -Xutf8 -B tools/verify_client_send.py --scope mobile --serial <实际独占emulator serial>`、`python -Xutf8 -B tools/verify_client_sync.py --scope mobile --serial <实际serial>`；`python -Xutf8 -B tests/clients/gui/android.py --serial <实际serial> --capture`。Android SDK/JDK17/Gradle及真实Android Studio emulator、有效TLS/受控证书、独占adb reverse/fixture启用；placeholder必须替换为真实值记录。Host/mock不能代替emulator。
- Web `python -Xutf8 -B tests/clients/web/verify.py`（locked install/build/behavior/appearance/source）；`node tests/clients/web/browser.mjs`实际原截图。Desktop现有locked build/`python -Xutf8 -B tests/clients/gui/native.py package` Windows安装包及真实截图/通知tray（仅后续产品任务激活后；需现有Windows x86_64 MSVC/Visual Studio vcvars64、Rust/Cargo/Tauri及locked npm依赖，遵循native.py的既有工具链路径；先完成package构建，再安装同候选制品并以其自身身份运行；缺工具链/安装/独占环境不计PASS）；`python -Xutf8 -B tests/clients/gui/regressions.py`只在输入与独占环境满足时运行。
- Backend现有`go test ./...`（cwd backend/go）和 `python -Xutf8 -B tools/verify_sync_runtime.py`适用真实Go/PostgreSQL/NATS/TLS入口；DB_TEST_ENABLE=1、实际受控DATABASE_URL/NATS_URL，缺环境skip不计PASS。受控数据/证书/进程创建与回滚须记录，不读取私人数据或凭据。
- 激活前为本任务新增场景明确实现并登记实际harness命令、fault hook/环境、fixture身份、独占资源及清理。现入口baseline不替代新增A/B/组件/语言证据；未执行命令不计PASS。
- Screenshot manifest绑定候选SHA/build/runtime/fixture/状态/尺寸/theme/font/density/语言与PNG hash，真实原图/Architect决策；独立Review/exact-head必需hosted jobs/protected integration/actual-main/safe sync全部完成才done。

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-I18N-001/`保存可复现场景/原始结果/failed记录/真实截图Architect/independent Review/hosted/main/sync；Research Recorder独立run。当前未执行产品验收；local/Recorder PASS不是Task/Stage PASS。

# Completion Metadata

acceptance_result: PASS
accepted_candidate_sha: 99a2dd70fa6c70a69762663ccc7ce38b20013d63
integrated_main_sha: 82cd512f659873a9d17cbef803da1acb873613cc
main_sync_result: PASS
independent_review_evidence: spec/progress/evidence/LOOP1-CLIENT-I18N-001/accepted-20261013/independent-report.md
hosted_acceptance_evidence: spec/progress/evidence/LOOP1-CLIENT-I18N-001/accepted-20261013/product-hosted-acceptance-20261013.json
main_sync_evidence: spec/progress/evidence/LOOP1-CLIENT-I18N-001/accepted-20261013/product-main-sync-20261013.json

# Handoff

Fresh implementation in assigned managed root H:/.codex/worktrees/i18n/IM-platform, task/LOOP1-CLIENT-I18N-001. Initial HEAD b52f8b85bc699821f3720e339fcd48e17b2b04b1. UIREF external final administrative seal PASS and every linked hash verified; supersedes historical current pending. Task passed backlog -> ready -> active after dependencies satisfied. No main writes or adoption of 781 unknown changes. Canonical efbe04c7 and historical PDF546915 match.

Minimum frozen/planning baseline exit0. Recovery Development first failed because nested python selected Python2.7; explicit Python3 PATH rerun exit0. Architecture all baseline independently recorded by parent PASS exit0. Local evidence is not acceptance. Recorder implementation run R-I18N-20261011-IMPL uses P-I18N-20261011-IMPL (same visible prompt; parent prompt already bound); initial rejected start retained as public fact.

# New Harness and Runtime Matrix

`python -Xutf8 -B tests/clients/i18n/verify.py`: actual TS/Kotlin resource key/placeholder/English-base negative controls and real adapter tests; no new libraries. `node tests/clients/i18n/browser.mjs`: built Web, actual browser locale/page/draft/appearance/invalid/unavailable/restart checks and raw screenshots. Android dedicated instrumentation under existing ui androidTest runs on owned API34 emulator; native adapter/preferences/Compose UI switch/state/restart. Desktop locked Windows package plus installed identity/native notifications/tray on same candidate; test harness records ownership and restores original owned fixture preferences/install/resources. Real backend regression uses accepted STATE harness with controlled TLS/Go/PostgreSQL/NATS fixtures; no mocks counted as runtime acceptance. Runtime/capture commands registered in tests/clients/i18n/README.md when executable; unexecuted commands remain PENDING. Screenshot manifest binds actual candidate/build/fixture/state/size/theme/font/density/locale/hash. Independent Architect/Review/hosted/integration/sync delegated to parent after exclusive writer release; no self acceptance.

# Next Action

Implement full language presentation, strict independent adapters and negative controls within allowed paths. Complete builds/local harness then clean candidate review handoff; keep S2 OPEN, acceptance/sync PENDING.

# Runtime Progress 2026-10-11

See evidence/runtime-progress-20261011.json: Web actual compiled26 captures PASS_LOCAL_CHECKS; Desktop renderer PASS_LOCAL_CHECKS and installed real backend login/history/zh-CN observed. Android Preferences passed, Compose retained failed diagnostics and SDK accessibility cache repair under test. Three preflight P2 fixes being authored externally. Human approved exact CurrentUser-only CA lease OPEN; close/remove and full root DER-set equality required before acceptance. No committed candidate, independent Review/Architect/CI/sync PASS claimed.

# Latest Runtime Handoff
User verified zh-CN/ja-JP tray menus and explicitly requested no repeat screenshots. English real popup original retained. Actual Web six A/B Go/PG/NATS checks PASS_LOCAL_CHECKS; Android Compose run7 PASS_LOCAL_CHECKS; fix8 Desktop/Android builds PASS, Android process restart built but not run. Physical Escape stopped Computer Use. Temporary CA removed with certutil; exact original user/machine DER sets restored. Evidence runtime-progress-tray-human.json; all clean-candidate independent Review/Architect/CI/integration/main sync remain PENDING.


# Resume 2026-10-12

User resumed from pause. Runtime/source/cleanup recovery evidence: spec/progress/evidence/LOOP1-CLIENT-I18N-001/resume-20261012.json; checkpoint 2026-10-12-loop1-client-i18n-001-runtime.md. All implementation remains parent-owned WIP at baseline b52f8b85bc699821f3720e339fcd48e17b2b04b1; clean candidate, independent acceptance and main sync remain PENDING. New Android true process restart and Desktop offline switch/ja native notification/true process restart PASS_LOCAL_CHECKS; original known installation/preferences restored and trust CLOSED. Next exact action: clean candidate and build binding, independent Architect/Review/required hosted/protected integration/main sync.

# Committed Candidate Handoff 2026-10-12

This supersedes earlier WIP and next-action prose.

Candidate e5de5ca83d5f75ced349697eab84292d65b2b9d0 committed/pushed on task/LOOP1-CLIENT-I18N-001. Independent semantic CODE PASS, exact-head hosted run38201496894 all14 jobs PASS. Clean Android actual Compose/Go and true process restart PASS_LOCAL_CHECKS, preferences restored. Web/Windows/Android builds and compiled Desktop renderer PASS. Full Task acceptance and S2 Gate remain PENDING.

Execution BLOCKED_EXTERNAL_ACCESS: Human-visible test CA invisible to fresh agent processes; normally validated real Web login fails. No TLS bypass. Resolve trust visibility before another test lease, then clean Web six A/B and installed Desktop native runtime, final Architect, protected integration, actual-main audit and safe main sync. Human confirmed deleting exact CA; actual-agent original root sets equal. Owned AVD/backend/relays closed, artifacts/failures retained. Known original Desktop install/preferences restored. User-accepted zh/ja tray needs no repeat screenshots.

Retain3builtins/en default/fallback ADR12; standalone en/ja JSON NOT_PUBLISHED. Static publication/download/install/delete/futurezhdefault/unifiedJSON deferred issue37. Accepted main b52 unchanged; parent sole writer owns uncommitted recovery docs, product source committed e5. Evidence: spec/progress/evidence/LOOP1-CLIENT-I18N-001/candidate-20261012.json.

# Repaired Candidate Handoff 2026-10-12

# I18N repaired Android candidate checkpoint

Candidate `9700c498700d1cfef3b48c445452d87851621c64`, task branch `task/LOOP1-CLIENT-I18N-001`, assigned root `H:\.codex\worktrees\i18n\IM-platform`. Exact local Android build, 19 original screenshots, TLS negative checks and five-phase true process restart passed locally. Independent review verdict and exact-head hosted evidence are preserved in `spec/progress/evidence/LOOP1-CLIENT-I18N-001/repaired-20261012.json`. No full Task/Gate PASS claimed.

Web/Desktop normal HTTPS remains BLOCKED_EXTERNAL_ACCESS due to distinct interactive-user/agent certificate views. Human confirmed deleting the exact test CA; agent original complete user/machine DER sets restored. No more Windows trust mutation. All owned runtime fixtures closed and Android preferences restored; artifacts/failures retained. Human accepted zh/ja tray menus; do not repeat.

Retain current three builtins/en default, unpublished en/ja artifacts and issue37. Task stays active, S1 PASS/S2 OPEN. Accepted main `b52f8b85bc699821f3720e339fcd48e17b2b04b1` unchanged; synchronization PENDING. Parent owns uncommitted recovery docs and retained runtime archives; unknown main changes untouched.

Next exact action: resolve normal HTTPS execution/trust visibility without bypass, then clean candidate Web/installed Desktop runtime, full Architect, protected integration, exact-head acceptance and safe main synchronization. Earlier e5/335 failed pixel evidence remains historical, not promoted.

# Acceptance resumed with bounded machine trust (2026-10-12)

Human explicitly approved temporary LocalMachine Root trust for exact CA8713a454493c0513e523e79ec1ec92b054120754 / SHA256 b758abdce1beb1032ed67cbe5782d06184acf2a9ce97edcb60b465fa68b3af30, localhost/127.0.0.1 constraints, expiry2026-10-12T15:09:20Z. Elevated owned helper has120min maximum and exact certificate removal/full original root-set comparison. Fresh process normal chain validates; actual default Edge Web six A/B scenarios PASS_LOCAL_CHECKS exact9700,69 originals. Independent Web pixel/proof Review ongoing, Desktop build/native runtime pending. Trust OPEN; mandatory cleanup before yield. This is test-environment authorization only, no product security/contract change. Earlier CurrentUser failures are preserved and not relabeled. Issue37 is explicitly outside task acceptance.

# Latest acceptance and cleanup checkpoint (2026-10-12)

Supersedes historical pending/trust-open/implementation next-action text. Product/capture candidate `e829352aa02c3e87d3d01376df4ef1ac2c9ede38` committed locally; latest two capture-only fixes are NOT pushed. Web3 six actual Go/PG/NATS A/B and69 original PNGs independently PASS. Android19 originals and true restart/TLS negative evidence independently accepted at9700; all product inputs unchanged through e829. Actual installed Desktop NSIS built9700, normalTLS login, 3language/maxappearance/pages/offline/retaineddraft/history, trueja restart and invalidEN→en restart, nativeFAILED→retry→SENT with0→1servermessage/1Outbox PASS_LOCAL_CHECKS; fresh Native Architect/fullsemantic review pending. Native originals are JPEG as returned by Computer Use, hash-bound, never edited. Initial metadata correction and refresh/reopened-selection qualifications remain explicit.

Trust CLOSED at2026-10-12T06:45:05Z; complete original CurrentUser74/LocalMachine72 thumbprint+DER sets restored, ownedCA absent, independently rechecked by fresh process. Known original installed3 and appearance exactbytes/language absence restored. Actual owned backend exit0/PASS cleanup; controlled fixture account data retained, no private DB/credential restoration claim. User-accepted zh/ja tray not repeated.

Auto-review rejected publicGitHub push requiring explicit Human publication authorization. Destination https://github.com/nilesthump/IM-platform is existing origin; configured task branch only, no unknown main data or private runtime artifacts intended. Prepare/review final committed recovery candidate then request final approval to push/PR through the existing protected workflow. Until approval+requiredexactheadCI/integration/actualmain/safeSync, task staysreview and Completion Metadata PENDING; do not reportdone or S2PASS. Issue37 explicitly not required. Durable evidence acceptance-20261012.json and latest checkpoint2026-10-12-loop1-client-i18n-001-acceptance.md. Parent owns task recovery and generated archives; no other active writer. Main acceptedb52f8 remains unchanged, unknown782 files preserved.

# Independent Native FAIL and minimal repair (2026-10-12)

Fresh independent review of b40/e829 found P2: Desktop green Online derives from session despite offline transport. Original FAIL preserved in navigation-repair-20261012.json. Fresh Fix Agent committed 1115ac496ddfc7f7a8f77166aa5f33b9d460d977 (Navigation stable connection plus renderer regression only), local typecheck/renderer/architecture checks passed. New installed build/targeted actual disconnected-reconnected pixels and a NEW fresh independent review remain required. Human now explicitly permits task publication after review and continued PR/CI/integration; no public push yet. Prior fixture restoration remains valid; any necessary approved exact CA reuse must again close and restore complete original root sets before yield. Task stays review/S2 OPEN, main b52 unchanged; issue37 excluded. Parent sole writer owns recovery and generated archives.

# Fixed native runtime and closed cleanup (2026-10-12)

Actual fix1115 clean Desktop build/install passed; normal default system TLS login, real disconnected language switches en/zh/ja and real reconnect ja/zh/en, thirteen original JPEGs demonstrate correct non-green offline/green online rail with retained account, Morgan selection, two Sent history rows, unsent multilingual draft and warm22/density1.2. Read-only controlled PG confirms2 messages/2 logical message.created Outbox and0 draft rows. This is targeted navigation regression, not newly claimed full native A/B proof; unchanged protocol/STATE evidence remains bounded. ExistingWeb3/Android evidence inputs unchanged.

Original three native files and exact appearance/language preferences restored, owned PID47444 stopped. Exact CA lease CLOSED07:32:02Z; fresh process confirms original user74/machine72 full DER sets restored and owned root absent. Owned actual backend exited0/PASS cleanup. All original failures retained. Fresh independent review still pending; no push/hosted/integration/main sync yet. Mainacceptedb52 unchanged. Evidence navigation-repair-20261012.json.

# Final product acceptance and closure recovery 2026-10-13

This supersedes historical pending current-action statements, not historical evidence. Product PASS candidate 99a2dd70fa6c70a69762663ccc7ce38b20013d63, protected PR38 actual main 82cd512f659873a9d17cbef803da1acb873613cc, exact-head hosted38354231620/actual-main38355749163 all14 SUCCESS, safe H:/IM-platform sync PASS original782 preserved. Fresh independent Review/Native Architect evidence and exact raw CI/integration/sync receipts: spec/progress/evidence/LOOP1-CLIENT-I18N-001/accepted-20261013/acceptance-manifest.json. Task moves review -> done only after product acceptance/integration/sync. S2 remains OPEN. English/Japanese packs NOT_PUBLISHED; issue37 excluded, no download claim.

Next exact action: fresh independent bounded administrative closure Review on the committed closure candidate, hosted/protected integration/actual-main/safe sync, then external final seal. No next task activation. Parent sole repository writer owns closure docs and known generated runtime; all product source committed/synchronized. Oct13 own test CA absent; two OTHER user roots removed since Oct12, owner unknown/preserved, historical restoration PASS not relabeled as today. Research lock collision/incomplete pre-start trace disclosed in product-acceptance.md.


# 当前后继规划（2026-10-15）

上方旧Next Action/证据保持当时候选历史。Human本轮批准LOOP1-GROUP-PLAN-001规划候选，I18N后追加LOOP1-GROUP-001（同时依赖该规划正式接受/集成/安全主目录同步），再到S2 Gate。I18N既有接受不重开、语言activation_task及i18n_product不改；新群文案复用当前资源。此轮仅规划入队，GROUP backlog/S2 OPEN/STOP，无群产品PASS。

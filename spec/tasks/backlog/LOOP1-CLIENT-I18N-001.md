---
task_id: LOOP1-CLIENT-I18N-001
title: 三端国际化拆包
status: backlog
owner: unassigned
stage: S2
gate: S2
client_supplement_phase: planned
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

Goal全部条目与spec/acceptance/client-supplement.md本任务段是强制验收，既有client-gui截图/Architect/独立Review/CI/main链共同生效。独立Reviewer核对真实请求/存储/状态/渲染或完整性/语言证据和实际import/minimality；不得以基线PASS代替新增场景。done前须Completion Metadata真实绑定独立接受/受保护集成/main同步，且相关证据文件可核对。前项接受树是本项baseline，不复用旧候选接受认定新SHA。

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

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

仅backlog规格交付，无产品实现/接受/同步。起点latest accepted main b4d271ceeed40343e627450f6b43cd9c9ad5ff0e，基线审计见规划evidence/baseline-audit.md；本规划pending，S1 PASS/S2 OPEN。无本Task uncommitted product ownership，未知main工作保留。激活时fresh context读最新前项完整接受/视觉/source并补充精确harness。

# Next Action

保持backlog。后续明确授权且所有依赖独立接受/集成/main同步满足才ready→active，声明client_supplement_phase: i18n_product并登记实际新增验收命令；本次不执行产品。

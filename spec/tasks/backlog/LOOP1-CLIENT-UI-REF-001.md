---
task_id: LOOP1-CLIENT-UI-REF-001
title: 组件拆分与完整性验证
status: backlog
owner: unassigned
stage: S2
gate: S2
client_supplement_phase: planned
---

# Goal

以任务一验收后的三端产品树为行为和视觉基线，规划并验收各端现有页面、组件和展示状态的职责拆分。

1. 根据实际源码拆分应用入口、Shell、导航、认证、会话列表、消息展示、输入区域、好友及设置等现有职责，明确入口挂载、组件输入输出、状态归属和导入方向。

2. 保持各端独立视觉实现及现有 Auth、Repository、Send、Sync 职责边界，共享现有协议、类型和适用展示语义。

3. 将组件展示文案、应用状态标识与业务判断建立清晰边界，为后续语言资源提取提供稳定接口。

4. 建立拆分前后的页面、入口、功能和测试覆盖对照表。完整回归现有客户端能力及任务一新增场景，验证状态保持、事件绑定、账号隔离、同步、重发、排序和外观设置的行为等价。

5. 完成各端构建、适用自动化测试、真实运行截图和 Architect 审查，以功能完整、行为等价和视觉基线保持作为验收结果。


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
client_framework: React
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

不改Repository/Auth/Send/Sync行为；依据实际入口拆职责，不引入通用store/事件总线/共享视觉组件。

# Dependencies

- LOOP1-CLIENT-STATE-001；须独立接受、protected integration/actual-main验证及H:/IM-platform同步全部完成，status done才可激活本项，不只是本地commit。

# Allowed Paths

- `clients/web/src/ui/main.tsx`
- `clients/web/src/ui/style.css`
- `clients/web/src/ui/components/**`
- `clients/web/src/application/client.ts`
- `clients/desktop/src/ui/main.tsx`
- `clients/desktop/src/ui/style.css`
- `clients/desktop/src/ui/components/**`
- `clients/desktop/src/ui/composer.ts`
- `clients/desktop/src/application/ui/workspace.ts`
- `clients/desktop/src/application/ui/auth.ts`
- `clients/mobile/app/src/main/kotlin/im/platform/client/MainActivity.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/components/**`
- `tests/clients/ui-ref/**`
- `tests/clients/web/behavior.mjs`
- `tests/clients/web/regressions.mjs`
- `tests/clients/web/browser.mjs`
- `tests/clients/gui/composer.mjs`
- `tests/clients/gui/desktop_render.mjs`
- `tests/clients/gui/auth.mjs`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/**`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/**`
- `spec/progress/checkpoints/*loop1-client-ui-ref-001*.md`
- `spec/tasks/backlog/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/active/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/review/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/done/LOOP1-CLIENT-UI-REF-001.md`

当前实际源码职责如client-supplement基线表；本项列出的新增组件/测试/资源目录仅承载本Task已明确职责，不授权整个clients/backend通配或跨职责搬迁。激活时以最新前项树核对，路径不足先登记scope修订并遵守authority；allowed_paths不是架构豁免。本项不得实施语言资源/语言持久化adapter或改语言/外观存储guard；UIREF仅分离稳定标识与显示接口，不提前国际化。

# Acceptance

Goal全部条目与spec/acceptance/client-supplement.md本任务段是强制验收，既有client-gui截图/Architect/独立Review/CI/main链共同生效。独立Reviewer核对真实请求/存储/状态/渲染或完整性/语言证据和实际import/minimality；不得以基线PASS代替新增场景。done前须Completion Metadata真实绑定独立接受/受保护集成/main同步，且相关证据文件可核对。前项接受树是本项baseline，不复用旧候选接受认定新SHA。

# Forbidden

不改变contracts/schema/ACK/security/兼容、技术边界或未来AI/plugin/runtime/Java功能；Web不新增聊天DB/离线历史/全量初始回填。不覆盖未知main work、不删除真实用户数据库/偏好/凭据，不自动跑StageGate。本规划endpoint不授权激活本Task。

# Minimality

使用既有Repository收敛/Send/Sync/UI与三端授权栈，直接满足本项要求；新抽象必须有现要求付租证明。无generic framework/事件总线/新库/未来migration机制。仅本项行为或组件完整性/视觉基线要求。

# Verification

- Minimum baseline: `python -Xutf8 -B ci/check_architecture.py --scope all --json`；`python -Xutf8 -B tools/verify_frozen_architecture.py`；`python -Xutf8 -B ci/check_s2_planning.py`；`tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed候选 `-Mode Acceptance`。
- `python -Xutf8 -B tools/verify_client_sqlite.py --scope shared`；`python -Xutf8 -B tools/verify_client_send.py --scope shared`及`--scope desktop`；`python -Xutf8 -B tools/verify_client_sync.py --scope shared`及`--scope desktop`；已接受checker命令是可执行基线，不把planned harness当PASS。
- Android `python -Xutf8 -B tools/verify_client_send.py --scope mobile --serial <实际独占emulator serial>`、`python -Xutf8 -B tools/verify_client_sync.py --scope mobile --serial <实际serial>`；`python -Xutf8 -B tests/clients/gui/android.py --serial <实际serial> --capture`。Android SDK/JDK17/Gradle及真实Android Studio emulator、有效TLS/受控证书、独占adb reverse/fixture启用；placeholder必须替换为真实值记录。Host/mock不能代替emulator。
- Web `python -Xutf8 -B tests/clients/web/verify.py`（locked install/build/behavior/appearance/source）；`node tests/clients/web/browser.mjs`实际原截图。Desktop现有locked build/`python -Xutf8 -B tests/clients/gui/native.py tauri` Windows安装包及真实截图/通知tray；`python -Xutf8 -B tests/clients/gui/regressions.py`只在输入与独占环境满足时运行。
- Backend现有`go test ./...`（cwd backend/go）和 `python -Xutf8 -B tools/verify_sync_runtime.py`适用真实Go/PostgreSQL/NATS/TLS入口；DB_TEST_ENABLE=1、实际受控DATABASE_URL/NATS_URL，缺环境skip不计PASS。受控数据/证书/进程创建与回滚须记录，不读取私人数据或凭据。
- 激活前为本任务新增场景明确实现并登记实际harness命令、fault hook/环境、fixture身份、独占资源及清理。现入口baseline不替代新增A/B/组件/语言证据；未执行命令不计PASS。
- Screenshot manifest绑定候选SHA/build/runtime/fixture/状态/尺寸/theme/font/density/语言与PNG hash，真实原图/Architect决策；独立Review/exact-head必需hosted jobs/protected integration/actual-main/safe sync全部完成才done。

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-UI-REF-001/`保存可复现场景/原始结果/failed记录/真实截图Architect/independent Review/hosted/main/sync；Research Recorder独立run。当前未执行产品验收；local/Recorder PASS不是Task/Stage PASS。

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

保持backlog。后续明确授权且所有依赖独立接受/集成/main同步满足才ready→active，声明client_supplement_phase: ui_ref_product并登记实际新增验收命令；本次不执行产品。

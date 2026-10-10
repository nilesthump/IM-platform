---
task_id: LOOP1-CLIENT-STATE-001
title: 消息状态、幂等重发与好友同步
status: backlog
owner: unassigned
stage: S2
gate: S2
client_supplement_phase: planned
---

# Goal

以最新三端实现和已有验收为基线，逐项记录现有能力、证据和待补齐内容，将以下要求写入任务目标与强制验收。

1. 消息可靠性的两个核心场景：
   A. 首次发送未在服务端提交，发送方超时显示 FAILED，用户点击重发后完成首次持久化并收敛为 SENT。
   B. 首次发送已在服务端提交，接收方已获得消息，发送方因成功确认丢失或延迟显示 FAILED；用户重发后获得原始提交结果，原消息收敛为 SENT。

2. 同一逻辑消息的每次重发复用原始 request_id、conversation_id、发送者身份和消息内容。服务端已有提交时返回原始 messageId、seq、createdAt；最终对应一条持久化消息、一条逻辑 Outbox 和各客户端的一条消息展示。

3. 覆盖 SENDING、FAILED、重发按钮和 SENT 的真实界面状态。FAILED 表达当前尝试未获得成功确认；迟到 ACK、实时消息和适用 Sync 均通过既有收敛入口更新原消息，SENT 保持终态。核对 Gateway/Core 超时与提交结果未知路径，使其处理符合实际提交结果和现行契约。

4. 同一会话的已确认消息以服务端 seq 为最终排序依据，覆盖：
   - R1 首次未提交，R2 先成功提交，R1 后重发成功：最终顺序为 R2、R1。
   - R1 首次已提交但确认超时，R2 随后提交，R1 再获得确认：最终顺序为 R1、R2。
   验证 UI 在 ACK、实时事件、Sync 交叉到达后保持正确身份、状态和顺序。

5. Desktop/Mobile 覆盖保留本地消息时的重启重发，以及受控测试中从全新账号本地数据库和初始同步游标恢复的流程。验证已提交历史按 seq 恢复，后续新消息使用新的 request_id 和服务端分配的序号，序号连续性与渲染顺序正确。Web 按当前页面内存生命周期和已接受的在线消息同步规则验收。

6. 补齐三端好友变更同步。明确既有好友查询和 User Sync 的触发、消费及界面刷新链路；任一端添加好友后，其余在线端最终更新好友列表、对应私聊和名称展示，并验证断线恢复与账号切换后的正确结果。

7. 使用真实服务端、数据库和客户端的受控故障注入验证上述链路。场景 B 同时取得服务端持久提交、接收方获得消息、发送方 FAILED、重发后原消息 SENT 的证据；分别核对存储记录、请求身份、序号、Outbox 和实际渲染。


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

只修本任务已证明缺口，Core持有message事务，Gateway只transport/unknown-outcome；不修改契约、schema或新增source职责。

# Dependencies

- LOOP1-WEB-001；须独立接受、protected integration/actual-main验证及H:/IM-platform同步全部完成，status done才可激活本项，不只是本地commit。
- LOOP1-CLIENT-SUPPLEMENT-PLAN-001；本规划必须正式生效、独立接受/合入/main同步完成才可ready/active。

# Allowed Paths

- `clients/web/src/application/client.ts`
- `clients/web/src/application/repository.ts`
- `clients/web/src/ui/main.tsx`
- `clients/desktop/src/application/send.ts`
- `clients/desktop/src/application/sync/application.ts`
- `clients/desktop/src/application/ui/workspace.ts`
- `clients/desktop/src/application/ui/auth.ts`
- `clients/shared/protocol-sdk/src/storage/repository.ts`
- `clients/desktop/src/ui/main.tsx`
- `clients/mobile/app/src/main/kotlin/im/platform/client/send/SendViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/sync/SyncViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/Workspace.kt`
- `clients/mobile/app/src/main/kotlin/im/platform/client/storage/Repository.kt`
- `backend/go/core/message.go`
- `backend/go/gateway/gateway.go`
- `backend/go/core/message_test.go`
- `backend/go/gateway/message_test.go`
- `backend/go/tests/message_test.go`
- `tests/clients/send/**`
- `tests/clients/sync/**`
- `tests/clients/gui/hold_send.py`
- `tests/clients/gui/go_runtime.py`
- `tests/clients/gui/regressions.py`
- `tests/clients/web/behavior.mjs`
- `tests/clients/web/regressions.mjs`
- `tests/clients/web/browser.mjs`
- `tests/clients/state/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/send/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/GuiAuthenticatedInstrumentation.kt`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-STATE-001/**`
- `spec/progress/checkpoints/*loop1-client-state-001*.md`
- `spec/tasks/backlog/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/active/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/review/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/done/LOOP1-CLIENT-STATE-001.md`

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
- Web `python -Xutf8 -B tests/clients/web/verify.py`（locked install/build/behavior/appearance/source）；`node tests/clients/web/browser.mjs`实际原截图。Desktop现有locked build/`python -Xutf8 -B tests/clients/gui/native.py package` Windows安装包及真实截图/通知tray（仅后续产品任务激活后；需现有Windows x86_64 MSVC/Visual Studio vcvars64、Rust/Cargo/Tauri及locked npm依赖，遵循native.py的既有工具链路径；先完成package构建，再安装同候选制品并以其自身身份运行；缺工具链/安装/独占环境不计PASS）；`python -Xutf8 -B tests/clients/gui/regressions.py`只在输入与独占环境满足时运行。
- Backend现有`go test ./...`（cwd backend/go）和 `python -Xutf8 -B tools/verify_sync_runtime.py`适用真实Go/PostgreSQL/NATS/TLS入口；DB_TEST_ENABLE=1、实际受控DATABASE_URL/NATS_URL，缺环境skip不计PASS。受控数据/证书/进程创建与回滚须记录，不读取私人数据或凭据。
- 激活前为本任务新增场景明确实现并登记实际harness命令、fault hook/环境、fixture身份、独占资源及清理。现入口baseline不替代新增A/B/组件/语言证据；未执行命令不计PASS。
- Screenshot manifest绑定候选SHA/build/runtime/fixture/状态/尺寸/theme/font/density/语言与PNG hash，真实原图/Architect决策；独立Review/exact-head必需hosted jobs/protected integration/actual-main/safe sync全部完成才done。

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-STATE-001/`保存可复现场景/原始结果/failed记录/真实截图Architect/independent Review/hosted/main/sync；Research Recorder独立run。当前未执行产品验收；local/Recorder PASS不是Task/Stage PASS。

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

保持backlog。后续明确授权且所有依赖独立接受/集成/main同步满足才ready→active，声明client_supplement_phase: state_product并登记实际新增验收命令；本次不执行产品。

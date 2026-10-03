---
task_id: LOOP1-CLIENT-GUI-001
title: Desktop/Mobile complete Loop1 GUI
status: backlog
owner: unassigned
stage: S2
gate: S2
---

# Goal

实现遵守 CLIENT-UI-ARCH 的 Desktop/Mobile 完整 GUI：Login/session、Chat、Friends、AI Placeholder、Plugin capability/unavailable、Settings/Profile、Cold AI/Warm Creative、本地字体/间距、Offline History、SENDING/SENT/FAILED/retry、Sync/reconnect、Desktop notification/tray/shortcut、Android Studio emulator。UI 发出意图并观察已有编排，不重复 SQLite/SEND/Sync。

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md`，§2.3/§3/§6/§10 SRC-01 through SRC-07/§11/§19/§20。
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`、`spec/architecture/decisions/ADR-0006-client-ui-architecture.md`、`spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`、`contracts/websocket/`。
- `spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`、`spec/acceptance/client-gui.md`。

# Technology Authorization

已接受 canonical §6.1/§6.5 与 ADR-0005/0006 授权；本声明不选择新依赖，未明技术按 §2.3 停止受影响实现。Mobile Kotlin 等价契约行为，不强制 TS 复用；Desktop TypeScript application/Repository 与 existing Tauri SQLx boundary。
client_language: TypeScript
client_language: Kotlin
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

# Dependencies

- LOOP1-CLIENT-SQLITE-001 (必须独立接受并 done).
- LOOP1-CLIENT-UI-ARCH-001 (必须独立接受并 done).
- LOOP1-CLIENT-SEND-001 (必须独立接受并 done).
- LOOP1-SYNC-001 (必须独立接受并 done).

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/desktop/src/ui/**`
- `clients/desktop/src/application/ui/**`
- `clients/desktop/src-tauri/src/desktop_capabilities.rs`
- `clients/desktop/src-tauri/tauri.conf.json`
- `clients/mobile/app/src/main/kotlin/im/platform/client/ui/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/MainActivity.kt`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/**`
- `tests/clients/gui/**`
- `spec/tasks/backlog/LOOP1-CLIENT-GUI-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-GUI-001.md`
- `spec/tasks/active/LOOP1-CLIENT-GUI-001.md`
- `spec/tasks/review/LOOP1-CLIENT-GUI-001.md`
- `spec/tasks/done/LOOP1-CLIENT-GUI-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-GUI-001/**`
- `spec/progress/checkpoints/*loop1-client-gui-001*.md`

# Acceptance

spec/acceptance/client-gui.md 完整适用：真实客户端截图 → Architect Review → 修复 → 重新截图 → Architect Approval → fresh independent Review → exact-head hosted CI → protected integration/actual main 与受保护同步。覆盖双主题/字体间距、真实原生能力、Android emulator 和账号隔离；截图不能代替存储/协议检查。
适用 architecture/source/dependency guard 与实际职责/import/minimality Review 必需。Task allowed_paths 不授权新架构。

# Forbidden

不得 AI API/chat/Agent/RAG、Plugin runtime/Marketplace/S4 renderer、新公共 API、UI 直接 SQLite、重复 SEND/Sync；不得自行选新敏感依赖或把 mockup 作真实截图。

# Minimality

仅实现当前目标，用已有 Repository/规范协议/已冻结技术；不增加未来机制。激活前读实际源码，路径不足先显式收窄/补充 task scope，不借范围泛化。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json 与 `tools/verify_frozen_architecture.py`。
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development；候选 clean Acceptance；独立 exact-head applicable hosted jobs。
- 激活时将新增实现的精确行为验证命令、运行环境、启用条件和负例写入本节；尚未运行的测试不计 PASS。

# Evidence

spec/progress/evidence/LOOP1-CLIENT-GUI-001/；本次仅规划，未生成产品验收；prospective Research Recorder 激活时独立运行。

# Handoff

Backlog 规格实例化 canonical 已批准规划 ID；GUI 是唯一新增产品 ID。S1 PASS/S2 OPEN；未实现、未验收、未同步产品；known good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。当前规划文本 /root 所有；不覆盖主仓库未知工作。具体 code paths 在激活时按责任与实际源码确认。

# Next Action

等待依赖与规划独立接受；本轮仅 SEND 允许随后激活，SYNC/GUI/WEB 保持 backlog。

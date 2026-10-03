---
task_id: LOOP1-WEB-001
title: Web complete memory-only Loop1 GUI
status: backlog
owner: unassigned
stage: S2
gate: S2
---

# Goal

既有 Web Task 承载完整 Loop1 GUI：Login/session、Chat、Friends、AI Placeholder、Plugin capability/unavailable、Settings/Profile、双主题与本地字体/间距；React + TypeScript memory only，no SQLite/no offline history。遵守 CLIENT-UI-ARCH。

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md`，§2.3/§3/§6/§10 SRC-01 through SRC-07/§11/§19/§20。
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`、`spec/architecture/decisions/ADR-0006-client-ui-architecture.md`、`spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`、`contracts/websocket/`。
- `spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`、`spec/acceptance/client-gui.md`。

# Technology Authorization

已接受 canonical §6.1/§6.5 与 ADR-0005/0006 授权；本声明不选择新依赖，未明技术按 §2.3 停止受影响实现。Mobile Kotlin 等价契约行为，不强制 TS 复用；Desktop TypeScript application/Repository 与 existing Tauri SQLx boundary。
client_language: TypeScript
client_framework: React

# Dependencies

- LOOP1-CLIENT-GUI-001 (必须独立接受并 done).

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/web/src/**`
- `clients/web/package.json`
- `clients/web/package-lock.json`
- `clients/web/tsconfig.json`
- `tests/clients/web/**`
- `spec/tasks/backlog/LOOP1-WEB-001.md`
- `spec/tasks/ready/LOOP1-WEB-001.md`
- `spec/tasks/active/LOOP1-WEB-001.md`
- `spec/tasks/review/LOOP1-WEB-001.md`
- `spec/tasks/done/LOOP1-WEB-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-WEB-001/**`
- `spec/progress/checkpoints/*loop1-web-001*.md`

# Acceptance

spec/acceptance/client-gui.md 真实浏览器截图与 Architect 审查修复重拍批准；内存协议状态/发送重试、页面生命周期后不保证消息保留、无聊天持久化；refresh/logout/session-expired。独立 Review、exact-head hosted CI、protected integration/main sync。
适用 architecture/source/dependency guard 与实际职责/import/minimality Review 必需。Task allowed_paths 不授权新架构。

# Forbidden

不得聊天 DB/历史持久化/离线历史，AI/Plugin runtime/Marketplace/S4 renderer、新契约/API 或未授权 router/state/data 库；本地外观机制必须先有 §2.3 所需授权。

# Minimality

仅实现当前目标，用已有 Repository/规范协议/已冻结技术；不增加未来机制。激活前读实际源码，路径不足先显式收窄/补充 task scope，不借范围泛化。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json 与 `tools/verify_frozen_architecture.py`。
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development；候选 clean Acceptance；独立 exact-head applicable hosted jobs。
- 激活时将新增实现的精确行为验证命令、运行环境、启用条件和负例写入本节；尚未运行的测试不计 PASS。

# Evidence

spec/progress/evidence/LOOP1-WEB-001/；本次仅规划，未生成产品验收；prospective Research Recorder 激活时独立运行。

# Handoff

Backlog 规格实例化 canonical 已批准规划 ID；GUI 是唯一新增产品 ID。S1 PASS/S2 OPEN；未实现、未验收、未同步产品；known good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。当前规划文本 /root 所有；不覆盖主仓库未知工作。具体 code paths 在激活时按责任与实际源码确认。

# Next Action

等待依赖与规划独立接受；本轮仅 SEND 允许随后激活，SYNC/GUI/WEB 保持 backlog。

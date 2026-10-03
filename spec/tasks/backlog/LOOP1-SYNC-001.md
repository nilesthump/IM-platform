---
task_id: LOOP1-SYNC-001
title: Desktop/Mobile two-level sync orchestration
status: backlog
owner: unassigned
stage: S2
gate: S2
---

# Goal

基于既有 Repository 实现 user cursor 与 per-conversation contiguous_seq 同步、实时交叉、缺口补偿及断线重连；不改存储职责。

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

- LOOP1-CLIENT-SEND-001 (必须独立接受并 done).

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/desktop/src/application/sync/**`
- `clients/shared/protocol-sdk/src/sync/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/sync/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/sync/**`
- `tests/clients/sync/**`
- `tools/verify_client_sync.py`
- `.github/workflows/ci.yml`
- `spec/tasks/backlog/LOOP1-SYNC-001.md`
- `spec/tasks/ready/LOOP1-SYNC-001.md`
- `spec/tasks/active/LOOP1-SYNC-001.md`
- `spec/tasks/review/LOOP1-SYNC-001.md`
- `spec/tasks/done/LOOP1-SYNC-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-SYNC-001/**`
- `spec/progress/checkpoints/*loop1-sync-001*.md`

# Acceptance

乱序/重复/交叉实时流不越过 gap；事务回滚 data/cursor 一致；FAILED 被服务端消息收敛 SENT；按账号隔离，Desktop/Mobile 真实运行。独立 Review、exact-head CI、protected main sync。
适用 architecture/source/dependency guard 与实际职责/import/minimality Review 必需。Task allowed_paths 不授权新架构。

# Forbidden

不实现 GUI/Web/Plugin/AI；不改契约、安全、ACK 或 Repository schema。

# Minimality

仅实现当前目标，用已有 Repository/规范协议/已冻结技术；不增加未来机制。激活前读实际源码，路径不足先显式收窄/补充 task scope，不借范围泛化。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json 与 `tools/verify_frozen_architecture.py`。
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development；候选 clean Acceptance；独立 exact-head applicable hosted jobs。
- 激活时将新增实现的精确行为验证命令、运行环境、启用条件和负例写入本节；尚未运行的测试不计 PASS。

# Evidence

spec/progress/evidence/LOOP1-SYNC-001/；本次仅规划，未生成产品验收；prospective Research Recorder 激活时独立运行。

# Handoff

Backlog 规格实例化 canonical 已批准规划 ID；GUI 是唯一新增产品 ID。S1 PASS/S2 OPEN；未实现、未验收、未同步产品；known good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。当前规划文本 /root 所有；不覆盖主仓库未知工作。具体 code paths 在激活时按责任与实际源码确认。

# Next Action

Public Sync transport prerequisite now accepted/synchronized at c2ff0502fdad80f463abe038a960ca1b798e6d7a. Await separate Human consent for concrete Go proposal and accepted actual Go User/Conversation Sync runtime; then reassess inputs and activate this existing SYNC task. Human endpoint remains SYNC done then stop; GUI/Web not selected.

# Authorized SYNC recovery and authority blocker (2026-10-03)

Human exact authorization: “开始 SYNC，完成后停止”. This supersedes the prior SEND-only execution endpoint for this new run; it authorizes SYNC only, not GUI/Web. Current dependency LOOP1-CLIENT-SEND-001 exists uniquely in done and is independently accepted/synchronized. Accepted main/base: a0304fcc7be18b87f5986d014849d6b48b96a071 (PR17 SEND administrative closure). No missing Human scope authorization remains.

Execution status: BLOCKED_BY_ARCHITECTURE. Queue remains unique backlog/status backlog because runtime/authority inputs are incomplete; do not activate ready/active. Fresh Implementation Agent /root/sync_implementation independently verified assigned Codex Git root H:/.codex/worktrees/sync-resume/IM-platform and branch task/LOOP1-SYNC-001. No product implementation, contract, backend, Repository/schema, frozen authority or GUI/Web edit.

Direct inspection establishes existing canonical Sync user metadata is sufficient for current Repository; no invented rich user payload is needed. The blocker is absent accepted public Sync transport binding and actual User Sync server entrypoint. sync-v1.schema.json defines four standalone wire shapes, but envelope.schema.json oneOf contains only AuthBind/AuthAck/MessageSend/MessageAck/MessageCreated/SessionRevoked/Ping/Pong. Current OpenAPI has only Auth/User/Friend routes. Gateway has no sync.user/sync.conversation/history routing. Core only privately serves Conversation history at POST /__core/history and explicitly excludes User Sync. Offline oracle/profile vectors cannot establish running Sync service acceptance.

Smallest decision question: Approve a prerequisite public Sync transport binding (for the existing user and Conversation shapes, including authentication/correlation/error behavior) and a narrowly scoped Go Core/Gateway runtime task before client orchestration? The exact route/transport choice must come from Architect/Human through approved contract/architecture process; this record does not choose one. SYNC allowed_paths excludes backend/contracts; neither scope nor tests may silently authorize these changes. Once approved/frozen and independently reviewed/applicable exact-head hosted CI accepted, implement and accept actual service inputs, then reassess SYNC readiness.

Verification: own recorded python -B ci/check_architecture.py --scope all --json PASS; own recorded python -B tools/verify_frozen_architecture.py PASS. Canonical SHA25616e9c7b488e00dd39c7c2b5da7286c22be6ac67c163f0e89733bbe00297d0a3c matches. Recorded corrected JSON inventory confirms missing binding. Earlier inspection used wrong envelope filename and had one missing gateway filename; corrected direct inventory succeeds. Windows Recorder pipeline/base64 registration and canonical-output encoding failures are disclosed in implementation/authority-blocker.md; prospective_resume explicitly marks incomplete initial read-only trace.

Evidence: spec/progress/evidence/LOOP1-SYNC-001/implementation/authority-blocker.md and implementation-research/. Local PASS is baseline evidence only; no SYNC Task PASS, runtime acceptance, hosted candidate acceptance or synchronization claimed. Main H:/IM-platform untouched; unknown work preserved. Branch commit identity is supplied in implementation handoff; main sync PENDING for this recovery record. Independent Review of blocker recovery is next; do not mark done. Last known good a0304fcc7be18b87f5986d014849d6b48b96a071. Coordinator /root owns pre-existing evidence/research; implementer owns only this appended note/current recovery/implementation evidence/own Recorder. No other-agent stream edited.
# Human-authorized prerequisite (2026-10-03)

Human authorizes minimal public Sync architecture/contract prerequisite LOOP1-SYNC-TRANSPORT-001. This is current active task; SYNC remains backlog BLOCKED_BY_ARCHITECTURE awaiting accepted binding and actual accepted Go service inputs. Go product implementation requires prerequisite independent Review/CI acceptance and Human consent to concrete plan beforehand. GUI/Web not authorized. No change to SYNC product allowed_paths/acceptance.

# Accepted transport prerequisite and remaining runtime input

LOOP1-SYNC-TRANSPORT-001 is independently accepted and synchronized at c2ff0502fdad80f463abe038a960ca1b798e6d7a, evidence acceptance/acceptance.md under that task. Earlier BLOCKED_BY_ARCHITECTURE/public-binding statements are historical: binding gap resolved by ADR0008 and existing four-shape HTTP contract; current execution BLOCKED_BY_RUNTIME_INPUT, unique backlog retained. No accepted live User Sync endpoint exists. Go needs separate Human plan consent and narrow task approval/independent runtime Review-CI-main sync before client activation. Single-page min(limit,100); continuously commit/apply pages through terminal latest committed read without fixed total cutoff. SYNC acceptance and allowed product paths unchanged. Known good accepted freeze c2ff050; no client products implemented.

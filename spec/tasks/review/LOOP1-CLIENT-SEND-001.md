---
task_id: LOOP1-CLIENT-SEND-001
title: Desktop/Mobile optimistic send orchestration
status: review
owner: fresh Implementation Agent
stage: S2
gate: S2
---

# Goal

用户意图 → 生成不可变 request_id → existing Repository 事务 SENDING → application observable state → canonical WSS message.send → durable ACK → Repository UPSERT SENT。timeout/offline → FAILED；retry 复用 SAME request_id。ACK/realtime/Sync 通过已有 Repository 收敛；SENT 不倒退。不实施 GUI/Sync runner/Web。

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

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/desktop/src/application/**`
- `clients/shared/protocol-sdk/src/send/**`
- `clients/mobile/app/src/main/kotlin/im/platform/client/send/**`
- `clients/mobile/app/src/androidTest/kotlin/im/platform/client/send/**`
- `tests/clients/send/**`
- `tools/verify_client_send.py`
- `clients/desktop/tsconfig.json`
- `clients/shared/protocol-sdk/tsconfig.json`
- `clients/mobile/app/build.gradle.kts`
- `clients/mobile/app/src/main/AndroidManifest.xml`
- `clients/mobile/app/src/androidTest/AndroidManifest.xml`
- `ci/classify.py`
- `tests/ci/test_classify.py`
- `.github/workflows/ci.yml`
- `spec/tasks/backlog/LOOP1-CLIENT-SEND-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-SEND-001.md`
- `spec/tasks/active/LOOP1-CLIENT-SEND-001.md`
- `spec/tasks/review/LOOP1-CLIENT-SEND-001.md`
- `spec/tasks/done/LOOP1-CLIENT-SEND-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-SEND-001/**`
- `spec/progress/checkpoints/*loop1-client-send-001*.md`

# Acceptance

验证发送前真实 Repository 事务完成、可观察 SENDING、WSS canonical envelope、timeout/offline FAILED、同 ID retry、迟到 ACK/实时/Sync 与终态防回退、账号/会话隔离、事务失败不发送、错误协议不确认。Desktop TypeScript + 真实 SQLx，Mobile Kotlin ViewModel/StateFlow + SDK SQLite，在适用 Android Studio emulator 运行；服务器 durable ACK 不改。fresh independent Review、exact-head CI 含真实 SEND 行为而非仅旧 SQLite 测试、protected integration/main sync 后 done。
适用 architecture/source/dependency guard 与实际职责/import/minimality Review 必需。Task allowed_paths 不授权新架构。

# Forbidden

不得直接从 UI 写 SQLite、重复 Repository、更改服务器/契约/HTTP route、引入未批准网络/核心依赖、提前 GUI/Sync/Web。

# Minimality

仅实现当前目标，用已有 Repository/规范协议/已冻结技术；不增加未来机制。激活前读实际源码，路径不足先显式收窄/补充 task scope，不借范围泛化。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json 与 `tools/verify_frozen_architecture.py`。
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development；候选 clean Acceptance；独立 exact-head applicable hosted jobs。
- 激活时将新增实现的精确行为验证命令、运行环境、启用条件和负例写入本节；尚未运行的测试不计 PASS。

# Evidence

spec/progress/evidence/LOOP1-CLIENT-SEND-001/；本次仅规划，未生成产品验收；prospective Research Recorder 激活时独立运行。

# Handoff

Backlog 规格实例化 canonical 已批准规划 ID；GUI 是唯一新增产品 ID。S1 PASS/S2 OPEN；未实现、未验收、未同步产品；known good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。当前规划文本 /root 所有；不覆盖主仓库未知工作。具体 code paths 在激活时按责任与实际源码确认。

# Next Action

等待依赖与规划独立接受；本轮仅 SEND 允许随后激活，SYNC/GUI/WEB 保持 backlog。


## 激活前具体范围与验证

依赖SQLITE和UIARCH唯一done；架构规划已接受actualmain10b77b2并同步。Coordinator按此真实状态backlog→ready→active；owner fresh Implementation Agent。本次增加CI classifier/test仅为新SEND verifier/fixture删除与正负触发覆盖，Android androidTest Manifest仅为测试Instrumentation声明，均不是新产品能力/技术选择。现有Repository/native/schema/contracts/backend不修改。
实现必须先读actual sources/contracts；共享仅协议编解码，不共享GUI。Desktop用现有Tauri accountDatabase/Repository；Mobile为Kotlin ViewModel/StateFlow + SDK SQLite，网络实现不得选未批准第三方库。Test fixtures可提供受控TLS服务器，但真实WSS/SQLx、Android Emulator以及已接受Go真实入口durableACK验证证据必须明确区分；不得把mock/接口stub称为完整真实运行。
精确验证命令在完成verifier时落实：python -B tools/verify_client_send.py --scope shared；--scope desktop；--scope mobile --serial emulator-<actual>。原SQLite行为验证必须保留。CI的Desktop/Mobile/shared必须实际执行SEND行为；CI修改按现有classify全矩阵。增加--scope构成verification内部入口，不是公共契约。
覆盖事务提交前不传输；可观察SENDING；offline/timeout/拒绝FAILED；same immutable ID retry/restart；lateACK/realtime/Sync收敛；SENT终态；账号隔离/会话撤销/旧连接事件；持久化失败不发布SENT；严格wire/malformed/错误会话；seq>2^53精确；完整git BASE10b77b2..HEAD diffcheck。真实Android runtime不可跳过。Scope解释仅限当前需求，不授权GUI/SYNCrunner/Web/newHTTP。
已接受UIARCH最终交接metadata（done/review队列移动与mvp-planning/closure/final证据）由Coordinator在SEND激活前生成，candidate审查分别按UIARCH与SEND的authoritative allowed_paths核验。SEND实现者不得修改它们。
Last accepted main10b77b22386234c98409ca41b3622ad6d25f3884；assigned root H:/.codex/worktrees/client-mvp-planning/IM-platform；main781未知工作原字节保护不动。

# Implementation Review Handoff (2026-10-03)

Status: review. Sole fresh implementer owns this candidate; it is not accepted or done. Assigned root H:/.codex/worktrees/client-mvp-planning/IM-platform; branch task/LOOP1-CLIENT-SEND-001; base8b33571990241f91a676e15069b07b065697317a. Accepted actual main10b77b22386234c98409ca41b3622ad6d25f3884 remains last known good. Main synchronization PENDING. No push/PR/integration/main writes.

Desktop application/account factory and Android ViewModel/StateFlow/account factory implement persistent send, same-ID retry/restart, strict canonical WSS, durable ACK/materialization and original-ID message.created convergence through existing Repo. No existing Repo/native/schema/backend/contracts or frozen decisions changed. No GUI/Web/Sync fetch runner. Standard TLS/WSS Android code uses platform trust and hostname verification; only approved lifecycle/coroutines packages added. The SEND runner uses an explicit Gradle property, retaining original storage runner.

Actual local commands: `tools/verify_client_send.py` --scope desktop PASS; --scope mobile --serial emulator-5590 PASS40 assertions API34, including waiting beyond active timer after Repository close with observable storage error and no crash. Shared behavior executed within Desktop PASS (strict mutations and canonical golden outputs). `tools/verify_client_sqlite.py` --scope desktop PASS13cases/141assertions and --scope mobile --serial emulator-5590 PASS13cases/137assertions install/data-clear. Real-Go smoke tests/clients/send/go_smoke.py PASS current Desktop application+SQLx -> verified Go WSS -> exact PostgreSQL Message/Outbox rows. Controlled TLS fixtures are separately identified and do not prove PostgreSQL durability. Sourceall/architecture53 and CI33 tests passed; four pre-existing Windows symlink-privilege skips are explicitly unexecuted, hosted Linux required.

Evidence: spec/progress/evidence/LOOP1-CLIENT-SEND-001/implementation/verification.md, commands.json, outputs/*.gz, android-artifacts.json. Research root H:/IM-platform/.git/worktrees/IM-platform4/send-implementation-research run R-CLIENT-SEND-IMPLEMENTATION-20261003; prospective_resume explicitly marks incomplete earlier read-only startup. Final immutable finish/validate follows clean commit. Historical failures preserved, including actual Manifest registration, Gradle/cwd/cache, fixture races and async timer issue. Reviewer must inspect final async liveness test and latest PASS separately from earlier FAIL logs.

Next exact action: Coordinator delegates fresh independent Review of actual clean committed candidate and full10b77b2..HEAD scope (root-owned activation/UIARCH metadata separately identified). On FAIL fresh Fix then new Review. On PASS actual exact-head hosted required CI/SEND/Go E2E, protected integration/actual-main independent verification and protected synchronization back to H:/IM-platform; only then done. Stop at accepted SEND endpoint; SYNC/GUI/WEB remain backlog. Main unknown781bytes/old private3metadata backups untouched. Final candidate SHA supplied by implementation handoff and immutable Recorder final_state; no self-review acceptance.

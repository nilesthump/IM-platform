---
task_id: LOOP1-CLIENT-GUI-001
title: Desktop/Mobile complete Loop1 GUI
status: active
owner: /root/gui_product_implementation
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

- LOOP1-CLIENT-NATIVE-ARCH-001 (Human-approved native/appearance freeze; independent acceptance/integration/main synchronization pending).

- LOOP1-CLIENT-SQLITE-001 (必须独立接受并 done).
- LOOP1-CLIENT-UI-ARCH-001 (必须独立接受并 done).
- LOOP1-CLIENT-SEND-001 (必须独立接受并 done).
- LOOP1-SYNC-001 (必须独立接受并 done).

- ADR-0007 本轮规划须独立 Review/精确 HEAD CI/集成 main 同步接受才可激活。依赖未满足保持 backlog；GUI/Web 在本轮 Human endpoint 之后，无本轮激活授权。

# Allowed Paths

- `clients/desktop/package.json` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/desktop/package-lock.json` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/desktop/tsconfig.json` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/desktop/src-tauri/Cargo.toml` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/desktop/src-tauri/Cargo.lock` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/desktop/src-tauri/src/lib.rs` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `clients/mobile/app/build.gradle.kts` (Human-authorized GUI assembly only; no new sensitive technology authority.)
- `.github/workflows/ci.yml` (Human-authorized GUI assembly only; no new sensitive technology authority.)

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

Current state active; sole writer /root/gui_product_implementation, exact assigned root H:/.codex/worktrees/s/IM-platform, branch task/LOOP1-CLIENT-GUI-001. Product source baedd9975d28e2ae9f9931dfd48a66dc5036dd9f remains a local unaccepted candidate. Android actual API34 local matrix PASS26/11 original images; Windows current package expected official NSS-marker bytes verified, native visual access interrupted by Coordinator with unknown capture outcome. Original failures preserved. Owned Go fixture stopped, no trust installed; both prospective runs are sealed/validated before writer release. Actual final recovery SHA is recorded in sealed final_state.json and handoff; main unknown work untouched.

# Next Action

Obtain supported Windows app access and actual pending Human fixture-trust decision, then new prospective run for unfinished Windows native/local visuals and approved authenticated fixture proof. Architect approval and fresh unified native+GUI Review/exact-head hosted CI/push/protected integration/actual-main synchronization remain required. No task review/done or S2 PASS before full applicable proof/acceptance/synchronization. Historical readiness and authorization chronology below remains provenance.

# Authorized GUI readiness recovery (2026-10-04)

Human exact visible prompt: 启动下一个task. This supersedes the earlier SYNC-only endpoint for GUI only. SYNC administrative closure is independently accepted at actual main ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597; old SYNC done/current endpoint text is historical. SQLITE/UI-ARCH/SEND/SYNC dependencies are accepted/done; Web and later tasks are not authorized. Human subsequent exact approval: 授权补充这 8 个文件，继续 GUI. Eight assembly paths above are scope authorization only.

Execution: BLOCKED_BY_ARCHITECTURE; unique backlog/status backlog retained because complete GUI runtime inputs still lack accepted native/appearance selections. No product code, dependency, contract, backend, frozen authority, schema, Send or Sync edits. Startup baseline is local evidence, not Task/Gate acceptance.

Assigned managed root H:/.codex/worktrees/s/IM-platform exactly verified by git rev-parse; branch task/LOOP1-CLIENT-GUI-001 clean at accepted main ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597. Do not copy unknown main changes or create a substitute workspace. Own Recorder R-GUI-IMPLEMENTATION-20261004 uses prospective_resume/fresh_context=true; initial read-only startup and a few direct inspections are explicitly incomplete command capture. Exact visible prompt P-GUI-START-20261004; parent R-GUI-COORDINATOR-20261004.

Existing Desktop is a storage host: no React dependencies/JSX compile, windows empty, lib only registers database commands, no registered desktop_capabilities module. Existing Mobile MainActivity renders a storage validation label; Navigation/Lifecycle runtime bindings absent. Approved eight-file scope solves assembly reachability, not sensitive native/prefs choices. SyncHttp supports injected fetch so existing orchestration can be reused through UI composition; accepted Send/Sync modules need no rewrite.

Smallest decision question: freeze the native HTTPS/OS-secure-refresh/notification/shortcut and appearance-storage adapters for this GUI task, with Windows Desktop validation and Android standard SDK mechanisms, before runtime implementation? Proposed choices and alternatives are in readiness/authority-gap.md; they are not decisions or approved imports. Native generic adapters must retain TypeScript auth/domain/protocol/Repository authority. No backend CORS change or new public API is proposed.

Baseline recorded commands: bundled Python3 -B ci/check_architecture.py --scope all --json PASS, zero violations; -B tools/verify_frozen_architecture.py PASS. Canonical SHA256 ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03 and PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 verified. No GUI runtime/screenshots/Architect Approval/independent GUI Review/hosted candidate acceptance claimed.

Next exact action: Architect/Human concrete decision -> accepted frozen authority/approved ADR and machine policy guards -> fresh independent Review/applicable exact-head CI/protected integration/actual-main sync -> reassess GUI readiness, then sequential backlog -> ready -> active and actual runnable GUI. Current recovery documentation itself requires fresh independent Review/CI/integration; do not mark GUI done. Last accepted ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597; main synchronization of this local recovery record PENDING. Sole writer owns only GUI task/current/readiness/checkpoint and private Recorder; no unknown main work touched.

## Approved prerequisite plan; freeze acceptance pending

Human exact response: 批准该最小前置方案并继续. The named concrete minimal native/appearance prerequisite plan is approved: Windows Desktop reqwest strict HTTPS, keyring Windows Credential Manager, official Tauri notification/global-shortcut plugins and existing Tauri tray; Desktop app_data JSON appearance values; Android SharedPreferences appearance, Keystore AES/GCM protected refresh credential ciphertext. Earlier proposed/unapproved/no-consent wording describes inspection before this answer. Current status APPROVED_PENDING_FREEZE; GUI remains BLOCKED_BY_ARCHITECTURE/backlog until authority is frozen and independently accepted. No missing Human plan/scope consent remains; do not ask again.

Next exact action is fresh prerequisite writer for LOOP1-CLIENT-NATIVE-ARCH-001/ADR-0009 with precise native responsibilities/policy markers, fresh independent Review/applicable exact-head CI/protected integration/actual-main/main sync. GUI sole writer releases after this clean recovery commit. Product implementation still waits for accepted prerequisite; no GUI agent writes frozen authority outside its allowed scope. Genuine Windows notification proof requires installed owned package, not development PowerShell identity/toast. Scope additions do not authorize backend CORS, public contract or native business migration. Main unchanged; recovery synchronization pending.

## Recovery verification outcomes

Development recovery verifier initially failed because Windows legacy PowerShell lacks Get-FileHash. Corrected to bundled PowerShell7; then failed four current.md required formatting controls (exact backtick Command/Evidence/SHA/checkpoint). Formatting repaired; rerun tools/verify-loop1-ctrl-002.ps1 -Mode Development exits0 PASS task GUI/backlog, queues5/task_specs30. Original failures remain in sealed command stream. Baseline architecture/frozen exit0 PASS. Development is local evidence only, not independent acceptance. All commands recorded; command summaries contain exact duration/output hashes. No Recorder failures.

## Native prerequisite dependency (2026-10-04)

ADR-0009/LOOP1-CLIENT-NATIVE-ARCH-001 freezes already approved concrete minimal native/appearance plan. GUI remains backlog/BLOCKED_BY_ARCHITECTURE until prerequisite done/effective/synchronized, then reassess runtime readiness. Exact eight assembly-path consent preserved; dependency grants no extra product scope. No missing Human approval remains for same plan.

## Latest Human unified local candidate authorization (2026-10-04)

Exact latest instruction: 完成GUI任务后统一审查推送. Source: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/unified-batch.md; localized ADR-0009 timing exception. Human explicitly supersedes separate-native-acceptance-before-GUI candidate preparation for this exact batch. Other SQLITE/UI-ARCH/SEND/SYNC dependencies already accepted/done; required inputs and local frozen native choices exist. No missing same-plan approval. Native Task remains review pending whole-batch review/publication; no native Task done/effectiveness/Stage PASS asserted.

GUI is now locally authorized candidate preparation, sequential backlog -> ready -> active. Previous BLOCKED_BY_ARCHITECTURE/backlog/standalone-acceptance statements above are historical before latest directive. Eight assembly paths/approved libraries/storage plan remain exact and unchanged; no new technology/contracts/backend/CORS/schema/ACK/security/business migration. Actual GUI readiness/verification/screenshot setup must be assessed by fresh implementation writer. Runtime screenshots -> Architect Review/fix/Approval remain mandatory, followed by fresh independent full-candidate Review/unified push/applicable exact-head hosted CI/protected integration/actual-main/safe sync. Native/GUI acceptance/done/main sync wait for their complete applicable evidence.

Next exact action: fresh GUI implementation writer resumes combined candidate from clean timing handoff. No independent Review PASS/hosted acceptance/push has yet occurred.

## Product implementation recovery 2026-10-04

Sole writer /root/gui_product_implementation; assigned worktree H:/.codex/worktrees/s/IM-platform, branch task/LOOP1-CLIENT-GUI-001; last committed HEAD 0d220e9ce41a80c7e2a2b3cf58ffb1412b1ce993. Task-owned GUI changes remain local/uncommitted. Both approved product clients compile, actual API34 GuiInstrumentation PASS with 14 assertions; Desktop auth/workspace delayed login/search/add isolation PASS. Real preliminary screenshot remains pre-fix/uncommitted QA. Existing tests/regressions, installed native capabilities, full SHA-bound runtime screenshots/Architect approval, unified independent review/exact-head hosted CI and main synchronization remain pending. Exact trust proposal is pending Human approval; no certificate installed. Current details and next action are in spec/progress/current.md; original failures preserved in Research Recorder R-GUI-PRODUCT-20261004. No Task done, native acceptance or S2 PASS claimed.

Local continuation: stable GUI candidate 7e6794e878a80b94e290ab6d87d566d23f5bd64d committed cleanly; actual API34 layout/scroll instrumentation follow-up is owned by /root/gui_product_implementation. Local proof and pending trust approval do not satisfy Architect review, unified independent review, hosted acceptance or synchronization.

Actual Android local continuation: 26 API34 assertions PASS for both themes at minimum/default/maximum independent appearance values; preserved 7ed032e source-bound local captures and new matrix instrumentation. Full authenticated screenshots, Windows installed capability proof, Architect approval and unified review/CI/integration remain pending.

Recovery endpoint: current clean-source local Android matrix PASS26 is saved under runtime/7f84da199ef5a2ee14dcf70a4a00e4cd811cb8d0. Exact unused owned Go fixture was stopped with verified cleanup; no OS trust installed. Await actual bounded trust decision and Coordinator Windows UI release, then resume prospective authenticated/runtime proof. Task remains active, all review/CI/integration/synchronization mechanisms pending.

Windows continuation recovery: current-source baedd997 NSIS build/owned installation exit0; exact expected NSS bundle-patched installed bytes verified, original raw-hash assertion failure preserved. Supported inventory succeeded, next native capture call Coordinator-cancelled with exact tool text aborted by user after 286.7s; outcome unknown, session reset, no UI retry. Windows native visual proof and distinct Human fixture-trust approval remain pending. GUI stays active; no acceptance/push/main sync. See windows-continuation.md/package JSON and current recovery.

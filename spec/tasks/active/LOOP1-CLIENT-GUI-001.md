---
task_id: LOOP1-CLIENT-GUI-001
title: Desktop/Mobile complete Loop1 GUI
status: active
owner: /root/gui_ui_update
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

- `clients/desktop/src-tauri/icons/**` (Human exact supplied logo, app icon only.)
- `clients/mobile/app/src/main/res/**` (Same logo for app icon/brand only.)
- `clients/mobile/app/src/main/AndroidManifest.xml` (App icon/label wiring only.)

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

## Latest Human-approved handoff

2026-10-04 exact existing trust proposal approved; release to another agent requested. No trust installed, no push/sync; GUI active. Earlier pending-trust status historical. Next exact action/risks/private paths: spec/progress/evidence/LOOP1-CLIENT-GUI-001/agent-release.md.


## Approved takeover recovery 2026-10-04
Sole writer /root/gui_resume_implementation, assigned managed gui-resume root, branch task/LOOP1-CLIENT-GUI-001. Anonymous desktop login guard fixed9032ad6; Windows native build/install and partial actual local GUI proof PASS. Both temporary trust environments fully rolled back with exact baselines/default TLS rejection. Android read-only overlay unavailable; Windows system certificate confirmation inaccessible, so authenticated matrix and native capability proof remain BLOCKED_EXTERNAL_ACCESS. Original failures/proofs preserved. Current Task remains active; no Architect acceptance/full independent Review/exact-head CI/push/main synchronization. Source/frozen/53 architecture/Development recovery PASS after owned ignored-output isolation/restoration. Next exact action, risks, commit provenance and Recorder limitations: spec/progress/evidence/LOOP1-CLIENT-GUI-001/resume-20261004/handoff.md; spec/progress/current.md. All pending files task-owned; release after final recovery commit. Main last-known-good ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597 unchanged.

## Second continuation recovery 2026-10-04
Fresh sole writer /root/gui_second_resume; root exactly verified managed gui-resume, branch task/LOOP1-CLIENT-GUI-001, recovered a801553. Product unchanged9032ad6, actual shortcut restoration PASS with original saved source-bound screenshot. Notification action exercised; OS toast/tray visual and full authenticated matrix unfinished. Exact Windows CA remained absent after CLI false-success and two normal-wizard access attempts; transient visible handle disappeared before action, no Human cancellation claimed. Final both trust baselines/root/non-root/Enforcing cleanup PASS. No fixture started. Source/frozen/53architecture tests PASS; Development result and Recorder validation at new handoff. Concrete unexecuted optional Android helper requires new explicit method approval; same Windows trust plan already approved. New handoff/decision: spec/progress/evidence/LOOP1-CLIENT-GUI-001/second-resume-20261004/. GUI active/BLOCKED_EXTERNAL_ACCESS; no Architect/full independent Review/CI/push/main sync/done/S2 PASS. Last accepted mainffd6b63 unchanged. All new changes task-owned; writer releases on clean committed recovery.


## Approved mount and final local recovery 2026-10-04

Human approved temporary helper (批准执行临时挂载工具), following bounded independent review5bf9c3e, and requested autonomous Windows import (你自行导入). Exact original CA/source/binary/paths unchanged. Approved Android readonly/topmost mount/default TLS inheritance PASS; complete rollback fresh134-cert baselines/no owned mounts/paths/reverse/Enforcing/uid2000/defaultSDK TLS rejection PASS. Owned Go runtime27180 normal stop/cleanup; labelled containers/volumes absent. Windows original74 Root set unchanged, exact CA absent API/physical store, owned import process absent.

Observed actual send/network-on-Main and logout async-parent crash repaired only allowed UI in14e0cc3/e39e190. Actual new APKca74da4b9e1462215b073c5d0d6ae85a87aefc2156f45f1e22f2aff960a19428: source-bound send/Go persistence, sameUUID FAILED→Retry→SENT, real PG-delay SENDING→sameUUID SENT, restart/refresh, isolation/logout, server-unavailable logout, server-expired secure cleanup and appearance combinations have local proof. Whole failed phases and screenshot gaps retained separately. Required final guards/Recorder results in handoff; coding/instrumentation/UTF-8 recovery failures remain durable, no self-acceptance.

Windows authenticated/native toast/tray proof remains BLOCKED_EXTERNAL_ACCESS after normal authorized API/UI attempts; cause unknown, no unsafe bypass/manual import pending. Task active, native review pending, S2 OPEN; no Architect/full independent Review/hosted CI/push/main sync/done. Accepted mainffd6b63 unchanged. Exact next action/source/APK/run/capture provenance: spec/progress/evidence/LOOP1-CLIENT-GUI-001/mount-approved-20261004/handoff.md and manifest.json. Sole writer releases after clean recovery commit; SHA external.


## Human UI revision 2026-10-04

Resume authorized from archive fac0c8fc205d44a2889f56ae12f1e67c83edb3da in assigned managed H:/.codex/worktrees/gui-ui-update/IM-platform. Sole writer /root/gui_ui_update. Snapshot preserves six unknown-origin screenshot renames byte-for-byte; do not reverse or alter them. Main remains unsynchronized.

Current acceptance additions: anonymous clients show only authentication; username/password/confirmation registration via existing canonical register with displayName=username; no server input (client-owned configured origin); unified latest-first private/group local conversation list; Desktop Nav/list/detail, initially blank detail and selected-row toggles close; Mobile list/detail with back and no navigation while in detail; original project logo required; Windows fixed-size auth adapts 14..22px without page scroll; frameless top-right native controls. No new protocol, storage, ACK, Sync or native technology. Original logo is absent from snapshot (icon is solid placeholder); original asset location requested, do not invent replacement. App icon asset/manifest paths require that exact asset and explicit scope before writes. Real Windows authenticated Chat/Friends plus changed Android UI captures remain required, Architect approval and independent full review/exact-head CI/main sync pending.


## UI update local evidence 2026-10-07

Exact supplied Human logo received and used byte-exact as source with deterministic platform icon resizes; prior absent-logo text above is historical. New bounded same-scope24h localhost/127.0.0.1 test certificate explicitly approved by Human. Assigned managed root H:/.codex/worktrees/gui-ui-update/IM-platform verified; sole writer /root/gui_ui_update; branch task/LOOP1-CLIENT-GUI-001-ui-update.

UI requested changes implemented; Desktop build/auth/registration/private+group recency/race tests PASS, Windows package/install PASS; actualAPI34 anonymous theme/font matrix PASS46 and authenticated revised UI PASS66 with13 raw screenshots. Original failed phases retained; hardware-back from focused composer remains unverified (top-left requested back is verified). Android temporary trust fully rolled back and default TLS rejection/134CA set/nonroot/Enforcing verified. Current Windows OS confirmation pending; authenticated Chat/Friends/native full proof remains unfinished. Evidence: spec/progress/evidence/LOOP1-CLIENT-GUI-001/ui-update-20261007/.

No Architect approval/unified independent Review/exact-head hosted CI/protected integration/main synchronization/taskdone/S2PASS asserted. Next exact action: supported Human completion of Windows security confirmation -> actual revised Windows captures -> rollback -> Architect screenshot approval -> fresh unified independent Review and applicable exact-head CI/protected integration/safe verified main synchronization. No unknown main changes touched; six recovery screenshot moves byte-exact preserved.

Final Windows status: security confirmation not observed, task-owned exact import process3428 stopped after command/path/fingerprint verification; original74Root set equal, exact owned CA absent API/physicalstore, no import process. Windows anonymous login and three-field registration screenshots captured via supported native tool; custom maximize then restore exercised. Windows authenticated Chat/Friends, full native matrix and14..22 actual Windows layout remain unverified. Node filesystem save EPERM preserved; exact native image/jpeg bytes saved through authorized shell without image transformation. Owned Go fixture85266 normal stop PASS label-bounded cleanup; no unrelated operation. Both temporary trust environments fully rolled back.


## Human window/row revision 2026-10-07

Human approved prior continuation and additionally requested Minimize/Maximize hover tips, true-maximized overlapping restore icon vs bold outlined square when restored, and contiguous full-width rectangle conversation rows on Mobile and Desktop. Implemented only existing allowed UI/native generic glue paths; no new dependency/technology/policy/business/schema/contract. One read-only native own-window maximized query is required to follow actual OS state instead of guessing click state.

Local Desktop build/auth/list lifecycle controls and Windows release/NSIS/exact installed package verification PASS; Android build and actualAPI34 ui-revision PASS66 run1791352772357, thirteen original screenshots with two actual friends and full-width zero-gap cold14/warm22 rows visually verified. Windows Human replied 已确认; exact approved CA installed and default .NET TLS/negative hostname controls passed. Native UI kernel failed before usable inventory after retry/reset/final attempt: windows sandbox failed: helper_unknown_error: setup refresh had errors. No current Windows native UI or authenticated Chat/Friends screenshot claimed. Both trust environments fully rolled back with original sets and same-live-fixture rejection; runtime cleanup follows evidence.

Task active/S2OPEN, no Architect full screenshot approval, unified independent Review, exact-head hosted CI, protected integration or actual main synchronization. Current last committed UI recovery02337033ae34ebe5abdb1ad2073c7151206d140c; this revision commit recorded in final-state evidence after commit. Current branch task/LOOP1-CLIENT-GUI-001-ui-update, sole writer/root as before; six unknown-origin screenshot moves preserved. Exact evidence/next action: spec/progress/evidence/LOOP1-CLIENT-GUI-001/window-rows-20261007/ and current.md.

## Native helper diagnostic recovery

Product candidate `f9bd53fe7352df33c6d44864b9ce90f95beb5866`; no product change during diagnosis. Actual logs identify Windows sharing violation32 on node_repl.exe then native VCRUNTIME140_1.dll. Exact old tool workers/helper restarted, helper automatically respawned by Codex; normal sandbox still fails and node tool transport is now closed. Minimal restart attempt not successful; next exact action is complete Human Codex exit/reopen, ordinary sandbox and supported sky list_windows regression, then resume approved real Windows capture workflow. Durable diagnosis/log excerpt under window-rows-20261007/diagnosis.md. Both temporary trusts and owned test runtime already fully rolled back; six original screenshots/main untouched. Taskactive/S2OPEN; no independent acceptance/main sync.

Recorder final validation disclosure: finished run44events validates individually, but repository validation FAIL on diagnostic prompt/run cross-link mismatch (both extra prompts associated with original run whose metadata points to original prompt). No Recorder evidence edited to force PASS. Repair only through supported Recorder workflow in next run; research validation is separate from product acceptance.

## Complete app restart regression

2026-10-07 actual new Codex/process creation verified14:20-14:21; ordinary shell still fails sharing violation32 on node_repl.exe, supported native list_windows fails trusted Node exited. Full restart is insufficient. No new product/trust/config changes; next action requires supported host runtime lifecycle repair, then native tool regression and actual Windows captures. Detailed evidence window-rows-20261007/restart-check.md. Worktree retained, main unchanged, taskactive/S2OPEN.

## Human-authorized outside-sandbox Windows verification

Human allows this Windows desktop UI outside sandbox. Existing installed app launched and official sky inventory identifies real window; screenshot/action APIs FAIL application approval elicitation unavailable in standalone host. No captured Windows proof, login, renewed trust or product change. Current blocker is supported host UI initialization/approval channel, not missing Human authorization. Details window-rows-20261007/outside-sandbox.md; taskactive/S2OPEN, worktree retained/main untouched.

## Human manual inspection runtime

Latest request only login/self-inspection. Fresh owned local project im-gui-product-20261004-39112 intentionally live, session58647; private go-39112, endpointlocalhost8443. GUI form unavailable to automation; actual login not verified. Windows temporary trust attempts report success but fresh74roots/noCA and PartialChain show trust absent. Await Human manual import/form; stop exact owned fixture after inspection and roll back exact manually installedCA with74root baseline. Detailed manual-inspection.md under current window-rows evidence. No product edits/main sync; taskactive/S2OPEN.

## Owned local service restart

Human Connection unavailable request: same project im-gui-product-20261004-39112 restarted; repaired dependency-start race by starting exact core/gateway after DB healthy. TLS health200 with exact fixtureCA, data/account retained. Windows default TLS still fails missing issuer/root; no GUI login proof. Service remains live for requested manual inspection, cleanup session58647 afterward. Evidence window-rows-20261007/service-restart.md. No product/main change; taskactive/S2OPEN.

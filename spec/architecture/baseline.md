# Frozen Architecture Baseline Manifest

- baseline_title: 面向十万级在线连接的可扩展分布式即时通信平台
- version: `v1.1`
- status: MVP planning accepted at actual main b60f116; administrative closure candidate review pending
- canonical_format: `markdown`
- repository_path: `spec/architecture/frozen-architecture.md`
- sha256: `a6b1670aae1707fd325a00f75e19f243c9bf8f5cb24cd5089c5f160314e67b72`
- previous_canonical_format: `pdf`
- previous_repository_path: `scalable-distributed-im-architecture.pdf`
- previous_sha256: `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`
- historical_migration_type: `representation_only`
- historical_semantic_change: `false`
- historical_migration_task_id: `LOOP1-ARCHDOC-001`
- historical_markdown_sha256: `ff498f37ade3328fac97a905d6cb8dd7148fed935af5173e69b6b48a14277e91`
- revision_type: `human_approved_client_clarification`
- semantic_change: `true`
- revision_task_id: `LOOP1-CLIENT-ARCH-CLARIFICATION-001`
- revision_adr: `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`
- approval_source: `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md`
- baseline_date: 2026-10-01

## Historical ADR-0003 acceptance discovery

At that prior revision, the Markdown was the single canonical source under the explicitly approved revision. Stage-one bounded acceptance: fresh Review of a09f4fbb1dc497c46c8dc0b8901b0417c534fb2d and hosted run 36714913796 on exact head 3e6e89fa2b378f1fcb4c944466fef2e3bc905379, all ten jobs successful; evidence spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/hosted-acceptance.md. This does not accept pending stages two through four, source compliance or remediation/S1 Gate. This revision tightens executable source ownership and governance semantics; it is NOT the historical representation-only migration. ADR-0002 and its original v1.0 migration facts are immutable history. The PDF remains the byte-for-byte immutable historical snapshot and is not a second current authority. No public wire, database, ACK/Sync, compatibility or security boundary is changed.

## Current completion discovery (2026-10-01)

The preceding stage-one paragraph is its bounded historical acceptance point. Subsequent task/product acceptance is now recorded in evidence004/final-hosted-acceptance.md (d0ae52f / hosted36744072690). Administrative finalization requires a new independent Review and exact-head hosted run. Version, hashes, approval and historical source metadata remain unchanged; S1 product Gate OPEN.

## Current Human-approved clarification (2026-10-01)

- previous_revision_sha256: `83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e`
- previous_revision_type: `conflict_resolution`
- previous_revision_task_id: `LOOP1-ARCH-REMEDIATION-001`
- previous_revision_adr: `spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md`
- previous_revision_approval_source: `spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/approval-and-recovery.md`

All preceding acceptance paragraphs are historical bounded discovery, not acceptance of these changed bytes. Version remains v1.1; canonical bytes/hash changed under ADR-0005. Original PDF, representation-only migration and ADR-0003 facts remain historical unchanged. S1 now PASS through accepted E2E/pre-PR7 tree restored by PR8; S2 OPEN. This clarification candidate requires NEW independent Review and exact-head hosted CI before effectiveness/product implementation. No public contract or product source change.

Supplemental Human Desktop decision freezes Tauri + SQLx(SQLite) atomic native transaction adapter; separate tauri-plugin-sql execute calls cannot emulate transaction. Mobile is Android Kotlin + Jetpack Compose, validated on Android Studio emulator; Mobile TS/TBD is superseded before candidate acceptance. Approval supplement: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-desktop-sqlx-mobile-emulator-decision.txt.

- superseded_preacceptance_candidate_sha256: `ac0421074c41589d1d409cc91729953984839aea3c05e805608fcf7677da4f68`
- mobile_approval_source: `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-mobile-kotlin-compose-decision.txt`

Candidate188d24a5a53abaa136aa939fded5968dd5fe728f was never accepted. New Human Mobile decision supersedes its TS/TBD clause before Review/CI. Previous accepted revision remains83d124b, not the superseded candidate hash. Android Kotlin/Compose same-contract behavior leaves Web/Desktop/shared TypeScript and Desktop SQLx boundaries unchanged.

## Accepted clarification discovery (2026-10-01)

Fresh independent Review accepts clean e7c80c726d4799ba3ddab026266be638c9e6b252 under scoped Human GString waiver; original4b5 Review FAIL immutable. Exactpush36881391141 selected5SUCCESS/8correctinactive and PR36881397009 all13/every stepSUCCESS. Canonicalaa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c/PDF546915 unchanged. ADR0005 effective at accepted prerequisite. Evidence: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/2026-10-01-coordinator-resume/acceptance.md. Earlier pending paragraphs are historical; later administrative closure needs NEW independent Review/exactHEADCI before S2activation. No product/contract change; S1PASS/S2OPEN.

## 当前 UI 修订候选（2026-10-03）

- ui_revision_type: `human_approved_client_ui_architecture`
- ui_semantic_change: `true`
- ui_revision_task_id: `LOOP1-CLIENT-UI-ARCH-001`
- ui_revision_adr: `spec/architecture/decisions/ADR-0006-client-ui-architecture.md`
- ui_approval_source: `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-request.txt`
- ui_supplement_source: `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/human-supplement.txt`
- ui_previous_sha256: `aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c`

以上基础修订字段保留 ADR-0005 的技术来源。最新 UI 修订为 ADR-0006；当前规范哈希为 a234bc06e33fd0ae08efd944331930320b8cf1d58800fa4e66886452d8084237。v1.1 保持不变；历史 PDF 和此前已接受谱系保持不可变。这是 Human 批准的候选，尚未生效：仍待新的独立 Review、精确 HEAD 托管 CI、集成/实际 main 验证与受保护同步。S1 PASS/S2 OPEN；不激活 GUI 或产品任务。

## UI 冻结验收发现（2026-10-03）

上述候选说明保留为历史过程。ADR-0006 / UI 规范内容已在候选 33cc754、PR12 实际 main 4f18d222 独立 Review 与精确 HEAD CI 接受，并已同步主仓库；当前规范哈希不变。完整证据：`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/accepted-freeze/acceptance.md`。收尾记录仍在 review，S1 PASS / S2 OPEN，不启动后续产品任务。

## 当前 MVP 规划修订（2026-10-03）

- planning_revision_type: `human_approved_client_mvp_task_planning`
- planning_semantic_change: `true`
- planning_revision_task_id: `LOOP1-CLIENT-UI-ARCH-001`
- planning_revision_adr: `spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md`
- planning_approval_source: `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/human-request.txt`
- planning_previous_sha256: `a234bc06e33fd0ae08efd944331930320b8cf1d58800fa4e66886452d8084237`

当前 sha256 指向本轮规范字节；保留 v1.1，历史 ADR-0005/0006 与既有 revision 字段仅为谱系，不是本轮验收。仅新增 CLIENT-GUI 产品 ID、复用既有任务 acceptance。新的独立 Review、exact-head hosted CI、protected integration/actual main 与受保护同步前不生效，不实施 SEND。历史 PDF 原字节、PR7/PR8/FAIL/Recorder evidence 不变。

## MVP 规划接受发现（2026-10-03）

上述planning候选段落保留为历史。ADR-0007当前规范16e9c7b4已在candidate7466ce7、PR14实际main b60f116a14f9265031bff255db500f3414f2a357通过fresh independent Review、精确候选与actualmain hosted CI，并受保护同步H:/IM-platform。完整证据：spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/closure/acceptance.md。v1.1/hash/PDF不变；本收尾候选另待新Review/CI/集成。本轮后续仅SEND；S1PASS/S2OPEN。

## Human-approved Sync transport candidate

- sync_revision_type: `human_approved_sync_https_binding`
- sync_semantic_change: `true`
- sync_revision_task_id: `LOOP1-SYNC-TRANSPORT-001`
- sync_revision_adr: `spec/architecture/decisions/ADR-0008-sync-https-transport.md`
- sync_approval_source: `spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/human-authorization.txt`
- sync_previous_sha256: `16e9c7b488e00dd39c7c2b5da7286c22be6ac67c163f0e89733bbe00297d0a3c`

Candidate only: fresh independent Review, exact-head hosted CI, protected integration/actual-main verification and main synchronization pending. Go product implementation additionally awaits Human consent to concrete plan after prerequisite acceptance. Existing wire shapes/PDF/prior accepted history unchanged; S2 OPEN.

分页修正候选：Human 保持 min(limit,100) 单页 cap，要求持续分页直到 terminal；批准见 paging-revision/human-authorization.txt。此前457c405b79ca068af2b398b9fbe49859810c455359b01dbfdb2d4c6d72a9d966为已审未 hosted 接受候选，保留谱系；新 SHA 须独立接受。

## Sync transport 接受发现 (2026-10-03)

ADR-0008 / 公开 HTTPS Sync 绑定 已在 candidate b8200783ea3eadc1ed4e4050238f051a7ab708b3 / PR18 actual main c2ff0502fdad80f463abe038a960ca1b798e6d7a 通过 fresh independent Review 与 精确 HEAD CI 接受，并同步 H:/IM-platform。 canonical ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03 / v1.1 / 历史 PDF 不变。 证据：spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/acceptance/acceptance.md。 此前 pending 段落为历史过程。 Go 产品仍待 方案展示后 Human 同意；SYNC backlog/S2 OPEN。 本收尾记录另待独立 Review/CI/同步。

## Human 批准的最小原生 GUI 前置候选（2026-10-04）

- native_revision_type: `human_approved_minimal_client_native_capabilities`
- native_semantic_change: `true`
- native_revision_task_id: `LOOP1-CLIENT-NATIVE-ARCH-001`
- native_revision_adr: `spec/architecture/decisions/ADR-0009-client-native-capabilities.md`
- native_approval_source: `spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/approval.md`
- native_previous_sha256: `ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03`

APPROVED_PENDING_FREEZE：当前 canonical 为窄原生能力候选；原 revision_adr/policy ADR-0005、UI/planning/Sync 谱系、v1.1/历史 PDF 保持。须经新独立 Review、适用 exact-head hosted CI、protected integration/actual-main 验证及安全主仓库同步。GUI backlog/S1 PASS/S2 OPEN，无产品/契约/schema 迁移。


## Native freeze accepted discovery (2026-10-08)

Native authority freeze independently accepted: candidate `89cacae924be7ae3e85c13779e99f9f463d2c6f8`, protected PR25 actual main `6a87751087de5b4063445d0fba9fe94534507a57` and safe main synchronization PASS. Exact candidate push37656041487/PR37656059375 and actual-main37657410444:5selected jobs SUCCESS,8classifier-false normally inactive, nofailedsteps. Fresh candidate Review and new same-role actual-main audit are independently bound to their exact SHA; canonical a6b1670/PDF546915/v1.1 unchanged. Task branch task/LOOP1-CLIENT-NATIVE-ARCH-001-close; receipt preserves781unknown files/status/index and recovery/s1-handoff-20261001 branch. Source approval choices unchanged; no product/contract/schema/ACK/security change, no GUI/Windows/S2 PASS. Earlier pending/blocked statements are preserved historical snapshots. Evidence: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/acceptance-20261008/acceptance.md.

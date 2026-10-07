# Architecture Index

This file is a resolver, not an independent architecture specification.

1. Read the [baseline manifest](./baseline.md).
2. Resolve and SHA-256-check the single canonical Markdown artifact named by that manifest.
3. Verify the retained historical PDF against the manifest's separate `previous_sha256` provenance value.
4. Apply approved decisions in [`decisions/`](./decisions/) through the documented architecture process.

The manifest and this index contain discovery and migration metadata only. They do not summarize, replace, or silently reinterpret the canonical Markdown. The PDF is an immutable pre-migration snapshot, not an active second canonical source. The Markdown remains frozen under the same ACP/ADR approval rule.

Previous accepted revision: v1.1 conflict resolution under ADR-0003. The manifest separates current revision semantics from ADR-0002 historical representation-only migration. Review/CI acceptance status is recorded in the current task and evidence; historical PDF bytes remain immutable.

Current client clarification accepted at e7c80c7: Android Kotlin/Jetpack Compose Mobile plus Web/Desktop/shared TypeScript, v1.1 under ADR-0005; canonical bytes/hash unchanged by closure. Acceptance discovery below records scoped waiver and remaining administrative confirmation; S2 OPEN.

## Accepted clarification discovery (2026-10-01)

Fresh independent Review accepts clean e7c80c726d4799ba3ddab026266be638c9e6b252 under scoped Human GString waiver; original4b5 Review FAIL immutable. Exactpush36881391141 selected5SUCCESS/8correctinactive and PR36881397009 all13/every stepSUCCESS. Canonicalaa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c/PDF546915 unchanged. ADR0005 effective at accepted prerequisite. Evidence: spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/2026-10-01-coordinator-resume/acceptance.md. Earlier pending paragraphs are historical; later administrative closure needs NEW independent Review/exactHEADCI before S2activation. No product/contract change; S1PASS/S2OPEN.

## UI 修订候选（2026-10-03）

ADR-0006 记录 Human 明确的客户端 UI、设计与截图验收决定，以及仅适用于 S2 的插件执行禁令。通过 baseline.md 的当前哈希和 ui_revision_adr 字段解析。候选仍待独立 Review、精确 HEAD 托管 CI 和集成后 main 验证；已接受 main 仍是最后已知良好提交。decisions/client-ui/ 和 spec/acceptance/client-gui.md 的从属说明不建立第二份规范权威或公共契约权威。ADR-0005 仍是基础技术来源；保留 S4 经审查的沙箱 Render Bundle。

## UI 冻结验收发现（2026-10-03）

上述候选说明保留为历史过程。ADR-0006 / UI 规范内容已在候选 33cc754、PR12 实际 main 4f18d222 独立 Review 与精确 HEAD CI 接受，并已同步主仓库；当前规范哈希不变。完整证据：`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/accepted-freeze/acceptance.md`。收尾记录仍在 review，S1 PASS / S2 OPEN，不启动后续产品任务。

## 当前 MVP 任务规划补充

通过 baseline.md 的 planning_revision_adr/approval_source/previous_sha256 解析 ADR-0007 与本轮 Human 请求。当前 canonical hash 记录规划候选，v1.1 不变；ADR-0006 已接受 UI 内容保持权威。仅新增 LOOP1-CLIENT-GUI-001，原 WEB 和 S3～S6 承接 GUI acceptance。待新的独立 Review、精确 HEAD hosted CI 与 protected integration/实际 main 同步接受后生效；此前不得实施 SEND。

## MVP 规划接受发现

planning_revision_adr对应ADR-0007的canonical16e9c7b4已接受于candidate7466ce7/PR14/actualmain b60f116并同步主仓库。证据见mvp-planning/closure/acceptance.md。此前候选pending语句为历史；此接受发现不改变canonical字节，不建立S2PASS。收尾metadata仍保留review至独立闭环，本轮随后只执行SEND。

## Sync transport prerequisite candidate (2026-10-03)

Resolve sync_revision_adr/approval_source/previous_sha256 in baseline.md for Human-authorized ADR-0008 additive public HTTPS binding at canonical section11.5. New candidate independent Review/exact-head hosted CI/protected integration/actual-main synchronization pending. No Go/client runtime acceptance. Concrete Go plan requires Human consent after prerequisite acceptance; SYNC stays backlog pending real service input, S2 OPEN.

## Sync transport 接受发现 (2026-10-03)

ADR-0008 / 公开 HTTPS Sync 绑定 已在 candidate b8200783ea3eadc1ed4e4050238f051a7ab708b3 / PR18 actual main c2ff0502fdad80f463abe038a960ca1b798e6d7a 通过 fresh independent Review 与 精确 HEAD CI 接受，并同步 H:/IM-platform。 canonical ef90846ba380df14086795a3c58aef43f6503447fe0cb83ee2d0772d725d8e03 / v1.1 / 历史 PDF 不变。 证据：spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/acceptance/acceptance.md。 此前 pending 段落为历史过程。 Go 产品仍待 方案展示后 Human 同意；SYNC backlog/S2 OPEN。 本收尾记录另待独立 Review/CI/同步。

## 最小原生 GUI 前置候选发现（2026-10-04）

通过 baseline.md 的 native_revision_adr/native_approval_source/native_previous_sha256 解析 Human 批准的 ADR-0009、§6.1/§6.5 与窄原生 policy。APPROVED_PENDING_FREEZE：新独立 Review、exact-head hosted CI、protected integration/actual-main 验证及安全同步待完成。ADR-0005 基础 policy、v1.1/PDF/历史不变；GUI backlog/S1 PASS/S2 OPEN。证据：spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/approval.md。


## Native freeze accepted discovery (2026-10-08)

Native authority freeze independently accepted: candidate `89cacae924be7ae3e85c13779e99f9f463d2c6f8`, protected PR25 actual main `6a87751087de5b4063445d0fba9fe94534507a57` and safe main synchronization PASS. Exact candidate push37656041487/PR37656059375 and actual-main37657410444:5selected jobs SUCCESS,8classifier-false normally inactive, nofailedsteps. Fresh candidate Review and new same-role actual-main audit are independently bound to their exact SHA; canonical a6b1670/PDF546915/v1.1 unchanged. Task branch task/LOOP1-CLIENT-NATIVE-ARCH-001-close; receipt preserves781unknown files/status/index and recovery/s1-handoff-20261001 branch. Source approval choices unchanged; no product/contract/schema/ACK/security change, no GUI/Windows/S2 PASS. Earlier pending/blocked statements are preserved historical snapshots. Evidence: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/acceptance-20261008/acceptance.md.

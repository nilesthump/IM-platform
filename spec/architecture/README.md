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

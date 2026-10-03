---
task_id: LOOP1-CLIENT-UI-ARCH-001
title: Client UI architecture, design direction and screenshot acceptance freeze
status: review
owner: Architecture Agent /root
stage: S2
gate: S2
---

# Goal

Freeze the Human-requested client UI architecture, information architecture, initial design-system direction and GUI acceptance protocol. Documentation only; no GUI or S2 product implementation.

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md`; accepted input SHA256 aa2398020beeda5f7f9456aac346da57bd8b75212192123c943c35dfdc80f84c and immutable PDF 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510. Canonical §2.1/2.3/3/6/7/8/10 SRC-01 through SRC-07/11/12-14/15/20/21.
- Approved ADR-0001 (expired), ADR-0002/0003/0004/0005; older authority/evidence remains immutable.
- `spec/governance/minimality.md`, `spec/governance/execution-boundaries.md`, `spec/governance/independent-review.md`, `spec/governance/technology-selection.md`.
- `spec/domain/messaging.md`, `spec/invariants/messaging.md`, `spec/domain/sync-plugin.md`, `spec/invariants/sync-plugin.md`, `spec/acceptance/s0-messaging.md`, `spec/acceptance/s0-sync-plugin.md`.
- `contracts/http/auth-user-friend.openapi.json`, `contracts/websocket/`, `contracts/plugin-api/`, canonical fixtures. Public contracts remain unchanged and sole machine authority.
- Human task and supplemental worktree/S2-only plugin decisions preserved in this task evidence directory.

# Technology Authorization

Existing accepted canonical §6.1 / ADR-0005 retains React/TypeScript Web; Tauri/React/TypeScript Desktop and SQLx atomic native adapter; Android Kotlin/Compose/SDK SQLite Mobile. Human prompt explicitly specifies React built-in state, independent Desktop UI, Mobile ViewModel/StateFlow/Jetpack Navigation Compose. Record these in ADR-0006 and canonical candidate before any future implementation. No additional named icon/accessibility/utility library or Web router/data library is selected. Generic library categories are not blanket dependency authorization.

# Dependencies

- LOOP1-CLIENT-ARCH-CLARIFICATION-001 done.
- LOOP1-CLIENT-SQLITE-001 done: accepted PR10/main23a03bb and later documentation-only PR11/main9c0eba8; original recovery metadata remains unmodified.
- LOOP1-CI-001 and LOOP1-RESEARCH-001 done; S1 PASS / S2 OPEN.
- Later Human instruction explicitly resumes only this architecture task after earlier STOP.

# Allowed Paths

- `AGENTS.md` (explicit Human worktree allocation supplement only).
- `spec/tasks/{active,review,done}/LOOP1-CLIENT-UI-ARCH-001.md` (exactly one queue).
- `spec/architecture/frozen-architecture.md`, `spec/architecture/baseline.md`, `spec/architecture/README.md` (explicit Human UI decision, v1.1/hash/lineage only).
- `spec/architecture/decisions/ADR-0006-client-ui-architecture.md`.
- `spec/architecture/decisions/client-ui/architecture.md`, `spec/architecture/decisions/client-ui/design-direction.md`.
- `spec/acceptance/client-gui.md`.
- `spec/progress/checkpoints/2026-10-03-client-ui-architecture-accepted.md` (only after actual accepted freeze; not created by this fix).
- `spec/progress/current.md`, `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/**`.
- Local `.git-ui-chinese-research/**` (fresh Chinese Fix Agent Recorder only, never product authority).
- Local `.git-ui-architecture-research/**` for Recorder artifacts only, never product authority.

# Acceptance

All three documents cover the visible Human requirements with truthful S2/S4 scope and source ownership. Canonical candidate/ADR resolve Desktop reuse and plugin boundaries; v1.1 and historical PDF/PR7/PR8 preserved. Unique current task, allowed_paths, unchanged product/contracts verified. Fresh independent clean committed candidate Review and exact-head hosted required jobs PASS are mandatory before freeze effectiveness, done, merge/integration and final synchronized-main verification. Screenshots/Architect approval supplement CI for future GUI tasks.

# Forbidden

No UI pages, component library, state library, Plugin runtime/renderer/install/Marketplace, AI API/features/fake data, backend, public contracts or S2 source edits. No next SEND/SYNC/WEB activation. No historical authority/evidence rewriting, no self-acceptance.

# Minimality

Three bounded documents and one ADR/canonical clarification. No component code, token generator, new tooling or speculative framework. Token categories are design semantics, not wire contracts. Screenshot evidence reuses task evidence and existing independent review/CI process.

# Verification

- Minimum baseline: Python 3 `ci/check_architecture.py --scope all --json` (PASS, zero violations).
- `tools/verify_frozen_architecture.py`, `python -B -m unittest discover -s tests/architecture`, `python -B ci/check_architecture.py --scope all --json`, `git diff --check`; exact command/result/time in evidence/Recorder.
- Recovery verifier `tools/verify-loop1-ctrl-002.ps1 -Mode Development` locally; Acceptance on clean committed candidate by independent reviewer and actual hosted CI. Development is not acceptance.

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/`; Recorder R-CLIENT-UI-ARCH-20261003, capture_mode prospective_resume; pre-Recorder read-only startup is incomplete and cannot be represented as a complete prospective trace.

# Handoff

Task branch `task/LOOP1-CLIENT-UI-ARCH-001`; assigned worktree `H:/.codex/worktrees/client-ui-architecture/IM-platform`, actual root matched. Parent accepted main9c0eba89219b3fab73fe9258a7cfc59831c499dc. All new task writes owned by /root; original tracked/untracked recovery work not copied or changed. No product/schema migration; pending independent Review/CI/main sync, S2 OPEN.

# Next Action

Fresh independent clean-candidate Review -> applicable exact-head hosted CI -> accepted integration and protected main synchronization. No next GUI/product implementation.

## Candidate handoff

Three documents, ADR-0006, canonical v1.1 UI amendment/hash and Settings-directory worktree allocation supplement complete. Frozen integrity/source all/architecture unit/diff checks PASS; recovery Development recheck PASS24 after disclosed initial metadata FAIL. Evidence candidate-checks.json and recovery-recheck.json; Windows GBK Recorder output failure retained. No source/contracts/PDF changes. Candidate not accepted; S1 PASS/S2 OPEN. Root writer released after commit for fresh Review. Current changes are task-owned only.

## 中文修订与 Review 修复交接（2026-10-03）

Fresh Fix Agent /root/ui_arch_chinese_fix 将 ADR-0006、UI architecture、design-direction、client-gui 四份新交付文档全部正文改为中文；同步翻译索引/清单最新 UI 候选段落。规范正文与 a234bc06 候选哈希不变。旧 Review 发现 BASE..HEAD diff whitespace FAIL；原始字节以 gzip 与 SHA 清单保留，文本副本明确标注 LF 规范化。历史提交、根 Agent Recorder、原始失败结论未覆盖。新证据位于 chinese-revision/。仍为 review，待新独立 Review、精确 HEAD 托管 CI、受保护集成/main 同步；不声明最终接受。最后已知良好 main9c0eba89219b3fab73fe9258a7cfc59831c499dc，S1 PASS/S2 OPEN。本修订仅由 fresh Fix Agent 写入；root 的本地 Recorder 未跟踪目录归 root 所有。

中文修订本地验证：frozen integrity/source all/53 architecture tests/完整 BASE 至工作区 diff check/recovery Development 均 PASS；精确命令、退出码、时长见 chinese-revision/checks.json。待提交后还须精确 BASE..HEAD 检查与新的独立验收。

## 架构内容已接受，收尾 review

候选33cc754及PR12/main4f18d222已由两个新鲜独立 Review 接受、精确 hosted CI通过并同步到 H:/IM-platform。当前 Last Known Good Commit：`4f18d222c75bb03166b2b5ead84b9999150a300c`。证据：`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/accepted-freeze/acceptance.md`。任务保留 review，下一步为本收尾记录的独立 Review、精确 HEAD CI、主仓库同步；禁止后续 GUI 激活。原始主仓库既有文件已受保护，收尾改动仅归 /root 所有。

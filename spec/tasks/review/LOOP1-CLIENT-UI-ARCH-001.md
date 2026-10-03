---
task_id: LOOP1-CLIENT-UI-ARCH-001
title: Human-approved MVP client GUI task planning supplement
status: review
owner: Coordinator /root
stage: S2
gate: S2
---

# Goal

复用已接受 UI 架构任务，执行 Human 2026-10-03 明确批准的最小规划补充。此前 UI 冻结已接受于 main59dcf34；本次补充未接受，不启动 SEND 或 GUI。仅新增一个产品 Task ID LOOP1-CLIENT-GUI-001；Web 和 S3～S6 复用既有规划 ID。

# Inputs

- `spec/architecture/README.md` -> `spec/architecture/baseline.md` -> `spec/architecture/frozen-architecture.md`; input a234bc06e33fd0ae08efd944331930320b8cf1d58800fa4e66886452d8084237，历史 PDF546915 不变。读取 §2/§3/§6/§10 SRC-01 through SRC-07/§11/§12-15/§19-21/附录 A。
- `spec/architecture/decisions/ADR-0006-client-ui-architecture.md`、`spec/architecture/decisions/client-ui/architecture.md`、`spec/architecture/decisions/client-ui/design-direction.md`、`spec/acceptance/client-gui.md`。
- `spec/governance/minimality.md`、`spec/governance/execution-boundaries.md`、`spec/governance/independent-review.md`、`spec/governance/technology-selection.md`。
- `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/human-request.txt`。
- `spec/domain/messaging.md`、`spec/invariants/messaging.md`、`spec/domain/sync-plugin.md`、`spec/invariants/sync-plugin.md`。契约只引用，不修改。

# Technology Authorization

仅规划；沿用已接受 §6.1/6.5、ADR-0005/0006；不增加敏感技术依赖。

# Dependencies

- LOOP1-CLIENT-ARCH-CLARIFICATION-001 done.
- LOOP1-CLIENT-SQLITE-001 done.
- LOOP1-CI-001 done; LOOP1-RESEARCH-001 done.
- UI 架构及收尾已接受 main59dcf34；本轮 Human 重新授权限定规划修订。

# Allowed Paths

- `spec/tasks/active/LOOP1-CLIENT-UI-ARCH-001.md`
- `spec/tasks/review/LOOP1-CLIENT-UI-ARCH-001.md`
- `spec/tasks/done/LOOP1-CLIENT-UI-ARCH-001.md`
- `spec/tasks/backlog/LOOP1-CLIENT-GUI-001.md`
- `spec/tasks/backlog/LOOP1-CLIENT-SEND-001.md`
- `spec/tasks/backlog/LOOP1-SYNC-001.md`
- `spec/tasks/backlog/LOOP1-WEB-001.md`
- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/README.md`
- `spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md`
- `spec/acceptance/client-gui.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/**`
- `spec/progress/checkpoints/2026-10-03-client-mvp-planning-accepted.md`
- `.git-mvp-research/**`

# Acceptance

§19/§20/S2 Gate 与队列一致；GUI 四项依赖完整、Web 在 GUI 后；S3 parity、S4 plugin UI/fixtures、S5 compat/release、S6 RC 的 GUI 要求并入原 ID。仅新增一个产品 UI ID。v1.1 不变、更新真实 hash/revision lineage；PDF/历史证据不变，无产品/契约变化。clean candidate、完整性/architecture/task-dependency/negative controls、fresh independent Review、精确 HEAD hosted CI、protected integration、实际 main 与受保护同步均必需。之后才激活 SEND；不激活 SYNC/GUI/Web。

# Forbidden

产品源码/后端/契约/schema/PDF/历史证据修改；GUI/SEND 提前实现；新 Web/parity/plugin/release/soak UI Task；自我验收；降低检查器或门禁。

# Minimality

复用 UI-ARCH 承载文档补充；最小 ADR-0007 记录新批准与 revision，ADR-0006 历史不变。四份 S2 队列规格实例化既有 SEND/SYNC/WEB 规划与唯一新增 GUI；后续要求直接进入既有规划表。

# Verification

- Minimum baseline: python -B ci/check_architecture.py --scope all --json PASS after sandbox temp permission failure.
- `tools/verify_frozen_architecture.py` --base-commit 59dcf34e4538d2f35ccafde8104e860f8cf5cd7a.
- python -B -m unittest discover -s tests/architecture; python -B ci/check_architecture.py --scope all --json; git diff --check.
- `tools/verify-loop1-ctrl-002.ps1` -Mode Development; clean independent candidate Acceptance.
- Evidence-local planning checker validates dependency queues and injects extra UI ID/missing dependency as negative controls.

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/mvp-planning/`; Recorder assigned Git metadata/mvp-planning-research R-CLIENT-MVP-20261003 prospective_resume，此前只读痕迹不完整。

# Handoff

Assigned H:/.codex/worktrees/client-mvp-planning/IM-platform 根已验证。branch task/LOOP1-CLIENT-MVP-PLAN-20261003，last good59dcf34e4538d2f35ccafde8104e860f8cf5cd7a。仅 /root 拥有本轮 scoped writes；主仓库 SQLite/E2E/研究及旧收尾记录原位不变。初次 shell encoding/Python27/range quoting 失败已暴露；架构基线首次 Go temp access FAIL，获准环境重跑 PASS。无未解决架构冲突；S1 PASS/S2 OPEN。

# Next Action

完成限定规划候选并提交，委派新独立 Review；exact-head hosted CI、protected integration/main sync 接受后继续 SEND。

## 本地候选交接

Frozen hash/PDF/source all/53 architecture tests、规划正例与三项负例、diff check/Recovery Development 全部 PASS；checks.json 记录命令/退出码/时长。规范候选 hash16e9c7b4、v1.1；仅 docs，无产品/contract/PDF 更改。等待 fresh independent Review/精确 HEAD CI/protected main sync；SEND 未激活。Recorder 仅原字节移到 assigned Git metadata，relocation manifest hashes 等同；不修改证据。

## Fresh whitespace fix / independent review FAIL

Independent Review of 6e9f7327c6cf301a3841bcc49244b70974e82a06 failed full BASE..HEAD diff --check (exit2); earlier diff PASS covered working diff only. Fresh fixer /root/mvp_whitespace_fix owns scoped repair writes in assigned worktree on task/LOOP1-CLIENT-MVP-PLAN-20261003. Original approval/log Git blob and checkout bytes, failed review and Recorder are preserved with hashes under mvp-planning/whitespace-fix/. LF copies explicitly change bytes; original checks.json bytes are gzip-preserved; its LF reading copy retains all result values; history/Recorder remain unchanged. Fixed-base full-range verification replaces limited working-diff check; separate rechecks preserve old results. Task stays review, S1 PASS/S2 OPEN. Next: clean fix commit -> NEW fresh independent Review -> exact-head hosted CI -> protected integration/actual-main synchronization; no SEND before acceptance. Last accepted main remains 59dcf34e4538d2f35ccafde8104e860f8cf5cd7a.

First repair verification found additional CRLF in checks.json, pr-body.md and recorder-relocation.json. Exact originals were preserved before LF-only normalization; first FAIL attempt is retained in whitespace-fix/rechecks-attempt1.zip. No old result/command/duration/relocation fact changed.

Local repair verification (not independent acceptance): frozen --base-commit PASS 0.188s; source all PASS 0.515s; 53 architecture tests PASS 6.032s; planning with3 negative controls PASS 0.171s; fixed-base full working diff PASS0.047s; Recovery Development PASS6.719s. Exact argv/exit/duration: whitespace-fix/rechecks-attempt2/checks.json. All original/archive/normalized hashes verified. Pending clean fix commit, complete staged and committed range checks, clean Recovery Acceptance, then NEW fresh independent Review/exact-head CI and main synchronization. No sync or completion claimed.

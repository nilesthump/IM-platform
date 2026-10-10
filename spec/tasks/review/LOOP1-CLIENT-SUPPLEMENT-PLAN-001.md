---
task_id: LOOP1-CLIENT-SUPPLEMENT-PLAN-001
title: S2 客户端补充架构与任务规划修订
status: review
owner: /root/s2_plan_fix_a
stage: S2
gate: S2
---

# Goal

仅交付 Human 授权的 Web 完成后 S2 补充规划：中文 ADR-0012、canonical/current hash/谱系、三个串行 backlog Task、验收和可执行 queue/dependency/Gate guards。独立接受、protected integration/actual-main audit、H:/IM-platform 安全同步后停止；S2 OPEN，不实现三个产品任务或评估 Stage Gate。

# Inputs

- spec/architecture/README.md -> baseline.md -> frozen-architecture.md §2.3/§3/§6/§10 SRC-01 through SRC-07/§11/§15/§19/§20/附录A。
- ADR-0005/0006/0007/0008/0009/0010/0011；client-ui/architecture.md、design-direction.md；client-gui.md；domain/invariants messaging 与 sync-plugin。
- spec/governance/minimality.md、execution-boundaries.md、independent-review.md、technology-selection.md；Task template。
- 本任务 evidence/human-request.txt 为直接 Human 批准，继续恢复原范围；最新 accepted administrative main b4d271ceeed40343e627450f6b43cd9c9ad5ff0e 与 accepted Web product a1b154d06c0a9d191ec8dca514fff3ab1b46ee25。

# Technology Authorization

规划控制仅 Python standard library/现有 PowerShell verifier；产品技术继承已接受 canonical §6.1/§6.5 与 ADR5/6/9/11。ADR12 明确未来语言偏好四标量/独立语言位置和阶段；本轮不安装依赖或写产品。

# Dependencies

- LOOP1-WEB-001 done，独立接受、PR29 集成和产品主仓库同步已成立；PR30 最新行政 main b4d271c 不改变产品树。

# Allowed Paths

- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/README.md`
- `spec/architecture/decisions/ADR-0012-client-supplement-planning.md`
- `spec/architecture/decisions/client-ui/architecture.md`
- `spec/acceptance/client-gui.md`
- `spec/acceptance/client-supplement.md`
- `ci/check_architecture.py`
- `ci/check_s2_planning.py`
- `ci/classify.py`
- `tools/verify_frozen_architecture.py`
- `tools/verify-loop1-ctrl-002.ps1`
- `tests/architecture/test_s2_planning.py`
- `tests/architecture/test_frozen_architecture.py`
- `tests/ci/test_classify.py`
- `ci/architecture-checks.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-SUPPLEMENT-PLAN-001/**`
- `spec/progress/checkpoints/*client-supplement-plan*.md`
- `spec/tasks/backlog/LOOP1-CLIENT-SUPPLEMENT-PLAN-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-SUPPLEMENT-PLAN-001.md`
- `spec/tasks/active/LOOP1-CLIENT-SUPPLEMENT-PLAN-001.md`
- `spec/tasks/review/LOOP1-CLIENT-SUPPLEMENT-PLAN-001.md`
- `spec/tasks/done/LOOP1-CLIENT-SUPPLEMENT-PLAN-001.md`
- `spec/tasks/backlog/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/active/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/review/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/done/LOOP1-CLIENT-STATE-001.md`
- `spec/tasks/backlog/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/active/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/review/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/done/LOOP1-CLIENT-UI-REF-001.md`
- `spec/tasks/backlog/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/ready/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/active/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/review/LOOP1-CLIENT-I18N-001.md`
- `spec/tasks/done/LOOP1-CLIENT-I18N-001.md`

# Acceptance

所有用户要求落实 canonical、ADR、从属验收与三个 backlog；实际源码/accepted evidence baseline逐项记录。可执行 guard 正负例验证任务唯一性、status/queue、串行dependency、activation acceptance/integration/sync和S2前置项，既有门禁不减弱。fresh independent Review -> exact-head applicable hosted CI -> protected integration -> actual-main验证 -> safe main同步；全部完成前本控制任务不得done。

# Forbidden

不写产品/contracts/schema，不改ACK/security/兼容，未知main工作不复制/覆盖；不激活backlog，不执行S2 Stage Gate/deferred helper，不复审或重开已接受WEB。

# Minimality

复用既有authority/Task/CI流程，仅一个行政任务和三个明确要求产品ID。新标准库guard直接校验当前要求，不增加通用调度或未来框架。

# Verification

- Minimum baseline: `python -Xutf8 -B ci/check_architecture.py --scope all --json` 与 `python -Xutf8 -B tools/verify_frozen_architecture.py`：起点b4d真实exit0。
- `python -Xutf8 -B ci/check_s2_planning.py`；`python -Xutf8 -B -m unittest discover -s tests/architecture`；`python -Xutf8 -B -m unittest discover -s tests/ci`。
- `tools/verify-loop1-ctrl-002.ps1 -Mode Development`，clean committed `-Mode Acceptance`；diff/scope与产品树保持验证。
- 实际 hosted classifier既有full matrix决定必需jobs；CI aggregate gate与S2 Stage Gate有别，不降低selection。

# Evidence

`spec/progress/evidence/LOOP1-CLIENT-SUPPLEMENT-PLAN-001/`；private Recorder root .git/worktrees/IM-platform7/s2-planning-research。本地检查/Recorder有效不是独立接受。

# Completion Metadata

acceptance_result: PENDING
accepted_candidate_sha: unavailable
integrated_main_sha: unavailable
main_sync_result: PENDING
independent_review_evidence: unavailable
hosted_acceptance_evidence: unavailable
main_sync_evidence: unavailable

# Handoff

Fresh Fix A修复6267726独立Review FAIL的三阻断；原Review报告/自动审批拒绝和静态dispatch事实原样保留于evidence/fix-a。唯一section/mandatory字段及严格真实路径拒绝links/reparse；三个backlog使用package和工具链/安装条件。architecture77 OK/1平台skip，CI35 OK/4原skip，planning/frozen/allarchitecture/Development exit0，Linux真实symlink待新hosted执行；无产品构建或实际S2 Gate。新commit/clean Acceptance/Recorder结果见private fix-a handoff；独立接受/同步PENDING，last accepted good b4d271c。

本轮规划实现完成，真实检查与原FAIL见 evidence/local-verification.json、local-verification.md 和 instrumentation-failures.md。三产品 Task 均 backlog，S2 OPEN，不执行 Gate。assigned root verified exact；起点/last accepted good b4d271ceeed40343e627450f6b43cd9c9ad5ff0e。提交候选后只允许 fresh independent Review 与修复/复审、精确 hosted CI、protected integration、actual-main 验证、安全主仓库同步。Implementation 自己不接受、不 done。独立接受 metadata 由 Coordinator 填实际证据，当前全部 PENDING。

# Next Action

Coordinator 在 clean committed candidate 上分配新鲜 Reviewer；若 FAIL 交 fresh Fix Agent 后 fresh Review。准确候选接受后集成及安全同步，最终此控制任务 done、三产品 backlog、S2 OPEN，并建立 accepted checkpoint。future order WEB → STATE → UI-REF → I18N → S2 Gate，STATE 同时依赖本规划 done 生效。

---
task_id: LOOP1-SYNC-TRANSPORT-001
title: Public Sync HTTPS transport prerequisite
status: done
owner: /root
stage: S2
gate: S2
---

# Goal

冻结现有四种 Sync JSON 形状的最小公开 HTTPS 传输绑定，完成契约及可执行守卫；产品实现另待 Human 同意。

# Inputs

- spec/architecture/README.md -> baseline.md -> frozen-architecture.md (§2.3/§3/§6/§7/§10 SRC-01..07/§11)
- spec/architecture/decisions/ADR-0005-client-technology-clarification.md
- spec/architecture/decisions/ADR-0006-client-ui-architecture.md
- spec/architecture/decisions/ADR-0007-client-mvp-task-planning.md
- spec/governance/{minimality,execution-boundaries,independent-review,technology-selection}.md
- spec/domain/{messaging,sync-plugin}.md; spec/invariants/{messaging,sync-plugin}.md
- contracts/websocket/sync-v1.schema.json; contracts/errors/http-errors.schema.json; contracts/http/auth-user-friend.openapi.json
- spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/human-authorization.txt

# Dependencies

Accepted SEND main a0304fcc7be18b87f5986d014849d6b48b96a071; confirmed SYNC authority/runtime gap at bc1bebb31fac6f0256db998746187005c9028606.
Human expressly authorizes this named prerequisite despite SYNC backlog; no future task selection authorization.

# Allowed Paths

- contracts/http/sync.openapi.json
- tools/verify_sync_transport.py
- tests/contract/test_sync_transport.py
- .github/workflows/ci.yml
- spec/architecture/frozen-architecture.md
- spec/architecture/baseline.md
- spec/architecture/README.md
- spec/architecture/decisions/ADR-0008-sync-https-transport.md
- spec/tasks/active/LOOP1-SYNC-TRANSPORT-001.md
- spec/tasks/review/LOOP1-SYNC-TRANSPORT-001.md
- spec/tasks/done/LOOP1-SYNC-TRANSPORT-001.md
- spec/tasks/backlog/LOOP1-SYNC-001.md
- spec/progress/current.md
- spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/**
- spec/progress/evidence/LOOP1-SYNC-001/research/**
- spec/progress/evidence/LOOP1-SYNC-001/implementation/authority-blocker.md
- spec/progress/evidence/LOOP1-SYNC-001/implementation-research/**
- spec/progress/checkpoints/*sync-transport*.md

# Acceptance

Fresh independent Review of clean committed candidate, applicable exact-head hosted CI and protected integration/actual-main verification/main synchronization. Contract references resolve, official OpenAPI structural lint passes, machine binding guards plus negative mutation tests pass; existing schema/ACK/Session/storage regressions preserved. Rule acceptance is not Go runtime or client SYNC acceptance; S2 OPEN.

# Forbidden

No Go/Java/client/UI/Web/plugin product code, database schema/migrations, existing four Sync shapes, ACK/security/compatibility changes or dependency selection. No Go code until accepted prerequisite and Human consent to concrete plan. Do not reopen done history or change immutable Recorder evidence.

# Minimality

Two HTTPS POST operations reuse existing shapes/errors/Bearer and generic Gateway proxy. No WSS message type, envelope, service, runtime or dependency. Bounded verifier uses existing official OpenAPI structural lint and schema validator, no generic validation framework.

# Verification

Minimum baseline: python -B ci/check_architecture.py --scope all --json; python -B tools/verify_frozen_architecture.py (both recorded PASS).
Candidate entry points: `tools/verify_sync_transport.py`; `tools/verify-loop1-ctrl-002.ps1` (Acceptance requires clean committed checkout). Commands: python -B tools/verify_sync_transport.py; python -B -m unittest discover -s tests/contract -p test_sync_transport.py; architecture tests and existing HTTP/WSS/Sync/plugin checks; applicable hosted jobs mandatory.

# Handoff

Accepted/synchronized public Sync prerequisite: branch task/LOOP1-SYNC-001, clean reviewed candidate b8200783ea3eadc1ed4e4050238f051a7ab708b3, protected actual main c2ff0502fdad80f463abe038a960ca1b798e6d7a, sync receipt PASS260changedpaths/781protectedentries. Fresh candidate Review PASS and independent same-role new actual-main audit PASS; exact runs37121974931/37122484526 each13jobs105stepsSUCCESS. Canonicalef90846 preserved; no Go/client runtime acceptance. Coordinator owns only administrative closure writes. Earlier sections below describe bounded historical candidates/failures; accepted facts in acceptance/ supersede their pending statements.

# Historical Review-ready handoff

Local final binding/ref/official OAI lint PASS; 4 Sync test groups and 53 architecture tests PASS; final architecture all/frozen PASS; existing HTTP/WSS/SyncPlugin regression PASS. Full actual commands/exit/elapsed/hash: spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/verification-history.md; failures retained. Predecessor implementation evidence/Recorder plus Coordinator sealed rootresearch are immutable authorized inputs, not permission to edit. No Go/product code. Fresh independent Review/exact-head hosted full13jobs/protected integration/actual-main acceptance/main sync pending. Concrete Go proposal requires Human consent after prerequisite acceptance. Known good accepted main a0304fc; ownership and startup-order exception in implementation-handoff.md; candidate SHA supplied after commit.

# Historical Independent Review and external publication hold

Fresh independent Review PASS for clean57404dcc, full range a0304fc..57404dcc. Report/35-event sealed validated Recorder archived byte-exact in independent-review-57404dcc/. Architecture/contract/regression checks PASS; commands/results in report. No hosted CI/integration/main sync. Auto-review rejected GitHub publication pending explicit Human authorization of this prerequisite branch to https://github.com/nilesthump/IM-platform.git. Execution BLOCKED_EXTERNAL_ACCESS; state review, no Task/Gate PASS. Next: review this administrative increment, specific publication consent, final full13-job exact-head CI/protected integration/actual-main audit-CI/main sync, then show Go proposal for separate consent. Last accepted main a0304fc unchanged; Coordinator owns administrative increment. No product writes/SYNC advancement. See external-publication-blocker.md.

# Historical Human 分页修正与发布恢复

Human 已明确授权推送既定分支到 GitHub/PR/CI及接受后保护合并同步，原发布阻断是历史。min(limit,100) 保持单页 cap；事务提交后持续分页至 terminal，无固定总条数/页数截断。canonical/ADR/contract binding及13文档mutation控制一致；四个JSON shapes不变。新修正待 fresh independent Review/精确 HEAD hosted CI/主仓库同步；不得沿用此前候选PASS关闭任务。writer /root/sync_paging_revision，lastgood main a0304fc，无 main/Go/client 写入；最新请求/恢复事实与验证在 paging-revision/。

# Evidence

Accepted proof: `spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/acceptance/acceptance.md`. Immutable fresh candidate/actual-main reports, raw providers/logs, sealed research and synchronization receipt included; previous FAIL evidence remains in recovery-fix/.

# Next Action

Complete this administrative record candidate through NEW independent Review/applicable exact-head hosted CI/protected integration/actual-main audit and preservation-verified main synchronization. Then show corrected Go proposal and obtain separate Human implementation consent before defining the runtime task; SYNC remains backlog on actual runtime input. Publication consent already received.

# Historical Fresh recovery fix handoff

Local existing Acceptance PASS at clean committed repair 8880ee22b16665ebddef042bedb6f6aaff4181f5; branch task/LOOP1-SYNC-001, zero status entries. Frozen integrity/Sync binding official OAI lint/4 Sync test groups PASS; architecture all and Acceptance embedded 53 architecture tests PASS. Exact commands/exit/elapsed/raw hashes in recovery-fix research and handoff.md. Final archival candidate requires NEW independent Review/hosted CI/integration/main sync; this fixer cannot independently accept. Ownership only metadata/new evidence, no main/product/authority writes.

---
task_id: LOOP1-SYNC-TRANSPORT-001
title: Public Sync HTTPS transport prerequisite
status: review
owner: /root/sync_transport_design
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
Candidate: python -B tools/verify_sync_transport.py; python -B -m unittest discover -s tests/contract -p test_sync_transport.py; architecture tests and existing HTTP/WSS/Sync/plugin checks; applicable hosted jobs mandatory.

# Handoff

In progress; accepted base a0304fcc7be18b87f5986d014849d6b48b96a071. Assigned exact root H:/.codex/worktrees/sync-resume/IM-platform; branch task/LOOP1-SYNC-001. Sole writer /root/sync_transport_design owns prerequisite paths; root sealed20eventBLOCKED Recorder input included unchanged by express Coordinator ownership authorization. Startup read-only gap/failures disclosed in prospective_resume. Independent Review/CI/integration/main sync pending. SYNC remains backlog blocked until approved binding AND actual accepted Go inputs.

# Review-ready handoff

Local final binding/ref/official OAI lint PASS; 4 Sync test groups and 53 architecture tests PASS; final architecture all/frozen PASS; existing HTTP/WSS/SyncPlugin regression PASS. Full actual commands/exit/elapsed/hash: spec/progress/evidence/LOOP1-SYNC-TRANSPORT-001/verification-history.md; failures retained. Predecessor implementation evidence/Recorder plus Coordinator sealed rootresearch are immutable authorized inputs, not permission to edit. No Go/product code. Fresh independent Review/exact-head hosted full13jobs/protected integration/actual-main acceptance/main sync pending. Concrete Go proposal requires Human consent after prerequisite acceptance. Known good accepted main a0304fc; ownership and startup-order exception in implementation-handoff.md; candidate SHA supplied after commit.

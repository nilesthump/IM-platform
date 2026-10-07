---
task_id: LOOP1-CLIENT-NATIVE-ARCH-001
title: Freeze minimal native GUI capabilities and appearance storage
status: review
owner: /root/native_architecture_freeze
stage: S2
gate: S2
---

# Goal

Freeze already Human-approved minimal native/appearance prerequisite for LOOP1-CLIENT-GUI-001. Authority documentation only.

# Inputs

- spec/architecture/README.md -> baseline.md -> frozen-architecture.md sections2.3/3/6.1/6.5/10 SRC-01 through SRC-07/11.
- ADR-0005/0006/0007/0008 and accepted client-ui architecture/design-direction.
- spec/governance/minimality.md, execution-boundaries.md, independent-review.md, technology-selection.md.
- spec/acceptance/client-gui.md; GUI readiness/authority-gap.md and human-decisions.md.
- research/README.md and accepted Instrumentation Epoch.

# Technology Authorization

Existing clients/mobile/ Kotlin and clients/desktop/ TypeScript responsibilities are read-only inputs here; no product write scope. ADR-0009/canonical freeze candidate; not effective until independent acceptance/integration/synchronization.
client_language: TypeScript
client_language: Kotlin
client_framework: Tauri
client_framework: Jetpack Compose
client_runtime: Tauri
client_runtime: Android

# Dependencies

- LOOP1-CLIENT-ARCH-CLARIFICATION-001 (accepted/done).
- LOOP1-CLIENT-UI-ARCH-001 (accepted/done).
- LOOP1-SYNC-001 (accepted/done at actual main ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597).
- Exact Human approval in GUI readiness/human-decisions.md.

# Allowed Paths

- spec/architecture/README.md
- spec/architecture/baseline.md
- spec/architecture/frozen-architecture.md
- spec/architecture/decisions/ADR-0009-client-native-capabilities.md
- spec/tasks/backlog/LOOP1-CLIENT-NATIVE-ARCH-001.md
- spec/tasks/ready/LOOP1-CLIENT-NATIVE-ARCH-001.md
- spec/tasks/active/LOOP1-CLIENT-NATIVE-ARCH-001.md
- spec/tasks/review/LOOP1-CLIENT-NATIVE-ARCH-001.md
- spec/tasks/done/LOOP1-CLIENT-NATIVE-ARCH-001.md
- spec/tasks/backlog/LOOP1-CLIENT-GUI-001.md (dependency/authority readiness only; eight assembly-path consent preserved).
- spec/progress/current.md
- spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/**
- spec/progress/checkpoints/*loop1-client-native-arch-001*.md

# Acceptance

Freeze exact approved choices/responsibilities/storage limits in canonical6.1/6.5/ADR0009 and native_packages. Manifest SHA/additive lineage resolve; prior revision/PDF/v1.1/history immutable. Fresh independent Review of clean candidate, required exact-head hosted jobs, protected integration/actual-main and safe main synchronization mandatory before done/effectiveness. Task acceptance is not S2 Gate PASS.

# Forbidden

No product/native implementation or installs, new framework/bundler, public API/backend/CORS/schema/ACK/security/compatibility/AI/plugin runtime, future OS parity, checker/governance/CI changes or historical evidence rewrite.

# Minimality

Current GUI acceptance requires HTTPS/refresh persistence/real notification/tray/shortcut/appearance. Existing SyncHttp injected fetch suffices; one narrow OS adapter and scalar appearance store per approved target. Official plugins/reqwest/keyring avoid handwritten Win32 FFI. No generic/future mechanism.

# Verification

- Minimum baseline: Python3 -B ci/check_architecture.py --scope all --json; -B tools/verify_frozen_architecture.py.
- Python3 -B -m unittest discover -s tests/architecture -p test_*.py.
- PowerShell7 `tools/verify-loop1-ctrl-002.ps1` -Mode Development, then clean committed -Mode Acceptance.
- git diff --check and scope/history/hash checks.
- Exact hosted CI/independent Review/main synchronization pending; durable local results in spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/verification.md.

# Evidence

spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/approval.md.
Own private Recorder R-NATIVE-ARCH-20261004, parent R-GUI-COORDINATOR-20261004, prospective_resume: initial read-only startup before registration explicitly incomplete.

# Handoff

S1 PASS/S2 OPEN; last accepted ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597. Assigned root H:/.codex/worktrees/s/IM-platform exactly verified before writes; branch task/LOOP1-CLIENT-NATIVE-ARCH-001 clean start37188ccd444591665e4267901bbfc53dce8e40b6 includes authorized GUI readiness. Sole writer owns bounded docs; main unknown work untouched. No product/data migrations. Acceptance/effectiveness/synchronization PENDING.

# Next Action

Finish bounded freeze/local verification/commit, move to review. Fresh independent Reviewer/Coordinator completes exact-head hosted CI/protected integration/actual-main/safe sync. GUI stays backlog until prerequisite done/effective.

## Local review handoff

Bounded freeze implemented; local corrected architecture all PASS/zero violations, frozen PASS, 53 architecture tests PASS, Development recovery PASS, diffcheck PASS. Failed initial metadata/formatting runs are preserved in verification.md/private Recorder. Native authority NOT effective: independent Review/exact-head hosted CI/protected integration/actual-main/main sync PENDING. Clean candidate commit is supplied by Git handoff; review range ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597..candidate includes the separately authorized immutable GUI readiness commits. No GUI runtime/install/migration. Main untouched. Next exact action fresh independent Review then applicable hosted acceptance/integration/safe synchronization; do not selfaccept/done.

## Latest Human unified-batch timing override

Exact Human: 完成GUI任务后统一审查推送. Source: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/unified-batch.md and ADR-0009 localized exception. Explicitly authorizes local GUI preparation against approved local frozen choices before standalone native acceptance; original standalone gate wording above is historical and superseded for this batch only. Native task remains review/pending; no acceptance/done/effectiveness/main sync claimed. Full GUI+freeze receives fresh independent Review/unified push/exact-head hosted CI/protected integration/actual-main/safe sync after GUI completion, including required screenshot/Architect approval. Canceled partial native Review is not PASS.

Additional metadata transition paths authorized only by this latest timing instruction: spec/tasks/ready/LOOP1-CLIENT-GUI-001.md and spec/tasks/active/LOOP1-CLIENT-GUI-001.md. No GUI product scope change. Sole timing writer is /root/native_architecture_freeze; next fresh GUI writer inherits exact unchanged eight assembly paths and native choices. No main/product writes in this followup.


## Latest Human standalone-first order (2026-10-07)

Human selected LOOP1-CLIENT-NATIVE-ARCH-001 and instructed: 先完成这项任务，然后再次尝试Windows验证. Evidence: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/completion-20261007/human-order.md and exact human-order.txt. This supersedes only the preceding unified native/GUI batch acceptance/publication timing: independently complete this authority-only native freeze, protected integration/actual-main audit/safe main synchronization, then retry Windows validation. Existing GUI candidate91598049dfb0bf4360b0ce8bdbc4598606db1407/PR24 remains review, not integrated or accepted. Original approved native choices and canonical a6b1670/PDF546915/v1.1 remain unchanged; no new technical or product authority. Original timing evidence is historical and preserved. Task remains review until applicable independent acceptance and synchronization; S2 remains OPEN.


Fresh local native completion checks: architecture all/frozen PASS, 53 architecture tests PASS. Initial Development FAIL (directory evidence/fullSHA formatting) preserved; corrected metadata Development PASS. Independent committed Acceptance/hosted/main synchronization still pending.


## Independent source Review and publication blocker (2026-10-07)

Independent Review PASS at clean `7dc3e8a3939ec618b4f1618c705b26ff18990a5f`; report/commands/hashes in completion-20261007/independent-review/. Exact hosted publication BLOCKED_EXTERNAL_ACCESS; Git pushes fail reset/connect, API write transports fail integration403/empty500. Full details: spec/progress/evidence/LOOP1-CLIENT-NATIVE-ARCH-001/completion-20261007/publication-blocker.md. No hosted run/main integration/sync/done. Root owns this subsequent evidence-only handoff; do not extend source Review PASS to it. Resume actual publication/independent acceptance/main sync before Windows retry. Last accepted main remains ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597; all unknown main work untouched.

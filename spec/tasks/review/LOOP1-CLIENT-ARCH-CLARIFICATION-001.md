---
task_id: LOOP1-CLIENT-ARCH-CLARIFICATION-001
title: Human-approved v1.1 client technology clarification and selection guards
status: review
owner: Coordinator; fresh independent Review pending
stage: S2
gate: S2
---

# Goal

Complete the separately accepted authority/governance/machine-guard prerequisite to S2 restart. Freeze Human-approved React/TypeScript Web, Tauri/React/TypeScript Desktop, TypeScript Mobile framework TBD, shared TypeScript direction and strict universal Agent technology-selection process. Keep version v1.1, disclose changed canonical bytes/hash and preserve PDF/history. No S2 product code in this task.

# Inputs

- spec/architecture/README.md -> baseline.md -> canonical Frozen Architecture SHA25683d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e; unchanged PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510.
- Canonical sections2,3,6,10 SRC-01 through SRC-07,11,12-15,19-21 and AppendixA/B. Existing ADR0001 expired, ADR0002/0003/0004 historical immutable.
- spec/governance/minimality.md, execution-boundaries.md, independent-review.md; AGENTS.md, agent-context.md, TASK_TEMPLATE.md.
- Full human-approved-request.txt and approval-and-recovery.md in this task evidence directory authorize this specific authority revision; not authority for unspecified dependencies/frameworks. Supplemental exact Human Desktop SQLx(SQLite)/Mobile emulator decision is byte-preserved at spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/human-desktop-sqlx-mobile-emulator-decision.txt (raw-byte SHA25691033f339f337105bc70f45b20c312b8ed2490d01c0b1607e197cda6e09c770b; normalized prompt SHA25678aa2191a4f3614185781a17ebd5204c949312d3a8eb159435af469d0d1929b5).
- ci/check_architecture.py, ci/classify.py, ci/check_gate.py, ci/architecture-checks.md, tools/verify_frozen_architecture.py and tests/architecture + tests/ci.

# Dependencies

- LOOP1-E2E-001 done; S1 PASS accepted actual maina0f0f137 restored by PR8.
- LOOP1-CI-001 done and operational; exact-head real hosted CI mandatory.
- LOOP1-RESEARCH-001 done with Instrumentation Epoch; prospective Recorder mandatory.

# Allowed Paths

- `spec/architecture/frozen-architecture.md`
- `spec/architecture/baseline.md`
- `spec/architecture/README.md`
- `spec/architecture/decisions/ADR-0005-client-technology-clarification.md`
- `AGENTS.md`
- `spec/handoff/agent-context.md`
- `spec/tasks/TASK_TEMPLATE.md`
- `spec/governance/technology-selection.md`
- `spec/governance/execution-boundaries.md`
- `spec/governance/independent-review.md`
- `ci/check_architecture.py`
- `ci/classify.py`
- `ci/architecture-checks.md`
- `.github/workflows/ci.yml`
- `tools/verify_frozen_architecture.py`
- `tests/architecture/**`
- `tests/ci/**`
- `spec/tasks/**/LOOP1-CLIENT-ARCH-CLARIFICATION-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/**`
- `spec/progress/checkpoints/*client-architecture*.md`
- `research/prompts/**`
- `research/runs/**`

allowed_paths does not waive architecture. Coordinator owns approval/recovery copies; new implementation may not rewrite them. External Recorder preferred. No modifications to historical ADR/evidence/Recorder/PDF, clients/, backend/, contracts/, migrations or deployment.

# Acceptance

- Canonical body explicitly captures every Human-approved client rule; v1.1 remains, current hash and revision metadata updated truthfully. New Human-approved ADR records motivation/impact/effectiveness/migration/rollback, PR7 withdrawn deviation, unchanged PDF and previous hash. Old ADR facts unchanged.
- Web memory-only/noSQLite/no offline history over HTTPS/WSS; Desktop Tauri native Rust only clients/desktop/src-tauri, business/repository API/protocol/model/plugin SDK stay TypeScript; Mobile TypeScript ecosystem, concrete framework TBD. No S4 implementation.
- Universal selection governance covers all listed architecture-sensitive categories; missing decision stops affected work BLOCKED_BY_ARCHITECTURE, smallest question -> Human/Architect decision -> frozen body/approved ADR -> independent Review/applicable CI -> product implementation. Task paths/tests/popularity/installed tools cannot authorize selection. Reviewer traces every new sensitive technology to accepted authority.
- Effective guard examines current clients/shared/web/desktop/mobile plus client CI/build configuration; rejects Dart/pubspec/Flutter/setup-dart and unapproved framework/runtime/dependency; source allowlist respects TS ecosystem/config/assets and limited Desktop Rust boundary. Historical archives are not active product and remain preserved. No grep-zero destruction.
- Negative controls prove forbidden sources/config/workflow/dependencies and unapproved new framework proposed in Task or implementation FAIL despite allowed_paths/tests. Positive controls show authorized TS/Tauri/native resources pass. Future authorization only via changed authority/new accepted decision, never task-only allowlist.
- Path-aware classification selects architecture for every client change including deletion plus applicable jobs; current workflow includes effective checking and gate enforcement with no failure suppression. Sourceall/current tests remain mandatory.
- Fresh independent Review of clean exact committed candidate/range, followed by actual applicable exact-head hosted successful required jobs. Missing/failed/cancelled/anomalously skipped jobs cannot PASS. S2 product coding begins only after this task is accepted done; S2 Gate stays OPEN.

# Forbidden

- S1 implementation/public contracts/ACK/Sync invariants/security/compatibility/server schema changes; PDF/old ADR/archive changes; Dart/Flutter restoration; selecting Mobile framework or any native SQLite crate/plugin other than explicitly approved SQLx(SQLite); early Java/S4/Loop2.
- Presenting previous PR7 tests/Review, local or Recorder PASS as this task/new TS/S2 acceptance.

# Minimality

Extend existing architecture verifier/checker/classifier and governance documents directly. No product dependency, general framework or speculative plugin machinery. Negative controls are currently required for the concrete PR7 selection failure.

# Verification

Entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`.

Baseline: pwsh -NoProfile -File tools/verify-frozen-architecture.ps1 PASS34 tests; hashes/tree/audit confirmed in approval-and-recovery.md. Recheck isolated baseline Recovery Development before edits.

- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development; independent clean committed -Mode Acceptance.
- pwsh -NoProfile -File tools/verify-frozen-architecture.ps1
- bundled Python -B ci/check_architecture.py --scope all --json
- bundled Python -B -m unittest discover -s tests/architecture -v
- bundled Python -B -m unittest discover -s tests/ci -v
- git diff --check; hash/tree preservation and current active-client audit.
- Real hosted CI exact candidate: verify selection and each actual required conclusion, not aggregate alone. Full workflow-trigger changes select all jobs.

# Evidence

spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/approval-and-recovery.md
External Coordinator Recorder H:/.codex/evidence/client-architecture-20261001/research/runs/R-CLIENT-ARCH-20261001; incomplete read-only pre-Recorder startup disclosed.

# Handoff

Authority inputs understood; task active, no product implementation. Coordinator initialized and now releases writer to fresh Implementation Agent. Last known good rollback main3f352a8e465c0c4b093cca8e5f404ea587550b6e; S1 PASS/S2 OPEN. Original uncommitted files preserved externally by snapshot; all new edits isolated H:/ica. Existing managed creation failures and startup encoding failures remain exposed in external trace/recovery. No services.

# Next Action

Fresh Implementation Agent completes only authority/governance/guards, records verification, commits review candidate, releases writer. Then NEW independent Review Agent and exact-head hosted CI; no S2 product coding before acceptance.

## Implementation completion (2026-10-01)

Bounded authority/governance/guards completed; local verification above PASS with exposed first Recovery/CI fixture failures repaired. Final architecture42 no skips, CI30 with4 existing Windows privilege skips, sourceall zero violations, frozen/product/hash/diff checks PASS. Durable implementation-local.md and implementation-command-history.json record limitations, exact commands and timings. No product code or Mobile framework choice. Supplemental Human approval freezes Desktop SQLx(SQLite), not product implementation. Last known good rollback main3f352a8e465c0c4b093cca8e5f404ea587550b6e. Isolated writer Implementation Agent owns changed candidate; Coordinator receives clean commit and sole writer release. Next exact action: NEW independent Review of final clean HEAD/range and clean Recovery Acceptance; then actual exact-head hosted CI before done or S2 product activation. S2 OPEN. Checkpoint2026-10-01-client-architecture-review-candidate.md.

Prompt raw-byte vs Recorder LF-normalized hashes are distinguished in spec/progress/evidence/LOOP1-CLIENT-ARCH-CLARIFICATION-001/prompt-hash-normalization.md; original approval/recovery and prompt bytes are preserved.

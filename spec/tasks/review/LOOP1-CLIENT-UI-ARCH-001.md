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
- `spec/progress/current.md`, `spec/progress/evidence/LOOP1-CLIENT-UI-ARCH-001/**`.
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

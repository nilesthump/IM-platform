---
task_id: LOOP1-DB-001
title: Establish canonical database schema and migration runner
status: active
owner: /root
stage: S0
gate: S0
---

# Goal

Create the canonical schema and independent migration runner for users, sessions, friendships, conversations, members, messages, outbox, and plugins.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 5, 7, 8, 9, 11, 17, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved contract set from LOOP1-CONTRACT-001 through LOOP1-CONTRACT-003.

# Dependencies

- LOOP1-CONTRACT-001 done.
- LOOP1-CONTRACT-002 done.
- LOOP1-CONTRACT-003 done.

# Allowed Paths

- `contracts/database/**`
- `contracts/fixtures/**`
- Database migration test locations under `tests/**`
- `spec/tasks/**/LOOP1-DB-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-DB-001/**` (Coordinator-authorized task evidence)
- `spec/progress/checkpoints/*loop1-db-001*.md` (accepted transition only)
- `research/prompts/**` (only Recorder prompts linked to `LOOP1-DB-001`)
- `research/runs/**` (only Recorder runs linked to `LOOP1-DB-001`)

The Coordinator prospectively authorizes these task-linked evidence and Recorder paths to satisfy `AGENTS.md` instrumentation and independent-acceptance requirements. This does not broaden database or product scope.

# Acceptance

- Canonical tables and required uniqueness constraints are represented.
- Migration runner is independent of application startup.
- Uniqueness and forward/rollback migration tests pass.

# Forbidden

- Implement Go or Java business modules.
- Change approved public contracts or database invariants without approved architecture process.
- Add unapproved datastores.

# Verification

- Run `tools/verify-loop1-ctrl-002.ps1 -Mode Development` while editing; use Acceptance only from a clean committed independent review checkout.
- Run schema validation, uniqueness tests, and migration forward/rollback tests.

# Evidence

- Activation Recorder run `R-20260928T155726Z-e6831664-d89d-46e2-b0e6-21753ebb56fe` finished and validated PASS (8 events). The first CTRL-002 Development recovery attempt failed because this Task Spec lacked an architecture resolver reference; after adding it, the same command passed with exit 0. Both results and exact durations are at `spec/progress/evidence/LOOP1-DB-001/2026-09-28-activation-development.md`. This is development recovery, not independent acceptance.
- Dependencies `LOOP1-CONTRACT-001`, `LOOP1-CONTRACT-002`, and `LOOP1-CONTRACT-003` are independently accepted and `done` on clean local `main` at `f25807e`. Contract 003 post-integration Sync/Plugin, WSS, frozen architecture, CTRL-002 Acceptance, and Recorder repository verification passed. S0 Gate remains NOT YET PASSED.

# Handoff

- Coordinator activated the dependency-satisfied task on isolated branch `task/LOOP1-DB-001` from clean local `main` at `f25807e`. Implementation, independent review, and task acceptance remain pending.

# Next Action

- Register task-linked Recorder instrumentation and delegate a fresh Implementation Agent for canonical database schema, standalone migration runner, and deterministic forward/rollback and uniqueness tests within allowed paths. Then request fresh independent review under ADR-0001.

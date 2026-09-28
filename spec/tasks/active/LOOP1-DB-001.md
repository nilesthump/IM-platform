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

- Implementation candidate adds `contracts/database/migrations/0001_initial.{up,down}.sql`, standalone `migrate.py`, database README, and `tests/database/test_migrations.py`. Required primary/unique constraints cover user/client session slots, normalized friendship and DIRECT pairs, non-null GROUP create identity, Conversation members, Conversation request and sequence identities, one `message.created` outbox event per message, and immutable plugin artifact versions. Migration SQL and ledger entry execute in one PostgreSQL transaction under an advisory lock. No application module or public HTTP/WSS/Sync/Plugin contract was changed.
- Development Recorder run `R-20260928T162338Z-5ba36fd3-29c6-48ab-b6b8-3e3aab4fae98`; exact commands/results and PostgreSQL environment limitation are recorded at `spec/progress/evidence/LOOP1-DB-001/2026-09-28-implementation-development.md`. Runtime PostgreSQL schema/uniqueness/forward/rollback verification remains pending because this host has no `psql` and Docker daemon is unavailable. Development checks are not independent acceptance.
- Linked GROUP create idempotency fix Recorder run `R-20260928T163630Z-74cf42e7-07d2-4e40-a86a-cecc67013be1` adds non-null GROUP request identity and negative cases; revised candidate requires fresh independent review.
- Activation Recorder run `R-20260928T155726Z-e6831664-d89d-46e2-b0e6-21753ebb56fe` finished and validated PASS (8 events). The first CTRL-002 Development recovery attempt failed because this Task Spec lacked an architecture resolver reference; after adding it, the same command passed with exit 0. Both results and exact durations are at `spec/progress/evidence/LOOP1-DB-001/2026-09-28-activation-development.md`. This is development recovery, not independent acceptance.
- Dependencies `LOOP1-CONTRACT-001`, `LOOP1-CONTRACT-002`, and `LOOP1-CONTRACT-003` are independently accepted and `done` on clean local `main` at `f25807e`. Contract 003 post-integration Sync/Plugin, WSS, frozen architecture, CTRL-002 Acceptance, and Recorder repository verification passed. S0 Gate remains NOT YET PASSED.

# Handoff

- Coordinator activated the dependency-satisfied task on isolated branch `task/LOOP1-DB-001` from clean local `main` at `f25807e`. Implementation candidate is committed for fresh independent review; runtime PostgreSQL verification and task acceptance remain pending. Last known accepted base is `f25807e`; the implementation commit is a review candidate only. No uncommitted task changes are intended after handoff.

# Next Action

- Fresh independent Review Agent: use a clean committed checkout, run database tests with `DB_TEST_ENABLE=1` against a disposable PostgreSQL database with `psql` available, inspect constraint/rollback behavior, run CTRL-002 Acceptance and Recorder validation, and record exact result under ADR-0001. On FAIL, retain unfinished task and delegate a fresh Fix Agent; on PASS, Coordinator may close acceptance.

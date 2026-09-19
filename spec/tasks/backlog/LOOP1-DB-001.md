---
task_id: LOOP1-DB-001
title: Establish canonical database schema and migration runner
status: backlog
owner: unassigned
stage: S0
gate: S0
---

# Goal

Create the canonical schema and independent migration runner for users, sessions, friendships, conversations, members, messages, outbox, and plugins.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 5, 7, 8, 9, 11, 17, 19 and appendix B.
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

# Acceptance

- Canonical tables and required uniqueness constraints are represented.
- Migration runner is independent of application startup.
- Uniqueness and forward/rollback migration tests pass.

# Forbidden

- Implement Go or Java business modules.
- Change approved public contracts or database invariants without approved architecture process.
- Add unapproved datastores.

# Verification

- Run schema validation, uniqueness tests, and migration forward/rollback tests.

# Evidence

- Pending.

# Handoff

- Unassigned; no changes yet.

# Next Action

- Promote only after all three contract tasks are independently accepted.

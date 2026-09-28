---
task_id: LOOP1-DB-001
title: Establish canonical database schema and migration runner
status: done
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

- Coordinator closure Recorder `R-20260928T174948Z-79f0e8fe-b6ff-4c79-adf0-5e0b873c9a7e` validated PASS (6 events), with `done` queue CTRL-002 Development exit 0. Closure record: `spec/progress/evidence/LOOP1-DB-001/2026-09-29-acceptance-closure.md`.
- Fresh independent Review Agent `/root/db001_review1` accepted exact product candidate `7a677cca7151a2bd06ec9ed78f15ea20ba1e2c6d` under ADR-0001 from a separate clean detached checkout. Actual PostgreSQL 16 forward/uniqueness/rollback tests passed 3/3; independent negative probes covered wrong-Conversation outbox, friendship linkage, destructive-down guard, and failed-migration atomicity. Frozen hashes, allowed scope, Recorder integrity, and clean detached CTRL-002 Acceptance passed. The reviewer did not implement or fix the schema. Evidence: `spec/progress/evidence/LOOP1-DB-001/2026-09-29-independent-review1-7a677cc-pass.md`; review closure `d9162459d9d1261402360ef22fa861fba10de192`; run `R-20260928T173049Z-550c5234-bc12-4f2b-9e57-d9d49f3d19ff`. Task PASS; S0 Gate NOT YET PASSED.
- Fresh independent Review Agent `/root/db001_review1` returned PASS under ADR-0001 on exact implementation `7a677cca7151a2bd06ec9ed78f15ea20ba1e2c6d`. A separate clean detached checkout passed all 3 database tests against disposable PostgreSQL 16, independent negative probes, frozen hashes, and CTRL-002 Acceptance at the committed `review` handoff. Task-level evidence: `spec/progress/evidence/LOOP1-DB-001/2026-09-29-independent-review1-7a677cc-pass.md`; Recorder run `R-20260928T173049Z-550c5234-bc12-4f2b-9e57-d9d49f3d19ff`. No product file changed in review; S0 Gate remains NOT YET PASSED.
- Coordinator's task-linked Recorder run `R-20260928T171255Z-1eb5541f-d2e0-41c8-a583-5b721eb3ff78` finished and validated (8 events). A disposable PostgreSQL 16 execution passed all 3 tests with exit 0; CTRL-002 Development recovered the task in `review` with exit 0. Exact commands, durations, environment, and the pre-run trace limit are at `spec/progress/evidence/LOOP1-DB-001/2026-09-29-review-transition.md`. These are development results, not independent acceptance.
- Coordinator started disposable `postgres:16` container `im-db-001-review` without a published host port and built local `im-db-review-runtime` from cached images to provide Python 3.11 and psql 16 without downloading packages. A pre-Recorder local run of `DB_TEST_ENABLE=1 python3 -m unittest discover -s tests/database -v` passed all 3 tests, including actual PostgreSQL forward/uniqueness/rollback; it is development evidence only. A fresh independent reviewer must repeat the test from a clean committed checkout. Evidence: `spec/progress/evidence/LOOP1-DB-001/2026-09-29-review-transition.md`.
- Implementation candidate adds `contracts/database/migrations/0001_initial.{up,down}.sql`, standalone `migrate.py`, database README, and `tests/database/test_migrations.py`. Required primary/unique constraints cover user/client session slots, normalized friendship and DIRECT pairs, non-null GROUP create identity, Conversation members, Conversation request and sequence identities, one `message.created` outbox event per message, and immutable plugin artifact versions. Migration SQL and ledger entry execute in one PostgreSQL transaction under an advisory lock. No application module or public HTTP/WSS/Sync/Plugin contract was changed.
- Development Recorder run `R-20260928T162338Z-5ba36fd3-29c6-48ab-b6b8-3e3aab4fae98`; exact commands/results and the original PostgreSQL environment limitation are recorded at `spec/progress/evidence/LOOP1-DB-001/2026-09-28-implementation-development.md`. The limitation was resolved with a disposable Docker PostgreSQL 16 environment; fresh independent runtime acceptance is recorded above. Development checks alone were not acceptance.
- Linked GROUP create idempotency fix Recorder run `R-20260928T163630Z-74cf42e7-07d2-4e40-a86a-cecc67013be1` adds non-null GROUP request identity and negative cases; revised candidate requires fresh independent review.
- Activation Recorder run `R-20260928T155726Z-e6831664-d89d-46e2-b0e6-21753ebb56fe` finished and validated PASS (8 events). The first CTRL-002 Development recovery attempt failed because this Task Spec lacked an architecture resolver reference; after adding it, the same command passed with exit 0. Both results and exact durations are at `spec/progress/evidence/LOOP1-DB-001/2026-09-28-activation-development.md`. This is development recovery, not independent acceptance.
- Dependencies `LOOP1-CONTRACT-001`, `LOOP1-CONTRACT-002`, and `LOOP1-CONTRACT-003` are independently accepted and `done` on clean local `main` at `f25807e`. Contract 003 post-integration Sync/Plugin, WSS, frozen architecture, CTRL-002 Acceptance, and Recorder repository verification passed. S0 Gate remains NOT YET PASSED.

# Handoff

- Independent review PASS is ready for Coordinator closure. The detached Acceptance checkout remained clean at handoff `a9c491d3fb6015bbb7ec751f0ca25dd5bba17989`; the reviewed product candidate is `7a677cca7151a2bd06ec9ed78f15ea20ba1e2c6d`. Reviewer owns only task-linked PASS evidence/probe, Task Spec/current recovery, and Recorder artifacts until their closure commit. Last accepted base remains `f25807e` until Coordinator closes DB.
- Coordinator activated the dependency-satisfied task on isolated branch `task/LOOP1-DB-001` from clean local `main` at `f25807e`. Clean implementation candidate `7a677cca7151a2bd06ec9ed78f15ea20ba1e2c6d` is in `review` for fresh independent acceptance. A local PostgreSQL runtime check passed but is not independent acceptance. Last known accepted base is `f25807e`; no product file changed during the review transition.

# Next Action

- Coordinator: integrate the accepted DB closure into clean local `main`, verify post-integration recovery and actual PostgreSQL tests, then activate dependency-satisfied `LOOP1-INFRA-001`. S0 Gate remains NOT YET PASSED.

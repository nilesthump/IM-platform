---
task_id: LOOP1-JAVA-AUTH-001
title: Java Auth and Session equivalence
status: backlog
owner: unassigned
stage: S3
gate: S3
---

# Goal

Implement Java Auth/Session observable parity only after accepted Java authority freeze. This backlog is a planning record; narrow product paths and exact runtime test commands must be resolved before activation.

# Inputs

Canonical §2.3/§3/§6.1/§10 SRC-01..07/§11/§20 resolved/hash-checked through spec/architecture/README.md and baseline.md; accepted ADR-0014 required. spec/domain/auth-user-friend.md, spec/invariants/auth-user-friend.md, spec/acceptance/s0-auth-user-friend.md; contracts/http/auth-user-friend.openapi.json, contracts/websocket/envelope.schema.json, contracts/database/migrations/0001_initial.up.sql and contracts/fixtures/auth-user-friend/. Read all five governance execution/minimality/review/technology/error-handling documents before activation. Go layout is not authority.

# Technology Authorization

Candidate ADR-0014 not effective yet. Approved Human selection must complete independent freeze before implementation. BCrypt-only primitive preserves existing credentials; no new password format, ORM or security authentication framework.

# Dependencies

- LOOP1-S2-GATE-001
- LOOP1-JAVA-ARCH-001
- LOOP1-CONTRACT-001

# Allowed Paths

- spec/tasks/backlog/LOOP1-JAVA-AUTH-001.md

# Error Handling Review

Fresh regular then different fresh specialist review final SHA before CI, repeated after every fix. Unknown errors propagate; no default success or misleading authentication classification.

# Acceptance

Same canonical Auth/Session positive/negative fixtures, three login slots, atomic epoch replacement, auth.bind, revocation-before-close, refresh/logout and no secrets in errors/logs/query. Go-created account authenticates on Java and Java-created account on Go with existing schema/password format. Exact runtime tests and source ownership/import controls, fresh reviews/exact-head hosted CI/protected integration/actual-main/safe sync required. No inferred S3 Gate PASS.

# Forbidden

No implementation before dependencies and narrow paths are complete; no Friend/Message/Sync/Outbox business expansion, no contract/schema/ACK/security changes, no permanent Java placeholder exception.

# Minimality

Use approved Spring stack within Core/Gateway responsibilities and minimal shared primitives; no speculative layers or additional modules.

# Verification

Before activation bind existing ci/check_architecture.py --scope all --json, tests/architecture and same live canonical fixture runner to actual Java role startup and services. Skipped runtime tests never PASS.

# Evidence

spec/progress/evidence/LOOP1-JAVA-ARCH-001/startup.md

# Handoff

Backlog; product untouched. Last known good98e0659673aa8a3bf54fb2a9936a26a5fae7d000. Runtime verification unexecuted, candidate freeze pending. No owned product changes.

# Next Action

After independent freeze acceptance and safe sync, resolve narrow implementation paths and real runtime verification, then ready/active under coordinator.

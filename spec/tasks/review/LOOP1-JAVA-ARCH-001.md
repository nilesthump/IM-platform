---
task_id: LOOP1-JAVA-ARCH-001
title: Freeze Human-approved minimal Java technology
status: review
owner: /root/java_start
stage: S3
gate: S3
---

# Goal

Freeze the Human-approved Java stack and BCrypt-only compatibility supplement before Java Auth implementation. S1/S2 PASS retained; S3 OPEN.

# Inputs

- spec/architecture/README.md and baseline.md resolve canonical frozen-architecture.md; previous SHA256 33b7b2a0a29b555b8c2842383890ae67fc382286b582b4681d2cd78b9f5829ca; §2.3/§3/§6.1/§10 SRC-01..07/§11/§20.
- spec/governance/minimality.md, execution-boundaries.md, independent-review.md, technology-selection.md, error-handling.md; research/README.md.
- spec/progress/evidence/LOOP1-JAVA-ARCH-001/human-approval.txt; ADR-0005 and candidate ADR-0014.
- spec/domain/auth-user-friend.md; spec/invariants/auth-user-friend.md; spec/acceptance/s0-auth-user-friend.md.
- contracts/http/auth-user-friend.openapi.json; contracts/websocket/envelope.schema.json; contracts/database/migrations/0001_initial.up.sql; contracts/fixtures/auth-user-friend/positive.json and negative.json; ADR-0004 scoped friend403 exception remains.

# Technology Authorization

Exact Human approvals in human-approval.txt authorize freezing §3.2 minimal Spring Boot/MVC/WebSocket/JDBC, PostgreSQL JDBC, Jackson, JDK cryptography, BCrypt-only Spring Security Crypto and later IM JNATS. Candidate authority is not effective until independently accepted. No product dependency added.

# Dependencies

- LOOP1-S2-GATE-001 (done; independent final publication seal binds main98e0659673aa8a3bf54fb2a9936a26a5fae7d000).

# Allowed Paths

- spec/tasks/active/LOOP1-JAVA-ARCH-001.md
- spec/tasks/review/LOOP1-JAVA-ARCH-001.md
- spec/tasks/done/LOOP1-JAVA-ARCH-001.md
- spec/tasks/backlog/LOOP1-JAVA-AUTH-001.md
- spec/architecture/frozen-architecture.md
- spec/architecture/baseline.md
- spec/architecture/README.md
- spec/architecture/decisions/ADR-0014-java-technology.md
- ci/check_java_technology.py
- ci/check_architecture.py
- tests/architecture/test_java_technology.py
- spec/progress/current.md
- spec/progress/evidence/LOOP1-JAVA-ARCH-001/**

# Error Handling Review

Fresh regular and different fresh specialist review final SHA before push/CI. Small static checker fails on missing/malformed policy/build input; unknown internal exceptions propagate. No product captures. Inspect exact inventory, retained catches and all changed files; any fix requires two new reviews.

# Acceptance

Approved selections trace through exact Human evidence, ADR, canonical policy/hash and bounded positive/negative controls. Existing Java placeholder passes; unauthorized ORM/security framework and malformed/dynamic declarations fail. No product/contracts delta. Fresh two reviews, exact-head applicable hosted CI, protected integration, actual-main verification and safe main synchronization required. JAVA-AUTH remains backlog until acceptance; Task PASS is not S3 PASS.

# Forbidden

No product, contracts, migrations, CI workflow, runtime/security config, password format changes, main unknown edits, or early Java/IM activation. No rewriting historical evidence.

# Minimality

One authority clause, ADR and a bounded standard-library static guard integrated into existing architecture command. No dependency resolver or build framework. Maven identifiers are a bounded supported inspection surface, not authorization for an alternative runtime. Review still examines actual dependency graph.

# Verification

Control entry point: `tools/verify-loop1-ctrl-002.ps1` (Development; clean committed Acceptance).

Minimum baseline: frozen verifier and ci/check_architecture.py --scope all --json. Final: python -Xutf8 -B tools/verify_frozen_architecture.py; python -Xutf8 -B ci/check_architecture.py --scope all --json; python -Xutf8 -B -m unittest discover -s tests/architecture; python -Xutf8 -B -m unittest discover -s tests/ci; pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development, then clean committed Acceptance. Existing integration services not executed in this authority-only task.

# Evidence

spec/progress/evidence/LOOP1-JAVA-ARCH-001/startup.md. External Recorder R-JAVA-START-20261113 under current visualization research; prospective_resume, startup trace incomplete.

# Handoff

Managed H:/.codex/worktrees/j/IM-platform, branch task/LOOP1-JAVA-ARCH-001; root verified, isolated from unknown main work. Last known good98e0659673aa8a3bf54fb2a9936a26a5fae7d000. Authority and bounded controls complete; local frozen/sourceall/95architecture tests(1skip)/35CI tests(4skips)/Control Development PASS. See verification.md; historical failures retained. Regular/error review, hosted acceptance, integration and main sync PENDING. No acceptance claim.

# Next Action

Fresh regular and different fresh error reviews of final committed candidate before GitHub CI.

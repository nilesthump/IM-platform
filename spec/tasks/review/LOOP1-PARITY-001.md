---
task_id: LOOP1-PARITY-001
title: Golden parity and unchanged client profile switch
status: review
owner: /root/implementation
stage: S3
gate: S3
---

# Goal

Run the same S3 golden checks against Go and Java, and exercise one locked Web client build on each real HTTPS/WSS deployment.

# Inputs

Frozen Architecture via spec/architecture/README.md and baseline.md, §§2.3, 3, 6.1, 10 (SRC-01..07), 11, 12, 15 and 20. Apply ADR-0004, ADR-0007, ADR-0008, ADR-0013 and ADR-0014. Use spec/{domain,invariants}/{auth-user-friend,messaging,group,sync-plugin}.md, spec/acceptance/{s0-auth-user-friend,s0-messaging,s0-sync-plugin,group,client-gui}.md and corresponding canonical HTTP, WSS, migration and fixture families in contracts/. Governance inputs are minimality, execution-boundaries, independent-review, technology-selection, error-handling and research/README.md.

# Technology Authorization

Retain the approved client, Node test runtime, Python test tooling, Compose roles and CI jobs. No new product technologies.

# Dependencies

S1 and S2 PASS. LOOP1-JAVA-AUTH-001 and LOOP1-JAVA-IM-001 are done. PR108 closure integrated at 3a5a54ab and actual-main CI 44872421363 passed.

# Allowed Paths

- tests/e2e/go_tls_messaging.py
- tests/e2e/parity.py
- tests/e2e/parity.mjs
- tests/clients/web/verify.py
- ci/classify.py
- tests/ci/test_classify.py
- tests/ci/test_java_im_job.py
- .github/workflows/ci.yml
- spec/tasks/active/LOOP1-PARITY-001.md
- spec/tasks/review/LOOP1-PARITY-001.md
- spec/tasks/done/LOOP1-PARITY-001.md
- spec/progress/current.md
- spec/progress/evidence/LOOP1-PARITY-001/**
- spec/progress/checkpoints/2026-11-21-parity.md

# Acceptance

Both actual profiles pass the same applicable canonical Auth/Session, Friend/DIRECT, Group idempotency, message/ACK/Outbox/retry, Sync and error/version checks. Identical built client code completes Web login, friend/DIRECT, message delivery, group creation, group send, Sync and logout against both gateways. Real product Web application code and shared SDK own protocol operations. ADR-0004's one deferred case remains explicitly identified. §15/§20 assign live plugin runtime/permission checks to S4, with vectors maintained under §11.3. No visual change. S3 Gate requires its own evidence and checkpoint.

# Forbidden

Do not change product, contracts, schema, architecture or security boundaries. Do not implement plugins, compatibility matrix, release or load testing.

# Minimality

Share the existing Web build and strict TLS fixture startup. Reuse canonical Auth/Group/IM/Sync suites and existing CI selection/required Gate.

# Error Handling Review

Inspect all new runner and test paths and existing paths affected by refactoring. Unexpected errors, failed checks, deadlines and subprocess/cleanup errors must fail. After implementation obtain fresh independent regular review then different fresh error-handling review for exact final SHA, before pushing or triggering CI.

# Verification

Baseline: python -Xutf8 -B ci/check_architecture.py --scope all --json (PASS at 3a5a54ab). Run CI classification tests, architecture checks, the locked Web build and dual-profile TLS parity with real Compose services. Require exact-head hosted CI, protected integration, actual-main CI and verified main synchronization.

# Evidence and Handoff

Both profiles passed the identical Web artifact test, strict TLS message goldens and separate Sync runtime checks. Local commands, results and scope are in spec/progress/evidence/LOOP1-PARITY-001/implementation.md. Branch task/LOOP1-PARITY-001 in H:/.codex/worktrees/p/IM-platform, baseline 3a5a54abff6410762d2039c4acf880abbe3269a5. The implementation writer owns these test and task changes. Regular review and different fresh error audit PENDING on the resulting commit. Next run both reviews, applicable exact-head hosted CI, protected integration, actual-main verification and safe synchronization. S3 remains OPEN.

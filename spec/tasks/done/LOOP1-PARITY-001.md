---
task_id: LOOP1-PARITY-001
title: Golden parity and unchanged client profile switch
status: done
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
- tests/e2e/test_parity_failures.py
- tests/contract/group/test_verification_failures.py
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

Run `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` from a clean committed checkout with Python 3 first on PATH.

# Evidence

The acceptance index `spec/progress/evidence/LOOP1-PARITY-001/acceptance.json` binds the final reviews, candidate CI, actual-main audit and sync receipt. Earlier failed reviews and the failed shared job on d990c045 remain in the same directory.

# Handoff

PR 109 integrated candidate `dfd046dc29e16bf8531723539e5652b34d9e5f65` into main `d91d89ad74f9cb2d97cf5fc9984993d0175049a8`. Fresh independent regular and error-handling reviews both passed on that candidate. Candidate push 44894997629, PR 44895000470 and actual-main 44895739120 each passed all 14 jobs. H:/IM-platform was synchronized. The recovery branch and 782 pre-existing local files were preserved.

The same locked Web application build passed login, DIRECT and GROUP messaging, Sync and logout over HTTPS/WSS against Go and Java. Both profiles passed durable ACK, Outbox, retry, rollback and revocation checks. The accepted artifact digest was `58bc0ef831639eecea2a71fec77db588a5b32a93e13efe05b96aebcb6b017577` for each profile. The Web application ran in Node using its production transports. ADR-0004's single deferred Friend authorization case and the S4 plugin permission checks retain their existing scope. S3 remains OPEN.

The assigned worktree is H:/.codex/worktrees/p/IM-platform on `task/LOOP1-PARITY-001`. The earlier implementation, fixes and reviews are committed. Each Research Recorder run owns its local instrumentation.

acceptance_result: PASS
accepted_candidate_sha: dfd046dc29e16bf8531723539e5652b34d9e5f65
integrated_main_sha: d91d89ad74f9cb2d97cf5fc9984993d0175049a8
main_sync_result: PASS
independent_review_evidence: spec/progress/evidence/LOOP1-PARITY-001/acceptance.json
hosted_acceptance_evidence: spec/progress/evidence/LOOP1-PARITY-001/acceptance.json
main_sync_evidence: spec/progress/evidence/LOOP1-PARITY-001/main-sync.json

# Next Action

Evaluate the S3 Gate separately against the frozen architecture and accepted S3 task evidence.

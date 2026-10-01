---
task_id: LOOP1-GO-SOCIAL-001
title: Implement Go search, friendship, and unique direct conversation
status: active
owner: /root/social_implementation (sole product writer after activation commit)
stage: S1
gate: S1
---

# Goal

Implement Go user search, immediate bidirectional friendship, and unique DIRECT Conversation creation or reuse.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, `spec/acceptance/s0-auth-user-friend.md`.
- Approved ADR-0004-loop1-friend-403-exception.md and canonical contracts/fixtures/auth-user-friend/loop1-exceptions.json (only friend403 deferred).
- Canonical HTTP/error/fixture, database and Sync contracts in `contracts/`.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-AUTH-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

# Allowed Paths

- `backend/go/core/auth.go` (only existing handler friend route registration; preserve search/Auth)
- `backend/go/core/social.go` (private normalized friendship/DIRECT/membership/Sync/Outbox transaction)
- `backend/go/core/social_test.go` (transaction/concurrency/rollback unit integration, no hidden business)
- `backend/go/tests/social_test.go` (public-handler canonical social outcomes using existing test helpers)
- `spec/tasks/**/LOOP1-GO-SOCIAL-001.md`
- `spec/architecture/decisions/ADR-0004-loop1-friend-403-exception.md` (only Human-approved Loop1 applicability exception; preserve frozen body/hash and prior ADRs)
- `contracts/fixtures/auth-user-friend/loop1-exceptions.json` (only stage applicability for friend-add-authorization-denied; OpenAPI and golden fixture unchanged)
- `spec/acceptance/s0-auth-user-friend.md` (only reference to approved Loop1 exception)
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-SOCIAL-001/**`
- `spec/progress/checkpoints/*loop1-go-social-001*.md`
- `research/prompts/**` and `research/runs/**` only this Task-linked Recorder artifacts.

Human2026-10-01 prospectively authorizes exact layout binding. Core/auth.go already owns handler/Auth/search; Core/http.go merely assembles it and needs no duplicate router. Existing Core/outbox.go Session dispatcher remains unchanged; Social transaction writes use canonical existing tables, no new generic dispatcher/service in shared or Gateway. No language-wide migration scope remains.

# Acceptance

- Search and friend operations match canonical HTTP/errors and stage applicability, with only Human-approved Loop1 friend403 exception under ADR-0004/loop1-exceptions.json. OpenAPI403 remains a future placeholder.
- Concurrent A-to-B and B-to-A add converges on one normalized friendship and one DIRECT Conversation, with both memberships, Sync events, and Outbox effects in one atomic transaction.
- Immediate bidirectional friendship is observable; no pending approval flow is exposed.
- All required applicable integration/canonical fixture checks pass; explicitly report friend-add-authorization-denied DEFERRED_BY_HUMAN separately, not PASS. Fresh independent review and applicable real CI accept the candidate.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Change public contracts or database invariants; add approval flow, messaging implementation, Java/client behavior, or speculative infrastructure.

# Minimality

Use the canonical uniqueness constraints and one direct transaction path; no extra social workflow or persistence model.

# Verification

- Entry points `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`: `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` during edits, Acceptance only clean committed candidate; `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`.
- Bundled Python3 -B `ci/check_architecture.py --scope all --json`; `python -B -m unittest discover -s tests/ci -v`; checker controls via frozen verifier/tests/architecture.
- With unique migrated disposable PostgreSQL16/NATS2.10 and DB_TEST_ENABLE=1/connection env, recursive gofmt/build/vet and `go -C backend/go test -count=1 ./...`, `go -C backend/go test -race -count=1 ./...`; actual live canonical social/auth, concurrent reversed pair, memberships/Sync/Outbox atomicity and rollback, auth/WSS/fallback regressions. No existing/production services or volumes modified. Loop1 friend-add-authorization-denied is an explicit Human-approved stage exception, report DEFERRED_BY_HUMAN (notPASS/environment skip); other applicable canonical cases must execute.
- Current accepted base279c1dc/main36764254107 all13SUCCESS; source/frozen/recovery and old accepted product coverage documented in integration evidence. Fresh implementation and independent Review/hostedCI after executable inputs, never old-head substitution.

# Evidence

Recovery/old-to-current file map: `spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-recovery-path-map.md`. Old implementation2a6eaa1/handoff5b35735 remains preserved, not independent accepted; current restoration contains no Social product yet.

# Handoff

Accepted main279c1dc and oldSocial2a6eaa1/5b35735 are preserved; no Social product transplanted. Old blocked403 finding remains historical. Human now explicitly approves a Loop1 exception while retaining OpenAPI placeholder under ADR-0004/canonical loop1-exceptions.json. Later workFRIEND-AUTHORIZATION-403 remains unimplemented. Bounded propagation independently accepted atf8d1a28/CI36807927903. Dependencies/readiness rechecked; task promoted backlog->ready->active for fresh /root/social_implementation. No productTaskPASS.

# Next Action

Fresh /root/social_implementation implements exact mapped Core/test scope after committedactivation; allrequired canonical/race/concurrency/rollback/atomicity/Authregressions, candidatecommit/newIndependentReview/realCI. Scopepropagation already accepted; see2026-10-01-social-activation.md. Do not invent restricted token or count deferred403PASS. No Message/E2E/Java/client/plugin/S2 or automatic Social PR merge.

# Last Known Good Commit

Actual main279c1dc4681683e2af3b3534a00e5222dde36be6. Old unaccepted Social2a6eaa167f90e32d69ee309fe373fd28e0ff3451/handoff5b35735ae6625b82c0de78d7bd64fdb9bd7e1123.

# Human-approved deferred work (2026-10-01)

Exact Human instruction: 明确loop1不实现403，记录为后续迭代待实现内容

Loop1 restricted-principal friend403 is DEFERRED_BY_HUMAN; later-iteration item FRIEND-AUTHORIZATION-403 is recorded in spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-human-403-deferral.md. No implementation or PASS is claimed. This records the discussed friendPUT case only; other-domain authorization remains required. DB/JWT permission model is unchanged.

Historical approval review blocked the broader proposal at2560dd5. Subsequent explicit Human instruction preserves OpenAPI and approves a Loop1 special case; bounded ADR/applicability/acceptance propagation now uses the prospectively bound paths. Original report/deferral record remains history. No silent waiver or deferred-casePASS.

# Additional explicit Human authorization (2026-10-01)

Exact instruction: 保留openapi占位，记为loop1特例. This approves the discussed friend403 Loop1 exception while retaining the OpenAPI placeholder. Before edits, exact additional ADR/applicability/acceptance paths above are bound for propagation; all other paths/requirements remain unchanged. No permission model, wire response, fixture expectation or database changes are authorized.

# Activation evidence

2026-10-01-social-activation.md binds acceptedexception subject/Review/CI, S0/Auth/remediation/integration dependencies, ownership and backlog->ready->active transitions. Implementation must preserve stageprofile and reportdeferrednotPASS; no selfreviewdone.

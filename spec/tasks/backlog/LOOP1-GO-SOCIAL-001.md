---
task_id: LOOP1-GO-SOCIAL-001
title: Implement Go search, friendship, and unique direct conversation
status: backlog
owner: /root Coordinator (recovery; no product writer)
stage: S1
gate: S1
---

# Goal

Implement Go user search, immediate bidirectional friendship, and unique DIRECT Conversation creation or reuse.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, `spec/acceptance/s0-auth-user-friend.md`.
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
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-SOCIAL-001/**`
- `spec/progress/checkpoints/*loop1-go-social-001*.md`
- `research/prompts/**` and `research/runs/**` only this Task-linked Recorder artifacts.

Human2026-10-01 prospectively authorizes exact layout binding. Core/auth.go already owns handler/Auth/search; Core/http.go merely assembles it and needs no duplicate router. Existing Core/outbox.go Session dispatcher remains unchanged; Social transaction writes use canonical existing tables, no new generic dispatcher/service in shared or Gateway. No language-wide migration scope remains.

# Acceptance

- Search and friend operations match canonical HTTP/errors and authorization.
- Concurrent A-to-B and B-to-A add converges on one normalized friendship and one DIRECT Conversation, with both memberships, Sync events, and Outbox effects in one atomic transaction.
- Immediate bidirectional friendship is observable; no pending approval flow is exposed.
- Integration and canonical fixture checks pass; fresh independent review and applicable real CI accept the candidate.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Change public contracts or database invariants; add approval flow, messaging implementation, Java/client behavior, or speculative infrastructure.

# Minimality

Use the canonical uniqueness constraints and one direct transaction path; no extra social workflow or persistence model.

# Verification

- Entry points `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`: `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` during edits, Acceptance only clean committed candidate; `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`.
- Bundled Python3 -B `ci/check_architecture.py --scope all --json`; `python -B -m unittest discover -s tests/ci -v`; checker controls via frozen verifier/tests/architecture.
- With unique migrated disposable PostgreSQL16/NATS2.10 and DB_TEST_ENABLE=1/connection env, recursive gofmt/build/vet and `go -C backend/go test -count=1 ./...`, `go -C backend/go test -race -count=1 ./...`; actual live canonical social/auth, concurrent reversed pair, memberships/Sync/Outbox atomicity and rollback, auth/WSS/fallback regressions. No existing/production services or volumes modified. Unconstructible/skipped403 is not fixturePASS.
- Current accepted base279c1dc/main36764254107 all13SUCCESS; source/frozen/recovery and old accepted product coverage documented in integration evidence. Fresh implementation and independent Review/hostedCI after executable inputs, never old-head substitution.

# Evidence

Recovery/old-to-current file map: `spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-recovery-path-map.md`. Old implementation2a6eaa1/handoff5b35735 remains preserved, not independent accepted; current restoration contains no Social product yet.

# Handoff

S0PASS/Authdone/remediationPASS/integrationdone dependencies verified; new clean restoration branch task/LOOP1-GO-SOCIAL-001-v1.1 from actualaccepted merge279c1dc. Old Social clean5b35735 intentionally paused and no active writer observed. Do not merge old AGENTS/current/task/package-main structure. Current Task remains backlog because required acceptance input is not executable: friend-add-authorization-denied presupposes insufficient-scope authenticated principal, absent from current six-claim JWT/implicit-caller PUT ownership. Fresh independent context confirms BLOCKED_BY_ARCHITECTURE; report and blocked-handoff archived under Social evidence. Recovery01765 cleanAcceptancePASS/CI36765878057 all13SUCCESS; no Social TaskPASS. Coordinator does not invent model or waive fixture.

# Next Action

Human has chosen later-iteration deferral for friend403; record is complete. Next obtain explicit approval for bounded public-contract applicability synchronization described in2026-10-01-human-403-deferral.md (automatic approval review rejected the broader amendment). No need to invent a Loop1 restricted credential. Public machine applicability is still unresolved; no contract/architecture changes performed. Only after approved constructible inputs complete backlog->ready->active and delegate fresh mapped Implementation, fresh Review/real hostedCI. No Message/E2E/Java/client/plugin/S2 and no automatic Social PR merge.

# Last Known Good Commit

Actual main279c1dc4681683e2af3b3534a00e5222dde36be6. Old unaccepted Social2a6eaa167f90e32d69ee309fe373fd28e0ff3451/handoff5b35735ae6625b82c0de78d7bd64fdb9bd7e1123.

# Human-approved deferred work (2026-10-01)

Exact Human instruction: 明确loop1不实现403，记录为后续迭代待实现内容

Loop1 restricted-principal friend403 is DEFERRED_BY_HUMAN; later-iteration item FRIEND-AUTHORIZATION-403 is recorded in spec/progress/evidence/LOOP1-GO-SOCIAL-001/2026-10-01-human-403-deferral.md. No implementation or PASS is claimed. This records the discussed friendPUT case only; other-domain authorization remains required. DB/JWT permission model is unchanged.

Public-contract applicability propagation was blocked by automatic approval review; canonical OpenAPI/negative fixture/architecture/acceptance remain unchanged. Before ready/active obtain explicit approval for the concrete minimal synchronization proposal in the decision record, then independently verify propagation. Historical blocked finding and evidence remain intact; no fixture waiver is silently applied.

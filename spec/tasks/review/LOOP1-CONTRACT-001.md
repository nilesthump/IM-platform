---
task_id: LOOP1-CONTRACT-001
title: Freeze HTTP Auth, User, and Friend contracts
status: review
owner: unassigned-fresh-fix-agent
stage: S0
gate: S0
---

# Goal

Define the canonical HTTP Auth/User/Friend OpenAPI contract, shared errors, and positive and negative golden fixtures.

# Inputs

- Architecture Baseline v1.0 chapters 2, 4, 7, 11, 19 and appendix B, resolved through `spec/architecture/README.md`.
- Approved ADRs/frozen decisions in `spec/architecture/decisions/`.
- `spec/domain/auth-user-friend.md`
- `spec/invariants/auth-user-friend.md`
- `spec/acceptance/s0-auth-user-friend.md`

# Dependencies

- LOOP1-CTRL-002 done.
- LOOP1-SPEC-001 done.

# Allowed Paths

- `contracts/http/**`
- `contracts/errors/**`
- `contracts/fixtures/**`
- `spec/domain/**`
- `spec/invariants/**`
- `spec/acceptance/**`
- `spec/tasks/**/LOOP1-CONTRACT-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-CONTRACT-001/**`

The Coordinator explicitly authorized the exact evidence path above on 2026-09-20 to satisfy repository-level durable-evidence governance. This prospective authorization does not erase the independent review's permanent finding that implementation commit `acfe36c2040e749ee508485ee8b577dc76604961` had previously self-expanded the write boundary.

# Acceptance

- Canonical OpenAPI and error contracts exist for Auth/User/Friend.
- Schema lint passes and positive/negative fixtures are complete.

# Forbidden

- Implement either backend.
- Invent semantics that conflict with Frozen Architecture.
- Change WSS, Sync, Plugin API, ACK, or compatibility semantics outside this task.

# Verification

- While editing, run `& .\tools\verify-loop1-ctrl-002.ps1 -Mode Development`; run default Acceptance mode only from a clean committed review checkout.
- Run schema lint and all positive/negative fixture checks defined by this task.

# Evidence

- Dependency `LOOP1-CTRL-002` is `done` with independent acceptance evidence at `spec/progress/evidence/LOOP1-CTRL-002/2026-09-20-independent-review-d86bf17-pass.md`.
- Dependency `LOOP1-SPEC-001` is `done` with independent acceptance evidence at `spec/progress/evidence/LOOP1-SPEC-001/2026-09-20-independent-review-aef6497-pass.md`.
- Required inputs `spec/domain/auth-user-friend.md`, `spec/invariants/auth-user-friend.md`, and `spec/acceptance/s0-auth-user-friend.md` are present and were independently accepted as part of reviewed commit `aef6497d6216d9a8251250d157935e7af418d86b`.
- Activated from local `main` closure commit `e5482b135a2ab7451c24c29c7517e1a8f19ce420` on dedicated branch `task/LOOP1-CONTRACT-001` after dependency and input validation.
- Implementation commit: `acfe36c2040e749ee508485ee8b577dc76604961`.
- Metadata recovery verified the object chain `e5482b135a2ab7451c24c29c7517e1a8f19ce420` -> `47d97b9b81c522c6a1331d8d83c50e4ad5c9a272` -> `acfe36c2040e749ee508485ee8b577dc76604961` -> `7ce56ff59c1cd6cc3c83d2d040911f2e1fba7e5b` and corrected the previously recorded nonexistent implementation SHA.
- Development evidence: `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-20-development-acfe36c-pass.md`.
- Metadata correction evidence: `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-20-metadata-sha-correction.md`.
- The task verifier passed on the clean committed implementation with 8 paths, 8 operations, 15 stable error codes, 5 positive fixtures, and 12 negative fixtures for both `go` and `java` profiles.
- `LOOP1-CTRL-002` passed in explicitly non-acceptance Development mode; `git diff --check main..HEAD` passed.
- After the metadata correction, the task verifier passed with exit `0` in `257.0893 ms`, CTRL-002 Development mode passed with exit `0` in `527.3556 ms`, and `git diff --check e5482b135a2ab7451c24c29c7517e1a8f19ce420..HEAD` passed with exit `0` in `56.2614 ms`; these remain development evidence only.
- Fresh independent Review Agent `/root/contract001_review` reviewed `1c2637cb253dc6eece0393c229fe77cd5934160e` from a clean detached isolated worktree and returned FAIL. Permanent evidence is `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-20-independent-review-1c2637c-fail.md`.
- The FAIL identified contradictory/non-validated bodies, an undeclared 403 fixture, unrestricted operation/status error codes and six missing shared-code cases, credentialless refresh, and the prior hard write-boundary violation.
- Fix commit: `12c566f71da9b038764ecb7a5303b116e77ca32f`.
- The repair defines 9 Auth/User/Friend paths and operations, retains all 15 stable shared errors, upgrades fixtures to version `1.1` with 6 positive and 21 negative scenarios, and covers every shared error code.
- The repaired verifier passed from the clean committed fix with exit `0` in `5280.2464 ms`; it validates fixture request/response bodies and statuses against OpenAPI, enforces operation/status error-code bindings, proves Go/Java normalized parity, and runs six mutation regressions.
- CTRL-002 Development mode passed from the clean committed fix with exit `0` in `402.055 ms`; baseline diff check from `e5482b135a2ab7451c24c29c7517e1a8f19ce420` passed with exit `0` in `40.6779 ms`. These are development evidence only at `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-20-fix-12c566f-pass.md`.
- Fresh independent Review Agent `/root/contract001_resume_review` reviewed candidate `12c566f71da9b038764ecb7a5303b116e77ca32f` from clean detached checkout `H:\.codex\worktrees\contract001-independent-review-resume-b5e568c3\IM-platform` under ADR-0001 and returned FAIL.
- The contract verifier passed on the unmodified candidate, but a disposable negative control removed OpenAPI 3.1-required `info.title` and the verifier still returned PASS, exit `0`, in `5981.2862 ms`. The required schema-lint acceptance is therefore not independently established.
- Permanent evidence: `spec/progress/evidence/LOOP1-CONTRACT-001/2026-09-21-independent-review-12c566f-fail.md`. Recorder run: `R-20260921T080248Z-b5e568c3-afdd-4f81-8ef7-5c3d236e16f4`.

# Handoff

- The original implementation at `acfe36c2040e749ee508485ee8b577dc76604961` and repaired candidate `12c566f71da9b038764ecb7a5303b116e77ca32f` both failed independent review; the latter now requires a fresh Fix Agent before another independent review.
- Canonical deliverables are `contracts/http/auth-user-friend.openapi.json`, `contracts/errors/http-errors.schema.json`, dual-profile golden fixtures under `contracts/fixtures/auth-user-friend/`, and deterministic verifier `contracts/http/verify-auth-user-friend.ps1`.
- The contract fixes wire-level endpoint and schema choices while preserving the frozen session slot/epoch, refresh-token hashing and revocation, token transport, normalized friendship, unique DIRECT conversation, two-member atomic transaction, immediate friendship, authorization, and error semantics. WEB cookie refresh and native body refresh are separate operations so a credentialless refresh is not representable.
- Fixture bodies now use exact nested `session`/`tokens`, `normalizedPair`, and `memberUserIds` structures. Every expected result contains canonical, Go-normalized, and Java-normalized observables that the verifier compares semantically.
- Each declared error response carries an enforced operation/status-specific `x-error-codes` set; negative fixtures exercise all 15 shared codes.
- No backend, WSS envelope/message schema, Sync, Plugin API, database schema, or frozen architecture was changed.
- The independent FAIL and the original hard process violation remain permanent evidence even though the Coordinator prospectively authorized this task's exact durable-evidence path for the repair cycle.
- The resumed independent review failed because the committed verifier is not an OpenAPI 3.1 structural schema lint: it accepted a document missing required `info.title`. The semantic contract checks otherwise passed, but that does not satisfy the explicit schema-lint acceptance item.
- A fresh Fix Agent must add a deterministic, repository-contained OpenAPI 3.1 schema lint (without relying on the paused Agent-owned untracked `contracts/http/schema-lint/` tree), preserve all existing semantics and fixtures, and commit the repair before a new fresh independent review.

# Next Action

- Delegate to a fresh Fix Agent. It must implement deterministic OpenAPI 3.1 structural schema lint and a regression proving a missing required `info.title` is rejected, without reading, copying, modifying, claiming, or depending on the paused Agent-owned untracked `contracts/http/schema-lint/` tree. Then delegate the committed repair to a new fresh independent Review Agent; no fixer may accept its own work.

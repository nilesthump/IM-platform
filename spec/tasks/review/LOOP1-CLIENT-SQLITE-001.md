---
task_id: LOOP1-CLIENT-SQLITE-001
title: Native client account SQLite repository and transactional convergence
status: review
owner: /root/sqlite_event_identity_fix
stage: S2
gate: S2
---

# Goal

Deliver an actual reusable native Dart SQLite storage foundation consumed by Desktop and Mobile storage packages. Local send, committed ACK, realtime and Sync converge transactionally on one logical row. This is storage foundation, not full UI, network send orchestration or S2 Gate completion.

# Inputs

- spec/architecture/README.md and baseline.md: canonical frozen-architecture.md SHA256 83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e; PDF provenance 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510.
- Canonical sections 3, 4.4, 6, 7.4, 10 SRC-01 through SRC-07, 11, 12-15, 19 and Appendix A/B. ADR-0001 expired; approved ADR-0002/0003/0004 unchanged.
- spec/governance/minimality.md, execution-boundaries.md and independent-review.md.
- spec/domain/messaging.md and sync-plugin.md; spec/invariants/messaging.md and sync-plugin.md; spec/acceptance/s0-messaging.md and s0-sync-plugin.md (applicable SQLite behavior only).
- contracts/websocket/envelope.schema.json and sync-v1.schema.json; contracts/fixtures/websocket/golden.json and contracts/fixtures/sync-plugin/golden.json; contracts/plugin-api/verify.py only as existing canonical oracle, never product implementation dependency.
- Accepted S1 actual main a0f0f13759ffb2a861b08c4820a1504b76d5c08a, product6346/PR5 acceptance and final PR6 actual-main independent proof. Existing brand/recovery records copied byte-for-byte; no logo changes.
- Human approve in response to entering S2 and implementing first dependency-satisfied task. Native Dart selected because current Desktop/Mobile share the same required SQLite rules and installed Dart3.12.2 exists; sqlite3 native library is one required direct dependency, no ORM/framework UI choice. Official reference https://pub.dev/documentation/sqlite3/latest/index.html.

# Dependencies

- LOOP1-E2E-001 done with S1 Gate PASS and final actual-main independent acceptance.
- LOOP1-CONTRACT-002 and LOOP1-CONTRACT-003 done with canonical WSS/Sync fixtures.
- LOOP1-CI-001 done; exact-head real hosted CI mandatory.

# Allowed Paths

- `clients/shared/local-store/**` (one native Dart package: private local schema/migration, account-bound repository, actual SQLite tests, package build/lock/ignore/README; no UI/transport/plugin runtime).
- `clients/desktop/storage/**` (thin native Dart consumer package and account-storage integration tests only).
- `clients/mobile/storage/**` (thin native Dart consumer package and account-storage integration tests only).
- `.github/workflows/ci.yml` (replace existing desktop/mobile S0 steps and their compatibility invocations with actual native Dart SQLite unit/migration/protocol tests; retain every other job/selection/Gate; setup Dart pinned compatible SDK).
- `tests/ci/test_s0_boundary.py` (actual-repository assertion recognizes desktop/mobile transition to real CI; preserve synthetic S0 rejection/symlink negative controls for all profiles).
- `spec/tasks/**/LOOP1-CLIENT-SQLITE-001.md`
- `spec/progress/current.md`
- `spec/tasks/done/LOOP1-E2E-001.md` and `spec/progress/evidence/LOOP1-E2E-001/2026-10-01-brand-baseline/**`, `spec/progress/evidence/LOOP1-E2E-001/2026-10-01-resume-scope.md` (Coordinator byte-preserved preexisting recovery/brand copy only; Implementation must not edit them).
- `spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/**`
- `spec/progress/checkpoints/*loop1-client-sqlite-001*.md`
- `research/prompts/**` and `research/runs/**` for this task only; external Recorder preferred.

The shared local-store path names a current responsibility shared by two actual consumers. Local SQLite tables are private client implementation, not public PostgreSQL/schema authority. No contracts/ changes. allowed_paths never exempts architecture.

# Acceptance

- Real native SQLite persists per-account stores; reopen retains rows, different account stores are isolated and mismatched account reuse is rejected. No tokens/credentials in SQLite or logs.
- UNIQUE(conversation_id, request_id), partial UNIQUE(server_message_id) and partial UNIQUE(conversation_id, server_seq) enforce canonical identities.
- Local send, matching committed ACK, realtime and Sync all use the same transactional convergence mechanism; duplicate/interleaved inputs converge to one row, conflicts roll back without changing prior data. ACK cannot confirm an unrelated missing local send or uncommitted status.
- FAILED matching server message becomes SENT; later local failure cannot regress SENT. Storage transitions only; scheduling, retry request generation and network transport remain later SEND task.
- Data plus cursor/contiguous prefix advance commit atomically. Gap/duplicate/out-of-order cases and fault before commit execute against real SQLite using unchanged canonical expected values. Persistence operations needed here do not implement Sync network orchestration.
- Initial version creation/migration/reopen/failure fixtures are genuine; no fabricated old client versions or unsupported complete compatibility claim. Unknown future schema is rejected without destructive downgrade.
- Desktop/Mobile consumer tests exercise actual shared repository; CI executes native SQLite tests/analyze/migration/protocol vectors. Applicable sourceall and architecture tests PASS; Java remains explicit S0 placeholder.
- Fresh independent Review checks exact committed candidate/range, actual storage behavior/imports/minimality; applicable exact-head hosted required jobs SUCCESS before done. Local or Recorder PASS is not Task/Gate PASS.

# Forbidden

- Frozen/ADR/public contract/server migration/backend/security/ACK/compatibility-rule changes.
- Web history or SQLite, UI app scaffolds, plugin implementation, token storage, new network route, backend repair, future Java/business infrastructure.
- Mock SQLite or canonical-oracle-only tests presented as runtime evidence; rewriting fixtures to fit implementation; invented prior schema/protocol versions; self-acceptance.

# Minimality

One direct sqlite3-backed repository and SQL transactions serve both native consumers; no ORM, generic storage strategy, message bus, code generator or extra framework. The account metadata binding is required by section6.1 isolation. Unique indexes/atomic local data and cursor are required by section6.3. Initial schema version marker is needed for genuine migration/reopen and future-version rejection. Package ignores/locks only bound generated build files and repeatable dependency resolution.

# Verification

- Discoverable entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`.

Minimum pre-edit baseline already observed at accepted HEAD: Recovery Development PASS; frozen verifier34 PASS; contracts/websocket/verify.py PASS; contracts/plugin-api/verify.py PASS; Dart SDK3.12.2; clean isolated checkout. Implementation rechecks current governance/source before edits.

- `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` while editing; clean committed `-Mode Acceptance` for independent candidate.
- `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`
- bundled Python `-B ci/check_architecture.py --scope all --json`; `-B -m unittest discover -s tests/architecture -v`; `-B -m unittest discover -s tests/ci -v`.
- bundled Python `-B contracts/websocket/verify.py`; `-B contracts/plugin-api/verify.py` (unchanged oracle).
- In each clients/shared/local-store, clients/desktop/storage, clients/mobile/storage: `dart pub get`, `dart analyze`, `dart test`; shared `dart format --output=none --set-exit-if-changed lib test` and consumers same format check. Tests must load real native SQLite and consume canonical fixture file path from repository.
- Independent native runtime on clean candidate must execute migration/rollback/account separation and all four entrypoint convergence; Windows native execution plus hosted Linux required checks. No mobile-device/UI or S2 full acceptance claim from host Dart tests.
- CI changes select full existing matrix, so all13 required jobs must complete SUCCESS; live Go/deploy tests remain enabled. Native dependencies/availability failure remains visible; do not bypass build hooks or skip required checks.

# Evidence

- 2026-10-01-activation.md records scope/approval/readiness and exact runtime/baselines. External Coordinator Recorder H:/.codex/evidence/s2-authorized-20261001-01/research/R-S2-AUTHORIZED-20261001-01; actual path runs/R-S2-AUTHORIZED-20261001-01.
- Previous recovery record retained byte-for-byte as 2026-10-01-prior-recovery-current.md. Preparation was read-only incomplete pre-Recorder; never independent acceptance.

# Handoff

Coordinator sole writer for bounded activation until committed; then fresh s2_sqlite_preparation sole Implementation writer in isolated H:/.codex/worktrees/s2-client-sqlite/IM-platform. Original H:/IM-platform unknown untracked files untouched. Last known good commit a0f0f13759ffb2a861b08c4820a1504b76d5c08a. S1 PASS, S2 OPEN. No services/migrations/product edits yet; no architecture conflict. Independent acceptance pending. Brand and prior recovery copying is Coordinator administrative preparation only; implementation scope does not edit E2E/brand history.

# Next Action

Commit bounded activation, release sole Implementation writer with Recorder, implement storage foundation and complete local verification; then fresh independent Review and exact candidate hosted CI before done. Do not advance to another S2 task before this task is accepted.

# Development implementation handoff (2026-10-01)

Implementation base: `5613aab`, branch `task/LOOP1-CLIENT-SQLITE-001`, isolated checkout `H:/.codex/worktrees/s2-client-sqlite/IM-platform`. Implementation writer: fresh `/root/s2_sqlite_preparation`; independent review has not occurred. Local results do not accept Task or S2 Gate.

Actual native Dart sqlite3 3.7.0 hook loaded on Windows. One account-bound private schema1/repository and two thin native storage consumers implement required uniqueness, transactional local/committed ACK/realtime/Sync convergence, immutable identity rejection, SENT terminal state, persisted gap-free prefixes and atomic user state/cursor. Initial empty-version0 migration is genuine; no fictitious legacy schema/device acceptance. No token, UI, transport, backend or public authority changes. Current native CI replaces retired Desktop/Mobile skeleton calls including compatibility; classifier and all remaining jobs are retained.

Final commands: in all three packages `dart pub get --enforce-lockfile`, `dart format --output=none --set-exit-if-changed lib test`, `dart analyze --fatal-infos`, `dart test`: all exit0, 0 format changes/issues; shared24 + Desktop1 + Mobile1 actual native tests. Shared suite replays13 unchanged canonical storage cases/timelines; WSS fixtures supply four-entrance data and ACK expectations. Trigger-based actual rollback probes execute between data write and cursor update.

Architecture34, CI29, frozen34, sourceall, WSS18 (18schema/26behavior mutations), Sync79 (16mutations) all exit0/PASS. CI suite has exactly4 Windows symlink privilege skips, retained synthetic negative controls; hosted Linux must execute them. Final Recovery Development PASS in unique review state. Exact argv/duration/exit/output hashes are in command-results.json; own external Recorder retains raw outputs.

Failures retained: initial prompt registration associated a not-yet-existing run and printed exit2; prompt persisted, start succeeded and warning recorded without trace edits. First pub get exit1 ran at repository root because Recorder forces cwd; corrected recorded package-directory invocation passed. Initial analyze exit0 reported8 deprecated dispose infos; corrected current close API, final strict analyze0issues. Preparation constrained-language/optional missing-path failures are incomplete pre-Recorder reads. Recorder finishes FAIL for its initialization failure; structural validation recorded separately. Final recovery twice failed because the evidence field combined an additional filename, then retained trailing punctuation; corrected exact standalone link passes. All three command outcomes are retained. No hidden product test failure.

No services launched; tests close native connections and delete only their own temporary directories. Generated Dart files remain package-ignored; locks committed. Original H:/IM-platform and unknown611-file snapshot untouched. Historical FAIL/partial/brand/E2E records unchanged.

Next exact action: NEW independent clean committed Review of implementation5613aab..candidate and full accepted-main a0f0f137..candidate, actual SQLite/native/import/minimality checks; applicable exact-head hosted all13 required jobs SUCCESS before done. Mobile host tests are not device/UI acceptance. No later S2 task is authorized. Last accepted main a0f0f137; S1 PASS/S2 OPEN; no architecture conflict.

Recorder finished FAIL65events for initialization error; structural validation PASS. External raw artifacts remain immutable. Post-finish ledger/outcome archival, staging/commit/status are outside the finished trace, explicitly disclosed; no post-finish event stream append.

# Independent Review FAIL and fresh Fix (2026-10-01)

Exact d792 independent /root/sqlite_independent_review FAIL P2 eventId discarded in applyUserPage; canonical oracle rejects same-ID changed payload, actual repository accepted and advanced state/cursor. Full durable byte-preserved report under spec/progress/evidence/LOOP1-CLIENT-SQLITE-001/2026-10-01-independent-review-d792-fail/. Hosted d792 push/PR each13SUCCESS does not override FAIL. Fresh /root/sqlite_event_identity_fix now owns bounded repair after explicit release; task remains review, no selfacceptance. Minimal persistence/checking of existing user-event identity and known payload fields inside same data/cursor transaction is presently justified by concrete canonical discrepancy; identical replay, conflicts within/across pages/reopen and rollback must be verified without oracle edits. Last accepted a0f0f137; no services or architecture conflict. Next action fix/commit/release, then NEW independent Reviewer and exact-head selected hosted jobs.

---
task_id: LOOP1-GO-MSG-001
title: Implement Go text messaging, durable ACK, Outbox, and NATS
status: review
owner: /root/message_fix (new Fix writer after Coordinator handoff)
stage: S1
gate: S1
---

# Goal

Implement one logical text Message per authorized send with Conversation sequence, durable ACK, idempotent retry, Outbox dispatch, and realtime NATS delivery.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- `spec/domain/messaging.md`, `spec/invariants/messaging.md`, `spec/acceptance/s0-messaging.md`.
- Canonical WSS/error/fixture, Sync and database contracts in `contracts/`.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-SOCIAL-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

# Allowed Paths

- `backend/go/core/message.go` (private canonical text write transaction/internal send adapter)
- `backend/go/core/message_test.go` (atomicity/idempotency/ACK/authorization fault tests)
- `backend/go/core/http.go` (only existing Core assembly/private adapter registration)
- `backend/go/core/outbox.go` (message-created dispatch, existing Session behavior preserved)
- `backend/go/core/outbox_test.go` (actual publication/retry/marking tests)
- `backend/go/core/sync.go` (only canonical ConversationRequest/Page gap compensation, no full client/user-sync feature)
- `backend/go/core/sync_test.go` (history authorization/order/page tests)
- `backend/go/gateway/gateway.go` (canonical WSS forwarding/local bound fan-out only)
- `backend/go/gateway/http.go` (existing transport/subscription assembly only)
- `backend/go/gateway/message_test.go` (transport/duplicate/wrong-Conversation local delivery tests)
- `backend/go/tests/auth_test.go` (only existing malformed message probe setup/comment/oracle; canonical VALIDATION_FAILED, live local Core URL; preserve all Auth assertions)
- `backend/go/tests/message_test.go` (blackbox canonical/live combined tests using existing helpers)
- `backend/go/main.go` (only dispatcher startup assembly if a name change is necessary)
- `spec/tasks/**/LOOP1-GO-MSG-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-GO-MSG-001/**`
- `spec/progress/checkpoints/*loop1-go-msg-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

Coordinator prospectively binds exact existing flat stage-four service layout before any product write on 2026-10-01. This is ordinary feature scope under canonical SRC-01..07, not language-wide migration or architecture exemption. No shared/Auth/Social/schema/workflow edits authorized. Existing Gateway-to-Core HTTP and Core/NATS/Gateway event boundaries may use private Core-only adapter locators carrying unchanged canonical send/ACK/history shapes and bound bearer; per-user NATS subjects carry unchanged canonical message.created. No new public /v1 endpoint/frame field or direct cross-service import. Core retains credential/membership/routing decisions and durable commit; Gateway only forwards and fans out to local bound connections. Concrete mapping/readiness: 2026-10-01-activation-and-path-map.md under Task evidence.

# Acceptance

- Non-member sends reject before persistence. Sequence allocation, Message and one logical Outbox event commit atomically; success ACK follows durable commit only.
- Retry with the same sender, Conversation and request identity returns the same logical Message and sequence; distinct Conversations remain independent.
- Dispatcher/NATS duplication cannot create duplicate logical Messages or client materialization; Sync closes missed-delivery gaps. One GROUP send stays one Message and Outbox event.
- Canonical fixtures, fault-injection integration tests, independent review, and applicable real CI pass.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Weaken ACK/idempotency/order/authorization rules, make NATS the source of truth, change contracts/migrations, or implement clients/Java/future-stage mechanisms.

# Minimality

Use the existing PostgreSQL transaction and Outbox/NATS skeleton directly; add no speculative broker or ordering layer.

# Verification

- Discoverable entry points: `tools/verify-loop1-ctrl-002.ps1` and `tools/verify-frozen-architecture.ps1`.

- During edits run `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development`; clean committed independent candidate runs Acceptance. Run `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`.

- Run WSS fixtures and Go messaging integration tests for rollback, ACK timing, duplicate retry/delivery, sequence and wrong-Conversation rejection; run recovery and architecture checks.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Activated backlog -> ready -> active on 2026-10-01 after independently accepted Social actual-main merge b442acd and hostedCI36813501417 SUCCESS. Readiness/path evidence: 2026-10-01-activation-and-path-map.md.

# Handoff

- Fresh /root/message_implementation completed read-only input/path planning. Coordinator release grants sole writer ownership of this Task only after activation commit. No product files changed at activation.

# Next Action

- Implementation Agent: read active task/current, register delegated visible prompt and start prospective Recorder before work; run minimum baseline, then implement bounded message transaction/dispatch/forwarding/gap checks. Commit development candidate and handoff to NEW independent Review plus exact hosted CI. Never self-accept or claim S1 Gate PASS.

# Bound verification and recovery (2026-10-01)

Minimum pre-edit baseline: `python -B contracts/websocket/verify.py`, `python -B ci/check_architecture.py --scope all --json`, Development recovery, existing live normal/race Go suites on unique migrated disposable PostgreSQL16/NATS2.10 with DB_TEST_ENABLE=1. Record actual enable variables/services/skips; environment skips are not live PASS. Frozen verifier/source tests/CI controls plus recursive gofmt/build/vet and normal/race remain applicable before handoff. Clean committed Acceptance only; NEW independent Review then applicable real exact-head hosted CI before done. Last known good actualmain b442acd26777c481620a6bd917863cebfaf79b35/CI36813501417. No known product baseline failure; Social friend403 DEFERRED_BY_HUMAN never applies to message membership. Governance activation owned by Coordinator until commit; product writes owned solely by fresh Implementation Agent after release.

# Prospective regression-scope binding

Coordinator authorizes exact tests/auth_test.go before edit: prior payload={} blanket AUTHORIZATION_DENIED stub oracle conflicts with canonical MessageSend required content/Conversation shape. Change only local live Core assembly and malformed-frame VALIDATION_FAILED expectation; retain Gateway no-per-message Session-query check, all valid authentication/membership denials. No runtime_test.go or contract change.

# Development candidate handoff (2026-10-01)

Six bound product files and six matching test files complete; main/shared/Auth/Social/contracts/schema/workflows untouched. Local migrated disposablePG16/NATS2.10 pre-edit baseline and final normal/race PASS with zero runtime skips. Canonical sends/duplication/order/wrongConversation/private gap, true PostgreSQL COMMIT fault probes, membership/content/cross-sender conflicts, GROUP500 and existing Auth/Social/Session/WSS/fallback regression executed. Build/vet/gofmt/sourceall/WSS/architecture34/frozen34/CI27/Development recovery PASS; exactly four Windows symlink-creation subcase skips (WinError1314) disclosed in implementation handoff, hostedLinux checks still required. This is local development evidence only. Recorder prospective_resume with startup/UTF8/redaction/truncation limitations exposed; finish/validate before candidate handoff. Failed attempts preserved, not overwritten into PASS.

Durable commands/hashes/results: spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-implementation-command-results.json; behavior/limits/ownership: 2026-10-01-implementation-handoff.md. Owned disposable services/volume removed after label verification; no product writer remains after candidate commit. Active->review, never self-done. Last known accepted main b442acd26777c481620a6bd917863cebfaf79b35/CI36813501417; next exact action NEW independent Review and exact hosted candidate CI/full PR range. S1 remains OPEN.

Development product commit `f64ae64e6e333ee52242b7b2100c663cd1f378c2`; local checkpoint `spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-local-review.md`. Final evidence/Recorder closure commit may change head without product bytes; independent review must use actual final candidate. CRLF staged-evidence whitespace check failed and was repaired only for own non-Recorder summaries/launcher; registered prompt/Recorder raw bytes preserved, standard Git cr-at-eol recognition used for preserved inputs. No verifier or repo config changed.

Recorder R-MSG-IMPLEMENTATION-20261001 finished/validated121events (research-only PASS). Exactly four local Windows symlink subcase skips; zero Go runtime skips. Final closure operations are outside finished run as disclosed. No writer/service remains after final commit.
Transport closure: research/.gitattributes originally filtered36 immutable raw artifacts CRLF toLF during staging; raw working validation remained PASS. Coordinator explicitly authorized only own-run .gitattributes, after separate pre-edit path/hash diagnosis. Ordinary add retained cached filtered entries and byte assertion failed; own-run add --renormalize repaired index transport. All124 original prompt/run files now working/index byte-identical; no raw event/blob/hash mutation. Diagnosis and full audit in 2026-10-01-transport-preservation.json / 2026-10-01-transport-byte-audit.json. Initial stage mismatch and dirty Acceptance remain disclosed development failures. Finished Recorder administrative closure remains outside trace.

# Independent FAIL and bounded fresh repair (2026-10-01)

NEW /root/message_independent_review rejected clean detached candidate `f1764fd90f632878666504dded0d49c0ce1fa8fa`. Permanent evidence: `spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-independent-review-f1764fd/2026-10-01-independent-review-report.md`. Actual Core/Gateway/WSS/PG16/NATS2.10 probe proves gateway.go265-268 deletes previous committed origin marker after conflicting retry, violating original-socket ACK-only. Actual PG Sync probe proves sync.go13/21 accepts missing/null required afterSeq. No product fix made by reviewer. Independent normal/race/structural/byte audits and exact hosted PRCI36816686898/push36816625962 passed; green CI does not override FAIL. Fresh Review Recorder65events finishedFAIL/validatePASS; old interrupted run remains historical partial, not rewritten.

Coordinator archives byte-identical reviewer report/commands/probes/CI metadata/Recorder and keeps review unfinished. New /root/message_fix may repair only confirmed findings in already bound gateway/gateway.go + gateway/message_test.go and core/sync.go + core/sync_test.go, optional existing blackbox messaging test for actual regression. Preserve prior origin marker on later rejected retry; distinguish absent/null required afterSeq from valid0. No new transport/security/architecture/contracts/DB/shared/root/Auth/Social/workflows. Readonly Fix prep complete; sole writer begins only after this handoff commit. New exact-head independent Review/hostedCI required after repair; never selfaccept. Last accepted actualmain b442acd; rejected f176 remains permanent history.

# Bounded fresh Fix development handoff (2026-10-01)

Fresh /root/message_fix repaired confirmed origin-marker deletion and missing/null required afterSeq only, product `0a13b119e0e4c8788c5b264571df35df76ad94cb`. Five bound files:two product/three tests. Actual production-chain delayed/duplicate conflict regression and local marker/required-field tests REDexit1 before repair then GREENexit0. Full live normal/race zero runtime skips; WSS/sourceall/architecture34/frozen34/CI27/build/vet/gofmt/Development localPASS; exactly four Windows CI symlink subcase skips disclosed. Exact command/results:2026-10-01-fix-command-results.json; limits/ownership:2026-10-01-fix-handoff.md. Own labeled PG16/NATS2.10/anonymousvolume cleanedexit0. Immutable FAIL archive unchanged. Recorder R-MSG-FIX-20261001 prospective_resume with incomplete preparation trace; finish/validate/byteaudit before clean finalclosure. Next NEW independent Review clean exactfinalhead/fullbranch plus hostedCI; reviewunfinished, never selfaccept/done/merge/S1PASS. Lastacceptedmain b442acd/CI36813501417. Coordinator owns after writerrelease.

Post-handoff recovery format check exit1 corrected to required Command/Result/Evidence fields. Subsequent default GBK read failed on Task existing UTF8; restored prior immutable Task text from84b7a63 before appending only own handoff with explicitUTF8. No raw evidence or product changed; failed commands preserved.

Final fix Recorder finished/validated97events (research-only PASS). Post-finish rawbyte staging audit and administrative commit lie outside finished trace. Own fix services removed. All bounded development work committed at final candidate; writer released to Coordinator on clean-status confirmation. NEW independent Review and exact-head hostedCI remain required.

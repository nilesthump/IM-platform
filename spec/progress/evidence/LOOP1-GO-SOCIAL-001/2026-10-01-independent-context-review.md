# Independent Social acceptance-context and recovery-control Review

Date: 2026-10-01 Asia/Shanghai. Reviewer: /root/social_acceptance_context_review, a fresh real multi-agent context. I neither implemented nor fixed Social, remediation, integration or candidate recovery controls. No self-review acceptance is asserted.

Subject: 01765d20bb681e12085c55102adce2a29a6d28d2, branch task/LOOP1-GO-SOCIAL-001-v1.1, range 279c1dc4681683e2af3b3534a00e5222dde36be6..01765d20bb681e12085c55102adce2a29a6d28d2. Method: existing committed restoration checkout inspected before/after, zero porcelain status entries and zero working diff; only tracked files were read in old Social checkout. No repository, product, contract, old worktree or governance writes. All reviewer artifacts reside externally.

## Outcome

Recovery/control Review PASS locally. Social acceptance-context result: confirmed BLOCKED_BY_ARCHITECTURE / unresolved canonical acceptance input. No constructible approved authenticated-but-unauthorized bearer/owner context was found for friend-add-authorization-denied. Social remains unique backlog; no ready/active/done promotion, no Social business execution/fixture PASS/Task acceptance, S1 Gate OPEN. This Review does not accept the old Social product. New control CI reported by Coordinator is separately bound to 01765d2 and cannot accept unimplemented Social.

## Primary-authority finding

- contracts/fixtures/auth-user-friend/negative.json:830-887 requires authenticated principal not permitted to mutate A's relationship; PUT /v1/friends/B with <insufficient-scope-token>, exact 403 AUTHORIZATION_DENIED, no friendship effects. Its AUF-D-009 source is transport/security secrecy, not a scope issuance or friendship permission model.
- contracts/http/auth-user-friend.openapi.json:311-368 defines addFriend with bearerAuth security [], only target friendUserId path parameter, no owner parameter or request body; 403 is specified but its credential/permission precondition is not constructed. Lines 518-522 describe JWT user_id, session_id, client_type, session_epoch, iat, exp. Register/LoginRequest have additionalProperties=false; no issuance input for restricted permissions. A HTTP bearer security requirement's [] is not an OAuth scope definition.
- frozen-architecture.md:326-343 (section4.1/4.2) lists the same six Access Token claims and immediate bidirectional friendship/atomic DIRECT outcome. Sections3/10/11/12-14 govern Core ownership, sole contracts authority and executable acceptance before readiness. Frozen hash83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e and historical PDF546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 independently match.
- contracts/database/migrations/0001_initial.up.sql:1-25 exposes users identity/password and sessions slot/binding/status/expiry fields, no per-user/per-session friend-mutation grants, account-disabled role or bearer scope; conversation_members role belongs to already existing conversations and cannot deny initial caller-target friend creation under any approved rule.
- All three approved ADRs read; ADR-0001 bootstrap has expired, ADR-0002 changes representation only, ADR-0003 preserves public contracts/security boundaries. No ADR supplies this negative credential. Domain/invariants/acceptance Auth/User/Friend inputs contain no limited principal issuance rule. A fixture placeholder is an expectation, not approval to invent claims, storage policy or hidden authorizer hooks.
- Plugin API v1 permissions/grants are plugin-host Query/Action/UI capabilities; query.friendship is a read query. Neither policy-v1 nor v1 schema includes a friend-add Action or a restricted user HTTP bearer. WSS golden non-member-send (golden.json:613-645) has an explicit conversation member=false context for message authorization; PUT friend has no conversation ID/required prior membership, so importing that permission test would change semantics. No these alternate domains construct this fixture.

## Concrete credential/owner elimination

Current backend/go/shared/security.go:15-22 defines the six Claims, Sign/Parse bind those primitive fields. backend/go/core/auth.go:62-97 authenticates a valid signed token against PostgreSQL user/client/session/epoch/active/expiry, and authResponse:296-298 issues those six claims. Current handler:133-141 owns existing Auth/search; new Social routes are absent. Old committed2a6eaa1 backend/go/social.go:45-51 delegates to that authenticate and :83-144 derives pair from authenticated c.UserID and target. Therefore:

1. An invalid signature, missing/expired token, revoked/stale or mismatched user/session/client binding is unauthenticated with canonical401, not the requested authenticated403.
2. A valid C token calling PUT/B is C-B under implicit caller ownership. The request carries no authority to designate owner A, so inability to mutate A is not a denial of that operation.
3. A valid B token calling PUT/B is self friendship canonical422, not403.
4. Valid A and B identities are immediately bidirectional, without approval workflow or scope-limited principal defined. Blocking a client type, device/version, arbitrary username, missing conversation member or plugin permission would invent a product/security rule.
5. An extra JWT scope claim or external fake authorizer is neither issued nor consumed under approved model and cannot constitute canonical acceptance. The six-claim description need not be treated as a formal ban on every optional JWT extension: the decisive gap is absence of any approved issuance, meaning, permission policy and friend-owner request context.

This is a reproducible authority/input deficiency, not a live observed403 failure. No credential probe or Social live test was run, and no skipped case is called PASS. Old candidate/handoff5b35735 explicitly discloses unexecuted403 (2026-09-30-implementation-handoff.md:7); old social_test.go:74 canonical cases do not execute that fixture. Old independent Social Review/CI are absent.

## Minimal future reuse map

The current Task's exact files match the accepted layout and present responsibility: core/auth.go two friend routes only, private core/social.go one normalized pair transaction with existing SQL uniqueness/two memberships/Sync/Outbox, core/social_test.go private concurrency/rollback probes, tests/social_test.go public-handler fixture coverage reusing accepted Auth helpers. Existing core/http.go assembles s.handler; Core Auth/private helpers and Session Outbox remain owners. No duplicate Auth/search/router/dispatcher, full Core in Gateway/shared, public interface layer or broad rootpackage-main transplant is needed. Old committed backend/go/social.go/social_test.go are package main and require this split/adaptation; the map does not claim transplant or product review already occurred. Product correctness/actual complexity/fixture coverage still require a fresh implementation and independent review after approval of executable inputs.

## Recovery-control and evidence inspection

Exactly15 changed paths are recovery/task/checkpoint/integration evidence. backend, contracts, checkers, workflows and tools unchanged from accepted actual merge279c1dc. Unique Current Task LOOP1-GO-SOCIAL-001 exists only backlog and declares backlog. Recovery verifier Acceptance PASS, frozen verifier PASS34 controls/zero skip, source/dependency all PASS/zero violations. All8 closure-evidence-transport manifest archived LF SHA256 values independently checked against committed git blobs; original source hashes remain explicitly separate. Archived PR36763289936 head a9f1393 checkout merge2b72ca3 and actual main36764254107 checkout279c1dc summaries each state13success; these archived facts are preserved subject-bound evidence, not newly fetched hosted results and not Social tests. Failed integration review remains durable. Current/checkpoint honestly separate remediation/integration PASS from Social unresolved.

## Smallest Architect decision question and next action

Which already approved credential issuance and server-side permission/owner context constructs an authenticated principal denied PUT /v1/friends/B with403AUTHORIZATION_DENIED under the current six-claim JWT and implicit caller model? Supply the exact existing authority and executable setup. If none exists, an Architect-approved smallest contract/security decision is required to reconcile this fixture before readiness; this run explicitly forbids making that decision or editing contracts/security boundaries. No scope addition, waiver, inapplicable label,401/422 reinterpretation or fake hook is approved.

Coordinator should archive this bounded report/proof, record confirmed BLOCKED_BY_ARCHITECTURE and unmet acceptance input in unique backlog Task/current, then obtain the decision. After approved constructible context: backlog->ready->active, fresh Implementation using exact map, fresh Review, real applicable hosted CI, Task closure; no automatic Social merge or Message/E2E/Java/client/plugin/S2 continuation.

## Instrumentation and limitations

Recorder R-SOCIAL-CONTEXT-20261001 is prospective_resume with pre_recorder_work=true/pre_recorder_trace_complete=false. Exact Human visible prompt independently registered as P-SOCIAL-CONTEXT-HUMAN SHA02c1aa2ffa9fc0a6fa45593b3e75f92767d357d057839cf005c09ba57fac9854; delegated public review prompt separately registered. Startup/direct source reads and unsuccessful Recorder setup/help are incomplete pre-start activity; no retrospective timings inferred. Default python was Python2 and produced SyntaxError, first IDs lacked required P-/R- prefixes, wrapper run-command rejected positional argv; corrected using bundled Python3. First external proof failed KeyError(cases)203ms and was repaired to scenarios, then PASS594ms; both real command results retained. Terminal displays truncated large search/proof/source output and initial Chinese text was mojibake; bundled Python3 -X utf8 reads canonical UTF8 correctly and Recorder blobs preserve successful proof. Source-checker Recorder output redaction=true, not silent/no-redaction completeness; its result/exit remain PASS. No unavailable hidden system prompt/model/token/cost metadata claimed. Recorder integrity is research validity only, not Social or Stage PASS.

Ownership: reviewer owns external report/proof/Recorder only; no product changes or repo ownership acquired. All write activity released after finish/validate. Root may archive public report/proof with explicit transport normalization and separate hashes; original Recorder streams must remain immutable.

## Exact recorded command results

- pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance: exit0, 5672.0ms, PASS; redaction=False.
- pwsh -NoProfile -File tools/verify-frozen-architecture.ps1: exit0, 5078.0ms, PASS; redaction=False.
- C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -B H:/.codex/worktrees/architecture-remediation/social-context-review-20261001/proof.py: exit1, 203.0ms, FAIL; redaction=False.
- C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -B H:/.codex/worktrees/architecture-remediation/social-context-review-20261001/proof.py: exit0, 594.0ms, PASS; redaction=False.
- C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -B ci/check_architecture.py --scope all --json: exit0, 344.0ms, PASS; redaction=True.

Recorder closure correction: first finish argument BLOCKED_BY_ARCHITECTURE rejected because schema permits PASS/FAIL/BLOCKED/CANCELLED; immediate validate truthfully reported partial. Corrected finish uses BLOCKED; task meaning remains BLOCKED_BY_ARCHITECTURE. No event stream edited.

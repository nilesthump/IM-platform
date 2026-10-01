---
task_id: LOOP1-E2E-001
title: Verify first Go end-to-end messaging slice
status: done
owner: /root/s1_e2e_preparation (sole Implementation writer after release)
stage: S1
gate: S1
---

# Goal

Prove A can log in, search/add B, obtain the unique DIRECT Conversation, send `hello`, receive durable ACK, and B receives it in realtime through the real TLS entrypoint.

# Inputs

- Current Frozen Architecture resolved/hash-checked through spec/architecture/README.md and baseline.md, applicable existing behavioral chapters plus §3/§10 SRC-01 through SRC-07/§11/§12-14; approved ADRs and Minimality Contract.
- Canonical HTTP, WSS, Sync, error, fixture and database contracts; accepted Go Auth/Social/Message implementations.

# Execution Constraints

Read spec/governance/execution-boundaries.md and independent-review.md. allowed_paths never exempts ownership/import direction. Before activation bind these responsibility paths to the actual accepted stage-four layout and any presently required exact assembly file. Coordinator must amend paths before edits if actual file names differ; no duplicate alternate packages or unapproved root/shared business. Canonical fixtures remain sole expectations.

# Dependencies

- `LOOP1-GO-MSG-001` done; S0 Gate PASS; LOOP1-ARCH-REMEDIATION batch PASS with final source/dependency/hosted acceptance.

# Allowed Paths

- `tests/e2e/go_tls_messaging.py` (canonical fixture-driven real Go HTTPS/WSS entrypoint harness; standard library only)
- `tests/e2e/README.md` (exact run/environment/result boundaries)
- `.github/workflows/ci.yml` (only existing deploy-job E2E step; no product contract or new stage mechanism)
- `ci/classify.py` (only tests/e2e selection of existing go/deploy/architecture/source_go jobs)
- `tests/ci/test_classify.py` (positive/deleted E2E path selection tests)
- `spec/tasks/**/LOOP1-E2E-001.md`
- `spec/progress/current.md`
- `spec/progress/evidence/LOOP1-E2E-001/**`
- `spec/progress/checkpoints/*loop1-e2e-001*.md`
- `research/prompts/**` and `research/runs/**` only for this task's Recorder artifacts.

# Acceptance

- A-to-B `hello` succeeds through HTTPS/WSS/TLS and B receives one correct realtime Message after a durable ACK.
- End-to-end retries, authorization, revocation, transaction rollback, Outbox/NATS delivery, and contract outcomes preserve the S1 correctness red lines.
- Clean-checkout integration/E2E checks, independent review, and applicable real CI pass; S1 Gate evidence is durable and a stable checkpoint exists.

- Applicable source/root/dependency checks pass; independent Review inspects actual behavior/responsibilities/imports/minimality. Java inherits canonical boundaries, not these Go paths.

# Forbidden

- Rewrite contracts, migrations, or product semantics to make E2E pass; introduce client UI, Java implementation, or future-stage infrastructure.

# Minimality

Exercise the accepted Go path with a direct fixture-driven harness; add only test wiring needed for actual TLS and service interaction.

# Verification

- Discoverable existing tools entry points: `tools/verify-loop1-ctrl-002.ps1` (Development while editing; clean committed Acceptance for independent candidate) and `tools/verify-frozen-architecture.ps1`.

- Run Go profile Compose and E2E over real TLS plus all S1 contract/integration checks; evaluate the S1 Gate checklist on a clean integrated candidate.

- Before activation bind exact accepted stage-three checker commands and stage-four live regression evidence; record actual integration enable conditions/services/skips. Planned tools or skipped integration are not PASS.

# Evidence

- Activated after Go Message acceptance and exact administrativeb51 independent/hosted acceptance; Human approved CI path scope. See bounded readiness below.

# Handoff

- Coordinator owns activation governance until committed; fresh /root/s1_e2e_preparation owns only bounded test/CI implementation after explicit release in isolated worktree.

# Next Action

NEW independent Review clean exactfinalcandidate/fullb442acd..HEAD, then exacthostedCI/directselectedjobs/newPRtreebinding beforedone. No selfacceptance. Coordinator owns administrativeclosure afterwriterrelease.

# Approved readiness and source/path binding (2026-10-01)

Human approve explicitly covers the three CI paths in this Task, solely E2E wiring/classification. Coordinator narrows tests/e2e to two exact files and removes speculative deploy write scope: existing Go Compose/Caddy/config suffice. This is no Frozen/public/security/ACK/schema/compatibility change. Product Auth/Social/Message accepted in this lineage; MSGuniquedone; S0/remediationPASS and latestboundedadministrativeb51 independentReview/hosted36828991394 PASS. PR4OPEN remainsunmerged; completedS1 will use NEW reviewedPR including inheritedacceptedMSG plusE2E.

Inputs exact: spec/architecture/frozen-architecture.md currentSHA83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e viaresolver/baseline; ADR0001expired/0002/0003/0004; canonical §§3/7/10 SRC01..07/11/12..15/AppendixA; spec/governance/{minimality,execution-boundaries,independent-review}.md; spec/domain and invariants Auth/Social/Messaging inputs; spec/acceptance/s0-auth-user-friend.md and s0-messaging.md; contracts/http/auth-user-friend.openapi.json, websocket/envelope.schema.json/sync-v1.schema.json, fixtures/{auth-user-friend,websocket}, errors/http-errors.schema.json, database/migrations/0001_initial.up.sql and accepted Go tests. Never use nonexistent s1.md/loop-1.md as authority. Friend403 solelynamedDEFERRED_BY_HUMAN, never appliesmessage-membershipdenial.

Minimum pre-edit baseline: bundledPython -B contracts/websocket/verify.py; bundledPython -B ci/check_architecture.py --scope all --json; pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development; pwsh -NoProfile -File tools/verify-frozen-architecture.ps1; actual live Go normal/race on owned disposablePG16/NATS2.10 with canonical0001, DB_TEST_ENABLE=1, loopbackPGHOST/PGPORT/PGUSER/PGDATABASE, NATS_URL. Commands go -C backend/go test -count=1 -v ./... and go -C backend/go test -race -count=1 -v ./...; runtime ---SKIP is not PASS. Historical launchers hardcode oldRecorder/evidence/container identities: do not execute them; this Task may create its own bounded evidence launcher, only same current commands. cleanup verifiesownedlabels/container/volume before removing own services. ActualDocker server29.5.2 Linux/DockerDesktop/Compose5.1.4 read-onlyavailable; PG16/NATS2.10/Caddy2 imagescached. This is environmentavailability, not integrationPASS.

Final local verification includes actual strictTLS E2E (bundledPython -B tests/e2e/go_tls_messaging.py), full Go normal/race/live fixture/fault probes, build/vet/gofmt, WSS/HTTP/architecture34/frozen/sourceall/CI path/Gate controls and Development recovery. Four localWindows symlink CI subcase skips must be disclosed and covered byexacthostedLinux; no runtimeintegration skip permitted. Independent Review replays from clean committed candidate with actualservices and validates fullPRrange responsibility/logic/imports/minimality/requiredjobs. All required exactcandidate hostedCI jobs completedSUCCESS; gate alone isnotenough. One writer; newReviewer neitherimplemented norfixed; ordinaryFAIL invokes freshFix then NEWfreshReview. No selfdone/merge/S1GatePASS.

StrictTLS: copy only publicCaddyroot.crt fromownedCompose intoTEMP, ssl.create_default_context(cafile), CERT_REQUIRED/check_hostname true; executeuntrustedCA/wronghostnamenegatives. Register/login/search/addfriend/uniqueDIRECT/sendcanonicalhello/ACK durablerows/OutboxNATSreceiver/retry/conflict/nonmember/revocationclose/staletoken throughtrueHTTPS/WSS. Accepted Go actual deferredCOMMIT probe plusentrypointdurablerows establish ACK-aftercommit; concurrentnetwork receiver read scheduling must not be treated as a new server ordering guarantee. Existing live fault probes cover rollback/duplicate/outoforder/Sync/GROUP500; no new publichistoryroute/clientfeature ortestframework. Fixture expectations remaincanonicalonly.

Preparation /root/s1_e2e_preparation read-only and incompletepreRecorder, nofiles/services. After activationcommit released, create isolated task/LOOP1-E2E-001 worktree, register delegatedvisibleprompt/start prospective_resume beforecommands/edits, then solewriter. All historyFAIL/partial/unknown605 files remainimmutable. Durable path/readiness: spec/progress/evidence/LOOP1-E2E-001/2026-10-01-activation-and-path-map.md. Coordinator owns onlyactivation/task/current/archive untilcommit; productwriter is released explicitlyafter. Lastacceptedadminb51/product183/mainb442acd. S1OPEN; stopgoalS2OPEN.

# Development implementation handoff (2026-10-01)


Development product commit `7a980cac3f3c129c78bfe65fc974ce6839091cb9`; branch `task/LOOP1-E2E-001`, isolated checkout `H:/.codex/worktrees/s1-e2e-approved`. Bounded implementation diff starts `0d4df7aa8a39426976a44ff0c42c94befe2e0b2e`; complete new S1 PR/review starts actual main `b442acd26777c481620a6bd917863cebfaf79b35` and includes independently accepted inherited MSG. The final administrative closure SHA is reported to Coordinator after commit; product bytes remain this commit. This is development evidence, never Task/S1 acceptance.

Five exact authorized files changed: two new E2E harness/README, two-line existing deploy CI step, classifier branch and positive/deleted-path tests. No backend/deploy/contract/migration/frozen/public/security/ACK change. Standard library only, no new job/framework/dependency/service. Present extra test setup: real deferred COMMIT failure is required by E2E transaction acceptance; scoped unique trigger/function exists only in the owned disposable database and is dropped in finally. Actual default Caddy unknown-SNI rejection cannot prove client hostname validation, as first FAIL showed; temporary owned in-memory fallback_sni delivers its existing localhost certificate to wrong.invalid. Strict CERT_REQUIRED/check_hostname remains enabled; only certificate verify code62/64 is accepted. Original JSON is restored and equality asserted before any positive business traffic. No private key copied. Official reference: https://caddyserver.com/docs/caddyfile/options#fallback-sni. Coordinator explicitly confirmed bounded temporary wiring.

Command: bundledPython -B tests/e2e/go_tls_messaging.py.
Result: fifth attempt exit0,32.547s, no runtime skips. Real Go3roles/PG16/NATS2.10/migration0001/Caddy; trustedCA/untrustedCA/hostname; HTTPS register/login/search/normalized friend uniqueDIRECT; WSS canonical hello/ACK backed by independent SQL Message+Outbox+sequence; NATS publication and correct one recipient; retry/conflict/nonmember no effects; actual deferred COMMIT rollback MESSAGE_COMMIT_FAILED/no rows/no sequence advance; replacement/logout revocation then close/staletokenreject. Original Caddy policy restoration verified. Receiver socket read scheduling does not establish a new cross-socket ACK ordering guarantee. Exact named friend403 separately DEFERRED_BY_HUMAN, never counted PASS.
Evidence: E2E individual ledgers/raw outputs plus `2026-10-01-implementation-command-results.json` and own Recorder.

Command: go -C backend/go test -count=1 -v ./...; go -C backend/go test -race -count=1 -v ./....
Result: pre-edit normal21.859s/race85.594s and final normal20.281s/race82.250s all exit0, zero runtime skips. DB_TEST_ENABLE=1,PGHOST127.0.0.1,PGPORT55651,PGUSERpostgres,PGDATABASEs1_e2e_regression,NATS_URLnats://127.0.0.1:42651; owned task-labeled disposable PostgreSQL16/NATS2.10 with unchanged canonical0001. Actual existing ACK-blocked COMMIT/rollback/idempotency/duplicate/outorder/Sync/wrongConversation/GROUP500/Auth/Social/Session/fallback regression executed. No runtime environments omitted.
Evidence: baseline/final ledgers and redacted raw command outputs.

Command: WSS/sourceall/Development/frozen/build/vet/HTTP/tests architecture/tests ci/gofmt.
Result: all exit0; architecture34/frozen34/CI29, WSS8positive10negative plus18schema26behavior mutations. Exactly4 Windows symlink-creation CI subcase skips WinError1314 disclosed; applicable exact Linux hosted checks still required. No integration skip. No full future Java/client/plugin/capacity/release claim.
Evidence: checks ledger/raw output; `tests/e2e/README.md` executable boundaries.

Four failed E2E attempts remain immutable: initial unknownSNI does not prove hostname verification; container-local localhost admin addressing corrected to127.0.0.1; missing explicit Caddy TLS policy corrected only in temporary negative JSON; transient Docker mirror alpine3.21 metadata403 succeeded on unchanged retry. Each attempt cleaned owned Compose containers/volumes with real project label inspection and absence checks. No registry/daemon config change. Failed Recorder verification_result event missing observed result key rejectedexit2, explicitly disclosed instrumentation_warning then corrected. Initial Windows text writes expanded CI newline diff; original HEADLF restored before commit. Preparation guessed-path/quoting/GBK/truncation failures before Recorder are incomplete pre-trace, never full prospective. None of these replace or hide a FAIL.

Research R-E2E-IMPLEMENTATION-20261001 prospective_resume, P-E2E-IMPLEMENTATION-20261001 delegated full visible release prompt. Only own nested .gitattributes preserve raw prompt/run/evidence bytes; old FAIL/partial/prior evidence unchanged. Finish/validate and stage audit precede final administrative candidate; post-finish staging/commit/status closure is disclosed separately. Research PASS is not Task PASS or S1 Gate PASS.

Cleanup: all five Compose attempts ownedresources removed; separate normal/race PG/NATS cleaned after exact owner label, actual mounted anonymous-volume inspection and exclusive container-volume binding. No active owned test services or writer after final commit/release. Original H:/IM-platform and605 unknown files untouched. Coordinator owns final review/CI/queue closure after release. Next exact action NEW independent Review from clean exact final SHA/fullmain range; exact hosted CI/direct selected jobs and new PR tree binding before taskdone. PR4 not merged; Coordinator authorized NEW reviewed S1 PR only. S1 OPEN; stop goal S2OPEN after approved newPRmerge/main verification. Lastaccepted adminb51/product183/mainb442acd. No architecture conflict.

# Independent acceptance and administrative closure (2026-10-01)

Fresh /root/s1_e2e_review independently accepts exact6346f39fc6786bba3cddbde7acc91bbad42446a1, full b442acd..6346 range, clean detached checkout. Recovery Acceptance, architecture34/frozen34/CI29/sourceall/HTTP/WSS/build/vet/gofmt pass. Actual strictTLS E2E36.156s/live normal21.156s/race84.203s exit0, runtime0SKIP. Typed TLS CA/hostname rejection and original policy restoration, durable ACK/Outbox/NATS, true deferred-COMMIT rollback, retry/conflict/nonmember/revocation and existing Go fault/Sync/GROUP probes executed. Exact push36831979992 and PR36832052224 each13/13 required jobs SUCCESS; Linux CI29 no symlinkSKIP. PR5 virtualmerge2dbe328b310e0b3328681d8cb629bd5c6fd40147 parents[b442acd,6346], tree87ca7df8c0a9284f64af00ce06f5289bcea91662 matches candidate. Raw report/manifest and all files preserved under spec/progress/evidence/LOOP1-E2E-001/2026-10-01-independent-review-6346.

All four S1 tasks uniquely done and product Gate criteria satisfied; S1 Gate PASS checkpoint now recorded. This subsequent administrative closure is pending NEW independent administrative Review and exact-head/PR hosted verification before PR5 merge. S2 remains inactive until accepted NEW PR5 merge and actual-main verification. PR4 must remain unmerged. No S2 implementation.

Known failures preserved: four implementation E2E attempts; independent Recorder association/cleanup-ID/manifest additive-script failures; Coordinator transient push reset and Recorder lock/result/prompt-association rejections. Original605/hash and4988 historical evidence objects independently PASS. Raw CRCRLF/whitespace preserved; no retroactive Recorder edits. Two finished Coordinator runs archived byte-for-byte; current closure Recorder remains external and ongoing. Administrative archive/state/commit are new linked run activity, never appended to finished product/reviewer traces. Friend403 remains solely DEFERRED_BY_HUMAN under ADR0004; message membership403 passed. Own services/volumes cleared, sole product writer released.

Next exact action: fresh bounded closure Review of 6346..HEAD plus exact required hosted jobs; finalize PR5 description/ready, merge NEW PR5 after PASS, independently verify actual main, record S2 OPEN without task activation and stop after original synchronization plus TEMP handoff. Last accepted product6346; current admin commit SHA supplied by committed review release. Coordinator owns only administrative closure in original H:/IM-platform;605 unknown files unchanged.

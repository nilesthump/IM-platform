# Independent Social product Review — PASS

Reviewer: /root/social_product_review, fresh context, neither implementer nor fixer. Coordinator froze candidate writes. Reviewed clean committed branch task/LOOP1-GO-SOCIAL-001-v1.1 at exact SHA 27862b95ef6269c7c353ad8c44c32c0e322e035a. Product range cc49b98a103a3426d23bfcbbd09958060b7e790b..27862b95; complete PR range 279c1dc4681683e2af3b3534a00e5222dde36be6..27862b95. Git status before and after was empty; no product, governance, contract or candidate Recorder file changed by this reviewer.

## Finding and decision

No actionable implementation defect found. Accept the Social candidate and exact applicable hosted CI. This is bounded Social Task acceptance, not S1 Gate PASS, a production/load claim, later-stage implementation, or authority to merge PR3.

Read mandatory recovery/task sequence, canonical resolver/manifest, frozen responsibility and behavioral sections, approved ADRs, domain/invariants/acceptance, execution boundaries, independent-review and Minimality Contract, canonical HTTP/errors/database/Sync/golden applicability. Canonical Markdown SHA256 83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e and historical PDF 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 verified. No implementation-authority reversal. Only unique Social task is review.

## Scope, behavior, responsibility and reuse

New product diff is exactly four allowed files: auth.go adds two friend route registrations; private Core/social.go owns normalized friendship/DIRECT/membership/Sync/Outbox transaction; Core/social_test.go checks assembly/reuse/rollback; tests/social_test.go exercises public handlers and canonical outcomes. Existing accepted search/Auth/error handling, Gateway/shared/root assembly, Session Outbox dispatcher, dependencies, OpenAPI, future golden responses, schema0001, frozen body and manifest remain unchanged. No extra public API, service, schema, configuration or speculative policy layer.

Compared preserved old2a6eaa1 package-main implementation: stable pair-derived friendship UUID/result/list, pair normalization, direct transactional assembly and event intent are selectively retained in private Core; accepted Auth helpers and current blackbox harness replace root-package coupling. UUID validation, current ordered account lock and Session recheck, DIRECT validation and canonical event shape support presently required correctness. Old root layout and governance were not copied. Actual current filename mapping matches scope and ownership/import graph.

Ordered user locks serialize A-to-B/B-to-A and same-user replacement login. PostgreSQL uniqueness and composite friendship/direct FK support one canonical pair and DIRECT. New/reused DIRECT is validated for exactly two active pair memberships; existing broken friendship reports409 without repair. Caller identity comes from authenticated bearer Session; target UUID is validated. Session identity/epoch/status/expiry are rechecked after account lock. Both parties receive six matched canonical low-frequency Sync/Outbox events in the same transaction, with no effects added on repeated friendship lookup. Commit precedes success; errors use accepted sanitized handling. List is immediately bidirectional. No pending approval state.

Reviewed substantive test oracles: canonical expected HTTP bodies/statuses consumed through existing fixture normalizer; SQL independently checks normalized pair/DIRECT/two memberships/event counts; Core checks matched Sync/Outbox payloads and identity, no duplicate retry events, completed-assembly rollback and a partial assembly conflict rollback. Public concurrency exercises both request directions (201+200/shared DIRECT); existing Auth/Session/WSS/fallback/search regression suite executes. No canonical acceptance expectation rewritten.

## Independent actual tests

Ran candidate source in the clean frozen committed checkout. Reviewer-owned disposable postgres:16 container social-review-pg-20261001 (ID c1b4787b4cd2db9ab35f4485fbae5243089f4da0eb84602a45a6ed02ccef8445, port61202) and nats:2.10 container social-review-nats-20261001 (ID071ec0bd4f4e5f612f44f2dd1910dd6dd487e343e75baeedda037c20f2524ce5, port61205) were created with review.owner=R-SOCIAL-PRODUCT-REVIEW-20261001. Localhost-only disposable trust database social_review; immutable0001 migration applied with ON_ERROR_STOP. DB_TEST_ENABLE=1, PGHOST127.0.0.1/PGUSERpostgres/PGDATABASEsocial_review/PGSSLMODEdisable and NATS_URL nats://127.0.0.1:61205.

- Acceptance recovery: exit0; unique review/task21/clean status.
- Frozen verifier: exit0,34 tests, zero skips.
- Source checker --scope all --json: exit0, no violations; inspected actual Core-only private business/imports.
- CI controls: exit0,27 tests,4 Windows symlink privilege subcase skips; hostedLinux controls execute.
- Recursive build/vet/nonmutating gofmt: exit0.
- go -C backend/go test -count=1 -v ./...: exit0; live Core/social, canonical Auth/Social, reverse concurrency, Session-lock expiry, WSS revoke/fallback checks executed; zero runtime environment skips.
- go -C backend/go test -race -count=1 -v ./...: exit0; same live requirements, zero runtime environment skips.
- Complete PR classifier: all applicable categories true except deploy false.12 selected jobs include classify/gate, all successful; deploy legitimately inactive.
- Diff --check: exit0. Golden OpenAPI/positive/negative/database/frozen diff from main is empty.

Exact Recorder command IDs, argv, exit codes, durations and output hashes are in command-results.json. External launchers identify exact live enable context; raw full transcripts are not part of the shared report.

## Deterministic investigation of logout concurrency

Initial hypothesis that logout could commit after the Social Session recheck but before Social commit was disproved through the actual legal logout path. In a reviewer-owned archive of exact27862b95 (unchanged tracked Go blobs; extra reviewer probe only), hold conversations table SHARE lock, start actual public friendPUT so it waits on conversation INSERT after Session recheck/user locks, then invoke actual public logout. Observe logout waits at canonical user_sync_events INSERT, because its user FK KEY SHARE conflicts with Social user FOR UPDATE. Uncommitted logout leaves the visible Session ACTIVE. Release table lock: Social201 commits, logout204 completes, subsequent same-token friendPUT401. Probe passed3 repetitions under -race, no deadlock. Do not require speculative new lock policy or treat isolated SQL Session mutations without canonical side effects as legal logout evidence. Probe script/source and archive blob-match proof are external reproducibility artifacts, not candidate modifications.

## Applicable hosted acceptance

Independently queried PR3 https://github.com/nilesthump/IM-platform/pull/3: draft/open/MERGEABLE, head27862b95, base279c1dc. Full pull_request run https://github.com/nilesthump/IM-platform/actions/runs/36810190233 SUCCESS,12 successful selected jobs, only deploy skipped by classifier. Actual classify checkout=head27862b95; all other selected job checkout=f9bd4b023e2184b7d3c91808b4c505863bf46ec7. GitHub commit API parents=[279c1dc,27862b95], tree bb2052d6bbdacd5009c0e9549c247c600c9e50df equals local candidate tree. This is synthetic tested merge, not actual Social merge.

Go actual logs show DB_TEST_ENABLE1, migrated0001/PostgreSQL16/NATS2.10, recursive formatting/build/vet/test/race and successful Core/Gateway/shared/public test packages; contracts/fixtures verifiers also succeed. Hosted output uses nonverbose go test, so do not invent individual per-case log lines or infer runtime coverage merely from schema fixture counts. Independent verbose live normal/race execution above provides executed-case/zero-skip evidence. Architecture34/CI27/sourceGo/Java and stage-appropriate compatibility boundaries pass. No real Java/client/plugin business claimed. Bounded hosted-ci-proof.json contains original job metadata, actual checkout/log proof and merge tree binding.

## Exception, limitations and ownership release

Only friend-add-authorization-denied runtime is DEFERRED_BY_HUMAN under accepted ADR-0004/loop1-exceptions.json; future OpenAPI403/golden response unchanged. Applicability test PASS means disposition validated, never runtime403PASS. No other403/security/transaction exemption. FRIEND-AUTHORIZATION-403 remains future not implemented/tested/done.

Both exact created disposable containers and their owned anonymous volume were removed; subsequent docker listing for those names empty. Cleanup label-format inspection command had an escaping failure; removal used the two exact creation names/IDs only, not enumeration or an unknown target. No other services, volumes or worktrees touched.

Research run R-SOCIAL-PRODUCT-REVIEW-20261001 is prospective_resume/pre-recorder-work, startup trace incomplete. Initial nonescalated Acceptance failed because read-only sandbox prevented temp creation; fresh escalated Acceptance and frozen34 succeeded. Early missing guessed paths and large truncated authority reads were corrected by actual paths/targeted reads. One malformed nested PowerShell build launcher exited1; corrected external build.ps1 completed build/vet/format exit0. Cleanup inspection formatting failure disclosed above. Some external script writes/inspection reads lie outside Recorder; redacted/display-truncated outputs and incomplete pre-start capture are not a complete prospective trace. These are reviewer instrumentation/launcher limitations, not suppressed product test failures. Recorder validation is research evidence, not Task/S1 acceptance.

No remaining writer ownership. Coordinator may archive bounded report/command metadata/hosted proof and update finite Task/current/checkpoint under authorized paths. No automatic Social PR merge or Message/E2E/Java/client/plugin/S2 continuation.


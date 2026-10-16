# Independent regular review — FAIL

Actor: `/root/group_regular_10b39c8`. Fresh review context; I did not implement, fix, or previously review this candidate. I made no repository, index, branch, main-repository, product, or runtime changes and delegated no work. All review outputs are in this external directory.

Candidate: `10b39c8688588c94f95a9a3d671b8496e076fcdf`, branch `task/LOOP1-GROUP-PLAN-001`, base `86b41e4dbacd2fd6c92033697ee2ebe05a8b0ed0`; reviewed range is base..candidate. Assigned and Git-resolved root both equal `H:/.codex/worktrees/grp/IM-platform`. Initial, independently recorded scope audit, clean Acceptance and final checks all observed the exact committed HEAD and zero status entries. No reset, checkout, clean, commit, push, PR, CI trigger, or main synchronization was performed.

## Blocking finding R1 — P2: complete the future contract-slice migration and hosted-verification scope

`spec/tasks/backlog/LOOP1-GROUP-001.md:46–48` authorizes and requires `0002_group_operations.up.sql` / `.down.sql`, and lines 125–127 require the additive migration to be independently accepted before the Core/client implementation. Its Allowed Paths omits **`contracts/database/migrate.py`** and **`tests/database/test_migrations.py`**. Line 160 postpones naming the real database verification commands instead of resolving this currently visible dependency.

This is a concrete execution gap. `contracts/database/migrate.py:17` fixes `VERSION = "0001_initial"`; lines 33–38 select only that version's SQL/checksum, and the ledger/application logic likewise handles only that version. The real hosted Go setup, `.github/workflows/ci.yml:168`, runs `python3 contracts/database/migrate.py up`. Existing database regression `tests/database/test_migrations.py:14–15,63–72` calls that same entrypoint. Adding the planned 0002 files alone therefore leaves the accepted deployment/CI entrypoint applying only 0001. The newly required operation-receipt schema is unavailable through that path. The task cannot connect its promised migration and real integration acceptance within its listed hard write boundary; changing immutable 0001 or hiding migration execution in Core/verifier code is not an acceptable substitute.

The same missing execution wiring also affects the independent **contract-first** slice. The Task authorizes `contracts/http/verify-group.py` and `tests/contract/group/**` but neither `.github/workflows/ci.yml` nor an existing called HTTP validation entrypoint. The actual shared contract step at workflow lines 332–345 invokes only Auth/User/Friend, Sync, WSS and Plugin validators and specifically discovers `test_sync_transport.py`. `verify-auth-user-friend.ps1:13–22` pins the auth document and auth fixtures; `tools/verify_sync_transport.py:10` pins Sync. They do not discover a new group contract/verifier/suite. Contract changes select the existing jobs, but selection does not execute the new group schema/negative fixtures. Thus this slice could receive green hosted checks while its promised independent group contract verification never runs. This is part of R1's incomplete executable path, not a request to place product validation inside architecture tests.

Smallest repair **in the planning documents only this round**: narrowly authorize the existing runner and existing migration regression file for this 0001→0002 transition, and name the real status/up/database-test verification entrypoints with the disposable PostgreSQL/`DB_TEST_ENABLE=1` conditions. Require evidence that the accepted runner applies the new migration, supports the agreed 0002 rollback/old-fixture compatibility, preserves immutable 0001 bytes/checksum/lock/failure behavior, and is independently frozen/accepted before runtime implementation. Also narrowly authorize `.github/workflows/ci.yml` only to connect the planned group contract verifier/suite to a required existing contract job, with genuine nonzero failure propagation and no suppression of old checks. Record that this wiring and group positive/negative verification belong to the first independently accepted contract slice. No new workflow/job/framework, service, present-round contract edit or product implementation is needed. The existing instruction to revise scope on activation is useful for new discoveries; it does not resolve these already-known necessary execution dependencies.

Evidence: `final-checks.json`, `final-checks.stdout` and extended `final-checks-ciwiring.stdout` bind the exact candidate, 0002 requirements, actual runner version, missing allowed paths, current regression, pinned validators and missing hosted group execution. These read-only checks exited 0 and do not claim a runtime PostgreSQL/group-contract test was executed. R1 blocks this planning candidate's regular acceptance. A fresh Fix context and then a new regular reviewer are required; a different fresh error specialist follows only after regular PASS on the new final SHA.

## Scope and semantic coverage

All 74 changed files were read as bytes, SHA-256-bound to exact candidate Git blobs, decoded/parsed where relevant and assigned a responsibility and inspection result in `per-file-inventory.json`. All changes match the control Task's Allowed Paths. The only executable production-control delta is the direct standard-library S2 checker; no product source or dependency delta exists.

Reviewed Human requirements across ADR13, canonical §4.3/§6.7/§15/§19/§20/appendices A/B, domain/invariants, G01–G09 and the future Task: creator's own-friend selection and automatic membership; arbitrary valid member adding their own friends without OWNER/creator-friend restriction; A–B/B–C/nonfriend A–C; authenticated actor and all-target authorization; normalized target-set/key binding, replay/conflict/concurrency/existing-member rules; atomic Core data/receipt/User Sync/Outbox commit; rollback and honest commit-unknown/response-loss handling; authorized member metadata and nonfriend sender identity; online invalidation plus cursor/offline compensation; unchanged ACK/seq/single-message/single-logical-Outbox semantics; current three client stacks, source direction and i18n; contract slice independently accepted before runtime; real browser/installed Tauri/Android emulator, raw screenshots and Architect approval. No additional blocking semantic defect was identified in these areas. R1 is the missing executable migration scope supporting that otherwise coherent plan.

Inspected the actual checker and all changed test logic, including malformed/duplicate Completion Metadata, bounded evidence paths/junction rejection, exact dependencies/phases, all old S2 prerequisites, GROUP backlog blocking claimed S2 PASS, GROUP-plan acceptance/sync, and explicit I18N activation independent of chain tail. OPEN S2 is not evaluated. The checker deliberately proves necessary structural links only; it cannot certify the contents of future acceptance/CI/sync evidence.

Current GROUP remains uniquely backlog/planned; the control Task remains uniquely review; S2 remains OPEN. The future exact allowed paths otherwise preserve Core/Gateway/shared/native responsibility boundaries and mark future harnesses unexecuted. No new language/framework/runtime/core dependency is selected. Persistent add-operation identity has a present response-loss/idempotency justification; no management/invitation/role system or future infrastructure was introduced.

## Preservation and implementation receipt

Canonical SHA-256 is `33b7b2a0a29b555b8c2842383890ae67fc382286b582b4681d2cd78b9f5829ca`; historical PDF remains `546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510`. Prior ADR/PDF/FAIL/research evidence trees were not rewritten. README, client-gui, client-supplement and done I18N retain exact base-blob prefixes and only append current discovery. Whole `contracts`, `backend`, `clients`, `plugins`, `deploy` tree OIDs equal base, preserving all 185 prior sealed product inputs. This is a byte-preservation audit, not a repeat of their historical runtime semantics or the Coordinator's completed prior final-seal acceptance audit.

Independently verified `implementation/final-receipt.json` SHA-256 `5d8c5563235e458452b7cf8e885e7583c708c339526161db00bd5449ee5acef4`: exact candidate/branch/base/tree/diff, all 74 owned blob IDs/SHA-256, clean final state, clean committed Acceptance exit 0 and source lease RELEASED. Actual external Recorder summaries/events/blobs were checked, including durable snapshots as exact prefixes. Old implementation run remains finished FAIL, 14 starts/13 finishes/one unmatched command; structural validation is not completeness. Resume run is finished PASS, 11/11 paired, structural validation succeeds. One stdout blob differs from its recorded raw hash because redaction is explicitly declared; its redacted durable-byte hash matches. No raw-hash equivalence is invented.

## Verification and limits

Exact argv, timestamps, exit codes, duration, stdout/stderr paths and hashes are in `commands.jsonl`; underlying Recorder evidence is under `research/`.

| Check | Result | Seconds |
| --- | --- | ---: |
| Frozen authority with explicit base86 | exit 0 | 0.360 |
| S2 planning | exit 0 | 0.234 |
| architecture `--scope all --json` | exit 0 | 1.859 |
| architecture unittest discovery | 88 tests, exit 0; 1 existing Windows/POSIX applicability skip | 28.453 |
| CI unittest discovery | 35 tests, exit 0; 4 existing OS applicability skips | 5.859 |
| Clean committed Acceptance | exit 0, exact review HEAD and status 0 | 30.703 |
| Evidence/receipt audit, final corrected run | exit 0 | 5.531 |
| Exact-scope/migration-gap/final-state audit | exit 0 | 0.391 |
| Real classifier on full base..candidate | exit 0, all 14 flags selected | 0.234 |

Two reviewer helper attempts failed visibly before the successful evidence audit: an incorrect external snapshot-directory spelling, then an assertion that failed to distinguish recorded raw hashes from explicitly redacted blob hashes. Failed outputs remain preserved; no repository evidence was edited. Their correction changes the reviewer helper only and does not mask product failures.

Recorder capture is `prospective_resume`, `pre_recorder_work=true`, `pre_recorder_trace_complete=false`: initial mandatory/root/help reads preceded the run; some later direct read-only Get-Content/rg/evidence inspections and external artifact preparation were outside command capture. Some display output was truncated; exact source bytes and captured reads were retained, and affected semantic locations were inspected in smaller reads. This is not a complete prospective trace. Repository tests and final verification commands were recorded. Global Git-ignore permission warnings and applicability skips are not hidden.

No real GROUP contract/PG/NATS/TLS/client runtime, screenshot/Architect, hosted candidate/PR/main job, protected integration or safe-main-sync acceptance was executed by this reviewer. Those remain future work; this FAIL is regular review only, not specialist, Task, Stage Gate or hosted acceptance.

Nonblocking wording advisory: group acceptance line25 says “PNG哈希”; “原始截图文件及SHA-256” would be clearer and format-neutral. It does not explicitly say PNG-only and is subordinate to canonical/client-gui raw-image rules. Earlier tool artifacts include original JPEG, while the final accepted Windows43-image set actually uses native PNG. No evidence establishes a currently forced transcode/rejection, so this is not a blocking finding and is not the reason for FAIL.

Result: **FAIL**, solely for R1. Source lease was never acquired; external evidence will be sealed and released to the Coordinator. Keep GROUP backlog and S2 OPEN; do not submit this candidate to CI.

# LOOP1-GO-AUTH-001 independent Review 2: local PASS

- Reviewer: fresh independent `/root/go_auth_review2`, distinct from implementation, Fix 1, and Review 1 actors. Reviewed exact candidate `c645014eb5964de36cf7c19dc32d8108c58de732` on branch `task/LOOP1-GO-AUTH-001`; repair diff `d035d88..c645014`, original product diff `f187cfa..a93569d`, and cumulative product diff `f187cfa..c645014`.
- Clean method: separate managed detached checkout `H:\.codex\worktrees\go-auth-review2\IM-platform` at exact `c645014`; `git status --short --branch` reported only `## HEAD (no branch)` before and after probes. Strict `tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` passed before and after review, exit 0, zero status entries and zero diff lines. Temporary mutations were restored byte-for-byte. The original `H:\IM-platform` unknown files were untouched.
- This is independent local review PASS, **not task acceptance**. `LOOP1-CI-001` is done, so applicable real hosted CI PASS is mandatory before `done`. S1 Gate remains NOT YET PASSED. Full local Go Compose smoke was not repeated after the disclosed Docker registry mirror HTTP 403; both Compose profile configurations validated, but that is not a running-profile PASS.

## Findings and negative controls

1. Review 1 fixture blocker is closed. The Go suite loads the current canonical Auth/User positive and negative JSON and relevant WSS golden JSON at runtime. It checks HTTP status/body/cookie fields, dynamic UUID/credential consistency, live slot/refresh/logout state, WSS bind/negative frame outcomes and revocation-before-close. Current Auth/User coverage is five positive and fourteen negative scenarios; Friend and message cases belong to later tasks. Existing live integration separately checks NATS-backed `session.revoked`, PostgreSQL transaction rollback, same-slot concurrency, refresh rotation and logout. The fixture runner's direct `hub.revoke` for its golden revoked-socket case is supported by that separate live NATS test, rather than being taken as proof of NATS delivery by itself.
2. Review 1 malformed-ID blocker is closed. `gateway.go` checks UUID shape before dispatching each inbound envelope. Reviewer probe `review2_uuid_mutation_probe.py` temporarily removed that guard; the Go WSS test failed for malformed `ping` with a returned `pong` and malformed `auth.bind` with a returned `auth.ack`. The probe exited 0 only after observing both expected failures, then restored the exact source bytes.
3. Reviewer probe `review2_fixture_mutation_probe.py` temporarily changed canonical `invalid-credentials` expected HTTP status from 401 to 418. The live Go fixture test failed specifically with `status 401, want fixture 418`; the probe exited 0 and restored the exact fixture bytes. This establishes that the Go test consumes and asserts the canonical outcome rather than just parsing the file.
4. Scope and minimality review found no task-blocking expansion. The added Go dependencies serve current PostgreSQL, NATS, bcrypt, and WSS needs. CI replaces the Go placeholder with migrated PostgreSQL/NATS integration and contract verification while retaining the other profile jobs and Gate semantics. `deploy/compose.yaml` changes only the explicitly Human-authorized read-only Go Core/Gateway configuration mount. No architecture, public contract, migration, Java, client, ACK, or future-stage path changed.

## Verification

| Exact command or method | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` in detached checkout, before/after probes | 0 | about 1.4 s each | PASS; exact commit, detached and clean |
| `go -C backend/go test -race -count=1 ./...` without live DB | 0 | 7.516 s | PASS; live cases correctly skipped pending services |
| Canonical `0001_initial.up.sql` piped into `psql` inside disposable PostgreSQL 16 container; host migration runner unavailable because host `psql` is absent | 0 | under 1 s | Schema applied to disposable database only |
| `go -C backend/go test -race -count=1 ./...` with `DB_TEST_ENABLE=1`, migrated disposable PostgreSQL 16 and NATS 2.10 | 0 | 16.187 s | PASS; live canonical HTTP/WSS fixtures, concurrency, rollback, revocation relay, logout |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` | 0 | 6.344 s | PASS; 9 operations, 6 positive, 21 negative artifact scenarios |
| Bundled Python 3 `contracts/websocket/verify.py` | 0 | 0.172 s | PASS; 8 positive, 10 negative golden scenarios |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 0.719 s | PASS; canonical Markdown and PDF hashes match manifest |
| Bundled Python 3 `-m unittest discover -s tests/ci -v` | 0 | 2.218 s | 19 PASS; four real Windows symlink subcases skipped for privilege, mock controls pass |
| Reviewer HTTP fixture mutation probe | 0 | 2.110 s | PASS; expected live test FAIL detected |
| Reviewer WSS UUID-guard mutation probe | 0 | 1.313 s | PASS; both malformed-ID outcomes detected |
| `go -C backend/go vet ./...` | 0 | 0.500 s | PASS |
| `docker compose -f deploy/compose.yaml --profile go config --quiet` and `--profile java config --quiet` | 0 each | under 1 s total | PASS; configuration validation only |
| `git diff --check f187cfa..c645014 -- backend/go deploy/compose.yaml .github/workflows/ci.yml ci tests/ci spec/tasks/review/LOOP1-GO-AUTH-001.md spec/progress/current.md spec/progress/evidence/LOOP1-GO-AUTH-001` | 0 | under 1 s | PASS for editable product and recovery text |
| Bundled Python 3 `tools/research/recorder.py validate-run --run-id R-20260929T151415Z-c0d03dff-1c6a-4238-86b0-96a4f38d19e5` | 0 | 0.157 s | Fix 1 Recorder integrity PASS, 34 events |

Disposable services used loopback PostgreSQL port 53181 and NATS port 53184, with trust authentication on the isolated temporary database. Both were for this review only and are removed at handoff. The host `contracts/database/migrate.py up` attempt exited 1 solely because `psql` is unavailable on Windows; the identical canonical SQL was applied in the PostgreSQL container. The broad `git diff --check f187cfa..c645014` reports whitespace in immutable Recorder raw stdout/stderr and captured diff files; the scoped editable-code check passes. One Recorder-wrapped broad-diff command hit a Windows GBK output-encoding error before `command_finished`; this is exposed, not represented as a product failure or hidden by editing Recorder evidence.

Review Recorder prompt `P-21e00043-b7ec-44bc-adcb-295e98a87204`, run `R-20260929T161307Z-fd438d62-f0ab-4d98-a031-b47933469e3a`, capture mode `prospective_resume`, finished PASS and validated integrity with 29 events. Mandatory startup inspections and first strict Acceptance check preceded `start-run` and are disclosed here. Recorder integrity is separate from task result.

## Recovery

The independent local review result is PASS at candidate `c645014`. Keep `LOOP1-GO-AUTH-001` in `review` until applicable hosted CI is successful at the reviewed candidate/closure and the Coordinator records acceptance. If hosted CI fails, repair through a fresh Fix/Review cycle. Last independently accepted base remains S0 `main` `09cec968f64faf0db319aea8d9c21d4fffe8ec49`. Reviewer owns only this task-linked review evidence, two temporary-probe scripts, Task Spec/current recovery updates, prompt and Recorder artifacts until the review closure commit.

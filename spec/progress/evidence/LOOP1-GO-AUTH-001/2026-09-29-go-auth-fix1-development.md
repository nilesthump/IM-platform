# LOOP1-GO-AUTH-001 Fix 1 development evidence

- Actor: fresh Fix Agent `/root/go_auth_fix1`, after independent Review 1 FAIL at closure `d035d88cc7bafd433375d9b1bd26b35ea8b2e05b`. Branch `task/LOOP1-GO-AUTH-001` in the isolated S1 worktree. This is implementation verification, not independent acceptance or S1 Gate PASS.
- Scope: `backend/go/auth.go`, `backend/go/gateway.go`, new `backend/go/contract_fixture_test.go`, this Task Spec/current recovery record, and task-linked evidence/Research Recorder artifacts. No public contract, migration, frozen architecture, Java, client, CI gate, or original `H:\IM-platform` unknown work was changed.
- Research Recorder: prompt `P-f9f3d76c-f3f5-4a1a-bb0c-a3fcfe87325d`; Fix run `R-20260929T151415Z-c0d03dff-1c6a-4238-86b0-96a4f38d19e5` in `prospective_resume`. Required startup inspections and the first local Go baseline attempt preceded the run; that baseline attempt failed because the read-only sandbox denied Go's temporary build directory. The later Recorder-wrapped baseline passed after write access. Recorder integrity is separate from task acceptance.

## Repair and fixture coverage

- WSS validates the UUID shape of every inbound `requestId` before dispatch. Regression sends malformed IDs in `ping` and `auth.bind` and requires the connection to close without a successful response.
- Go tests load `contracts/fixtures/auth-user-friend/{positive,negative}.json` and `contracts/fixtures/websocket/golden.json` at runtime. They assert canonical HTTP statuses and bodies, secure WEB refresh-cookie attributes, normalized dynamic user/session IDs and credentials, WSS frame bodies, slot state, refresh rotation, logout persistence, and revocation-before-close. The Go CI job already runs `go test` with migrated PostgreSQL and NATS, so these checks execute in that job without changing its gate.
- The runner executes all five current Auth/User positive scenarios and 14 current Auth/User negative scenarios. The `missing-authentication` fixture targets `/v1/friends`, which belongs to the later Friend slice; friend-add and message/send scenarios remain outside this task. Relevant WSS scenarios exercised are valid bind, ping before bind, unauthenticated send, stale epoch, expired token, wrong client type, invalid signature, and revoked socket. The existing live integration test additionally asserts the NATS-backed revocation event and logout WSS closure.
- Canonical execution exposed HTTP error-message mismatches, refresh client-type classification, and signed access-token binding classification. The Go runtime now returns the fixture's outcomes. WSS rejected error messages use the canonical generic `Request rejected` text, without credential content.
- The test normalizer requires real UUIDs, preserves repeated fixture-ID consistency, requires nonempty dynamic credentials, and compares every expected body field. It does not treat fixture artifact verification alone as runtime coverage.

## Verification

| Command / environment | Exit | Result |
| --- | ---: | --- |
| `go -C backend/go test -race -count=1 ./...` with `DB_TEST_ENABLE=1`, canonical migration in isolated PostgreSQL 16, disposable NATS 2.10 | 0 | PASS, 14.263 s final Go output; includes fixture runner, existing concurrency/rollback/Outbox/WSS integration |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` | 0 | PASS, 9 operations, 6 positive and 21 negative contract scenarios |
| bundled Python 3 `contracts/websocket/verify.py` | 0 | PASS, 8 positive and 10 negative golden scenarios |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | PASS, canonical Markdown and historical PDF hashes unchanged |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Development` | 0 | PASS, development mode only |
| bundled Python 3 `-m unittest discover -s tests/ci -v` | 0 | 19 PASS; 4 real Windows symlink subcases skipped for OS privilege, deterministic mock checks passed |
| `go -C backend/go vet ./...` | 0 | PASS |
| `git diff --check` before staging and staged product/recovery-path whitespace check | 0 | PASS for editable code and documentation; captured Recorder output and raw diff preserve their original whitespace |

The disposable database used loopback port 55439 and NATS port 44239. Test-only credentials were environment-local and are not committed. Both containers are removed at handoff. The full local Go Compose smoke was not repeated after the prior Docker mirror HTTP 403; hosted CI and fresh independent clean-checkout review remain required before the task enters `done`.

The linked Recorder stdout/stderr blobs use a run-local `blobs/.gitattributes` rule to preserve their exact bytes through Git checkout. The run finalized PASS and validated with 34 events before staging; its raw output and diff artifacts were not edited to satisfy whitespace checks.

## Next action

Commit the scoped candidate cleanly, delegate a different independent Review Agent, then obtain a real hosted CI PASS. Any Review FAIL starts a fresh Fix/Review cycle. The last independently accepted base remains S0 `main` `09cec968f64faf0db319aea8d9c21d4fffe8ec49`.

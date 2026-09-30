# LOOP1-GO-AUTH-001 independent Review 1: FAIL

- Reviewer: fresh independent `/root/go_auth_review1`; not the implementation or fix actor.
- Reviewed product commit: `a93569d2153e8766c298e11d12ef1549565312b7`; handoff commit `046b0e4e5be5454f95f15f244f40a956a3b532c4` reviewed separately. Branch `task/LOOP1-GO-AUTH-001`; product diff `f187cfa2b7c083447aa5f1694ef8553a9d26758c..a93569d2153e8766c298e11d12ef1549565312b7`.
- Clean method: separate detached managed worktree `H:\.codex\worktrees\go-auth-review\IM-platform` at exactly `a93569d`; `git status --short --branch` reported only `## HEAD (no branch)` before review and after temporary negative probe removal. Strict CTRL-002 Acceptance on that checkout passed, exit 0, reporting zero status entries and zero diff lines. No product files were changed.
- S0 Gate PASS remains the entry state; S1 Gate has not passed. Hosted CI for this candidate has not run. Local Docker API access was denied in this reviewer environment, so full Compose smoke was not repeated; the implementation already disclosed Docker mirror HTTP 403 before service startup. These are unverified limits, not profile PASS.

## Blocking findings

1. **Go integration and CI do not execute the canonical positive and negative fixtures.** The task requires deterministic Go contract/integration tests exercising those fixtures. `backend/go/auth_test.go` contains one handwritten live DB/NATS integration test and two unit tests, with no reader or runner for `contracts/fixtures/auth-user-friend/positive.json`, `negative.json`, or `contracts/fixtures/websocket/golden.json`. The Go CI job invokes `go test` followed by `contracts/websocket/verify.py` and `contracts/http/verify-auth-user-friend.ps1`; those latter scripts validate the contract artifacts, not Go runtime outcomes. Thus both verifiers and the Go test can pass while a canonical scenario diverges. Add a Go profile fixture runner for the current Auth/Session and WSS slice, normalize dynamic IDs/tokens, and assert positive and negative responses/state against canonical expected outcomes in CI. Future social/message scenarios remain outside this task.
2. **WSS accepts a malformed envelope ID.** `contracts/websocket/envelope.schema.json` defines `requestId` as UUID for `ping` and `pong`; `backend/go/gateway.go` checks only `e.RequestID != ""` before echoing it. An independent temporary Go test sent `{"protocolVersion":"1.0","type":"ping","requestId":"not-a-uuid","payload":{}}` and received a successful `pong` with the same invalid ID. The focused probe command exited 1 as expected. Reject non-UUID IDs and cover the negative control in the Go suite. This is a public contract mismatch, not an instruction to change the contract.

## Verification

| Exact command in detached checkout | Exit | Elapsed | Result |
| --- | ---: | ---: | --- |
| `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance` | 0 | about 1.8 s | PASS, clean committed recovery (run before Recorder start) |
| `go -C backend/go test -race -count=1 ./...` | 0 | 10.375 s | Unit tests PASS; live PostgreSQL/NATS integration skipped because `DB_TEST_ENABLE` was unset |
| `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1` | 0 | 7.766 s | Contract artifact PASS: 9 operations, 6 positive and 21 negative scenarios; not runtime execution |
| `python3 contracts/websocket/verify.py` via bundled Python 3 | 0 | 0.109 s | Contract artifact PASS: 8 positive, 10 negative scenarios; not runtime execution |
| `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1` | 0 | 0.875 s | Canonical Markdown and historical PDF hashes PASS |
| `go -C backend/go test -run TestReviewMalformedRequestIDRejected -count=1 ./...` with temporary reviewer probe | 1 | 2.516 s | Expected FAIL: malformed UUID received successful `pong`; probe removed afterward |
| Bundled Python 3 `-m unittest discover -s tests/ci -v` | 0 | 3.218 s | 19 tests PASS; 4 real symlink subcases skipped on Windows |
| Bundled Python 3 `tools/research/recorder.py validate-run --run-id R-20260929T113637Z-033a1064-c4d8-4276-b309-717762d4d6ab` | 0 | not recorded | Implementation Recorder integrity PASS, 30 events |

The reviewer Recorder `R-20260929T143107Z-279b7a3e-f218-418d-925a-5a7f42e4421e` finished `FAIL` and validated with 16 events. Prompt `P-d08c2d61-de17-4dcc-8706-8b35cd6dbb3a`. Its command events contain exact executable paths, outputs, exit codes and durations. **Recorder limitation:** startup inspection and the first CTRL-002 baseline check preceded `start-run`, while its metadata says `prospective` and `pre_recorder_trace_complete=true`. That field overstates the visible trace; these activities are explicitly disclosed here, and the Recorder artifacts were not edited to conceal it. Recorder integrity PASS is separate from this Task FAIL.

## Recovery

Leave task in `review`. Coordinator delegates a fresh Fix Agent for the two findings, then a new independent reviewer of a clean committed candidate. Real hosted CI remains mandatory before `done`. Last independently accepted base is clean S0 `main` `09cec968f64faf0db319aea8d9c21d4fffe8ec49`. Reviewer owns only this evidence, Task Spec/current recovery, and linked prompt/Recorder artifacts until the review closure commit; the detached product checkout is clean and the original `H:\IM-platform` untracked files were untouched.

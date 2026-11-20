# Human decision and scoped Go conformance

At b61b7df2b4be36dd2954c990e4f8a4d29526ea05 the worktree contained the Java repair and a documented divergence. The original review FAIL, pre-fix experiment and previous blocked record are preserved in that commit and the current task evidence directory. The Human resolved the question with this instruction:

> 沿用小写契约，授权本轮仅修复 Go 的 message.send 校验并补双后端回归

Recorder decision HD-b1cd1d33-9ebf-402c-a507-1f3522f7d39f, run R-20261120T131112Z-50e7ee21-4d99-492f-9802-1e4963e4e1f4. This authorizes existing-contract conformance in Go message.send and a shared regression. The task allows two Go product files for that purpose.

Go Gateway checks an inbound message.send request ID before bind rejection or forwarding. An invalid correlation uses the existing malformed-envelope connection close. A canonical request can only receive an ACK with the exact correlation string. Go Core returns HTTP 400 on its private adapter when it has no valid correlation. With a valid request ID and an invalid conversation ID it returns the existing VALIDATION_FAILED rejection before the transaction. Successful storage and ACK use the already validated canonical IDs. No new production catch or fallback. The existing transport-close path is used solely because the malformed request provides no admissible public correlation value.

The same HTTPS/WSS Compose regression runs on Java and Go. With an authenticated member it sends an uppercase request ID, requires close without an ACK, sends an invalid uppercase conversation ID with a canonical request ID and requires the correlated VALIDATION_FAILED response, then verifies zero message and Outbox rows and the unconsumed first sequence. A subsequent lowercase spelling of the original request commits once at sequence 1, echoes the exact lowercase ID and reaches the authorized recipient. Existing idempotent replay and conflict checks use this same identity.

| Local verification | Exit | Duration |
| --- | --- | --- |
| gofmt -l backend/go/core/message.go backend/go/gateway/gateway.go | 0, empty after formatting | 0.016 s |
| python -Xutf8 -B tools/verify_java_im.py --build-dir EXTERNAL | 0, final Java/Go/Java | 74.391 s |
| go -C backend/go build ./... | 0 | 1.781 s |
| go -C backend/go vet ./... | 0 | 4.656 s |
| go -C backend/go test -count=1 ./... | 0 | 30.359 s |
| go -C backend/go test -race -count=1 ./... | 0 | 102.812 s |
| python -Xutf8 -B tests/e2e/go_tls_messaging.py --profile go | 0 | 35.297 s |
| python -Xutf8 -B tests/e2e/go_tls_messaging.py --profile java | 0 | 150.906 s |
| python -Xutf8 -B ci/check_architecture.py --scope all --json | 0, no violations | 1.047 s |
| python -Xutf8 -B -m unittest discover -s tests/architecture | 0, 99 tests, 1 skip | 23.016 s |
| python -Xutf8 -B contracts/websocket/verify.py | 0 | 0.094 s |
| pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1 | 0 | 7.578 s |

The pre-fix Java and Go wire results are in uuid-case-observations.json. Java checks and timestamp controls are in fix5.md. Both fresh final-SHA reviews, applicable exact-head hosted CI, protected integration and actual-main synchronization remain pending. S3 OPEN. Owner /root/fix5 on task/LOOP1-JAVA-IM-001. Last accepted main 18597c06f15c6ba5d50e055a88890a54f737fd52.

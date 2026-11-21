# Local parity implementation evidence

Branch `task/LOOP1-PARITY-001`, base PR108 `3a5a54abff6410762d2039c4acf880abbe3269a5`, managed root `H:/.codex/worktrees/p/IM-platform`. Research run `R-20261121T071251Z-73a87b54-7ed4-4c4b-8f21-d068534623fb`. The Java IM implementation, S1 and S2 were independently accepted before this change.

## Golden coverage and client behavior

| S3 behavior | Same check on Go and Java |
| --- | --- |
| Session, Auth, invalid credentials, unsupported version, authorization and rotation | Existing Java CI invokes `tools/verify_java_auth.py` on both profiles and checks same-database profile switch. Its runner consumes canonical Auth positive and negative fixtures. |
| Group operations, membership and idempotency | Existing `tools/verify_java_im.py` executes GroupFixtures on both profiles and checks persisted state across switches. |
| Friend/DIRECT uniqueness, durable ACK and Outbox, retry/conflict, forbidden send, rollback and revocation | `tests/e2e/parity.py` invokes the existing TLS messaging fixture and its canonical expected-response oracle separately for both deployments. |
| Paged Sync and recovery | Both execute `tools/verify_sync_runtime.py` against strict HTTPS, real committed messages, pagination/terminal pages, replay, foreign conversation, version and cursor checks. |
| Same client | One npm-locked production Web build, with a SHA-256 inventory digest verified after each deployment. The same emitted WebClient (the GUI's application entry for protocol operations) uses its default fetch/WebSocket transports. Two independent client instances login, find/add a friend, synchronize DIRECT and GROUP membership, send and receive the same committed message identity and ordered sequence, synchronize the visible conversation, and logout. |

The WebClient exercise runs in Node with the disposable public root CA, without a browser renderer. No GUI or protocol code changed. ADR-0004 defers only `friend-add-authorization-denied`. The live plugin permission cases in §11.3 belong to the S4 runtime and permission Gate under §§15/20.

## Local commands

- `python -Xutf8 -B tools/verify_frozen_architecture.py` and `python -Xutf8 -B ci/check_architecture.py --scope all --json` passed. Canonical Markdown SHA-256 a52e871d4f48708c1fa7e06ea2e4ffae3922a93a9be6128cb79b3292b6b36bef, historical PDF 546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510.
- `python -Xutf8 -B -m unittest discover -s tests/architecture -q` passed 99 run, one platform skip. The first attempt rejected prose in the allowed-path list. The final task declares one parseable path per entry.
- `python -Xutf8 -B -m unittest discover -s tests/ci -q` passed 41 run, four platform skips. `python -Xutf8 -B -m unittest discover -s tests/clients/web -q` passed 14 run. `git diff --check` passed.
- `python -Xutf8 -B tests/e2e/parity.py` passed in 106.425 seconds. Both real Compose profiles passed the same observable checks and verified the unchanged digest `58bc0ef831639eecea2a71fec77db588a5b32a93e13efe05b96aebcb6b017577`. Both disposed their owned containers and volumes.
- `python -Xutf8 -B tools/verify_sync_runtime.py --profile go` and `--profile java` each passed with 208 user events and 205 durable WSS messages, paging, replay, negative cases and owned-project cleanup.

## Handoff

Implementation complete locally. Fresh independent regular Review and subsequent distinct error-handling audit are pending on the committed candidate. Hosted candidate/pull-request/actual-main results and safe synchronization remain pending. The last known good main is PR108. S3 remains OPEN.

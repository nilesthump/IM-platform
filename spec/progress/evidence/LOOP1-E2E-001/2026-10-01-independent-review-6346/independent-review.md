# Independent S1 E2E candidate review

Result: PASS for exact `6346f39fc6786bba3cddbde7acc91bbad42446a1`, branch `task/LOOP1-E2E-001`. Full review range actual main `b442acd26777c481620a6bd917863cebfaf79b35..6346f39fc6786bba3cddbde7acc91bbad42446a1`.

Independent actor `/root/s1_e2e_review` neither implemented nor fixed candidate product. Reviewed clean detached committed checkout `H:/.codex/worktrees/s1-e2e-review-6346`; own evidence outside checkout. Initial and final actual status empty; Acceptance recovered unique E2E review task with zero diff. Recorder initial snapshot used original checkout while creation was recorded; clean acceptance is the isolated exact candidate, never the dirty original.

No actionable correctness, scope, architecture, security or minimality findings. Actual inherited MSG reviewed, not merely old PASS: Core owns authorization/session-write/transaction/seq/message/singleOutbox; Session and membership locks last through COMMIT; ACK follows actual COMMIT. Gateway forwards bound bearer/canonical frame and local NATS user fanout, no membership/persistence business. Rejected conflict preserves prior origin; private history requires present nonnegative integer afterSeq. Main assembly only selects roles and connects modules. No service internal cross-import or shared Auth business. Contract/schema/frozen hashes unchanged.

E2E adds only standard-library test harness+README, two-line existing deploy step, exact E2E classification and positive/deleted tests; no new job/dependency/service/framework. Fixture Oracle normalizes runtime UUIDs/timestamps while retaining exact keys/scalars and stable identities. SQL uses validated generated UUID identity in owned disposable DB. TLS CERT_REQUIRED/check_hostname remains enabled for HTTPS/WSS. Only public Caddy CA copied. UntrustedCA uses actual client certificate error; wrong hostname accepts only client SSLCertVerificationError codes62/64. Temporary owned Caddy fallback_sni localhost serves existing cert only during negative handshake; finally exact originalJSON restored/asserted before business. Current failure evidence and official option semantics justify this smallest test setup: https://caddyserver.com/docs/caddyfile/options#fallback-sni . No production proxy edit or relaxed positive trust.

Actual deferred constraint trigger fails COMMIT through TLS/WSS and must yield canonical MESSAGE_COMMIT_FAILED, no message/outbox/sequence advance or delivery; scoped by exact generated request+conversation and removed in finally. Independent SQL confirms hello identity/singleMessage/singleOutbox/seq before success observation; existing blockedCOMMIT test independently proves ACK timing. Receiving socket after ACK read adds no cross-socket ordering promise. Stable retry/conflict/nonmember/replacement/logout/staletoken executed; only named friend403 remains DEFERRED_BY_HUMAN, not PASS.

Local verification (exact argv, exits and elapsed seconds in commands.json; raw bytes and Recorder blobs retained):
- `git -c core.excludesFile=.git/info/exclude status --porcelain=v1 --untracked-files=all`: exit 0, 0.157s.
- `git rev-parse HEAD`: exit 0, 0.125s.
- `git diff --name-status 0d4df7a..HEAD`: exit 0, 0.187s.
- `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B contracts/websocket/verify.py`: exit 0, 0.172s.
- `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B ci/check_architecture.py --scope all --json`: exit 0, 2.156s.
- `pwsh -NoProfile -File tools/verify-loop1-ctrl-002.ps1 -Mode Acceptance`: exit 0, 6.0s.
- `pwsh -NoProfile -File tools/verify-frozen-architecture.ps1`: exit 0, 5.328s.
- `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest discover -s tests/architecture -v`: exit 0, 4.907s.
- `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B -m unittest discover -s tests/ci -v`: exit 0, 2.859s.
- `pwsh -NoProfile -File contracts/http/verify-auth-user-friend.ps1`: exit 0, 6.297s.
- `go -C backend/go build ./...`: exit 0, 1.297s.
- `go -C backend/go vet ./...`: exit 0, 0.844s.
- `gofmt -l backend/go`: exit 0, 0.14s.
- `C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -B tests/e2e/go_tls_messaging.py`: exit 0, 36.156s.
- `go -C backend/go test -count=1 -v ./...`: exit 0, 21.156s.
- `go -C backend/go test -race -count=1 -v ./...`: exit 0, 84.203s.

Go normal/race use DB_TEST_ENABLE=1, actual isolated PostgreSQL16 at127.0.0.1:55661 DBs1_e2e_review and NATS2.10 at127.0.0.1:42661, unchanged canonical0001 migrated via owned PostgreSQL client. Both zero runtime SKIP. Actual ACK-blockedCOMMIT/rollback/identity/dup/outorder/Sync/GROUP500/Auth/Social/Session/revocationfallback and delayedorigin tests executed. Local architecture34 and CI29 pass; exactly4 Windows symlink subcase skips reported and independently covered by both hosted Linux29 (no skips), never hidden as integration PASS. gofmt stdout empty.

Cleanup: strictTLS harness owned Compose cleanup PASS. Reviewer regression cleanup first conservatively aborted because docker ps returns shortIDs while inspect returns fullIDs; preserve original review.py failure and commands21-23. New cleanup.py resolves all real fullIDs, confirms exact owner label and exclusive volume binding, removes only those two containers/anonymous volume, then asserts absent services and clean candidate. No product candidate fix. Initial register-prompt --run-id before run creation produced exit2 after prompt persisted; subsequent start succeeded, current prompt/run linkage valid. Both instrumentation/setup failures are public warning events, not erased.

Hosted independent direct API acceptance: push36831979992 and PR36832052224 exact6346 each all13 required jobs completedSUCCESS: classify, architecture, source_go, source_java, go, java, web, desktop, mobile, shared, compatibility, deploy, gate. CI path modifications correctly select all current obligations; old_client/plugin/migration are represented by compatibility, no nonexistent standalone-job claim. Direct job JSON and full logs retained; LinuxCI29 with zero symlinkSKIP and actual strictTLS fixture/revocation/cleanup PASS. Not inferred from gate/overall status.

PR5 https://github.com/nilesthump/IM-platform/pull/5 head6346/baseb442. Virtual merge2dbe328b310e0b3328681d8cb629bd5c6fd40147 parents exactly[b442acd26777c481620a6bd917863cebfaf79b35,6346f39fc6786bba3cddbde7acc91bbad42446a1], tree87ca7df8c0a9284f64af00ce06f5289bcea91662 equals exact candidate tree. New PR only; PR4 not merged. This review does not accept later administrative state commits or actual main merge; those require applicable independent acceptance. No task queue mutation, S1 closure, S2 implementation, push or merge by Reviewer.

Preservation: all4988 existing research/evidence blobs atactivation match candidate by Git blobOID; frozenMarkdown SHA83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e and historicalPDF SHA546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510 match authority. Independent original H:/IM-platform605 file sizes/SHA256 PASS against historical inventory using only human-approved one-file relocation, no writes or ownership inference. Existing301 archive and historicalFAIL/partial remain within unchanged history; current4 failed E2E/rawCRCRLF preserved in candidate.

Recorder R-E2E-REVIEW-6346 / P-E2E-REVIEW-6346 external research root, prospective_resume, pre_recorder_work=true/pre_recorder_trace_complete=false: earlier read-only preparation/formal startup incomplete, never full prospective. FinishedPASS/validated structurally; Research PASS distinct from this exact Task candidate acceptance and Stage Gate. This report and final transport manifest are generated after finish, outside immutable Recorder trace. External artifacts only; Coordinator may archive exact bytes, later administrative commits need fresh review/exactCI.

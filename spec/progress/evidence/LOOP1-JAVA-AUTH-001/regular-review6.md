# Independent regular review

FAIL. Candidate 7679f24a848cf167a214311b3fbb83a5511ffdd5, base e4aee5ce2c4327904990d5c651267ca5eaae389d, branch task/LOOP1-JAVA-AUTH-001, assigned Git root H:/.codex/worktrees/j/IM-platform. Reviewer /root/review_fatal_regular is a fresh independent agent who did not implement, fix, previously review or integrate this candidate. All review artifacts are external to the repository.

## Blocking finding

**P1. Java Gateway broadcasts a false Session revocation to refreshed connections.** In backend/java/gateway/auth/Gateway.java:151, expiry of one connection's access token calls revoke for its entire Session. Lines 82–89 remove every registration with that Session ID and send session.revoked followed by close. The post-bind recheck at line 148 also sends a Session-wide revocation for any ApiFailure, including AUTH_TOKEN_EXPIRED. An ordinary successful refresh preserves the Session ID and epoch, changes the refresh hash and issues a new access token in CoreAuth.java:138–141. A second connection bound with the new token can therefore be retired, while its authentication is current and the authoritative database slot is ACTIVE. The existing web client clears the active login on that event (clients/web/src/application/client.ts:42). The contract distinguishes access-token expiry and Session invalidation. Frozen §4.1/7.1–7.3, AUF-D-004, and the refresh HTTP operations preserve PostgreSQL Session authority.

Restrict credential-expiry handling to the affected connection, including the post-bind check. Keep Session-wide delivery for actual Session invalidation. Add an ordinary regression using two connections with different token expiries for the same still-active Session. Check that the refreshed peer remains bound until real logout or replacement, and that genuine revocation still closes it. The older Go watcher also fans out known token-check failures (backend/go/gateway/gateway.go:232 onward); only complete-frame decoding is currently authorized as a Go product edit. This observation does not authorize a wider Go change. The finding is based on source inspection. No vulnerability reproduction was run.

## Scope and verification

Reviewed full change range, canonical document hashes, accepted ADR-0014 and scoped ADR-0004 deferral, source ownership and fixture authority. Core owns slot mutations, refresh hash rotation and transactional Session Outbox; Gateway performs readonly validation, caches socket registrations, forwards HTTP and subscribes to Session events. Main selects roles. Shared config, token and BCrypt primitives avoid service imports. Maven dependencies trace to the frozen Java stack. No new public contract, schema migration or cross-service dependency. Scoping the Spring external JDBC namespace retains declaration checks. The Dockerfile stages specific source/build inputs and Compose mounts operator configuration. The Go change retains the frame size limit and checks whole-message JSON. The common live runner reads authoritative fixtures, checks status/body/header/state, real DB binding/rotation and WSS outputs, exercises the two profiles sequentially, and excludes later-stage scenarios. The second disposable DB exists to establish mismatched ownership with a genuine issued token.

Both prior specialist findings are resolved in this candidate. An independent run of both packaged roles observed normal shutdown exit 0 and actual interrupted-worker exit 1 with redacted class diagnostic within the configured 30-second bound. A separate thread initiates JVM shutdown so the Spring hook can join the failed worker. Both rejection paths preserve the primary send throwable and suppress the cleanup throwable using try-with-resources. Live Outbox rollback/retry and peer retirement cases also passed. These narrowly scoped changes add no new product dependency. The four process checks and rejection controls execute from the normal Java verifier.

Exact command argv and environment derivation are recorded in checks.py, with numbered result and wall time below. All profile runs use migrated PostgreSQL plus NATS; the issuer DB is distinct from the target. The pre-existing architecture suite has one platform-conditional skip and CI unit discovery has four existing skips. TLS deployment smoke on these bytes is separate coordinator evidence in lifecycle-local-tls.json. I did not independently rerun deployment smoke.

RESULT 0 exit 0 elapsed 0.343
RESULT 1 exit 0 elapsed 1.141
RESULT 2 exit 0 elapsed 20.328
RESULT 3 exit 0 elapsed 9.563
RESULT 4 exit 0 elapsed 0.172
RESULT 5 exit 0 elapsed 6.031
RESULT 6 exit 0 elapsed 23.844
RESULT 7 exit 1 elapsed 3.704
RESULT 7 exit 0 elapsed 5.828
RESULT 8 exit 0 elapsed 91.875
RESULT 9 exit 0 elapsed 10.641
RESULT 10 exit 0 elapsed 39.812

Check indexes 0–6 are frozen hash, all source boundaries, architecture tests, CI tests, WSS contract, HTTP contract and clean Control Acceptance. Index 7 is offline Maven verify plus dependency classpath. The original cache-access failure was retained and the approved retry built and tested successfully. Indexes 8–10 are Java (28 fixtures), Go (28 fixtures) and credential switching in both directions. Input SHA-256 manifest input-hashes.json hashes surviving changed checkout paths, SHA-256 806e4ffd35d33e658dc0850ff7a06c309c5a0300df5d7393ed3bcf8239d7f6c3. Removed paths remain in the Git diff. Clean root/HEAD confirmed before and after verification. The Research Recorder used prospective_resume for pre-capture startup, including an initial unavailable Python 3 command from PATH. Manual source reads were performed separately, including corrected PowerShell path filters. Full command records are in research/runs/R-NOV18-FINAL-REGULAR. Retain review state. Fresh fix and two fresh reviews of its resulting commit are required before submission to hosted CI; S3 remains open.

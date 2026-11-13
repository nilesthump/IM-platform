# Implementer catch and failure inventory (not independent Review)

This record explains present behavior for the mandatory fresh specialist. It does not accept the candidate. Source hashes are in `source-inventory.json`.

| Location | Concrete input/failure | Current basis and outcome |
| --- | --- | --- |
| Main role/config startup | Unknown role, missing config, failed role/NATS startup | Propagates and process startup fails. No fallback role/config. |
| Main default worker handler | Uncaught worker defect | Reports exception type and exits1. It cannot be classified as a valid Auth result or silently continue. |
| Main context-close InterruptedException | Shutdown wait interrupted | Restores interrupt and propagates cause in IllegalStateException. |
| Config | JSON/file/config/secret/driver errors | No catch/default credential; startup fails. File credentials are never printed by task tools. |
| Tokens SHA/HMAC checked crypto errors | Required JDK primitive unavailable/invalid initialization | Preserves cause and fails via IllegalStateException; no alternative algorithm. |
| Tokens Base64 decode IllegalArgumentException | Untrusted malformed token encoding, narrow decode block only | Canonical AUTH_TOKEN_INVALID. SQL/mapper/callback errors are outside this catch. |
| Tokens JsonProcessingException | Untrusted malformed signed payload JSON | Canonical AUTH_TOKEN_INVALID. Other IOException is UncheckedIOException, preserving unknown failure. |
| PasswordHash | Wrong password versus malformed stored BCrypt | Direct approved BCrypt primitive; wrong password false, malformed persisted salt propagates. Unit and real HTTP500 corruption probe verify distinction. No custom crypto/normalizing corrupt hashes. |
| CoreAuth JsonProcessingException | Invalid request JSON | Canonical VALIDATION_FAILED. Body stream I/O propagates. |
| CoreAuth ApiFailure handler | Explicit known validation/auth/session errors | Projects canonical status/code/message. No catch-all SQLException/RuntimeException projection. |
| CoreAuth unique registration conflict | PostgreSQL username conflict only | ON CONFLICT(username) DO NOTHING maps zero insertion to409. Other uniqueness/internal SQL failures propagate. |
| CoreAuth transactions | Login replacement/refresh/logout failure | Spring transaction rollback spans Session write and required event records. Missing invariant rows are failures, not fake defaults. |
| SessionOutbox NATS status | Reconnecting/disconnected connection before batch | Keeps rows pending; next existing500ms tick checks status. No fake publication. |
| SessionOutbox flush TimeoutException | Actual flush did not confirm publication | Cause preserved, transaction rolls back, worker fails/process exits1. No published_at update. |
| SessionOutbox flush InterruptedException | Flush interrupted | Restores interrupt, rollback and explicit worker failure. Normal close sets stopping and joins without interrupting an in-flight publish. |
| SessionOutbox worker sleep InterruptedException | Unexpected interruption | Unless stopping, restores interrupt and fails; no blanket batch catch. Closed-NATS real-connection probe demonstrates pending SQL state. |
| Gateway subscription InterruptedException | Explicit destroy interrupts blocking receive | Stops only when stopping flag is set; otherwise failure propagates. |
| Gateway subscription IOException | Malformed committed event JSON or socket send I/O | Preserves cause in UncheckedIOException and worker fails. No silently dropped committed event or fabricated delivery success. |
| Gateway malformed WebSocket JSON | Known JsonProcessingException from client frame | Closes BAD_DATA. Other implementation errors propagate through WebSocket failure path. |
| Gateway bind ApiFailure | Known token/readonly Session rejection | Canonical auth.ack rejection then close. SQL/internal errors are not auth rejection. |
| Gateway post-insert validation ApiFailure | Concurrent revocation/replacement during bind | Sends session.revoked and closes the registered binding; no stale cached authority. |
| Gateway close cleanup | Revoke/reject or role destroy | Attempts actual socket close; failures remain failures. No normal-state fallback. |
| Python readiness | Connection/URL transport unavailable during startup | Bounded60/120s retry; exited roles immediately fail; timeout fails. No live test skips. |
| Python role cleanup | Exit/stop failure | Exit is checked for Go fixture host; Java owned processes terminate/wait; cleanup errors propagate. Original exceptions remain chained by Python. |
| Fixture mutation controls | Deliberately changed expected code/input | Catch only AssertionError and require the intended mismatch reason; inability to detect mutation fails. |
| Fixture post-revoke write | ExecutionException from actual WebSocket send | Only IOException with output already closed satisfies failed-send expectation; otherwise rethrow. Still requires terminal observation. |
| Fixture terminal observation | Go abrupt TCP close without protocol close frame | Accepts close callback, or IOException only with both JDK input/output closed. Unknown errors/timeout/additional application frame fail. Event is asserted first; no client abort before closure proof; message persistence unchanged. |
| TLS smoke cleanup | Compose shutdown fails after primary failure | Existing script preserves primary exception and reports cleanup failure. .NET static test-only certificate callback avoids background PowerShell Runspace failure. |

No production catch broadens scope to classify unknown database/callback defects as authentication, networking, or success. The fresh independent specialist must still inspect every source file, including files with no catches, and final SHA semantics.

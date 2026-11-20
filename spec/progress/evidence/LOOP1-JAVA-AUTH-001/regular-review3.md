# Independent regular Review: FAIL

Reviewer: /root/java_auth_review3, fresh context with no implementation or Fix participation. Candidate `3b8f79049e03f6934ba6b1f5b8056d761e3007ef`, branch `task/LOOP1-JAVA-AUTH-001`, entire range `e4aee5ce2c4327904990d5c651267ca5eaae389d..3b8f79049e03f6934ba6b1f5b8056d761e3007ef`. Assigned root `H:/.codex/worktrees/j/IM-platform`; exact HEAD and clean status verified. This report is independent regular review, not the required distinct error specialist or hosted acceptance.

## Required correction

**P1 — Ordinary peer disconnect during Session revocation can terminate the entire Gateway.** In `backend/java/gateway/auth/Gateway.java`, `revoke` removes the matching socket, calls `send` and closes it in finally. A socket-write/close IOException escapes the loop to the Session notification thread's catch, which wraps it in UncheckedIOException. `backend/java/Main.java` installs a default uncaught handler that calls System.exit(1). Consequently a client disconnect racing logout/replacement can abort notification of the remaining sockets and terminate unrelated live sessions. The failure is a known per-connection transport outcome, not an unknown programming/database/committed-event invariant failure.

Canonical §3.1/§7.2–7.3 assign Gateway per-connection lifecycle and Session revocation; §11.2 requires equivalent observable behavior. `spec/governance/error-handling.md` explicitly permits the current recovery of closing a connection after a write failure, while requiring unknown failures to propagate. The Go reference `connection.send`/`hub.revoke` scopes transport cleanup to the affected connection and proceeds with other connections. This reference corroborates existing behavior; it is not new contract authority.

Use a narrow known socket-transport failure boundary around revocation delivery/cleanup so the affected connection is definitively retired and other connections continue. Keep serialization/internal defects and malformed committed events outside that recoverable boundary; do not add a broad event-loop catch or pretend successful delivery. Add an ordinary disconnect-during-revocation regression establishing that the Gateway stays available and another bound connection receives its required notification/close. Update the retained-catch inventory to explain this concrete failure/recovery. This is a static control-flow finding, not a claimed runtime reproduction or an offensive probe.

## Reviewed scope

Read the complete CoreAuth, Gateway, SessionOutbox, Main, shared config/token/password primitives, health role, dependency declarations, shared Auth fixture harness, NATS recovery test, Python orchestrator, Go bootstrap and Go Gateway delta, deployment/CI changes and canonical HTTP/WSS/error schemas. Authority hashes were checked in preparation and the final frozen verifier passes. The task remains uniquely in review; S3 remains OPEN.

Core retains Auth/Session transaction ownership; Gateway validation is readonly; shared code contains primitives only. BCrypt stays the approved primitive with the existing prehash. No ORM or authentication framework is introduced. The approved JDBC namespace checker exception preserves prior local declaration ownership checks. The Task explicitly includes the Coordinator-authorized Go complete-message JSON correction; its six-line delta retains the existing limits and routing/ACK behavior. No contracts or schema migrations change.

The previous three findings are addressed in source and existing normal application verification: the committed CI preparation rewrites and saves the smoke Origin18444, with removal controls; both Gateway parsers consume the complete JSON document; WSS send boundaries collect credentials, incoming frames exclude secrets and the exported inventory drives actual role-log checks. Literal WSS-only and derived tokens pass through the same collection; response/frame/log controls remain explicit mutations rather than claims of production leakage. No new offensive or vulnerability probes were created in this review.

Earlier timeout recovery/TTL/origin/scalar fixes remain bounded. The flush wrapper is produced only for known TimeoutException and retries through the existing tick after rollback; other worker failures remain visible. The small synchronous test client and delayed-PONG test have present justification from observed acceptance gaps, without new product abstractions.

## Independent verification

- Fresh offline Maven build: PASS, 5 tests, zero skips.
- Existing Java live suite: PASS all28 cases, canonical input/expected controls, actual Session/NATS revocation, malformed persisted BCrypt500, lost-event reconnect, complete-JSON/scalar/disclosure controls.
- Existing real Outbox tests: pending rollback, delayed-PONG same-worker recovery and non-publication worker failure visibility PASS. Nondefault73/419 token duration checks PASS.
- Same Go live suite: PASS all28 cases and terminal closure checks. Sequential same-database credential compatibility PASS in both directions.
- Source-all checker and frozen verifier PASS; CI suite39 PASS with4 documented platform symlink skips.
- Command argv, actual exit codes, elapsed time and output hashes are retained in Recorder `research/runs/R-JAVA-REVIEW3-FINAL`. Input hashes and exported command records accompany this report. The combined normal verification command completed exit0; that does not cancel the static P1 finding.
- Fresh TLS/architecture-full/Control checks were not repeated after the conclusive source finding. Parent supplied separate Control/TLS evidence, not represented as this review's independent execution. Hosted CI, distinct specialist, protected integration and main synchronization remain pending.

## Recovery / instrumentation

No repository writes, pushes or service provisioning were performed. Existing harness cleanup ended its role processes; root-owned PostgreSQL/NATS remain untouched in ownership. External runtime folders contain disposable secrets and must not be published wholesale. Initial direct reads and supplementary source reads were outside full Recorder coverage; prospective_resume records this limitation. An initial read of nonexistent fix2.md failed; actual evidence filenames are fix2-stop.md and fix2-resume-20261118.md. No failed record was erased or relabeled.

Next: fresh Fix, then entirely new regular reviewer and distinct error specialist on the final new SHA. Do not publish the rejected candidate. Recorder validation is not Task or Stage acceptance.

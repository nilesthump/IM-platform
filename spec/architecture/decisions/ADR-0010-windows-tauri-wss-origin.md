# ADR-0010: Windows Tauri WSS Origin exception

Status: Human-approved frozen decision candidate; independent Review and applicable exact-head hosted CI pending. No product implementation yet. Date: 2026-10-08. Task: LOOP1-CLIENT-GUI-001. Exact Human approval and bounded path expansion: spec/progress/evidence/LOOP1-CLIENT-GUI-001/windows-origin20261008/approval.json.

## Present requirement and observed failure

Accepted GUI/native requirements require real Windows Tauri WSS SEND/reconnect with existing Go Gateway. Actual installed native Login/profile/HTTP Sync succeeds under default system TLS in the actual desktop Explorer context. Controlled default-TLS ClientWebSocket opens with absent Origin; identical endpoint with Origin http://tauri.localhost rejects403. Gateway currently uses gorilla websocket.Upgrader{} default same-host check. Windows Tauri2 production origin is http://tauri.localhost; required native client is cross-host to the authenticated localhost Gateway. Evidence default-tls.json/wss-origin.json and reviewable proposal.diff. Source responsibility remains Gateway connection/transport admission, separate from Core business.

## Approved narrow decision

Allow exactly the serialized Origin http://tauri.localhost in Go Gateway WebSocket upgrade. Preserve existing absent-Origin and same-host behaviors, reject unrelated cross-host origins, and retain mandatory auth.bind, token/session/authorization, query-token prohibition, protocol parsing, TLS/hostname checks, durable ACK/retry/Sync semantics. This is an explicit bounded security admission exception; an Origin never establishes identity or authorization.

No wildcard origins, blanket CheckOrigin=true, reverse-proxy Origin stripping, TLS bypass, credential cookies or query tokens, backend HTTP/CORS replacement auth/Sync entry point, new native WSS adapter/dependency, alternate frontend host or future-platform origins. Existing approved Go/gorilla/Tauri/TypeScript choices and source direction remain; no new dependency/framework, public API/schema, storage migration or ACK change.

## Implementation scope and acceptance

Human explicitly expands current Task allowed_paths to this decision record, backend/go/gateway/gateway.go and focused backend/go/gateway/origin_test.go, in addition to existing GUI/evidence/recovery paths. Canonical Markdown/PDF/version and contracts remain byte-frozen. Independently Review this exact decision candidate and its applicable exact-head hosted checks before dependent product implementation; no local statement is hosted acceptance. New product fix receives a fresh independent reviewer and existing GUI full acceptance/protected integration/actual-main/safe synchronization chain before Task done.

Focused tests must prove absent/same-host/Tauri upgrade acceptance and unrelated or lookalike host rejection, while accepted connections still need auth.bind. Actual native Windows must bind and demonstrate committed SEND, unchanged retry identity/convergence and reconnect under default TLS; existing gateway auth/protocol checks remain applicable. Screenshots alone do not establish ACK semantics.

Rollback removes only this exact Origin admission exception after approval and independent acceptance; no data migration. Broader Origin or native transport changes require a new decision. S2 remains OPEN. Before authority candidate acceptance affected repair is BLOCKED_BY_ARCHITECTURE; unaffected verification may continue.

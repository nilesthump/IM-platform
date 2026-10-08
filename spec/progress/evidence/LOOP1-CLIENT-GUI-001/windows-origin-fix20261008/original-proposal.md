# Pending bounded Windows WSS origin decision

Actual desktop default OS TLS health200 and native authenticated Login/profile/HTTP history succeeded. Controlled actual desktop WSS absent-Origin opens; Origin http://tauri.localhost yields HTTP403. Accepted gateway currently uses gorilla websocket.Upgrader{} default same-host policy. Tauri2 production Windows host default is http://tauri.localhost. Actual native Chat remains Offline/local history; no SENT/reconnect PASS.

Proposal, NOT implemented: add exactly http://tauri.localhost to gateway upgrade allowed origins, retain current no-Origin/same-host behavior and reject other cross-host Origins, keep auth.bind/token/session/ACK/protocol/TLS checks. No allow-all, header stripping, fixture proxy bypass or native transport dependency. Attached proposal.diff is reviewable text only, untested until scope/authority approval. Existing default multiple-Origin behavior is preserved; reviewer must check public/security authority before acceptance.

Requested authority: bounded approved architecture decision record for this exact Origin exception; explicit current Task allowed_paths addition backend/go/gateway/gateway.go and focused gateway origin test, plus named decision-record path. Current architecture text/contract bodies remain frozen unless separately approved. New authority record must receive fresh independent Review/applicable exact-head CI before dependent product implementation.

Verification after approval: absent/same-host/Tauri Origin handshake accepted but still unauthenticated until auth.bind; arbitrary-host and tauri.localhost.evil403; no cookies/token-in-query; existing gateway auth rejection tests; actual desktop WSS authenticated bind/message.send/committed ACK/idempotent retry, Sync reconnect. FullGUI/Task/S2 acceptance and protected integration/main sync remain separate.

Blocker is BLOCKED_BY_ARCHITECTURE for affected WSS repair (outside current allowed_paths and security boundary); task queue remains review. Unaffected native presentation/notifications/tray/session controls may continue.

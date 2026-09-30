# Expected original Go violations

Final actual source checker exit1/resultFAIL, 72 distinct body/import/path findings; producttree inheritedc0373ab unchanged. Raw AST/literals/imports in expected-old-go.json. Multiple manifestations are not distinct product defects.

- SRC-01/02 backend/go/auth.go: outside exact root whitelist/service ownership
- SRC-01/02 backend/go/auth_test.go: outside exact root whitelist/service ownership
- SRC-01/02 backend/go/config.go: outside exact root whitelist/service ownership
- SRC-01/02 backend/go/contract_fixture_test.go: outside exact root whitelist/service ownership
- SRC-01/02 backend/go/gateway.go: outside exact root whitelist/service ownership
- SRC-01/02 backend/go/outbox.go: outside exact root whitelist/service ownership
- SRC-01/03 backend/go/auth.go: root contains business SQL: INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,payload) VALUES($1,'sessio
- SRC-01/03 backend/go/auth.go: root contains business SQL: INSERT INTO sessions(user_id,client_type,session_id,session_epoch,refresh_token_hash,status,device_i
- SRC-01/03 backend/go/auth.go: root contains business SQL: INSERT INTO user_sync_events(user_id,event_type,payload) VALUES($1,'session.revoked',$2)
- SRC-01/03 backend/go/auth.go: root contains business SQL: INSERT INTO users(user_id,username,display_name,password_hash) VALUES($1,$2,$3,$4)
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT client_type FROM sessions WHERE user_id=$1 AND session_id=$2
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT session_id, client_type, session_epoch, status, expires_at FROM sessions WHERE user_id=$1 AND
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT session_id,session_epoch,status FROM sessions WHERE user_id=$1 AND client_type=$2
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT session_id,status,session_epoch FROM sessions WHERE user_id=$1 AND client_type=$2 FOR UPDATE
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT user_id FROM users WHERE user_id=$1 FOR UPDATE
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT user_id,password_hash FROM users WHERE username=$1
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT user_id,session_id,refresh_token_hash,status,session_epoch,expires_at,device_id,client_type F
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT user_id,username,display_name FROM users WHERE username=$1
- SRC-01/03 backend/go/auth.go: root contains business SQL: SELECT username,display_name FROM users WHERE user_id=$1
- SRC-01/03 backend/go/auth.go: root contains business SQL: UPDATE sessions SET refresh_token_hash=$1,expires_at=$2,updated_at=now() WHERE user_id=$3 AND client
- SRC-01/03 backend/go/auth.go: root contains business SQL: UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL,updated_at=now() WHERE user_id=$1 AND c
- SRC-01/03 backend/go/auth.go: root owns business route GET /v1/users/me
- SRC-01/03 backend/go/auth.go: root owns business route GET /v1/users/search
- SRC-01/03 backend/go/auth.go: root owns business route POST /v1/auth/login
- SRC-01/03 backend/go/auth.go: root owns business route POST /v1/auth/logout
- SRC-01/03 backend/go/auth.go: root owns business route POST /v1/auth/refresh/native
- SRC-01/03 backend/go/auth.go: root owns business route POST /v1/auth/refresh/web
- SRC-01/03 backend/go/auth.go: root owns business route POST /v1/auth/register
- SRC-01/03 backend/go/auth.go: root owns prohibited persistence call s.db.Begin
- SRC-01/03 backend/go/auth.go: root owns prohibited persistence call s.db.Exec
- SRC-01/03 backend/go/auth.go: root owns prohibited persistence call s.db.QueryRow
- SRC-01/03 backend/go/auth.go: root owns prohibited persistence call tx.Exec
- SRC-01/03 backend/go/auth.go: root owns prohibited persistence call tx.QueryRow
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'ses
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: DELETE FROM sessions WHERE user_id=$1
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: DELETE FROM user_sync_events WHERE user_id=$1
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: DELETE FROM users WHERE user_id=$1
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: SELECT count(*) FROM outbox_events WHERE aggregate_type='session' AND aggregate_id=$1
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: SELECT status FROM sessions WHERE user_id=$1 AND client_type='DESKTOP'
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: SELECT status,refresh_token_hash FROM sessions WHERE user_id=$1 AND client_type='MOBILE'
- SRC-01/03 backend/go/auth_test.go: root contains business SQL: UPDATE sessions SET status='REVOKED' WHERE user_id=$1 AND client_type='DESKTOP'
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/auth/login
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/auth/logout
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/auth/refresh/native
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/auth/refresh/web
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/auth/register
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/users/me
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/users/me?accessToken[REDACTED]
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/users/search?username=
- SRC-01/03 backend/go/auth_test.go: root owns business route /v1/users/search?username=missinguser
- SRC-01/03 backend/go/auth_test.go: root owns prohibited persistence call db.Begin
- SRC-01/03 backend/go/auth_test.go: root owns prohibited persistence call db.Exec
- SRC-01/03 backend/go/auth_test.go: root owns prohibited persistence call db.QueryRow
- SRC-01/03 backend/go/auth_test.go: root owns prohibited persistence call tx.Exec
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: DELETE FROM outbox_events WHERE aggregate_type='session' AND aggregate_id IN (SELECT (payload->>'ses
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: DELETE FROM sessions WHERE user_id=$1
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: DELETE FROM user_sync_events WHERE user_id=$1
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: DELETE FROM users WHERE user_id=$1
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: SELECT count(*) FROM sessions WHERE user_id=$1 AND client_type='DESKTOP' AND status='ACTIVE'
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: SELECT count(*) FROM sessions WHERE user_id=$1 AND client_type='WEB' AND status='ACTIVE'
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: SELECT status FROM sessions WHERE user_id=$1 AND client_type='WEB'
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: SELECT status,refresh_token_hash FROM sessions WHERE user_id=$1 AND client_type='DESKTOP'
- SRC-01/03 backend/go/contract_fixture_test.go: root contains business SQL: SELECT user_id FROM users WHERE username=$1
- SRC-01/03 backend/go/contract_fixture_test.go: root owns business route /v1/auth/login
- SRC-01/03 backend/go/contract_fixture_test.go: root owns business route /v1/auth/register
- SRC-01/03 backend/go/contract_fixture_test.go: root owns prohibited persistence call db.Exec
- SRC-01/03 backend/go/contract_fixture_test.go: root owns prohibited persistence call db.QueryRow
- SRC-01/03 backend/go/outbox.go: root contains business SQL: SELECT event_id,payload FROM outbox_events WHERE event_type='session.revoked' AND published_at IS NU
- SRC-01/03 backend/go/outbox.go: root contains business SQL: UPDATE outbox_events SET published_at=now(),attempts=attempts+1 WHERE event_id=$1
- SRC-01/03 backend/go/outbox.go: root owns prohibited persistence call db.Begin
- SRC-01/03 backend/go/outbox.go: root owns prohibited persistence call tx.Exec
- SRC-01/03 backend/go/outbox.go: root owns prohibited persistence call tx.Query

## Additional independent semantic preflight inventory

Coordinator conveyed read-only independent Reviewer facts: main.go has infra HTTP health/WS handshake route handlers, Core Auth handler selection, Gateway NATS callback/revoke/WSS route and HTTP forwarding. Root may keep role selection/config/dependency connection/minimal service startup, while transport handling and revocation/fan-out belong service owners. gateway.go holds complete *authService, calls authenticate/mustSign: stage004 must actually replace this coupling with only allowed readonly Gateway Session/token validation and connection abilities. Core retains register/login/refresh/logout/Session write transactions/Outbox. Shared must not hide full Auth. No stage003 product edit. Static PASS cannot prove root pure assembly; independent Review inspects actual runtime responsibility.

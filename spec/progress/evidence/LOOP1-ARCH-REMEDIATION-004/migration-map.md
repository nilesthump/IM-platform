# Actual migration map BEFORE product edits

Base6cdd981 (003closure), inherited productAuth59d92f3 unchanged. One-time004 authorization exits at batch closure; ordinary later task scopes remain narrow. Single existing Go module and single role binary retained.

| Actual original file/responsibility | Destination and responsibility |
| --- | --- |
| root auth.go all registration/login/refresh/logout/user HTTP, password hashing, Session write transactions and atomic revocation/Sync/Outbox | core/auth.go retains private business methods; core/http.go supplies only root-required NewHandler; Core readonly authentication stays Core |
| root auth.go JWT claims/sign/parse/random/UUID/hash/clienttype/error DTO primitives | shared/security.go token/crypto/DTO only, NO database, completeAuth or Session business. Existing semantics unchanged |
| root outbox.go transaction/publish/mark | core/outbox.go; root-required RelaySessionRevocations context lifecycle |
| root gateway.go hub/fullAuth reference/watch/resign | gateway/gateway.go owns WSS and connection tracking; gateway/session.go owns independent read-only authoritative Session checks, token codec. No Core imports, no fullAuth dependency, no token re-sign in Gateway |
| root main.go Auth routes, NATS revocation callbacks, WSS/proxy and infra WS handling | service http.go handlers (Core/Gateway/plugin-host). root main.go only role/config/PG+NATS connection creation/close, start service API/listener |
| root config.go config+credential file decoding | shared/config.go; config test follows shared. No business SQL/flow |
| root auth_test.go token/config/unit helpers + integrated Auth/WSS/DBrollback | shared token/config unit tests; tests/auth_test.go preserves blackbox HTTP/WSS/NATS/concurrency/security cases; private writeRevocation rollback stays core/rollback_test.go rather than exporting internals |
| root contract_fixture_test.go all canonical HTTP/WSS fixture assertion paths | tests/contract_fixture_test.go same canonical originals at ../../../contracts/fixtures; shared token primitives generate invalid tokens; public handler boundaries, NATS event replaces private hub revoke |
| existing root Dockerfile/go.mod/go.sum/config.example.json | remain assembly/build/support allowlist. No new modules/dependency/runtime infrastructure |
| existing CI root-only gofmt/build/test step | recursive Go source formatting, all packages build/vet/unit/race/live enabled; existing matrix/Gate retained |

Exports limited to current assembly consumers: Core handler/relay, Gateway handler, plugin-host handler; shared actual primitives/config. No wholesale field/method export. Cross-service tests live tests/; runtime service imports only own/shared. FullAuth remains privateCore. Gateway READ ONLY DB validator duplicates only authoritative slot checks within its own responsibility; shared contains no Session repository. Temporary fixture configs/credentials generated outside product tree, not committed or printed. Historical/canonical/public contracts remain byte-for-byte unchanged.

Validation: accepted ci/check_architecture.py --scope all --json and34architecturecontrols/24CItests; recursivegofmt/build/vet; all original tests retained and live DB_TEST_ENABLE=1/NATS_URL; disposable canonical migratedPG16+NATS; true roleHTTPforward/revocation; existing Compose/TLS smoke. No skipped integration counted asPASS. Fresh independentReview/actual finalheadhosted mandatory.

Actual bounded-operation rule repair: canonical7.3 forbids PostgreSQL in each message path. Gateway uses validated connection binding/expiry+NATS revocation; authoritative database check remains on everybind/reconnect and existing1second safetywatch fallback, without a new cache infrastructure. Gateway-specific infraWSprobe remains Gateway; shared healthonly is generic support. Initial migration compilation errors (Fail parameter capitalization and residualtest newHub/uuid) repaired; nonlive default tests compile/pass but DB tests skip and are NOT live acceptance.

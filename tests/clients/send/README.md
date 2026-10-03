# SEND verification

Run `python -B tools/verify_client_send.py --scope shared`, `--scope desktop`, or `--scope mobile --serial emulator-<actual>` with the existing approved toolchains. Every missing build/runtime is FAIL; Mobile requires a fully booted/unlocked API34 emulator.

Desktop uses the same SQLx atomic adapter as the Tauri commands through its existing private `storage_probe` transport, and the platform WebSocket client against verified fixture TLS. Android executes the actual SDK SQLite Repository, ViewModel/StateFlow and standard TLS socket/WSS implementation in instrumentation. Private TLS trust is supplied only by the test fixture. Production uses platform trust and mandatory HTTPS hostname checking. Both fixtures are controlled client behavior checks, not PostgreSQL durability evidence.

The default Gradle runner remains `StorageInstrumentation`. SEND verification explicitly builds with `-PimSendInstrumentation=im.platform.client.send.SendInstrumentation`; the original storage verifier uses the unchanged default and remains independently executable. CI runs the original storage verification before SEND in each affected job.

`python -B tests/clients/send/go_smoke.py <actual-storage_probe>` additionally connects the Desktop application to a task-owned real Go/PostgreSQL/NATS/TLS Compose profile. Its credential values arrive through private stdin, not process arguments/logs. It checks the client SENT row against exactly one PostgreSQL Message and one matching Outbox/sequence allocation, then inspects and removes only its own Compose resources. Existing Go E2E remains the broader rollback-before-ACK/idempotency/membership/durability oracle and continues to run in required CI.

SEND owns no GUI, HTTP send route, schema migration or Sync fetch runner. `mergeMessages` is the existing Repository materialization boundary for already authoritative Sync input. Account factories create Repository instances from bound account identities; retiring a SEND instance clears observations, sockets and timers. Injected test Repositories retain explicit test ownership; the Android account factory closes its owned Repository on disposal/lifecycle retirement.

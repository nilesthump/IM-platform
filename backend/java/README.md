# Java Auth profile

One executable artifact starts separate `core`, `gateway`, or `plugin-host` roles. Core owns Auth/User/Session transactions and Session Outbox; Gateway proxies HTTP and owns WSS authentication, readonly Session verification and revocation routing. The plugin-host role is health-only until its own approved task.

Provide `IM_CONFIG_FILE` naming an operator-controlled JSON file shaped like `config.example.json`. Credentials live in the named files; never commit them. `IM_LISTEN_PORT` defaults to8080 for each container; local isolated tests assign separate ports. Migrations run through the independent canonical migration component before startup.

Build with `mvn -f backend/java/pom.xml -Dim.build.dir=ABSOLUTE_EXTERNAL_DIRECTORY verify`; generated files must stay outside the source tree. The approved stack is ADR-0014. Credentials retain the Go password prehash and bcrypt representation. This task does not implement Friend/Message/Sync or claim S3 parity Gate PASS.

For the mandatory live comparison, add `dependency:build-classpath -Dmdep.outputFile=ABSOLUTE_EXTERNAL_DIRECTORY/classpath.txt` to the Maven command. Provision migrated disposable PostgreSQL and NATS, then provide `PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`, `PGPASSWORD`, `PGSSLMODE`, and `NATS_URL` through the environment. Run `python tools/verify_java_auth.py --build-dir ABSOLUTE_EXTERNAL_DIRECTORY --profile java`, repeat with `--profile go`, then `--profile-switch`. The same runner consumes canonical fixtures against both profiles; missing runtime inputs fail. Evidence logs/configs stay in the external build directory and contain test credentials, so do not publish that directory wholesale.

Compose requires `IM_JAVA_CONFIG_DIR` pointing to an operator-owned config/secret directory. `tests/infrastructure/smoke.ps1 -Profile java` verifies real HTTPS Auth and WSS bind/logout through the existing TLS entry. Direct HTTP component results do not replace TLS acceptance.

Configure `publicOrigin` to the exact public HTTPS origin (including nondefault port); it is an operator value, never inferred from client Forwarded headers. Default example is https://localhost:8443; the TLS smoke config uses https://localhost:18444. Token lifetimes are positive integer seconds: `accessTokenSeconds` default900 and `refreshTokenSeconds` default2592000, refresh longer than access.

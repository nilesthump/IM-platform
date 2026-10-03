# Desktop storage slice

Approved stack: Tauri + TypeScript with SQLx(SQLite) only; accepted canonical §6.1 / ADR-0005. React UI and actual send/Sync orchestration are outside this storage task. The Tauri adapter registers generic account query/atomic transaction commands. TypeScript owns Repository/models/schema/migration/intents. Native account UUID filenames are normalized and bounded to the application data directory.

Verification: python -B tools/verify_client_sqlite.py --scope desktop.
This compiles shared/adapter TypeScript, tests/builds actual SQLx, then executes canonical and additional storage cases through the same native atomic adapter. A small private hex test transport exists solely to carry current SQL/bind instructions to that adapter without an unapproved serialization package; it is not product IPC or a replacement runtime. Each test batch calls the adapter once. Query connections are physically read-only; transactions roll back on any statement or row-count mismatch.

Required tools: Node build tooling, npm, stable Rust/MSVC on Windows (or system Tauri build prerequisites on Linux). CARGO_TARGET_DIR may point outside the checkout. Exact dependency versions are in lockfiles; no global PATH or unrelated toolchain changes are required. Native/full UI/network/S2 acceptance remains for later slices.

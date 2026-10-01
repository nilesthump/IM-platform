# Native account SQLite storage

One private materialized view serves Desktop and Mobile through their storage packages. Requires Dart 3.12 and the pinned sqlite3 3.7 native build hook. No ORM, authentication credentials, network transport or UI is included.

`LocalStore.openAccount(privateDirectory, accountId)` opens an account-named database. The application supplies a private native data directory. `open(path, accountId)` also binds an explicit file to one account; mismatched reuse fails. Close each store when its account lifetime ends. Logout policy and OS token storage belong to the application.

Schema 1 is created in a transaction from an empty version-0 database. Account metadata, Message uniqueness indexes, Conversation contiguous prefixes, user event identities and low-frequency user state are private implementation details. There is no released older client/schema to simulate. Future schema versions fail without downgrading.

Local send, committed ACK, realtime and message Sync use SQL UPSERT transactions with immutable identity/content checks. ACK requires an existing complete local send. SENT is terminal; FAILED can converge through server input. Message data and contiguous prefixes commit together. User pages persist and compare the five typed event fields, rejecting changed payloads under a reused event identity even after reopen. Identity, materialized revisions and opaque cursor commit together; `expectedCursor` binds a page to its starting cursor when callers fetch concurrently.

Run `dart pub get --enforce-lockfile`, `dart analyze`, `dart test` and `dart format --output=none --set-exit-if-changed lib test` from this package. Tests load unchanged fixtures from `../../../contracts`, replay all 13 applicable storage cases and their canonical timelines, and use actual native SQLite triggers for before-commit failure. Additional tests cover native load, four entrances, missing/rejected ACK, identity rollback, account isolation, reopen, initial migration failure and future-version rejection.

Windows host and hosted Linux tests validate this storage foundation. Mobile package tests run on the host Dart VM; they do not establish device/UI or complete S2 acceptance. Later SEND/Sync tasks own request generation, scheduling, network reconnection and synchronization orchestration.

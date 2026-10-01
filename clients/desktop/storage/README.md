# Native desktop storage

Thin consumer of the shared account SQLite repository. The application supplies its private native directory and account ID to `openAccountStorage`; credentials are never passed into storage. Run `dart pub get --enforce-lockfile`, `dart analyze`, `dart test` and the lib/test format check here. The test exercises real SQLite account separation and reopen on the host Dart VM; no UI or mobile device acceptance is claimed.

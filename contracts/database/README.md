# Canonical PostgreSQL schema

`migrations/0001_initial.up.sql` is the shared schema for Go and Java profiles.
Run the migration before application startup, using a normal PostgreSQL `psql`
client and libpq connection settings (`PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`,
and secure credential handling outside the command line):

```text
python3 contracts/database/migrate.py status
python3 contracts/database/migrate.py up
python3 contracts/database/migrate.py down --allow-data-loss
```

The runner applies each SQL file and its checksum ledger entry in one transaction
under a PostgreSQL advisory transaction lock. Applied SQL is immutable. The down
migration drops all product tables and requires explicit data-loss acknowledgement;
release rollback still requires a backup and compatibility assessment.

`sessions` is one row per `(user_id, client_type)` slot. A replacement login must
rotate `session_id`, increment `session_epoch`, and revoke the old session in one
transaction. The server must validate both session ID and epoch against PostgreSQL.
The database constraints reject duplicate normalized friendship and DIRECT pairs,
request IDs and sequence numbers within a Conversation, and duplicate logical
`message.created` outbox events. Message authorization, sequence allocation,
matching Outbox insertion, friend/direct/membership/sync transaction assembly, and
post-commit ACK remain application transaction obligations. A unique constraint
alone cannot prove those multi-row operations occurred atomically.

With a disposable PostgreSQL database configured through libpq variables, run
`python3 -m unittest discover -s tests/database -v`. The integration test uses
an isolated temporary schema and exercises forward, uniqueness, and rollback.

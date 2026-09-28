"""Standalone PostgreSQL migration runner. Requires psql and normal libpq PG* environment.

Run before starting either backend profile. `down` is destructive and requires an
explicit flag; production rollback must also follow the release compatibility plan.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
MIGRATIONS = ROOT / "migrations"
VERSION = "0001_initial"
LOCK = 481233001


def psql(sql: str, *, capture: bool = False) -> str:
    proc = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t"],
        input=sql, text=True, capture_output=True,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f"psql exited {proc.returncode}")
    if not capture and proc.stdout.strip():
        print(proc.stdout.strip())
    return proc.stdout.strip()


def migration_sql(direction: str) -> str:
    return (MIGRATIONS / f"{VERSION}.{direction}.sql").read_text(encoding="utf-8")


def checksum() -> str:
    return hashlib.sha256(migration_sql("up").encode("utf-8")).hexdigest()


def applied() -> str | None:
    result = psql("SELECT to_regclass('schema_migrations') IS NOT NULL;", capture=True)
    if result != "t":
        return None
    result = psql(f"SELECT checksum FROM schema_migrations WHERE version = '{VERSION}';", capture=True)
    return result or None


def run(direction: str) -> None:
    if not shutil.which("psql"):
        raise RuntimeError("psql is required; set PGHOST/PGPORT/PGUSER/PGDATABASE as needed")
    known = applied()
    digest = checksum()
    if known is not None and known != digest:
        raise RuntimeError("applied migration checksum differs from the canonical SQL")
    if direction == "up" and known == digest:
        print(f"{VERSION}: already applied")
        return
    if direction == "down" and known is None:
        print(f"{VERSION}: already rolled back")
        return
    prelude = (
        "BEGIN;\n"
        f"SELECT pg_advisory_xact_lock({LOCK});\n"
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version text PRIMARY KEY, checksum text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now());\n"
    )
    # Check again under the transaction lock, so concurrent runner attempts cannot
    # apply or roll back a migration against stale inspection state.
    expected = "false" if direction == "up" else "true"
    guard = f"""DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM schema_migrations WHERE version = '{VERSION}') <> {expected} THEN
        RAISE EXCEPTION 'migration state changed concurrently';
      END IF;
    END $$;
    """
    body = migration_sql(direction)
    ledger = (
        f"INSERT INTO schema_migrations(version, checksum) VALUES ('{VERSION}', '{digest}');"
        if direction == "up" else
        f"DELETE FROM schema_migrations WHERE version = '{VERSION}' AND checksum = '{digest}';"
    )
    psql(prelude + guard + body + "\n" + ledger + "\nCOMMIT;\n")
    print(f"{VERSION}: {direction} complete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=("up", "down", "status"))
    parser.add_argument("--allow-data-loss", action="store_true", help="required for destructive down migration")
    args = parser.parse_args()
    try:
        if args.direction == "down" and not args.allow_data_loss:
            raise RuntimeError("down drops product tables; pass --allow-data-loss only after backup/compatibility review")
        if args.direction == "status":
            if not shutil.which("psql"):
                raise RuntimeError("psql is required")
            known = applied()
            print(f"{VERSION}: {'applied' if known else 'pending'}")
            if known and known != checksum():
                raise RuntimeError("applied checksum differs from canonical SQL")
        else:
            run(args.direction)
        return 0
    except RuntimeError as exc:
        print(f"migration error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

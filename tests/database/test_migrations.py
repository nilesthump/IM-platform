"""PostgreSQL integration tests. Set DB_TEST_ENABLE=1 for a disposable database."""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import unittest
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "contracts" / "database" / "migrate.py"
UP = ROOT / "contracts" / "database" / "migrations" / "0001_initial.up.sql"


class StaticSchemaTests(unittest.TestCase):
    def test_single_ordered_reversible_migration_and_runner(self):
        self.assertTrue(UP.is_file())
        self.assertTrue(UP.with_name("0001_initial.down.sql").is_file())
        text = UP.read_text(encoding="utf-8")
        for table in ("users", "sessions", "friendships", "conversations",
                      "conversation_members", "messages", "outbox_events",
                      "plugin_artifacts", "plugin_instances", "plugin_kv"):
            self.assertRegex(text, rf"CREATE TABLE {table}\s*\(")
        self.assertIn("UNIQUE (conversation_id, request_id)", text)
        self.assertIn("UNIQUE (conversation_id, seq)", text)
        self.assertIn("PRIMARY KEY (user_id, client_type)", text)
        self.assertIn("PRIMARY KEY (user_low_id, user_high_id)", text)
        self.assertIn("UNIQUE (direct_user_low_id, direct_user_high_id)", text)

    def test_down_requires_explicit_data_loss_acknowledgement(self):
        result = subprocess.run([sys.executable, str(RUNNER), "down"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("--allow-data-loss", result.stderr)


@unittest.skipUnless(os.environ.get("DB_TEST_ENABLE") == "1", "set DB_TEST_ENABLE=1 with a disposable PostgreSQL database")
class PostgreSQLMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("psql"):
            raise unittest.SkipTest("psql unavailable")
        cls.schema = "db_test_" + uuid.uuid4().hex
        cls.env = os.environ.copy()
        cls.psql(f"CREATE SCHEMA {cls.schema};", env=cls.env)
        cls.env["PGOPTIONS"] = f"-c search_path={cls.schema}"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "schema"):
            cls.psql(f"DROP SCHEMA {cls.schema} CASCADE;", env=os.environ.copy())

    @classmethod
    def psql(cls, sql, env=None):
        result = subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t"],
                                input=sql, text=True, capture_output=True, env=env or cls.env)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def migrate(self, *args):
        result = subprocess.run([sys.executable, str(RUNNER), *args],
                                text=True, capture_output=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_forward_uniqueness_and_rollback(self):
        self.migrate("up")
        self.assertIn("already applied", self.migrate("up"))
        self.assertIn("applied", self.migrate("status"))
        # Every rejected insert is executed in its own PL/pgSQL exception block;
        # the expected constraint error is caught without aborting the suite.
        sql = """
        INSERT INTO users(user_id, username, display_name, password_hash) VALUES
          ('00000000-0000-0000-0000-000000000001','alice','Alice','hashed'),
          ('00000000-0000-0000-0000-000000000002','bob','Bob','hashed');
        INSERT INTO sessions(user_id, client_type, session_id, session_epoch, refresh_token_hash, status, device_id, expires_at)
          VALUES ('00000000-0000-0000-0000-000000000001','WEB','00000000-0000-0000-0000-000000000011',1,'hashed','ACTIVE','browser',now()+interval '1 day');
        DO $$ BEGIN
          INSERT INTO sessions(user_id, client_type, session_id, session_epoch, refresh_token_hash, status, device_id, expires_at)
            VALUES ('00000000-0000-0000-0000-000000000001','WEB','00000000-0000-0000-0000-000000000012',2,'hashed','ACTIVE','browser',now()+interval '1 day');
          RAISE EXCEPTION 'duplicate session slot accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by)
          VALUES ('00000000-0000-0000-0000-000000000021','DIRECT','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001');
        DO $$ BEGIN
          INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by)
            VALUES ('00000000-0000-0000-0000-000000000022','DIRECT','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001');
          RAISE EXCEPTION 'duplicate direct pair accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
          VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000021');
        DO $$ BEGIN
          INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
            VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000021');
          RAISE EXCEPTION 'duplicate friendship accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
            VALUES ('00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000021');
          RAISE EXCEPTION 'reverse friendship accepted';
        EXCEPTION WHEN check_violation THEN NULL; END $$;
        INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
          VALUES ('00000000-0000-0000-0000-000000000031','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000041',1,'TEXT','hello');
        DO $$ BEGIN
          INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
            VALUES ('00000000-0000-0000-0000-000000000032','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000041',2,'TEXT','retry');
          RAISE EXCEPTION 'duplicate request accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
            VALUES ('00000000-0000-0000-0000-000000000032','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000042',1,'TEXT','other');
          RAISE EXCEPTION 'duplicate seq accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
          VALUES ('00000000-0000-0000-0000-000000000051','Message','00000000-0000-0000-0000-000000000031','message.created','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000031','{}');
        DO $$ BEGIN
          INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
            VALUES ('00000000-0000-0000-0000-000000000052','Message','00000000-0000-0000-0000-000000000031','message.created','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000031','{}');
          RAISE EXCEPTION 'duplicate outbox event accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO plugin_artifacts(plugin_id,version,package_hash,backend_hash,renderer_hash,manifest,status)
          VALUES ('echo','1','p','b','r','{}','VERIFIED');
        DO $$ BEGIN
          INSERT INTO plugin_artifacts(plugin_id,version,package_hash,backend_hash,renderer_hash,manifest,status)
            VALUES ('echo','1','changed','b','r','{}','VERIFIED');
          RAISE EXCEPTION 'duplicate artifact identity accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          UPDATE plugin_artifacts SET renderer_hash='changed' WHERE plugin_id='echo';
          RAISE EXCEPTION 'mutable artifact accepted';
        EXCEPTION WHEN raise_exception THEN
          IF SQLERRM = 'mutable artifact accepted' THEN RAISE; END IF;
        END $$;
        DO $$ BEGIN
          DELETE FROM plugin_artifacts WHERE plugin_id='echo';
          RAISE EXCEPTION 'artifact deletion accepted';
        EXCEPTION WHEN raise_exception THEN
          IF SQLERRM = 'artifact deletion accepted' THEN RAISE; END IF;
        END $$;
        """
        self.psql(sql)
        self.migrate("down", "--allow-data-loss")
        self.assertIn("pending", self.migrate("status"))
        self.assertEqual(self.psql("SELECT to_regclass('users') IS NULL AND to_regclass('messages') IS NULL;"), "t")
        self.migrate("up")
        self.migrate("down", "--allow-data-loss")


if __name__ == "__main__":
    unittest.main()

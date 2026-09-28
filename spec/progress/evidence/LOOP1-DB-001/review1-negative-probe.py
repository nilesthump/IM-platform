"""Independent PostgreSQL probes for the LOOP1-DB-001 review."""
import os
import subprocess
import sys
import uuid


def run(argv, *, sql=None, env=None, success=True):
    result = subprocess.run(argv, input=sql, text=True, capture_output=True, env=env)
    if (result.returncode == 0) != success:
        raise AssertionError(f"unexpected exit {result.returncode}: {result.stdout} {result.stderr}")
    return result


schema = "db_review_" + uuid.uuid4().hex
fault_schema = "db_review_fault_" + uuid.uuid4().hex
base = os.environ.copy()
work = base.copy()
work["PGOPTIONS"] = f"-c search_path={schema}"
psql = ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t"]
runner = [sys.executable, "contracts/database/migrate.py"]

try:
    run(psql, sql=f"CREATE SCHEMA {schema};", env=base)
    run(runner + ["up"], env=work)
    run(psql, sql="""
        INSERT INTO users(user_id,username,display_name,password_hash) VALUES
          ('00000000-0000-0000-0000-000000000001','alice','Alice','hash'),
          ('00000000-0000-0000-0000-000000000002','bob','Bob','hash');
        INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by)
          VALUES ('00000000-0000-0000-0000-000000000011','DIRECT',
          '00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002',
          '00000000-0000-0000-0000-000000000001');
        INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id)
          VALUES ('00000000-0000-0000-0000-000000000012','GROUP',
          '00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000013');
        INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
          VALUES ('00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000011',
          '00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000022',1,'TEXT','hello');
    """, env=work)
    # A message.created event cannot claim a different Conversation.
    run(psql, sql="""
        INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
          VALUES ('00000000-0000-0000-0000-000000000031','Message',
          '00000000-0000-0000-0000-000000000021','message.created',
          '00000000-0000-0000-0000-000000000012',
          '00000000-0000-0000-0000-000000000021','{}');
    """, env=work, success=False)
    # A friendship cannot point to a GROUP or an unrelated DIRECT pair.
    run(psql, sql="""
        INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
          VALUES ('00000000-0000-0000-0000-000000000001',
          '00000000-0000-0000-0000-000000000002',
          '00000000-0000-0000-0000-000000000012');
    """, env=work, success=False)
    # The destructive down migration must refuse without its explicit flag.
    run(runner + ["down"], env=work, success=False)
    count = run(psql, sql="SELECT count(*) FROM messages;", env=work).stdout.strip()
    if count != "1":
        raise AssertionError(f"down guard lost live data: {count}")
    run(runner + ["down", "--allow-data-loss"], env=work)
    if run(psql, sql="SELECT to_regclass('messages') IS NULL;", env=work).stdout.strip() != "t":
        raise AssertionError("destructive down left product tables")
    print("PASS: wrong-Conversation outbox and friendship rejected; down guard preserved live data; explicit rollback succeeded")
    # Force a DDL conflict halfway through the first migration. Neither the
    # ledger nor subsequent product tables may survive the failed transaction.
    run(psql, sql=f"CREATE SCHEMA {fault_schema}; CREATE TABLE {fault_schema}.users (marker integer);", env=base)
    fault = base.copy()
    fault["PGOPTIONS"] = f"-c search_path={fault_schema}"
    run(runner + ["up"], env=fault, success=False)
    state = run(psql, sql="SELECT to_regclass('schema_migrations') IS NULL AND to_regclass('sessions') IS NULL;", env=fault).stdout.strip()
    if state != "t":
        raise AssertionError(f"failed migration left partial state: {state}")
    print("PASS: failed migration left no ledger or partially created schema")
finally:
    run(psql, sql=f"DROP SCHEMA IF EXISTS {schema} CASCADE;", env=base)
    run(psql, sql=f"DROP SCHEMA IF EXISTS {fault_schema} CASCADE;", env=base)

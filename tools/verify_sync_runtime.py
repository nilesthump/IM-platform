#!/usr/bin/env python3
"""Real public Sync through existing Compose TLS -> Gateway -> Core/PostgreSQL."""
import importlib.util
import json
import os
from pathlib import Path
import secrets
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("go_tls_harness", ROOT / "tests/e2e/go_tls_messaging.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
require = harness.require


def main():
    project = "im-sync-runtime-" + str(os.getpid()) + "-" + secrets.token_hex(4)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    env = os.environ.copy()
    env.update(IM_HTTPS_PORT=str(port), COMPOSE_PROGRESS="quiet")
    command = ["docker", "compose", "-f", str(ROOT / "deploy/compose.yaml"), "-p", project, "--profile", "go"]

    def docker(args, data=None):
        result = subprocess.run(args, env=env, input=data, capture_output=True, timeout=600)
        if result.returncode:
            raise RuntimeError("Disposable Compose command failed: " + result.stderr.decode(errors="replace"))
        return result.stdout

    def compose(*args):
        return docker(command + list(args))

    def sql(query):
        return compose("exec", "-T", "postgres", "psql", "-U", "im", "-d", "im", "-v", "ON_ERROR_STOP=1", "-Atc", query).decode().strip()

    with tempfile.TemporaryDirectory(prefix="im-sync-runtime-") as temp:
        config = Path(temp) / "config"
        config.mkdir()
        env["IM_GO_CONFIG_DIR"] = str(config)
        (config / "config.json").write_bytes((ROOT / "backend/go/config.example.json").read_bytes())
        (config / "pg_password").write_text("local-development-only", encoding="utf-8")
        (config / "jwt_key").write_text(secrets.token_urlsafe(48), encoding="utf-8")
        ws = None
        try:
            compose("config", "--quiet")
            compose("up", "-d", "--build")
            tls_id = compose("ps", "-q", "tls-go").decode().strip()
            require(bool(tls_id), "TLS role missing")
            ca = Path(temp) / "root.crt"
            for _ in range(60):
                try:
                    docker(["docker", "cp", tls_id + ":/data/caddy/pki/authorities/local/root.crt", str(ca)])
                    break
                except RuntimeError:
                    time.sleep(.5)
            else:
                raise RuntimeError("Public root CA unavailable")
            context = ssl.create_default_context(cafile=str(ca))
            require(context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED, "TLS verification disabled")

            def call(path, body, token=None, expected=200, raw=None):
                headers = {"Content-Type": "application/json"}
                if token:
                    headers["Authorization"] = "Bearer " + token
                request = urllib.request.Request("https://localhost:" + str(port) + path,
                                                 data=json.dumps(body).encode() if raw is None else raw, headers=headers, method="POST")
                try:
                    response = urllib.request.urlopen(request, context=context, timeout=20)
                except urllib.error.HTTPError as error:
                    response = error
                with response:
                    require(response.code == expected, "Unexpected status " + str(response.code) + " on " + path)
                    value = json.loads(response.read())
                    if path.startswith("/v1/sync/"):
                        require(response.headers.get("Cache-Control") == "no-store", "Sync response cacheable")
                        require(value.get("requestId") == body["requestId"], "Sync correlation lost")
                    return value

            for _ in range(60):
                try:
                    with urllib.request.urlopen("https://localhost:" + str(port) + "/__infra/health", context=context, timeout=2) as response:
                        require(response.read().strip() == b"profile=go role=gateway", "Wrong HTTPS role")
                    break
                except OSError:
                    time.sleep(.5)
            else:
                raise RuntimeError("Verified TLS Gateway unavailable")
            try:
                with socket.create_connection(("localhost", port), timeout=5) as raw:
                    ssl.create_default_context().wrap_socket(raw, server_hostname="localhost")
            except ssl.SSLCertVerificationError:
                pass
            else:
                raise AssertionError("Untrusted CA accepted")
            users = []
            for i in range(2):
                name = "sync" + secrets.token_hex(8)
                user = call("/v1/auth/register", {"username": name, "password": "fixture-password-not-a-real-secret",
                                                "displayName": name}, expected=201)["user"]["userId"]
                token = call("/v1/auth/login", {"username": name, "password": "fixture-password-not-a-real-secret",
                                               "clientType": "DESKTOP", "deviceId": "sync-test", "clientVersion": "1.0.0",
                                               "protocolVersion": "1"})["tokens"]["accessToken"]
                users.append((user, token))
            # Existing public social mutation creates the existing three metadata kinds.
            req = urllib.request.Request("https://localhost:" + str(port) + "/v1/friends/" + users[1][0],
                                         data=b"{}", method="PUT",
                                         headers={"Content-Type": "application/json", "Authorization": "Bearer " + users[0][1]})
            with urllib.request.urlopen(req, context=context, timeout=20) as response:
                require(response.code == 201, "Friend creation failed")
                conversation = json.loads(response.read())["directConversationId"]
            # Fixture-only metadata records, under the existing producer serialization.
            # No new producer is introduced for plugin.changed.
            sql(f"""DO $$ DECLARE c bigint; k text; e uuid; BEGIN
                PERFORM user_id FROM users WHERE user_id='{users[0][0]}' FOR UPDATE;
                FOR i IN 1..205 LOOP
                    k := (ARRAY['friend.changed','conversation.changed','membership.changed','plugin.changed'])[(i-1)%4+1];
                    e := gen_random_uuid();
                    INSERT INTO user_sync_events(user_id,event_type,payload)
                        VALUES('{users[0][0]}',k,'{{}}') RETURNING cursor_id INTO c;
                    UPDATE user_sync_events SET payload=jsonb_build_object('eventId',e,'cursor',c::text,
                        'kind',k,'subjectId','{conversation}','revision',1)
                        WHERE user_id='{users[0][0]}' AND cursor_id=c;
                END LOOP;
                INSERT INTO user_sync_events(user_id,event_type,payload) VALUES('{users[0][0]}','session.revoked','{{}}');
                END $$;""")
            ws = harness.WS(context, port)
            ws.send(harness.frame("auth.bind", {"accessToken": users[0][1]}))
            require(ws.read()["payload"]["status"] == "bound", "WSS authentication failed")
            for i in range(205):
                frame = harness.frame("message.send", {"conversationId": conversation, "content": {"kind": "TEXT", "text": "sync " + str(i)}})
                ws.send(frame)
                for _ in range(10):
                    ack = ws.read()
                    if ack["type"] == "message.ack" and ack["requestId"] == frame["requestId"]:
                        require(ack["payload"]["status"] == "committed" and ack["payload"]["seq"] == i + 1, "Commit or sequence failed")
                        break
                else:
                    raise AssertionError("Durable ACK missing")

            def body(user, position):
                value = {"syncVersion": "1.0", "type": "sync.user.request" if user else "sync.conversation.request",
                         "requestId": str(uuid.uuid4()), "limit": 10**100}
                value.update({"cursor": position} if user else {"conversationId": conversation, "afterSeq": position})
                return value

            # Literal coefficients/exponents beyond 64KiB must not create a
            # numeric domain cap or unbounded server buffering.
            for user in (True, False):
                path = "/v1/sync/user" if user else "/v1/sync/conversation"
                probe = body(user, "0" if user else 0)
                probe["limit"] = 1
                for numeric, count in (("1"+"0"*70000,100), ("1e"+"9"*70000,100), ("1"+"0"*70000+"e-70000",1)):
                    raw = json.dumps(probe).replace('"limit": 1', '"limit": '+numeric).encode()
                    page = call(path, probe, users[0][1], raw=raw)
                    require(len(page["events" if user else "messages"]) == count and page["hasMore"], "Long exact numeric limit differs")
            probe = body(False, 0)
            raw = json.dumps(probe).replace('"afterSeq": 0', '"afterSeq": 1'+"0"*70000).encode()
            require(not call("/v1/sync/conversation", probe, users[0][1], raw=raw)["messages"], "Long above-head integer differs")
            counts_before = sql("SELECT (SELECT count(*) FROM messages)||','||(SELECT count(*) FROM outbox_events)")
            for user in (True, False):
                path = "/v1/sync/user" if user else "/v1/sync/conversation"
                position = "0" if user else 0
                total, seen, kinds = 0, set(), set()
                while True:
                    page = call(path, body(user, position), users[0][1])
                    items = page["events" if user else "messages"]
                    expected_keys = {"syncVersion", "type", "requestId", "hasMore"} | ({"events", "nextCursor"} if user else {"messages", "conversationId"})
                    require(set(page) == expected_keys, "Noncanonical page keys")
                    require(len(items) <= 100, "Page cap exceeded")
                    require(not page["hasMore"] or items, "Empty nonterminal page")
                    for item in items:
                        key = item["eventId" if user else "messageId"]
                        require(key not in seen, "Duplicate across pages")
                        seen.add(key)
                        if user:
                            require(set(item) == {"eventId","cursor","kind","subjectId","revision"}, "Noncanonical event")
                            kinds.add(item["kind"])
                            position = item["cursor"]
                        else:
                            require(item["seq"] == total + 1 and item["conversationId"] == conversation, "Gap or identity")
                            require(set(item) == {"conversationId","seq","messageId","senderId","requestId","createdAt","content"}, "Noncanonical Message")
                            position = item["seq"]
                        total += 1
                    if not page["hasMore"]:
                        break
                require(total == (208 if user else 205), "Total synchronization truncated")
                if user:
                    require(kinds == {"friend.changed","conversation.changed","membership.changed","plugin.changed"}, "Metadata projection differs")
                terminal = body(user, position)
                replay = call(path, terminal, users[0][1])
                require(not replay["hasMore"] and not replay["events" if user else "messages"], "Terminal position failed")
                if user:
                    foreign = call(path, terminal, users[1][1], expected=400)
                    require(foreign["error"]["code"] == "VALIDATION_FAILED", "Foreign cursor accepted")
                query_error = call(path + "?accessToken=fake", terminal, users[0][1], expected=400)
                require(query_error["error"]["code"] == "VALIDATION_FAILED", "Query credential accepted")
                auth_error = call(path, terminal, expected=401)
                require(auth_error["error"]["code"] == "AUTH_REQUIRED", "Missing auth accepted")
                version = dict(terminal, syncVersion="2.0")
                require(call(path, version, users[0][1], expected=426)["error"]["code"] == "PROTOCOL_VERSION_UNSUPPORTED", "Version accepted")
            require(sql("SELECT (SELECT count(*) FROM messages)||','||(SELECT count(*) FROM outbox_events)") == counts_before, "Sync wrote authoritative effects")
            # A terminal read covers its visible commit, not future writes.
            frame = harness.frame("message.send", {"conversationId": conversation, "content": {"kind": "TEXT", "text": "after terminal"}})
            ws.send(frame)
            for _ in range(10):
                ack = ws.read()
                if ack["type"] == "message.ack" and ack["requestId"] == frame["requestId"]:
                    require(ack["payload"]["status"] == "committed" and ack["payload"]["seq"] == 206, "New commit failed")
                    break
            else:
                raise AssertionError("New durable ACK missing")
            latest = call("/v1/sync/conversation", body(False, 205), users[0][1])
            require(not latest["hasMore"] and len(latest["messages"]) == 1 and latest["messages"][0]["seq"] == 206, "New commit missing after terminal")
            above = body(False, 10**100)
            require(call("/v1/sync/conversation", above, users[0][1])["messages"] == [], "Huge above-head failed")
            print("PASS: strict trusted-CA HTTPS proxy/Gateway/Core; real PG 208 User and 205 durable WSS Message items, all pages <=100, terminal/new-commit/replay/auth/foreign/query/version/read-only", flush=True)
        finally:
            if ws:
                ws.close()
            # Bound cleanup to actually inspected owned resources, preserving other projects.
            for resource, listing in (("container", ["docker","ps","-aq","--filter","label=com.docker.compose.project="+project]),
                                      ("volume", ["docker","volume","ls","-q","--filter","label=com.docker.compose.project="+project])):
                for name in docker(listing).decode().split():
                    obj = json.loads(docker(["docker",resource,"inspect",name]))[0]
                    labels = obj["Config"]["Labels"] if resource == "container" else obj["Labels"]
                    require(labels.get("com.docker.compose.project") == project, "Cleanup ownership differs")
            compose("down", "--volumes", "--remove-orphans")
            require(not docker(["docker","ps","-aq","--filter","label=com.docker.compose.project="+project]).strip(), "Owned containers remain")
            require(not docker(["docker","volume","ls","-q","--filter","label=com.docker.compose.project="+project]).strip(), "Owned volume remains")
            print("PASS: inspected disposable project cleanup", flush=True)


if __name__ == "__main__":
    main()

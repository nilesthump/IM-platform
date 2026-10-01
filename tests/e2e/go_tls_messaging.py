"""Real Go Compose HTTPS/WSS slice; only stdlib and canonical fixture oracles."""
import base64
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import ssl
import struct
import subprocess
import tempfile
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def fixture(path, scenario):
    scenarios = json.loads((ROOT / path).read_text(encoding='utf-8'))['scenarios']
    return next(s for s in scenarios if s['id'] == scenario)


class Oracle:
    """Only normalize runtime UUIDs/timestamps; exact canonical shape/scalars."""
    def __init__(self, identities=None):
        self.ids = identities or {}
        self.times = {}

    def check(self, expected, actual):
        if isinstance(expected, dict):
            require(isinstance(actual, dict) and expected.keys() == actual.keys(), 'canonical object keys differ')
            for k in expected:
                self.check(expected[k], actual[k])
        elif isinstance(expected, list):
            require(isinstance(actual, list) and len(expected) == len(actual), 'canonical array differs')
            for e, a in zip(expected, actual):
                self.check(e, a)
        elif isinstance(expected, str):
            try:
                uuid.UUID(expected)
            except ValueError:
                try:
                    datetime.datetime.fromisoformat(expected.replace('Z', '+00:00'))
                except ValueError:
                    require(expected == actual, 'canonical string differs')
                else:
                    datetime.datetime.fromisoformat(actual.replace('Z', '+00:00'))
                    require(self.times.setdefault(expected, actual) == actual, 'committed timestamp changed')
            else:
                uuid.UUID(actual)
                require(self.ids.setdefault(expected, actual) == actual, 'canonical identity changed')
        else:
            require(type(expected) is type(actual) and expected == actual, 'canonical value differs')


class WS:
    def __init__(self, context, port):
        self.s = context.wrap_socket(socket.create_connection(('localhost', port), timeout=10), server_hostname='localhost')
        self.s.settimeout(10)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET /v1/ws HTTP/1.1\r\nHost: localhost:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        head = b''
        while not head.endswith(b'\r\n\r\n'):
            head += self.exact(1)
            require(len(head) < 16384, 'oversized upgrade headers')
        require(head.split(b'\r\n')[0].startswith(b'HTTP/1.1 101 '), 'WSS upgrade failed')
        headers = dict(line.split(b':', 1) for line in head.split(b'\r\n')[1:] if b':' in line)
        expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        require(any(k.lower() == b'sec-websocket-accept' and v.strip() == expected for k, v in headers.items()), 'WSS accept differs')

    def exact(self, n):
        out = b''
        while len(out) < n:
            b = self.s.recv(n - len(out))
            if not b:
                raise EOFError('socket closed')
            out += b
        return out

    def send(self, frame):
        b = json.dumps(frame).encode()
        mask = os.urandom(4)
        header = bytes([0x81, 0x80 | len(b)]) if len(b) < 126 else bytes([0x81, 0xfe]) + struct.pack('!H', len(b))
        self.s.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(b)))

    def read(self):
        a, b = self.exact(2)
        require(a & 0x80 and not b & 0x80, 'unexpected fragmented/masked server frame')
        n = b & 127
        if n == 126:
            n = struct.unpack('!H', self.exact(2))[0]
        elif n == 127:
            n = struct.unpack('!Q', self.exact(8))[0]
        require(n <= 65536, 'oversized server frame')
        payload = self.exact(n)
        if a & 15 == 8:
            raise EOFError('WebSocket close')
        require(a & 15 == 1, 'unexpected server opcode')
        return json.loads(payload)

    def quiet(self):
        self.s.settimeout(1)
        try:
            self.read()
        except socket.timeout:
            pass
        else:
            raise AssertionError('unexpected extra or unauthorized frame')
        finally:
            self.s.settimeout(10)

    def closed(self):
        try:
            self.read()
        except EOFError:
            return
        raise AssertionError('revoked socket remained open')

    def close(self):
        self.s.close()


def frame(kind, payload):
    return {'protocolVersion': '1.0', 'type': kind, 'requestId': str(uuid.uuid4()), 'payload': payload}


def main():
    project = 'im-s1-e2e-' + str(os.getpid()) + '-' + secrets.token_hex(4)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    env = os.environ.copy()
    env.update(IM_HTTPS_PORT=str(port), COMPOSE_PROGRESS='quiet')
    command = ['docker', 'compose', '-f', str(ROOT / 'deploy/compose.yaml'), '-p', project, '--profile', 'go']
    sockets = []

    def docker(args, *, data=None):
        result = subprocess.run(args, env=env, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        if result.returncode:
            raise RuntimeError('Docker test command failed: ' + result.stderr.decode(errors='replace'))
        return result.stdout

    def compose(*args):
        return docker(command + list(args))

    def sql(query):
        return compose('exec', '-T', 'postgres', 'psql', '-U', 'im', '-d', 'im', '-v', 'ON_ERROR_STOP=1', '-Atc', query).decode().strip()

    def cleanup():
        # Inspect every actually owned resource before the bounded Compose cleanup.
        ids = docker(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=' + project]).decode().split()
        for cid in ids:
            obj = json.loads(docker(['docker', 'inspect', cid]))[0]
            require(obj['Config']['Labels'].get('com.docker.compose.project') == project, 'container ownership mismatch')
        volumes = docker(['docker', 'volume', 'ls', '-q', '--filter', 'label=com.docker.compose.project=' + project]).decode().split()
        for name in volumes:
            obj = json.loads(docker(['docker', 'volume', 'inspect', name]))[0]
            require(obj['Labels'].get('com.docker.compose.project') == project, 'volume ownership mismatch')
        compose('down', '--volumes', '--remove-orphans')
        require(not docker(['docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=' + project]).strip(), 'owned container remains')
        require(not docker(['docker', 'volume', 'ls', '-q', '--filter', 'label=com.docker.compose.project=' + project]).strip(), 'owned volume remains')
        print('PASS cleanup: inspected owned Compose containers/volumes removed', flush=True)

    with tempfile.TemporaryDirectory(prefix='im-s1-e2e-') as temp:
        config = Path(temp) / 'config'
        config.mkdir()
        env['IM_GO_CONFIG_DIR'] = str(config)
        (config / 'config.json').write_bytes((ROOT / 'backend/go/config.example.json').read_bytes())
        (config / 'pg_password').write_text('local-development-only', encoding='utf-8')
        (config / 'jwt_key').write_text(secrets.token_urlsafe(48), encoding='utf-8')
        try:
            compose('config', '--quiet')
            compose('up', '-d', '--build')
            tls_id = compose('ps', '-q', 'tls-go').decode().strip()
            require(bool(tls_id), 'TLS role missing')
            ca = Path(temp) / 'root.crt'
            # Retrieve only the generated PUBLIC root CA, never a private key.
            for _ in range(60):
                try:
                    docker(['docker', 'cp', tls_id + ':/data/caddy/pki/authorities/local/root.crt', str(ca)])
                    break
                except RuntimeError:
                    time.sleep(.5)
            else:
                raise RuntimeError('Caddy public root CA unavailable')
            context = ssl.create_default_context(cafile=str(ca))
            require(context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED, 'TLS verification disabled')

            def call(method, path, body=None, token=None):
                headers = {'Content-Type': 'application/json'}
                if token:
                    headers['Authorization'] = 'Bearer ' + token
                data = None if body is None else json.dumps(body).encode()
                request = urllib.request.Request(f'https://localhost:{port}' + path, data=data, headers=headers, method=method)
                with urllib.request.urlopen(request, context=context, timeout=10) as response:
                    return response.status, json.loads(response.read() or b'{}')

            for _ in range(60):
                try:
                    with urllib.request.urlopen(f'https://localhost:{port}/__infra/health', context=context, timeout=2) as response:
                        require(response.read().strip() == b'profile=go role=gateway', 'wrong HTTPS role')
                    break
                except OSError:
                    time.sleep(.5)
            else:
                raise RuntimeError('verified TLS Gateway unavailable')
            # Exact negative controls: generic TLS failures cannot prove name checking.
            try:
                with socket.create_connection(('localhost', port), timeout=5) as raw:
                    ssl.create_default_context().wrap_socket(raw, server_hostname='localhost')
            except ssl.SSLCertVerificationError as error:
                require(error.verify_code not in (62, 64), 'untrusted-CA probe failed for wrong reason')
            else:
                raise AssertionError('untrusted local CA accepted')
            # Default Caddy rejects unknown SNI before serving a certificate.
            # Temporarily serve its existing localhost certificate for this negative
            # handshake, then restore the exact original policy before business E2E.
            original_config = json.loads(compose('exec', '-T', 'tls-go', 'wget', '-qO-', 'http://127.0.0.1:2019/config/'))
            negative_config = copy.deepcopy(original_config)
            servers = negative_config['apps']['http']['servers']
            tls_servers = [server for server in servers.values() if ':443' in server['listen']]
            require(len(tls_servers) == 1, 'unexpected TLS server configuration')
            policies = tls_servers[0].setdefault('tls_connection_policies', [{}])
            require(len(policies) == 1, 'unexpected TLS connection policies')
            policies[0]['fallback_sni'] = 'localhost'

            def load_caddy(configuration):
                docker(command + ['exec', '-T', 'tls-go', 'wget', '-qO-', '--header=Content-Type: application/json', '--post-file=/dev/stdin', 'http://127.0.0.1:2019/load'], data=json.dumps(configuration).encode())

            try:
                load_caddy(negative_config)
                try:
                    with socket.create_connection(('localhost', port), timeout=5) as raw:
                        with context.wrap_socket(raw, server_hostname='wrong.invalid'):
                            pass
                except ssl.SSLCertVerificationError as error:
                    require(error.verify_code in (62, 64), 'hostname probe failed for another certificate reason')
                else:
                    raise AssertionError('wrong certificate hostname accepted')
            finally:
                load_caddy(original_config)
                restored = json.loads(compose('exec', '-T', 'tls-go', 'wget', '-qO-', 'http://127.0.0.1:2019/config/'))
                require(restored == original_config, 'original Caddy configuration not restored')
            print('PASS TLS: trusted CA/CERT_REQUIRED/hostname HTTPS+WSS; untrusted CA and certificate name mismatch rejected', flush=True)
            require(sql('SELECT version FROM schema_migrations') == '0001_initial', 'canonical migration missing')
            for role in ['core', 'gateway', 'plugin-host']:
                require(compose('exec', '-T', role + '-go', 'wget', '-qO-', 'http://localhost:8080/__infra/health').strip() == f'profile=go role={role}'.encode(), 'real role missing')

            http_fixture = 'contracts/fixtures/auth-user-friend/positive.json'
            registration = fixture(http_fixture, 'registration-and-authorized-user-search')['steps'][0]
            login_input = fixture(http_fixture, 'same-slot-login-replaces-only-that-slot')['steps'][0]['request']['body']
            users, tokens, names, logins = [], [], [], []
            for index in range(3):
                body = copy.deepcopy(registration['request']['body'])
                body['username'] = 'e2e' + secrets.token_hex(8)
                names.append(body['username'])
                status, registered = call('POST', '/v1/auth/register', body)
                require(status == registration['expected']['status'], 'registration status differs')
                expected = copy.deepcopy(registration['expected']['body'])
                expected['user']['username'] = body['username']
                Oracle().check(expected, registered)
                users.append(registered['user']['userId'])
                body = copy.deepcopy(login_input)
                body['username'] = names[-1]
                body['password'] = registration['request']['body']['password']
                status, login = call('POST', '/v1/auth/login', body)
                require(status == 200 and login['session']['userId'] == users[-1], 'login failed')
                tokens.append(login['tokens']['accessToken'])
                logins.append(login)
            status, found = call('GET', '/v1/users/search?username=' + names[1].upper(), token=tokens[0])
            require(status == 200 and len(found['users']) == 1 and found['users'][0]['userId'] == users[1], 'exact normalized search failed')
            friend_steps = fixture(http_fixture, 'friend-add-normalizes-and-reuses-direct')['steps']
            status, first = call('PUT', '/v1/friends/' + users[1], token=tokens[0])
            require(status == friend_steps[0]['expected']['status'], 'first friendship failed')
            low, high = sorted(users[:2])
            friend_oracle = Oracle({'10000000-0000-4000-8000-000000000001': low, '20000000-0000-4000-8000-000000000002': high})
            expected = copy.deepcopy(friend_steps[0]['expected']['body'])
            # Membership is a set; canonical fixture order is normalized pair order.
            first['memberUserIds'].sort()
            friend_oracle.check(expected, first)
            conv = first['directConversationId']
            status, reverse = call('PUT', '/v1/friends/' + users[0], token=tokens[1])
            require(status == friend_steps[1]['expected']['status'], 'reverse friendship failed')
            reverse['memberUserIds'].sort()
            friend_oracle.check(friend_steps[1]['expected']['body'], reverse)
            for index in [0, 1]:
                status, friends = call('GET', '/v1/friends', token=tokens[index])
                require(status == 200 and len(friends['friends']) == 1 and friends['friends'][0]['directConversationId'] == conv, 'friend list differs')
            require(sql(f"SELECT count(*) FROM friendships WHERE user_low_id='{low}' AND user_high_id='{high}'") == '1', 'duplicate friendship')
            require(sql(f"SELECT count(*) FROM conversations WHERE kind='DIRECT' AND direct_user_low_id='{low}' AND direct_user_high_id='{high}'") == '1', 'duplicate DIRECT')
            require(sql(f"SELECT count(*) FROM conversation_members WHERE conversation_id='{conv}' AND left_at IS NULL") == '2', 'DIRECT members differ')

            def bind(token):
                ws = WS(context, port)
                sockets.append(ws)
                request = frame('auth.bind', {'accessToken': token})
                ws.send(request)
                ack = ws.read()
                require(ack['type'] == 'auth.ack' and ack['requestId'] == request['requestId'], 'bind identity differs')
                return ws, ack

            sender, bound = bind(tokens[0]); require(bound['payload']['status'] == 'bound', 'A not bound')
            receiver, bound = bind(tokens[1]); require(bound['payload']['status'] == 'bound', 'B not bound')
            outsider, bound = bind(tokens[2]); require(bound['payload']['status'] == 'bound', 'C not bound')
            wss_fixture = 'contracts/fixtures/websocket/golden.json'
            durable = fixture(wss_fixture, 'durable-send-and-created')['steps'][0]
            oracle = Oracle({'30000000-0000-4000-8000-000000000001': conv, '10000000-0000-4000-8000-000000000001': users[0]})
            send = copy.deepcopy(durable['in']); send['payload']['conversationId'] = conv
            sender.send(send)
            ack = sender.read()
            oracle.check(durable['out'][0], ack)

            def durable_rows():
                return sql(f"SELECT json_build_object('messages',(SELECT count(*) FROM messages WHERE conversation_id='{conv}'),'outbox',(SELECT count(*) FROM outbox_events WHERE conversation_id='{conv}' AND event_type='message.created'),'nextSeq',(SELECT next_seq FROM conversations WHERE conversation_id='{conv}'))")

            require(json.loads(durable_rows()) == {'messages': 1, 'outbox': 1, 'nextSeq': 2}, 'ACK not backed by durable atomic rows')
            mid = ack['payload']['messageId']
            require(sql(f"SELECT count(*) FROM messages m JOIN outbox_events o ON o.message_id=m.server_message_id AND o.conversation_id=m.conversation_id WHERE m.server_message_id='{mid}' AND m.sender_id='{users[0]}' AND m.request_id='{send['requestId']}' AND m.seq=1 AND m.text_body='hello' AND o.event_type='message.created'") == '1', 'durable message/Outbox identity differs')
            oracle.check(durable['out'][1], receiver.read())
            receiver.quiet(); outsider.quiet(); sender.quiet()
            # Do not impose cross-socket read ordering as new ACK semantics.
            require(sql(f"SELECT count(*) FROM outbox_events WHERE message_id='{mid}' AND published_at IS NOT NULL AND attempts>=1") == '1', 'NATS publication not recorded')
            sender.send(send)
            oracle.check(fixture(wss_fixture, 'idempotent-retry')['steps'][1]['out'][0], sender.read())
            conflict = copy.deepcopy(fixture(wss_fixture, 'conflicting-retry')['steps'][1]['in'])
            conflict['payload']['conversationId'] = conv
            sender.send(conflict)
            oracle.check(fixture(wss_fixture, 'conflicting-retry')['steps'][1]['out'][0], sender.read())
            rejected = copy.deepcopy(fixture(wss_fixture, 'non-member-send')['steps'][0]['in'])
            rejected['requestId'] = str(uuid.uuid4()); rejected['payload']['conversationId'] = conv
            outsider.send(rejected)
            expected = copy.deepcopy(fixture(wss_fixture, 'non-member-send')['steps'][0]['out'][0]); expected['requestId'] = rejected['requestId']
            Oracle().check(expected, outsider.read())
            require(json.loads(durable_rows()) == {'messages': 1, 'outbox': 1, 'nextSeq': 2}, 'retry/conflict/nonmember changed durable rows')

            # Minimal actual COMMIT fault: scoped to this test send in disposable DB.
            failed = copy.deepcopy(fixture(wss_fixture, 'rollback-before-ack')['steps'][0]['in'])
            failed['requestId'] = str(uuid.uuid4()); failed['payload']['conversationId'] = conv
            name = 'e2e_commit_' + secrets.token_hex(8)
            sql(f"CREATE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.event_type='message.created' AND NEW.conversation_id='{conv}'::uuid AND NEW.payload->>'requestId'='{failed['requestId']}' THEN RAISE EXCEPTION 'E2E deferred commit rollback'; END IF; RETURN NEW; END $$; CREATE CONSTRAINT TRIGGER {name} AFTER INSERT ON outbox_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION {name}()")
            try:
                sender.send(failed)
                expected = copy.deepcopy(fixture(wss_fixture, 'rollback-before-ack')['steps'][0]['out'][0]); expected['requestId'] = failed['requestId']
                Oracle().check(expected, sender.read())
                require(json.loads(durable_rows()) == {'messages': 1, 'outbox': 1, 'nextSeq': 2}, 'rollback persisted effects or sequence gap')
                require(sql(f"SELECT count(*) FROM messages WHERE conversation_id='{conv}' AND request_id='{failed['requestId']}'") == '0', 'failed Message persisted')
                receiver.quiet(); outsider.quiet(); sender.quiet()
            finally:
                sql(f'DROP TRIGGER {name} ON outbox_events; DROP FUNCTION {name}()')
            print('PASS fixtures: HTTPS register/login/search/friend unique DIRECT; WSS hello/SQL durable ACK/one Outbox/NATS recipient; retry/conflict/nonmember/deferred COMMIT rollback; no duplicates/wrong recipient', flush=True)

            body = copy.deepcopy(login_input); body['username'] = names[0]; body['password'] = registration['request']['body']['password']
            _, replacement = call('POST', '/v1/auth/login', body)
            require(replacement['session']['sessionEpoch'] == logins[0]['session']['sessionEpoch'] + 1, 'replacement epoch not advanced')
            event = sender.read()
            require(event['type'] == 'session.revoked' and event['payload'] == {'sessionId': logins[0]['session']['sessionId'], 'reason': 'REPLACED'}, 'replacement revocation differs')
            sender.closed()
            stale, ack = bind(tokens[0]); require(ack['payload']['status'] == 'rejected', 'old token rebound')
            stale.close()
            current, ack = bind(replacement['tokens']['accessToken']); require(ack['payload']['status'] == 'bound', 'replacement not bound')
            require(call('POST', '/v1/auth/logout', token=replacement['tokens']['accessToken'])[0] == 204, 'logout failed')
            event = current.read()
            require(event['type'] == 'session.revoked' and event['payload'] == {'sessionId': replacement['session']['sessionId'], 'reason': 'LOGOUT'}, 'logout revocation differs')
            current.closed()
            require(json.loads(durable_rows()) == {'messages': 1, 'outbox': 1, 'nextSeq': 2}, 'revocation changed messaging rows')
            print('PASS revocation: replacement epoch/revoked then close/stale token reject/logout then close; no runtime skips', flush=True)
            print('DEFERRED_BY_HUMAN: friend-add-authorization-denied only (ADR-0004); not counted PASS', flush=True)
        finally:
            for ws in sockets:
                ws.close()
            cleanup()


if __name__ == '__main__':
    main()

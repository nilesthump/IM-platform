"""Exercise failure propagation through the two live parity runner entry points."""
from contextlib import ExitStack
import os
from pathlib import Path
import ssl
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import urllib.error

import go_tls_messaging as tls


class ClientCleanup(unittest.TestCase):
    def test_registration_and_disposal_failures_are_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            application = root / 'web/src/application'
            application.mkdir(parents=True)
            (root / 'package.json').write_text('{"type":"module"}')
            (application / 'client.js').write_text("""
                let next = 0;
                globalThis.fetch = async () => { throw new Error('registration fault'); };
                export class WebClient {
                  id = ++next;
                  dispose() {
                    console.log('disposed', this.id);
                    if (process.env.FAULT_DISPOSE === 'yes') throw new Error('cleanup fault ' + this.id);
                  }
                }
            """)
            for fault in ['yes', 'no']:
                with self.subTest(fault=fault):
                    result = subprocess.run(
                        ['node', str(Path(__file__).with_name('parity.mjs')), tmp, 'https://localhost'],
                        env=dict(os.environ, FAULT_DISPOSE=fault), text=True, capture_output=True, timeout=15)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout.splitlines(), ['disposed 1', 'disposed 2'])
                    self.assertIn('Error: registration fault', result.stderr)
                    if fault == 'yes':
                        for message in ['AggregateError', 'Error: cleanup fault 1', 'Error: cleanup fault 2']:
                            self.assertIn(message, result.stderr)
                    else:
                        self.assertNotIn('AggregateError', result.stderr)


class ProfileFailures(unittest.TestCase):
    def run_faults(self, docker, health=None):
        context = Mock(check_hostname=True, verify_mode=ssl.CERT_REQUIRED)
        with patch.object(tls.subprocess, 'run', side_effect=docker), \
                patch.object(tls.ssl, 'create_default_context', return_value=context), \
                patch.object(tls.urllib.request, 'urlopen', side_effect=health), patch.object(tls.time, 'sleep'):
            tls.run_profile('java')

    def test_ca_copy_and_health_classification(self):
        missing = b'Could not find the file /data/caddy/pki/authorities/local/root.crt in container tls-id'
        for fault, expected_attempts in [(b'permission denied', 1), (missing, 60), (None, 1)]:
            with self.subTest(fault=fault):
                copies = []
                def docker(argv, **kwargs):
                    if argv[1] == 'cp':
                        copies.append(argv)
                        if fault:
                            return subprocess.CompletedProcess(argv, 1, b'', fault)
                    output = b'tls-id' if argv[-3:] == ['ps', '-q', 'tls-java'] else b''
                    return subprocess.CompletedProcess(argv, 0, output, b'')

                cert_error = urllib.error.URLError(ssl.SSLCertVerificationError('invalid certificate'))
                health = Mock(side_effect=cert_error)
                with self.assertRaises((RuntimeError, urllib.error.URLError)) as raised:
                    self.run_faults(docker, health)
                self.assertEqual(len(copies), expected_attempts)
                if fault == missing:
                    self.assertIn(missing.decode(), str(raised.exception.__cause__))
                elif fault:
                    self.assertIn('permission denied', str(raised.exception))
                else:
                    self.assertIs(raised.exception, cert_error)
                    health.assert_called_once()

    def test_gateway_startup_retries_only_transient_faults(self):
        refused = urllib.error.URLError(ConnectionRefusedError())
        http = lambda code: urllib.error.HTTPError('https://localhost', code, 'response', {}, None)
        with patch.object(tls.time, 'sleep'):
            check = Mock(side_effect=[refused, http(502), None])
            tls.wait_for_startup(check, tls.gateway_starting, 'gateway')
            self.assertEqual(check.call_count, 3)
            for error, attempts in [(refused, 60), (http(403), 1), (PermissionError(), 1)]:
                with self.subTest(error=error):
                    check = Mock(side_effect=error)
                    with self.assertRaises(Exception) as raised:
                        tls.wait_for_startup(check, tls.gateway_starting, 'gateway')
                    self.assertIs(raised.exception.__cause__ if attempts == 60 else raised.exception, error)
                    self.assertEqual(check.call_count, attempts)

    def test_socket_faults_still_run_owned_compose_cleanup(self):
        calls = []
        def fail_close(name):
            calls.append(name)
            raise OSError(name)

        class WithFaultySockets(ExitStack):
            def callback(self, callback, *args, **kwargs):
                super().callback(callback, *args, **kwargs)
                super().callback(fail_close, 'close 1')
                super().callback(fail_close, 'close 2')

        def docker(argv, **kwargs):
            if argv[-1] == '--quiet':
                raise ValueError('body fault')
            if 'down' in argv:
                calls.append('compose down')
                raise RuntimeError('compose fault')
            return subprocess.CompletedProcess(argv, 0, b'', b'')

        with patch.object(tls, 'ExitStack', WithFaultySockets), self.assertRaises(RuntimeError) as raised:
            self.run_faults(docker)
        self.assertEqual(calls, ['close 2', 'close 1', 'compose down'])
        error = raised.exception
        for message in ['compose fault', 'close 1', 'close 2', 'body fault']:
            self.assertEqual(str(error), message)
            error = error.__context__


if __name__ == '__main__':
    unittest.main()

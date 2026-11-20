"""Exercise the live harness teardown with failing roles, without starting services."""
import contextlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
import verify_java_auth as harness


class ProfileCleanupTest(unittest.TestCase):
    def test_failed_roles_release_logs_and_binding_and_preserve_body_failure(self):
        for name in ('go', 'java'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
                folder = Path(tmp)
                (folder / 'url').write_text('http://localhost')
                env = dict(PGHOST='localhost', PGPORT='1234', PGUSER='test', PGDATABASE='fixture',
                           PGPASSWORD='fixture', JAVA_AUTH_SIGNING_KEY='fixture', NATS_URL='nats://localhost')
                seed = stack.enter_context(patch.object(harness.subprocess, 'run'))
                launch = stack.enter_context(patch.object(harness.subprocess, 'Popen'))
                stack.enter_context(patch.object(harness, 'wait_for'))
                disclosure = stack.enter_context(patch.object(harness, 'check_disclosure'))
                failed = Mock()
                timeout = harness.subprocess.TimeoutExpired('role', 15)
                if name == 'go':
                    failed.wait.return_value = 2
                    failed.poll.return_value = 2
                    launch.return_value = failed
                else:
                    healthy = Mock()
                    healthy.poll.return_value = failed.poll.return_value = None
                    failed.wait.side_effect = [timeout, 0]
                    launch.side_effect = [healthy, failed]
                body = AssertionError('fixture assertion')
                with self.assertRaises(BaseExceptionGroup) as observed:
                    with harness.profile(name, folder, folder, env, 'java', 'cp', folder / 'binding'):
                        raise body
                primary, secondary = observed.exception.exceptions
                self.assertIs(body, primary)
                if name == 'go':
                    self.assertRegex(str(secondary), 'Go fixture host failed: 2')
                else:
                    self.assertIs(secondary, timeout)
                    failed.kill.assert_called_once()
                    healthy.terminate.assert_called_once()
                self.assertEqual(seed.call_args.args[0][-3], 'cleanup')
                disclosure.assert_called_once()
                logs = disclosure.call_args.args[1]
                self.assertEqual(len(logs), 1 if name == 'go' else 2)
                self.assertTrue(all(log.closed for log in logs))


if __name__ == '__main__':
    unittest.main()

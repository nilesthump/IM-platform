"""Negative controls for the prerequisite/product CI boundary, not GUI acceptance."""
import importlib.util
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('web_verifier', ROOT/'tests/clients/web/verify.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class WebVerificationControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = mock.patch.dict(os.environ, {'GITHUB_ACTIONS': 'false'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.put('clients/web/.gitkeep', '')
        self.put('clients/shared/protocol-sdk/src/types.ts', 'export type Id = string;')
        self.put('spec/tasks/backlog/LOOP1-WEB-001.md', '---\nstatus: backlog\n---\nweb_verification_phase: appearance_prerequisite\n')
        self.put('spec/progress/current.md', 'Current Task: LOOP1-WEB-001\nCurrent Task State: backlog\nExecution Status: APPROVED_PENDING_FREEZE\n')
        self.git('init', '-q')
        self.commit()
        self.commands = []

    def put(self, name, content):
        p = self.root/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content.encode('utf-8'))
        return p

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.STDOUT).decode().strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Web verifier control', '-c', 'user.email=web-control@example.invalid', 'commit', '-qm', 'control input')
        return self.git('rev-parse', 'HEAD')

    def collect(self, command, *, cwd, env=None):
        self.commands.append(command)
        if command[-2:] == ['run', 'build']:
            artifact = Path(env['WEB_BUILD_DIR'])
            artifact.mkdir(parents=True)
            (artifact/'index.html').write_text('<html/>')
            (artifact/'app.js').write_text('export const built = true;')

    def product(self):
        for name in verifier.REQUIRED:
            self.put('clients/web/'+name, '{}')
        for name in verifier.BEHAVIOR:
            self.put(name, '// fixture; runner is explicitly mocked, never GUI evidence')

    def test_only_exact_marker_at_explicit_backlog_prerequisite_is_allowed(self):
        for marker in verifier.MARKERS:
            with self.subTest(marker=marker):
                (self.root/'clients/web/.gitkeep').write_bytes(marker)
                self.assertEqual(verifier.verify(self.root, runner=self.collect), 'PREREQUISITE_SKELETON_ONLY')
                self.assertFalse(any('npm' in str(arg) for command in self.commands for arg in command))
        for marker in (b' ', b'\n\n', b'product source'):
            with self.subTest(marker=marker):
                (self.root/'clients/web/.gitkeep').write_bytes(marker)
                with self.assertRaisesRegex(ValueError, 'Incomplete Web product'):
                    verifier.verify(self.root, runner=self.collect)

    def test_active_paused_or_ambiguous_task_cannot_use_skeleton_branch(self):
        task = self.root/'spec/tasks/backlog/LOOP1-WEB-001.md'
        original = task.read_bytes()
        for content in ('status: active\nweb_verification_phase: appearance_prerequisite',
                        'status: backlog\nweb_verification_phase: product'):
            task.write_text(content)
            with self.assertRaisesRegex(ValueError, 'cannot bypass'):
                verifier.verify(self.root, runner=self.collect)
        task.write_bytes(original)
        other = self.put('spec/tasks/active/LOOP1-WEB-001.md', 'status: active')
        with self.assertRaisesRegex(ValueError, 'cannot bypass'):
            verifier.verify(self.root, runner=self.collect)
        other.unlink()
        self.put('spec/progress/current.md', 'Current Task: LOOP1-WEB-001\nCurrent Task State: backlog\nExecution Status: PAUSED_BY_HUMAN')
        with self.assertRaisesRegex(ValueError, 'cannot bypass'):
            verifier.verify(self.root, runner=self.collect)

    def test_partial_source_manifest_missing_lock_or_behavior_never_falls_back(self):
        source = self.put('clients/web/src/ui/main.tsx', 'export const App = null;')
        with self.assertRaisesRegex(ValueError, 'Incomplete Web product'):
            verifier.verify(self.root, runner=self.collect)
        source.unlink()
        self.product()
        for name in ('clients/web/package-lock.json', 'tests/clients/web/appearance.mjs', 'clients/web/src/ui/appearance.ts'):
            p = self.root/name
            original = p.read_bytes()
            p.unlink()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Incomplete Web product'):
                verifier.verify(self.root, runner=self.collect)
            p.write_bytes(original)
        self.assertEqual(self.commands, [])

    def test_deleting_previously_committed_product_cannot_regain_empty_exception(self):
        product = self.put('clients/web/src/real.ts', 'export const real = true;')
        self.commit()
        product.unlink()
        (self.root/'clients/web/src').rmdir()
        with self.assertRaisesRegex(ValueError, 'cannot bypass'):
            verifier.verify(self.root, runner=self.collect)

    def test_product_failures_propagate_before_any_success_or_skeleton_result(self):
        self.product()
        with mock.patch.object(verifier.shutil, 'which', side_effect=lambda value: value):
            for phase in ('source', 'ci', 'build', 'behavior.mjs', 'appearance.mjs'):
                self.commands = []
                def failing(command, *, cwd, env=None):
                    if ((phase == 'source' and 'ci/check_architecture.py' in command)
                            or (phase == 'ci' and 'ci' in command)
                            or (phase == 'build' and command[-2:] == ['run', 'build'])
                            or any(str(arg).endswith('/'+phase) or str(arg).endswith('\\'+phase) for arg in command)):
                        raise subprocess.CalledProcessError(17, command)
                    self.collect(command, cwd=cwd, env=env)
                with self.subTest(phase=phase), self.assertRaises(subprocess.CalledProcessError):
                    verifier.verify(self.root, runner=failing)
                self.assertFalse(any('ci/check_s0_boundary.py' in command for command in self.commands))

    def test_complete_product_route_requires_artifacts_and_both_actual_test_entries(self):
        self.product()
        with mock.patch.object(verifier.shutil, 'which', side_effect=lambda value: value):
            self.assertEqual(verifier.verify(self.root, runner=self.collect), 'PRODUCT_VERIFIED')
            self.assertEqual(sum('ci' in command for command in self.commands), 1)
            for test in verifier.BEHAVIOR:
                self.assertTrue(any(str(self.root/test) in command for command in self.commands))
            with self.assertRaisesRegex(ValueError, 'build artifacts missing'):
                verifier.verify(self.root, runner=lambda *args, **kwargs: None)
        self.assertFalse((self.root/'clients/web/node_modules').exists())

    def test_symlink_inputs_fail_without_os_link_privilege(self):
        original = Path.is_symlink
        for target in (self.root/'clients/web', self.root/'clients/web/.gitkeep'):
            def marked(path):
                return path == target or original(path)
            with self.subTest(target=target), mock.patch.object(Path, 'is_symlink', marked):
                with self.assertRaisesRegex(ValueError, 'symlink'):
                    verifier.verify(self.root, runner=self.collect)

    def test_hosted_base_and_exact_head_come_from_event_and_product_base_is_not_ignored(self):
        base = self.git('rev-parse', 'HEAD')
        self.put('control.txt', 'change')
        head = self.commit()
        event = self.put('event.json', json.dumps({'before': base, 'after': head}))
        with mock.patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_PATH': str(event), 'GITHUB_EVENT_NAME': 'push'}):
            self.assertEqual(verifier.compared_base(self.root), base)
            event.write_text(json.dumps({'before': base, 'after': base}))
            with self.assertRaisesRegex(ValueError, 'exact event head'):
                verifier.compared_base(self.root)
            event.write_text(json.dumps({'pull_request': {'base': {'sha': base}, 'head': {'sha': head}}}))
            with mock.patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'pull_request'}):
                self.assertEqual(verifier.compared_base(self.root), base)


if __name__ == '__main__':
    unittest.main()

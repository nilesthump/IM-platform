import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('client_checker', ROOT/'ci/check_architecture.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class ClientTechnologyControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('spec/architecture/baseline.md', 'spec/architecture/frozen-architecture.md', 'spec/architecture/decisions/ADR-0005-client-technology-clarification.md'):
            destination = self.root/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/name, destination)

    def put(self, name, content):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def test_current_active_clients(self):
        self.assertEqual([], checker.check_clients(ROOT))

    def test_approved_ts_native_config_assets(self):
        for name, content in {
            'clients/shared/protocol-sdk/types.ts': 'export type Envelope = {request_id: string};',
            'clients/shared/ui/view.tsx': 'import React from "react"; export const View = () => <div/>;',
            'clients/web/package.json': '{"dependencies":{"react":"18","react-dom":"18"},"devDependencies":{"typescript":"5","@types/react":"18"}}',
            'clients/web/tsconfig.json': '{}',
            'clients/web/tool.config.mjs': 'export default {};',
            'clients/desktop/src-tauri/main.rs': 'fn main() {}',
            'clients/desktop/src-tauri/build.rs': 'fn main() {}',
            'clients/desktop/src-tauri/Cargo.toml': '[dependencies]\ntauri="2"\nsqlx={version="0.8",features=["sqlite"]}\n[build-dependencies]\ntauri-build="2"',
            'clients/desktop/src-tauri/capabilities/default.json': '{}',
            'clients/desktop/package.json': '{"dependencies":{"react":"18","@tauri-apps/api":"2"}}',
            'clients/mobile/data/model.ts': 'export type State = "SENDING" | "SENT" | "FAILED";',
            'clients/mobile/data/migration.sql': 'CREATE TABLE messages(id TEXT);',
            'clients/web/style.css': 'body {color:black}',
            'clients/web/logo.svg': '<svg/>',
        }.items(): self.put(name, content)
        self.assertEqual([], checker.check_clients(self.root))

    def test_forbidden_source_and_config_controls(self):
        cases = {
            'clients/shared/store.dart': 'void main() {}',
            'clients/mobile/pubspec.yaml': 'name: app',
            'clients/shared/pubspec.lock': 'packages: {}',
            'clients/desktop/.metadata': 'project_type: app',
            'clients/mobile/lib/App.swift': 'import UIKit',
            'clients/shared/repository.rs': 'fn repository() {}',
            'clients/web/src/main.js': 'export const message = {};',
            '.github/workflows/client.yml': 'steps:\n- uses: dart-lang/setup-dart@v1',
            'clients/mobile/build.yml': 'run: flutter build apk',
            'clients/mobile/native.json': '{"runtime":"expo"}',
            'clients/web/config.json': '{"runtime":"Deno"}',
            'clients/web/data.ts': 'const db = indexedDB.open("history");',
            'clients/web/storage.sql': '-- SQLite history',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                path = self.put(name, content)
                self.assertTrue(checker.check_clients(self.root))
                path.unlink()

    def test_unapproved_generic_dependencies_and_imports(self):
        cases = {
            'clients/shared/package.json': '{"dependencies":{"new-client-framework":"1"}}',
            'clients/web/package.json': '{"devDependencies":{"new-runtime":"1"}}',
            'clients/mobile/package.json': '{"dependencies":{"react":"18"}}',
            'clients/mobile/platform.ts': 'import {x} from "new-client-framework";',
            'clients/shared/runtime.ts': 'const x = require("new-runtime");',
            'clients/shared/platform.ts': 'const x = import("new-framework");',
            'clients/desktop/src-tauri/Cargo.toml': '[dependencies]\nstorage={package="rusqlite",version="1"}',
            'clients/desktop/src-tauri/Cargo.toml.sqlx_other_db': '[dependencies]\nsqlx={version="0.8",features=["postgres"]}',
            'clients/desktop/sql_calls.ts': 'import Database from "@tauri-apps/plugin-sql"; db.execute("BEGIN"); db.execute("INSERT"); db.execute("COMMIT");',
            'clients/desktop/src-tauri/Cargo.toml.target': '[target.windows.dependencies]\nnew-native="1"',
            '.github/workflows/client.yml': 'run: npm install new-client-framework',
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                if name.endswith('.target'): name = name.removesuffix('.target')
                if name.endswith('.sqlx_other_db'): name = name.removesuffix('.sqlx_other_db')
                path = self.put(name, content)
                self.assertTrue(checker.check_clients(self.root))
                path.unlink()

    def test_task_paths_and_passing_tests_cannot_approve_framework(self):
        task = '# Allowed Paths\n- `clients/mobile/**`\n# Technology Authorization\nclient_framework: NewFramework\nclient_runtime: NewRuntime\n# Verification\nTests PASS\n'
        errors = checker.client_task_violations(task, 'spec/tasks/active/TASK.md', self.root)
        self.assertTrue(any('NewFramework' in error for error in errors))
        self.assertTrue(any('NewRuntime' in error for error in errors))
        self.assertTrue(checker.client_task_violations(task.replace('NewFramework', 'React'), 'TASK.md', self.root))
        valid = 'client_language: TypeScript\nclient_framework: React\nclient_runtime: Tauri\nclient_dependency: typescript\n'
        self.assertEqual([], checker.client_task_violations(valid, 'TASK.md', self.root))
        native = '# Allowed Paths\n- `clients/desktop/src-tauri/**`\nclient_dependency: sqlx\nclient_language: Rust\n'
        self.assertEqual([], checker.client_task_violations(native, 'TASK.md', self.root))
        self.assertTrue(checker.client_task_violations(native.replace('clients/desktop/src-tauri/', 'clients/shared/'), 'TASK.md', self.root))

    def test_authority_missing_or_mutated_is_failure(self):
        self.put('spec/architecture/frozen-architecture.md', 'client_framework: NewFramework')
        self.assertTrue(checker.check_clients(self.root))
        self.assertTrue(checker.client_task_violations('client_framework: NewFramework', 'TASK.md', self.root))

    def test_history_is_not_active_client_implementation(self):
        self.put('research/runs/immutable/example.dart', 'void main() {}')
        self.put('spec/progress/evidence/HISTORICAL/pubspec.yaml', 'dependencies: flutter')
        self.assertEqual([], checker.check_clients(self.root))

    def test_symlink_cannot_bypass_boundary(self):
        source = self.put('archive/bad.dart', 'void main() {}')
        link = self.root/'clients/shared/store.ts'
        link.parent.mkdir(parents=True)
        try: link.symlink_to(source)
        except OSError:
            # Windows without symlink privilege still exercises the rejection branch.
            from unittest.mock import patch
            self.put('clients/shared/store.ts', 'export const x = 1;')
            original = Path.is_symlink
            with patch.object(Path, 'is_symlink', lambda path: path == link or original(path)):
                self.assertTrue(checker.check_clients(self.root))
        else:
            self.assertTrue(checker.check_clients(self.root))

if __name__ == '__main__': unittest.main()
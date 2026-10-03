import importlib.util
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("classify", ROOT / "ci/classify.py")
classify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_module)


class PathMatrixTests(unittest.TestCase):
    def assert_jobs(self, path, expected):
        actual = classify_module.classify([path])
        self.assertEqual({job for job, enabled in actual.items() if enabled}, set(expected), path)

    def test_profile_and_client_changes_are_local(self):
        for path, job in (
            ("backend/go/main.go", {"go", "architecture", "source_go"}),
            ("backend/java/App.java", {"java", "architecture", "source_java"}),
            ("clients/web/src/App.tsx", {"web", "architecture"}),
            ("clients/desktop/db/schema.sql", {"desktop", "architecture"}),
            ("clients/mobile/app.kt", {"mobile", "architecture"}),
        ):
            with self.subTest(path=path):
                self.assert_jobs(path, job if isinstance(job, set) else {job})

    def test_shared_changes_fan_out_to_full_compatibility(self):
        for path in (
            "contracts/http/api.json",
            "contracts/database/migrations/0001.sql",
            "contracts/plugin-api/v1.schema.json",
            "database/changes.sql",
            "migrations/0002.sql",
            "sdk/protocol/types.go",
            "sdks/plugin/api.ts",
            "shared/protocol/wire.json",
            "backend/shared/protocol.go",
            "backend/java/migrations/0002.sql",
            "clients/shared/sdk.ts",
            "tests/database/test_migrations.py",
        ):
            with self.subTest(path=path):
                self.assert_jobs(path, classify_module.FULL_COMPATIBILITY)

    def test_send_verification_paths_select_actual_runtimes(self):
        expected={"architecture", "desktop", "mobile", "shared", "compatibility"}
        for path in ("tools/verify_client_send.py", "tests/clients/send/desktop.mjs", "tests/clients/send/tls_fixture.py"):
            self.assert_jobs(path,expected)

    def test_deleted_send_fixture_still_runs_actual_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            subprocess.run(["git","init","-q",str(root)],check=True)
            subprocess.run(["git","-C",str(root),"config","user.name","CI test"],check=True)
            subprocess.run(["git","-C",str(root),"config","user.email","ci@example.invalid"],check=True)
            fixture=root/"tests/clients/send/tls_fixture.py"
            fixture.parent.mkdir(parents=True);fixture.write_bytes(b"pass\n")
            subprocess.run(["git","-C",str(root),"add","."],check=True)
            subprocess.run(["git","-C",str(root),"commit","-qm","base"],check=True)
            base=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
            fixture.unlink();subprocess.run(["git","-C",str(root),"add","-u"],check=True)
            subprocess.run(["git","-C",str(root),"commit","-qm","delete"],check=True)
            previous=pathlib.Path.cwd()
            try:
                import os
                os.chdir(root);paths=classify_module.diff_paths(base,"HEAD")
            finally:
                os.chdir(previous)
            self.assertEqual(paths,["tests/clients/send/tls_fixture.py"])
            self.assert_jobs(paths[0],{"architecture","desktop","mobile","shared","compatibility"})

    def test_ci_changes_run_all_jobs(self):
        for path in ("ci/classify.py", "ci/check_s0_boundary.py", ".github/workflows/ci.yml", "tests/ci/test_classify.py"):
            with self.subTest(path=path):
                self.assert_jobs(path, classify_module.JOBS)

    def test_deploy_changes_run_deploy_validation(self):
        for path in ("deploy/compose.yaml", "tests/infrastructure/smoke.ps1"):
            with self.subTest(path=path):
                self.assert_jobs(path, {"deploy"})

    def test_e2e_paths_select_go_deploy_and_boundaries(self):
        for path in ("tests/e2e/go_tls_messaging.py", "tests/e2e/README.md"):
            with self.subTest(path=path):
                self.assert_jobs(path, {"go", "deploy", "architecture", "source_go"})

    def test_deleted_e2e_path_still_selects_live_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "CI test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "ci@example.invalid"], check=True)
            test = root / "tests/e2e/old.py"
            test.parent.mkdir(parents=True)
            test.write_text("pass\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            base = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            test.unlink()
            subprocess.run(["git", "-C", str(root), "add", "-u"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "delete"], check=True)
            head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            previous = pathlib.Path.cwd()
            try:
                import os
                os.chdir(root)
                paths = classify_module.diff_paths(base, head)
            finally:
                os.chdir(previous)
            self.assertEqual(paths, ["tests/e2e/old.py"])
            selected = {job for job, enabled in classify_module.classify(paths).items() if enabled}
            self.assertEqual(selected, {"go", "deploy", "architecture", "source_go"})

    def test_union_and_deleted_paths(self):
        result = classify_module.classify(["backend/go/old.go", "clients/web/new.ts"])
        self.assertEqual({key for key, value in result.items() if value}, {"go", "web", "architecture", "source_go"})

    def test_client_changes_always_select_architecture(self):
        for path, job in [('clients/web/view.tsx','web'), ('clients/desktop/src-tauri/main.rs','desktop'), ('clients/mobile/adapter.ts','mobile'), ('clients/shared/deleted.ts','shared')]:
            with self.subTest(path=path):
                selected = classify_module.classify([path])
                self.assertTrue(selected['architecture'])
                self.assertTrue(selected[job])
        self.assertTrue(all(classify_module.classify(['package.json']).values()))

    def test_git_diff_includes_deleted_shared_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "CI test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "ci@example.invalid"], check=True)
            contract = root / "contracts" / "wire.json"
            contract.parent.mkdir()
            contract.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            base = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            contract.unlink()
            subprocess.run(["git", "-C", str(root), "add", "-u"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "delete"], check=True)
            head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            previous = pathlib.Path.cwd()
            try:
                import os
                os.chdir(root)
                self.assertEqual(classify_module.diff_paths(base, head), ["contracts/wire.json"])
            finally:
                os.chdir(previous)

    def test_git_diff_includes_both_sides_of_shared_renames(self):
        for source in ("contracts/wire.json", "database/schema.sql", "sdk/types.json"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as temp:
                root = pathlib.Path(temp)
                subprocess.run(["git", "init", "-q", str(root)], check=True)
                subprocess.run(["git", "-C", str(root), "config", "user.name", "CI test"], check=True)
                subprocess.run(["git", "-C", str(root), "config", "user.email", "ci@example.invalid"], check=True)
                old = root / source
                old.parent.mkdir(parents=True)
                old.write_text("unique fixture content\n", encoding="utf-8")
                subprocess.run(["git", "-C", str(root), "add", "."], check=True)
                subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
                base = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
                new = root / "docs" / old.name
                new.parent.mkdir()
                old.rename(new)
                subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
                subprocess.run(["git", "-C", str(root), "commit", "-qm", "rename"], check=True)
                head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
                previous = pathlib.Path.cwd()
                try:
                    import os
                    os.chdir(root)
                    paths = classify_module.diff_paths(base, head)
                finally:
                    os.chdir(previous)
                self.assertCountEqual(paths, [source, f"docs/{old.name}"])
                selected = {job for job, enabled in classify_module.classify(paths).items() if enabled}
                self.assertEqual(selected, classify_module.FULL_COMPATIBILITY)

    def test_unrelated_files_do_not_schedule_product_jobs(self):
        self.assert_jobs("docs/unrelated.md", set())

    def test_governance_changes_cannot_skip_architecture(self):
        for path in ("README.md", "AGENTS.md", "CLAUDE.md", "spec/architecture/baseline.md",
                     "spec/architecture/decisions/ADR-9999.md", "spec/handoff/agent-context.md",
                     "spec/tasks/TASK_TEMPLATE.md", "spec/tasks/active/TEST.md",
                     "spec/batches/BATCH.md", "spec/acceptance/s1.md", "spec/governance/minimality.md",
                     "tools/architecture/go_source_graph.go", "tools/verify-frozen-architecture.ps1",
                     "tools/verify_frozen_architecture.py",
                     "tools/verify-loop1-min-001.ps1",
                     "tests/architecture/test_source.py"):
            with self.subTest(path=path):
                self.assert_jobs(path, {"architecture", "source_go", "source_java"})

    def test_governance_deleted_and_renamed_paths_still_trigger(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "CI test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "ci@example.invalid"], check=True)
            for name in ("AGENTS.md", "spec/tasks/TASK_TEMPLATE.md", "tools/verify_frozen_architecture.py"):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("execution rule\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            base = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            (root / "AGENTS.md").unlink()
            (root / "spec/tasks/TASK_TEMPLATE.md").rename(root / "MOVED.md")
            (root / "tools/verify_frozen_architecture.py").rename(root / "MOVED_VERIFY.py")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "move and delete"], check=True)
            head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            previous = pathlib.Path.cwd()
            try:
                import os
                os.chdir(root)
                paths = classify_module.diff_paths(base, head)
            finally:
                os.chdir(previous)
            self.assertCountEqual(paths, ["AGENTS.md", "spec/tasks/TASK_TEMPLATE.md", "MOVED.md", "tools/verify_frozen_architecture.py", "MOVED_VERIFY.py"])
            result = classify_module.classify(paths)
            self.assertEqual({k for k, v in result.items() if v}, {"architecture", "source_go", "source_java"})

    def test_rejects_paths_outside_repo(self):
        for path in ("../outside", "/absolute", "a/../b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                classify_module.classify([path])

    def test_github_outputs_are_lowercase_booleans(self):
        with tempfile.TemporaryDirectory() as temp:
            output = pathlib.Path(temp) / "output"
            classify_module.main(["--paths", "contracts/errors/x.json", "--github-output", str(output)])
            values = dict(line.split("=", 1) for line in output.read_text().splitlines())
            self.assertEqual(values["go"], "true")
            self.assertEqual(values["compatibility"], "true")
            self.assertEqual(values["deploy"], "false")





class ClientStoragePaths(unittest.TestCase):
    def test_actual_storage_runner_and_deleted_fixture_select_actual_clients(self):
        for path in ("tests/clients/sqlite/deleted-fixture.json","tools/verify_client_sqlite.py","tools/verify-client-sqlite.ps1"):
            matrix=classify_module.classify([path])
            for job in ("architecture","desktop","mobile","shared","compatibility"):
                self.assertTrue(matrix[job],(path,job))


if __name__ == "__main__":
    unittest.main()

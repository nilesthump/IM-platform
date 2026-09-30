import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("s0_boundary", ROOT / "ci/check_s0_boundary.py")
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


class S0BoundaryTests(unittest.TestCase):
    def test_committed_skeleton_contains_no_unexpected_source(self):
        for profile in boundary.ALLOWED:
            with self.subTest(profile=profile):
                self.assertEqual(boundary.unexpected_files(ROOT, profile), [])

    def test_empty_markers_are_ignored_but_new_source_is_rejected(self):
        for profile, (relative_dir, allowed) in boundary.ALLOWED.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                directory = root / relative_dir
                nested = directory / "src"
                nested.mkdir(parents=True)
                (directory / ".gitkeep").touch()
                (nested / ".gitkeep").touch()
                for name in allowed:
                    (directory / name).write_text("existing S0 entry", encoding="utf-8")
                self.assertEqual(boundary.unexpected_files(root, profile), [])

                (nested / "future-source.txt").write_text("new source", encoding="utf-8")
                self.assertEqual(boundary.unexpected_files(root, profile), ["src/future-source.txt"])

                (nested / "future-source.txt").unlink()
                (nested / ".gitkeep").write_text("hidden source", encoding="utf-8")
                self.assertEqual(boundary.unexpected_files(root, profile), ["src/.gitkeep"])

    def test_allowed_entry_name_is_only_allowed_at_profile_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            nested = root / "backend/java/src"
            nested.mkdir(parents=True)
            (nested / "InfraPlaceholder.java").write_text("class InfraPlaceholder {}", encoding="utf-8")
            self.assertEqual(boundary.unexpected_files(root, "java"), ["src/InfraPlaceholder.java"])

    def test_symlinks_cannot_hide_behind_allowed_names_or_profile_root(self):
        for profile, (relative_dir, allowed) in boundary.ALLOWED.items():
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                directory = root / relative_dir
                directory.mkdir(parents=True)
                target = root / "target"
                target.write_text("source", encoding="utf-8")
                name = next(iter(allowed), ".gitkeep")
                try:
                    (directory / name).symlink_to(target)
                except (OSError, NotImplementedError) as error:
                    self.skipTest(f"symlink creation unavailable: {error}")
                self.assertEqual(boundary.unexpected_files(root, profile), [name])

                (directory / name).unlink()
                directory.rmdir()
                directory.symlink_to(root, target_is_directory=True)
                self.assertEqual(boundary.unexpected_files(root, profile), [directory.name])

    def test_allowed_name_and_profile_root_symlink_checks_without_os_link_privilege(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / "backend/java"
            directory.mkdir(parents=True)
            allowed = directory / "InfraPlaceholder.java"
            allowed.write_text("source", encoding="utf-8")
            original = Path.is_symlink

            def marks_path(path):
                return path == allowed or original(path)

            with mock.patch.object(Path, "is_symlink", marks_path):
                self.assertEqual(boundary.unexpected_files(root, "java"), ["InfraPlaceholder.java"])

            def marks_directory(path):
                return path == directory or original(path)

            with mock.patch.object(Path, "is_symlink", marks_directory):
                self.assertEqual(boundary.unexpected_files(root, "java"), ["java"])

    def test_all_affected_workflow_jobs_use_boundary_checker(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("python3 ci/check_s0_boundary.py go"), 0)
        self.assertIn("go test -count=1 ./...", workflow)
        self.assertIn("contracts/http/verify-auth-user-friend.ps1", workflow)
        self.assertEqual(workflow.count("python3 ci/check_s0_boundary.py java"), 1)
        for profile in ("web", "desktop", "mobile"):
            self.assertEqual(workflow.count(f"python3 ci/check_s0_boundary.py {profile}"), 2)
        self.assertNotIn("test ! -d clients/", workflow)


if __name__ == "__main__":
    unittest.main()

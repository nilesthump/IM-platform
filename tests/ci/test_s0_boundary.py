import importlib.util
from pathlib import Path
import tempfile
import unittest


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
            nested = root / "backend/go/src"
            nested.mkdir(parents=True)
            (nested / "main.go").write_text("package main", encoding="utf-8")
            self.assertEqual(boundary.unexpected_files(root, "go"), ["src/main.go"])

    def test_all_affected_workflow_jobs_use_boundary_checker(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("python3 ci/check_s0_boundary.py go"), 1)
        self.assertEqual(workflow.count("python3 ci/check_s0_boundary.py java"), 1)
        for profile in ("web", "desktop", "mobile"):
            self.assertEqual(workflow.count(f"python3 ci/check_s0_boundary.py {profile}"), 2)
        self.assertNotIn("test ! -d clients/", workflow)


if __name__ == "__main__":
    unittest.main()

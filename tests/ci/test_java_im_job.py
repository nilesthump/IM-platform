from pathlib import Path
import unittest

from test_classify import classify_module


ROOT = Path(__file__).resolve().parents[2]
RUNNERS = ("tools/verify_java_im.py", "tests/e2e/go_tls_messaging.py", "tools/verify_sync_runtime.py")


class JavaImJobTest(unittest.TestCase):
    def test_changed_runner_selects_live_jobs(self):
        for path in RUNNERS:
            with self.subTest(path=path):
                jobs = classify_module.classify([path])
                self.assertTrue(jobs["java"])
                if path != RUNNERS[0]:
                    self.assertTrue(jobs["deploy"])

    def test_required_runners_are_present_in_selected_jobs(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf8")
        java = workflow.split("\n  java:\n", 1)[1].split("\n  web:\n", 1)[0]
        deploy = workflow.split("\n  deploy:\n", 1)[1].split("\n  gate:\n", 1)[0]
        self.assertIn('run: python3 -B tools/verify_java_im.py --build-dir "$RUNNER_TEMP/java-build"', java)
        self.assertIn("run: python3 -B tests/e2e/parity.py\n", java)
        self.assertIn("run: python3 -B tools/verify_sync_runtime.py --profile java\n", java)
        for path in RUNNERS[1:]:
            self.assertIn(f"run: python3 -B {path}\n", deploy)


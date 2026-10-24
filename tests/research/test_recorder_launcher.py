from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

LAUNCHER = Path(__file__).resolve().parents[2] / "tools" / "research" / "recorder.ps1"
POWERSHELL = shutil.which("powershell")


@unittest.skipUnless(sys.platform == "win32", "Windows launcher wrapper only")
@unittest.skipUnless(POWERSHELL is not None, "powershell.exe not available")
class LauncherTest(unittest.TestCase):
    """Regression tests for the interpreter discovery documented in PR #47.

    The launcher must honor RESEARCH_RECORDER_PYTHON when PATH discovery
    cannot find a working interpreter (Microsoft Store python/python3 alias
    stubs crash naive probes), and a set-but-unusable override must fail
    loudly instead of silently falling back to discovery.
    """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "research").mkdir()
        self.previous = os.environ.get("RESEARCH_RECORDER_PYTHON")

    def tearDown(self):
        if self.previous is None:
            os.environ.pop("RESEARCH_RECORDER_PYTHON", None)
        else:
            os.environ["RESEARCH_RECORDER_PYTHON"] = self.previous
        self.temp.cleanup()

    def launch(self, override):
        environment = os.environ.copy()
        environment["RESEARCH_RECORDER_PYTHON"] = override
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER),
             "validate-repository", "--allow-partial", "--repo", str(self.repo)],
            capture_output=True, text=True, env=environment, timeout=120,
        )

    def test_launcher_honors_explicit_interpreter_override(self):
        result = self.launch(sys.executable)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS: Research Recorder repository artifacts validated.", result.stdout)

    def test_launcher_fails_loudly_on_unusable_override(self):
        bogus = Path(self.temp.name) / "definitely-not-python.exe"
        result = self.launch(str(bogus))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("RESEARCH_RECORDER_PYTHON is set but does not point to an executable file", result.stderr)


if __name__ == "__main__":
    unittest.main()

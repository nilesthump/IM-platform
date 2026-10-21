from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
LAUNCHER = REPO / "tools" / "verify-client-sqlite.ps1"
POWERSHELL = shutil.which("powershell")


@unittest.skipUnless(sys.platform == "win32", "Windows launcher only")
@unittest.skipUnless(POWERSHELL is not None, "powershell.exe not available")
class ClientSqliteLauncherTest(unittest.TestCase):
    """Regression tests for the -Python override in the client verifier launcher.

    The underlying verifier (npm/tsc/cargo/gradle chains) is too heavy for a
    launcher unit test, so these lock the deterministic override-validation
    paths; the discovery loop mirrors the already-tested verify-frozen and
    recorder launchers.
    """

    def run_ps(self, *extra):
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(LAUNCHER), *extra],
            capture_output=True, text=True, timeout=120, cwd=str(REPO),
        )

    def test_rejects_missing_override_path(self):
        bogus = Path(tempfile.gettempdir()) / "definitely-not-python.exe"
        result = self.run_ps("-Scope", "shared", "-Python", str(bogus))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Specified -Python path does not exist", result.stderr)

    def test_rejects_non_python_override(self):
        git = shutil.which("git")
        if git is None:
            self.skipTest("git executable not on PATH")
        result = self.run_ps("-Scope", "shared", "-Python", git)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Specified -Python is not a working Python 3", result.stderr)


if __name__ == "__main__":
    unittest.main()

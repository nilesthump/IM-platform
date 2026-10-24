from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
FROZEN = REPO / "tools" / "verify-frozen-architecture.ps1"
CTRL = REPO / "tools" / "verify-loop1-ctrl-002.ps1"
POWERSHELL = shutil.which("powershell")


@unittest.skipUnless(sys.platform == "win32", "Windows PowerShell launchers only")
@unittest.skipUnless(POWERSHELL is not None, "powershell.exe not available")
class VerifierLauncherTest(unittest.TestCase):
    """Regression tests for the -Python override fixed in the verifier PRs.

    Covers the stub-tolerant discovery and explicit-override contract, plus the
    case-insensitive `$Python` parameter vs `$python`-style internal state
    collision that previously nullified the override.
    """

    def run_ps(self, script, *extra):
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *extra],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )

    def test_frozen_rejects_missing_override_path(self):
        bogus = Path(tempfile.gettempdir()) / "definitely-not-python.exe"
        result = self.run_ps(FROZEN, "-Python", str(bogus))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Specified -Python path does not exist", result.stderr)

    def test_frozen_rejects_non_python_override(self):
        git = shutil.which("git")
        if git is None:
            self.skipTest("git executable not on PATH")
        result = self.run_ps(FROZEN, "-Python", git)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Specified -Python is not a working Python 3", result.stderr)

    def test_frozen_override_actually_runs_the_verifier(self):
        # Guards the case-insensitive parameter/internal-state collision: the
        # override must be used instead of falling back to (failing) discovery.
        # The integrity phase always prints its PASS marker at a healthy HEAD;
        # the trailing unittest phase may legitimately error on machines
        # without javac, so only the interpreter-usage marker is asserted.
        result = self.run_ps(FROZEN, "-Python", sys.executable)
        self.assertIn("PASS: v1.1 current SHA/PDF provenance", result.stdout,
                      result.stdout[-2000:] + result.stderr[-2000:])

    def test_ctrl_reports_design_failure_for_missing_override(self):
        bogus = Path(tempfile.gettempdir()) / "definitely-not-python.exe"
        result = self.run_ps(CTRL, "-Mode", "Acceptance", "-Python", str(bogus))
        self.assertNotEqual(0, result.returncode)
        combined = result.stdout + result.stderr
        self.assertIn("FAIL: recovery verification found", combined)
        self.assertIn("Specified -Python path does not exist", combined)


if __name__ == "__main__":
    unittest.main()

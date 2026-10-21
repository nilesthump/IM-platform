from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import unittest

REPO = Path(__file__).resolve().parents[2]
LINT = REPO / "contracts/http/check-openapi-3.1.js"
DOCUMENT = REPO / "contracts/http/auth-user-friend.openapi.json"
NODE = shutil.which("node")


@unittest.skipUnless(NODE is not None, "node executable not available")
class OpenApiLintStdinTest(unittest.TestCase):
    """Regression tests for stdin handling of the offline OpenAPI 3.1 lint.

    Windows PowerShell 5.1 pipeline stdin prepends a UTF-8 BOM; the contract
    verifier itself pipes JSON to this lint, so a BOM-prefixed document must
    still validate instead of failing with a misleading parse error.
    """

    def run_lint(self, payload: bytes):
        return subprocess.run([NODE, str(LINT)], input=payload,
                              capture_output=True, timeout=60, cwd=str(REPO))

    def test_bom_prefixed_canonical_document_passes(self):
        result = self.run_lint(b"\xef\xbb\xbf" + DOCUMENT.read_bytes())
        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", "replace"))

    def test_plain_canonical_document_passes(self):
        result = self.run_lint(DOCUMENT.read_bytes())
        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", "replace"))

    def test_structurally_invalid_document_fails_with_diagnostics(self):
        result = self.run_lint(json.dumps({"openapi": "3.0.0"}).encode("utf-8"))
        self.assertEqual(1, result.returncode)
        self.assertTrue(result.stderr, "structural diagnostics expected")

    def test_malformed_json_fails_distinctly(self):
        result = self.run_lint(b"{not-json")
        self.assertEqual(2, result.returncode)
        self.assertIn("could not be validated", result.stderr.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main()

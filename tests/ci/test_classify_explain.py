"""Explain mode for the CI classifier: which rule selected which job, per path.

classify() must keep its exact public behavior; classify_detailed() is the
instrumented form behind it, and --explain surfaces its attribution so the
recurring zero-selection and surprise-selection questions become answerable.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("classify_explain", ROOT / "ci/classify.py")
classify_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify_module)


class ClassifyBackwardCompatibilityTests(unittest.TestCase):
    def test_classify_matrix_is_unchanged_for_representative_paths(self):
        cases = {
            "AGENTS.md": {"architecture", "source_go", "source_java"},
            "backend/go/core/group.go": {"go", "architecture", "source_go"},
            "clients/shared/protocol-sdk/x.ts": set(classify_module.JOBS) - {"deploy"},
            "tools/verify_sync_runtime.py": set(),
            "ci/classify.py": set(classify_module.JOBS),
            "deploy/compose.yaml": {"deploy"},
        }
        for path, expected in cases.items():
            matrix = classify_module.classify([path])
            self.assertEqual({job for job in classify_module.JOBS if matrix[job]}, expected, path)

    def test_classify_still_rejects_non_relative_paths(self):
        with self.assertRaises(ValueError):
            classify_module.classify(["/abs/path"])
        with self.assertRaises(ValueError):
            classify_module.classify(["a/../b"])


class ClassifyDetailedTests(unittest.TestCase):
    def test_single_rule_attribution(self):
        matrix, reasons = classify_module.classify_detailed(["backend/go/core/group.go"])
        self.assertEqual(["backend-go"], [reason["rule"] for reason in reasons])
        self.assertEqual("backend/go/core/group.go", reasons[0]["path"])
        self.assertEqual(["architecture", "go", "source_go"], reasons[0]["jobs"])

    def test_multiple_rules_fire_for_one_path(self):
        _, reasons = classify_module.classify_detailed(["clients/shared/protocol-sdk/x.ts"])
        rules = [reason["rule"] for reason in reasons]
        self.assertIn("clients", rules)
        self.assertIn("shared-contract", rules)
        merged = set().union(*(set(reason["jobs"]) for reason in reasons))
        self.assertEqual(set(classify_module.JOBS) - {"deploy"}, merged)

    def test_zero_selection_paths_have_empty_reasons(self):
        matrix, reasons = classify_module.classify_detailed(["tools/verify_sync_runtime.py", "research/schema/event.schema.json"])
        self.assertEqual([], reasons)
        self.assertFalse(any(matrix.values()))

    def test_governance_paths_attribute_three_jobs(self):
        _, reasons = classify_module.classify_detailed(["spec/architecture/baseline.md", "README.md"])
        self.assertEqual({"governance"}, {reason["rule"] for reason in reasons})
        for reason in reasons:
            self.assertEqual(["architecture", "source_go", "source_java"], reason["jobs"])


class ExplainCliTests(unittest.TestCase):
    def run_main(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = classify_module.main(argv)
        return code, stdout.getvalue()

    def test_explain_adds_reasons_to_json_output(self):
        code, out = self.run_main(["--paths", "backend/go/core/group.go", "--explain"])
        self.assertEqual(0, code)
        value = json.loads(out)
        self.assertEqual(["backend-go"], [reason["rule"] for reason in value["reasons"]])
        self.assertIn("jobs", value)

    def test_without_explain_output_has_no_reasons_key(self):
        code, out = self.run_main(["--paths", "backend/go/core/group.go"])
        self.assertEqual(0, code)
        self.assertNotIn("reasons", json.loads(out))

    def test_explain_with_github_output_keeps_matrix_lines(self):
        with tempfile.TemporaryDirectory(prefix="classify-explain-") as temp:
            output = Path(temp) / "outputs.txt"
            code, _ = self.run_main(["--paths", "deploy/compose.yaml", "--explain", "--github-output", str(output)])
            self.assertEqual(0, code)
            lines = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())
            self.assertEqual("true", lines["deploy"])
            self.assertEqual("false", lines["go"])


if __name__ == "__main__":
    unittest.main()

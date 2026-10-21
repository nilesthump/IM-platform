import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("gate", ROOT / "ci/check_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def needs(self):
        outputs = {name: "false" for name in (*gate.JOBS, "old_client", "plugin", "migration")}
        result = {name: {"result": "skipped"} for name in gate.JOBS}
        result["classify"] = {"result": "success", "outputs": outputs}
        return result

    def test_selected_job_must_succeed(self):
        needs = self.needs()
        needs["classify"]["outputs"]["go"] = "true"
        for status in ("skipped", "failure", "cancelled"):
            needs["go"]["result"] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                gate.check(needs)
        needs["go"]["result"] = "success"
        gate.check(needs)

    def test_classifier_failure_fails_gate(self):
        needs = self.needs()
        needs["classify"]["result"] = "failure"
        with self.assertRaises(ValueError):
            gate.check(needs)

    def test_shared_subchecks_require_compatibility(self):
        needs = self.needs()
        needs["classify"]["outputs"]["migration"] = "true"
        with self.assertRaises(ValueError):
            gate.check(needs)

    def test_architecture_jobs_missing_invalid_skipped_failed_cancelled(self):
        for job in ("architecture", "source_go", "source_java"):
            for status in ("skipped", "failure", "cancelled"):
                needs = self.needs()
                needs["classify"]["outputs"][job] = "true"
                needs[job]["result"] = status
                with self.subTest(job=job, status=status), self.assertRaises(ValueError):
                    gate.check(needs)
            needs = self.needs()
            del needs[job]
            with self.subTest(job=job, missing=True), self.assertRaises(ValueError):
                gate.check(needs)
            needs = self.needs()
            needs["classify"]["outputs"][job] = "bogus"
            with self.subTest(job=job, invalid=True), self.assertRaises(ValueError):
                gate.check(needs)

    def test_unselected_job_must_not_run(self):
        # A job the classifier did not select must report `skipped`; anything
        # else means the workflow ran unselected work and the gate fails.
        for status in ("success", "failure", "cancelled"):
            needs = self.needs()
            needs["web"]["result"] = status
            with self.subTest(status=status), self.assertRaises(ValueError):
                gate.check(needs)

    def test_every_shared_subcheck_requires_compatibility(self):
        # old_client, plugin and migration all select the compatibility job;
        # the existing test only exercised migration.
        for subcheck in ("old_client", "plugin", "migration"):
            needs = self.needs()
            needs["classify"]["outputs"][subcheck] = "true"
            with self.subTest(subcheck=subcheck), self.assertRaises(ValueError):
                gate.check(needs)
            needs = self.needs()
            needs["classify"]["outputs"]["compatibility"] = "true"
            needs["classify"]["outputs"][subcheck] = "true"
            needs["compatibility"]["result"] = "success"
            gate.check(needs)

    def test_invalid_subcheck_selection_output_fails(self):
        for subcheck in ("old_client", "plugin", "migration"):
            needs = self.needs()
            needs["classify"]["outputs"][subcheck] = "bogus"
            with self.subTest(subcheck=subcheck), self.assertRaises(ValueError):
                gate.check(needs)

    def test_classify_entry_missing_fails(self):
        needs = self.needs()
        del needs["classify"]
        with self.assertRaises(ValueError):
            gate.check(needs)

    def test_all_unselected_gate_passes(self):
        gate.check(self.needs())


if __name__ == "__main__":
    unittest.main()

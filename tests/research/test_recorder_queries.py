"""Run query commands (list-runs, run-stats) over a hand-built research root.

The loader is a tolerant read-only view: it lists state, including broken run
directories, and never mutates anything. Gating correctness stays the job of
validate-repository; these tests pin the query contract.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import unittest.mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("recorder_queries", ROOT / "tools/research/recorder.py")
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8", newline="\n")


def metadata(run_id, task_id, role="implementation", capture_mode="prospective",
             status="finished", model_name="glm-test"):
    return {"recorder_schema_version": "1.0.0", "run_id": run_id, "task_id": task_id,
            "role": role, "capture_mode": capture_mode, "status": status,
            "experiment_group": "full_governance", "started_at": "2026-10-25T00:00:00Z",
            "prompt_id": "P-X", "agent_harness": "test", "model_name": model_name}


def event(run_id, seq):
    return {"schema_version": "1.0.0", "seq": seq, "run_id": run_id, "event_type": "command_finished"}


def build(root, run_id, task_id="TASK-A", meta=None, summary=None, events=3):
    directory = root / "runs" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    write_json(directory / "metadata.json", meta or metadata(run_id, task_id))
    if summary is not None:
        write_json(directory / "summary.json", summary)
    (directory / "events.jsonl").write_text(
        "".join(json.dumps(event(run_id, i + 1), sort_keys=True) + "\n" for i in range(events)),
        encoding="utf-8", newline="\n")


def namespace(**kwargs):
    names = {"task_id": None, "role": None, "capture_mode": None, "status": None, "result": None, "json": False}
    names.update(kwargs)
    return unittest.mock.Mock(**names)


class ListRunsTests(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(prefix="recorder-query-")
        self.root = Path(self._temp.name) / "research"
        (self.root / "runs").mkdir(parents=True)
        self.addCleanup(self._temp.cleanup)

    def run_list(self, **kwargs):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = recorder.cmd_list_runs(namespace(**kwargs), ROOT, self.root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_lists_sorted_rows_with_event_counts(self):
        build(self.root, "R-B", task_id="TASK-B")
        build(self.root, "R-A", summary={"result": "PASS"}, events=5)
        code, out, err = self.run_list()
        self.assertEqual(0, code)
        self.assertEqual("", err)
        lines = out.strip().splitlines()
        self.assertIn("R-A", lines[1])
        self.assertIn("5", lines[1])
        self.assertIn("R-B", lines[2])
        self.assertIn("3", lines[2])

    def test_json_shape_and_filters(self):
        build(self.root, "R-A", summary={"result": "PASS"})
        build(self.root, "R-B", task_id="TASK-B", meta=metadata("R-B", "TASK-B", role="review"))
        build(self.root, "R-C", meta=metadata("R-C", "TASK-A", status="partial"))
        code, out, err = self.run_list(json=True, task_id="TASK-A", status="finished")
        self.assertEqual(0, code)
        self.assertEqual("", err)
        value = json.loads(out)
        self.assertEqual(["R-A"], [row["run_id"] for row in value["runs"]])
        self.assertEqual("TASK-A", value["runs"][0]["task_id"])
        self.assertEqual("PASS", value["runs"][0]["result"])
        self.assertEqual(3, value["runs"][0]["event_count"])
        self.assertEqual(3, value["total_discovered"])
        self.assertEqual(1, value["matched"])
        self.assertEqual([], value["errors"])

    def test_role_capture_mode_and_result_filters(self):
        build(self.root, "R-A", summary={"result": "PASS"})
        build(self.root, "R-B", meta=metadata("R-B", "TASK-A", role="review", capture_mode="retrospective_backfill"))
        build(self.root, "R-C", summary={"result": "FAIL"})
        for field, value, expected in (("role", "review", ["R-B"]),
                                       ("capture_mode", "retrospective_backfill", ["R-B"]),
                                       ("result", "FAIL", ["R-C"])):
            code, out, _ = self.run_list(json=True, **{field: value})
            self.assertEqual(0, code)
            self.assertEqual(expected, [row["run_id"] for row in json.loads(out)["runs"]])

    def test_invalid_run_reported_as_error_and_excluded(self):
        build(self.root, "R-A")
        (self.root / "runs" / "R-BAD").mkdir()
        code, out, err = self.run_list(json=True)
        self.assertEqual(0, code)
        value = json.loads(out)
        self.assertEqual(["R-A"], [row["run_id"] for row in value["runs"]])
        self.assertEqual(1, len(value["errors"]))
        self.assertIn("R-BAD", err)
        self.assertIn("R-BAD", value["errors"][0]["run"])

    def test_run_id_directory_mismatch_is_an_error(self):
        build(self.root, "R-A", meta=metadata("R-OTHER", "TASK-A"))
        code, out, err = self.run_list(json=True)
        self.assertEqual(0, code)
        value = json.loads(out)
        self.assertEqual([], value["runs"])
        self.assertEqual(1, len(value["errors"]))

    def test_no_match_yields_empty_rows_without_error(self):
        code, out, _ = self.run_list(json=True, task_id="NOPE")
        self.assertEqual(0, code)
        value = json.loads(out)
        self.assertEqual([], value["runs"])
        self.assertEqual(0, value["matched"])


class RunStatsTests(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(prefix="recorder-stats-")
        self.root = Path(self._temp.name) / "research"
        (self.root / "runs").mkdir(parents=True)
        self.addCleanup(self._temp.cleanup)

    def run_stats(self, **kwargs):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = recorder.cmd_run_stats(namespace(**kwargs), ROOT, self.root)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_aggregates_tallies_events_and_duration(self):
        build(self.root, "R-A", summary={"result": "PASS"}, events=5)
        first = metadata("R-A", "TASK-A")
        first["duration_ms"] = 100.0
        write_json(self.root / "runs" / "R-A" / "metadata.json", first)
        build(self.root, "R-B", task_id="TASK-B", summary={"result": "FAIL"})
        second = metadata("R-B", "TASK-B", role="review", capture_mode="retrospective_backfill")
        second["duration_ms"] = 300.0
        write_json(self.root / "runs" / "R-B" / "metadata.json", second)
        build(self.root, "R-C", meta=metadata("R-C", "TASK-A", status="partial"))
        code, out, err = self.run_stats(json=True)
        self.assertEqual(0, code)
        self.assertEqual("", err)
        value = json.loads(out)
        self.assertEqual(3, value["matched"])
        self.assertEqual({"finished": 2, "partial": 1}, value["by_status"])
        self.assertEqual({"implementation": 2, "review": 1}, value["by_role"])
        self.assertEqual({"FAIL": 1, "PASS": 1, "unavailable": 1}, value["by_result"])
        self.assertEqual(11, value["events_total"])
        self.assertEqual(400.0, value["duration_ms_total"])
        self.assertEqual(200.0, value["duration_ms_mean"])

    def test_missing_summary_counts_as_unavailable_result(self):
        build(self.root, "R-A", meta=metadata("R-A", "TASK-A", status="partial"), events=0)
        code, out, _ = self.run_stats(json=True)
        value = json.loads(out)
        self.assertEqual({"unavailable": 1}, value["by_result"])
        self.assertEqual(0, value["events_total"])

    def test_task_filter_scopes_every_tally(self):
        build(self.root, "R-A", summary={"result": "PASS"}, events=2)
        build(self.root, "R-B", task_id="TASK-B", summary={"result": "PASS"})
        code, out, _ = self.run_stats(json=True, task_id="TASK-A")
        value = json.loads(out)
        self.assertEqual(1, value["matched"])
        self.assertEqual(2, value["events_total"])

    def test_empty_root_yields_zeroed_stats(self):
        code, out, _ = self.run_stats(json=True)
        value = json.loads(out)
        self.assertEqual(0, value["matched"])
        self.assertEqual({}, value["by_status"])
        self.assertIsNone(value["duration_ms_mean"])


if __name__ == "__main__":
    unittest.main()

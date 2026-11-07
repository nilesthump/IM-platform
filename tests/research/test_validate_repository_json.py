"""Machine-readable validate-repository output.

--json only changes the output format: failures still exit nonzero and the
plain mode keeps raising RecorderError exactly as before. Fixtures build one
real finished run through the recorder's own commands, plus deliberately
broken directories for the failure paths.
"""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("recorder_valjson", ROOT / "tools/research/recorder.py")
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)

CURRENT_TASK = """# Current Execution State
Current Task: TEST-001
Current Task State: active
## Last Known Good Commit
`0000000000000000000000000000000000000000`
## Latest Checkpoint
`unavailable`
"""


class ValidateRepositoryJsonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.root = self.repo / "research"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Fixture"], check=True)
        for relative, content in (("AGENTS.md", "fixture authority\n"),
                                  ("spec/handoff/agent-context.md", "fixture handoff\n"),
                                  ("spec/progress/current.md", CURRENT_TASK),
                                  ("spec/tasks/active/TEST-001.md", "---\ntask_id: TEST-001\nstatus: active\nowner: fixture\n---\n"),
                                  ("spec/architecture/README.md", "fixture\n"),
                                  ("spec/architecture/baseline.md", "fixture\n")):
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "fixture"], check=True)

    def ns(self, **kwargs):
        names = {"allow_partial": False, "json": False}
        names.update(kwargs)
        return argparse.Namespace(**names)

    def record_one_finished_run(self):
        source = self.repo / "prompt-input.txt"
        source.write_text("human task\n", encoding="utf-8", newline="\n")
        recorder.cmd_register_prompt(self.ns(file=str(source), prompt_id=None, task_id="TEST-001",
                                             source="human", template_version=None, run_id=None),
                                     self.repo, self.root)
        prompt_id = next((self.root / "prompts").iterdir()).name
        recorder.cmd_start_run(self.ns(role="implementation", capture_mode="prospective",
                                       experiment_group="full_governance", pre_recorder_work=False,
                                       run_id=None, task_id="TEST-001", prompt_id=prompt_id,
                                       parent_run_id=None, related_run_id=None, agent_harness="fixture",
                                       model_name="unavailable", fresh_context="unavailable",
                                       explicit_token_budget="unavailable", context_mode="unavailable",
                                       public_reasoning_mode="unavailable", baseline_id="unavailable",
                                       replicate_id="unavailable", mutation_id="unavailable",
                                       model_condition="unavailable", budget_condition="unavailable"),
                               self.repo, self.root)
        run_id = next((self.root / "runs").iterdir()).name
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        return run_id

    def run_validate(self, **kwargs):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = recorder.cmd_validate_repository(self.ns(**kwargs), self.repo, self.root)
        return code, stdout.getvalue()

    def test_json_pass_reports_counts(self):
        self.record_one_finished_run()
        code, out = self.run_validate(json=True)
        self.assertEqual(0, code)
        value = json.loads(out)
        self.assertEqual("PASS", value["result"])
        self.assertEqual(1, value["runs"])
        self.assertEqual(1, value["prompts"])

    def test_json_fail_lists_failures_and_exits_nonzero(self):
        self.record_one_finished_run()
        (self.root / "runs" / "R-BROKEN").mkdir()
        code, out = self.run_validate(json=True)
        self.assertEqual(1, code)
        value = json.loads(out)
        self.assertEqual("FAIL", value["result"])
        self.assertTrue(any("R-BROKEN" in failure for failure in value["failures"]))

    def test_plain_mode_keeps_pass_line_and_error_raise(self):
        self.record_one_finished_run()
        code, out = self.run_validate()
        self.assertEqual(0, code)
        self.assertIn("PASS: Research Recorder repository artifacts validated.", out)
        (self.root / "runs" / "R-BROKEN").mkdir()
        with self.assertRaises(recorder.RecorderError) as caught:
            recorder.cmd_validate_repository(self.ns(), self.repo, self.root)
        self.assertIn("repository validation failed", str(caught.exception))
        self.assertIn("R-BROKEN", str(caught.exception))

    def test_allow_partial_counts_running_runs_as_valid(self):
        source = self.repo / "prompt-input.txt"
        source.write_text("human task\n", encoding="utf-8", newline="\n")
        recorder.cmd_register_prompt(self.ns(file=str(source), prompt_id=None, task_id="TEST-001",
                                             source="human", template_version=None, run_id=None),
                                     self.repo, self.root)
        prompt_id = next((self.root / "prompts").iterdir()).name
        recorder.cmd_start_run(self.ns(role="implementation", capture_mode="prospective",
                                       experiment_group="full_governance", pre_recorder_work=False,
                                       run_id=None, task_id="TEST-001", prompt_id=prompt_id,
                                       parent_run_id=None, related_run_id=None, agent_harness="fixture",
                                       model_name="unavailable", fresh_context="unavailable",
                                       explicit_token_budget="unavailable", context_mode="unavailable",
                                       public_reasoning_mode="unavailable", baseline_id="unavailable",
                                       replicate_id="unavailable", mutation_id="unavailable",
                                       model_condition="unavailable", budget_condition="unavailable"),
                               self.repo, self.root)
        code, out = self.run_validate(json=True, allow_partial=True)
        self.assertEqual(0, code)
        self.assertEqual("PASS", json.loads(out)["result"])


if __name__ == "__main__":
    unittest.main()

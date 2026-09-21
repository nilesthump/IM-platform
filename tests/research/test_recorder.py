from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "research" / "recorder.py"
SPEC = importlib.util.spec_from_file_location("research_recorder", MODULE_PATH)
recorder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(recorder)


class RecorderTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.root = self.repo / "research"
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Fixture"], check=True)
        self.write("AGENTS.md", "fixture authority\n")
        self.write("spec/handoff/agent-context.md", "fixture handoff\n")
        self.write("spec/progress/current.md", """# Current Execution State
Current Task: TEST-001
Current Task State: active
## Last Known Good Commit
`0000000000000000000000000000000000000000`
## Latest Checkpoint
`unavailable`
""")
        self.write("spec/tasks/active/TEST-001.md", "---\ntask_id: TEST-001\nstatus: active\nowner: fixture\n---\n")
        self.write("spec/architecture/README.md", "fixture\n")
        self.write("spec/architecture/baseline.md", "fixture\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "fixture"], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative: str, content: str):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def ns(self, **kwargs):
        return argparse.Namespace(**kwargs)

    def prompt(self, content="human task"):
        source = self.repo / "prompt-input.txt"
        source.write_text(content, encoding="utf-8")
        args = self.ns(file=str(source), prompt_id=None, task_id="TEST-001", source="human",
                       template_version=None, run_id=None)
        recorder.cmd_register_prompt(args, self.repo, self.root)
        return next((self.root / "prompts").iterdir()).name

    def start(self, capture="prospective", pre=False, role="implementation", prompt_id=None):
        args = self.ns(role=role, capture_mode=capture, experiment_group="full_governance",
                       pre_recorder_work=pre, run_id=None, task_id="TEST-001", prompt_id=prompt_id,
                       parent_run_id=None, related_run_id=None, agent_harness="fixture", model_name="unavailable",
                       fresh_context="unavailable", explicit_token_budget="unavailable", context_mode="unavailable",
                       public_reasoning_mode="unavailable", baseline_id="unavailable", replicate_id="unavailable",
                       mutation_id="unavailable", model_condition="unavailable", budget_condition="unavailable")
        recorder.cmd_start_run(args, self.repo, self.root)
        return next((self.root / "runs").iterdir()).name

    def cli(self, *args):
        return subprocess.run([sys.executable, str(MODULE_PATH), args[0], "--repo", str(self.repo),
                               "--research-root", str(self.root), *args[1:]], capture_output=True, text=True)

    def test_start_run_unique_and_schema(self):
        first = self.start()
        second_args = self.ns(role="review", capture_mode="prospective", experiment_group="unassigned",
                              pre_recorder_work=False, run_id=None, task_id="TEST-001", prompt_id=None,
                              parent_run_id=first, related_run_id=first, agent_harness="fixture", model_name="unavailable",
                              fresh_context="yes", explicit_token_budget="unavailable", context_mode="fresh",
                              public_reasoning_mode="unavailable", baseline_id="unavailable", replicate_id="unavailable",
                              mutation_id="unavailable", model_condition="unavailable", budget_condition="unavailable")
        recorder.cmd_start_run(second_args, self.repo, self.root)
        runs = sorted((self.root / "runs").iterdir())
        self.assertEqual(2, len(runs))
        self.assertNotEqual(runs[0].name, runs[1].name)
        metadata = recorder.read_json(runs[0] / "metadata.json")
        self.assertEqual("1.0.0", metadata["recorder_schema_version"])

    def test_prompt_hash_link_and_system_prompt_unavailable(self):
        source = self.repo / "prompt-input.txt"
        source.write_bytes(b"stable prompt\r\nsecond line\r\n")
        recorder.cmd_register_prompt(self.ns(file=str(source), prompt_id=None, task_id="TEST-001",
                                     source="human", template_version=None, run_id=None), self.repo, self.root)
        prompt_id = next((self.root / "prompts").iterdir()).name
        meta = recorder.read_json(self.root / "prompts" / prompt_id / "metadata.json")
        prompt_path = self.root / "prompts" / prompt_id / "prompt.txt"
        self.assertEqual(b"stable prompt\nsecond line\n", prompt_path.read_bytes())
        self.assertEqual(recorder.sha256_bytes(prompt_path.read_bytes()), meta["prompt_sha256"])
        self.assertEqual("unavailable", meta["system_prompt_capture"])
        run_id = self.start(prompt_id=prompt_id)
        self.assertEqual(prompt_id, recorder.read_json(self.root / "runs" / run_id / "metadata.json")["prompt_id"])
        self.assertEqual(run_id, recorder.read_json(self.root / "prompts" / prompt_id / "metadata.json")["associated_run_id"])
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        recorder.cmd_validate_repository(self.ns(allow_partial=False), self.repo, self.root)

    def test_prompt_registry_rejects_hash_and_cross_link_tampering(self):
        prompt_id = self.prompt("stable prompt\n")
        run_id = self.start(prompt_id=prompt_id)
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        prompt_path = self.root / "prompts" / prompt_id / "prompt.txt"
        prompt_path.write_bytes(b"tampered\n")
        with self.assertRaisesRegex(recorder.RecorderError, "prompt content hash mismatch"):
            recorder.cmd_validate_repository(self.ns(allow_partial=False), self.repo, self.root)

    def test_git_capture_dirty_without_modification(self):
        self.write("dirty.txt", "unchanged by capture")
        before = (self.repo / "dirty.txt").read_bytes()
        state = recorder.capture_git(self.repo)
        self.assertFalse(state["clean"])
        self.assertIn("dirty.txt", state["changed_paths"])
        self.assertEqual(before, (self.repo / "dirty.txt").read_bytes())
        self.assertEqual(40, len(state["head_sha"]))

    def test_event_append_seq_hash_and_duplicate_rejected(self):
        run_id = self.start()
        recorder.append_event(self.root, run_id, "finding_created", {"finding": "x"})
        records = recorder.validate_events(self.root / "runs" / run_id / "events.jsonl", run_id)
        self.assertEqual(list(range(1, len(records) + 1)), [e["seq"] for e in records])
        records[-1]["seq"] = records[-2]["seq"]
        path = self.root / "runs" / run_id / "events.jsonl"
        path.write_text("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in records), encoding="utf-8")
        with self.assertRaisesRegex(recorder.RecorderError, "duplicate or non-monotonic"):
            recorder.validate_events(path, run_id)

    def test_malformed_and_partial_jsonl_rejected(self):
        run_id = self.start()
        path = self.root / "runs" / run_id / "events.jsonl"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("{")
        with self.assertRaisesRegex(recorder.RecorderError, "partial JSONL"):
            recorder.validate_events(path, run_id)

    def test_run_command_executes_and_propagates_zero(self):
        run_id = self.start()
        result = self.cli("run-command", "--run-id", run_id, "--", sys.executable, "-c", "print('ok')")
        self.assertEqual(0, result.returncode)
        events = recorder.validate_events(self.root / "runs" / run_id / "events.jsonl", run_id)
        self.assertEqual(0, events[-1]["data"]["exit_code"])
        self.assertEqual("PASS", events[-1]["data"]["result"])

    def test_run_command_propagates_failure_and_records_fail(self):
        run_id = self.start()
        result = self.cli("run-command", "--run-id", run_id, "--", sys.executable, "-c", "raise SystemExit(7)")
        self.assertEqual(7, result.returncode)
        events = recorder.validate_events(self.root / "runs" / run_id / "events.jsonl", run_id)
        self.assertEqual(7, events[-1]["data"]["exit_code"])
        self.assertEqual("FAIL", events[-1]["data"]["result"])

    def test_finish_captures_final_diff_duration_and_locks_history(self):
        run_id = self.start()
        self.write("change.txt", "change\n")
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        directory = self.root / "runs" / run_id
        self.assertTrue((directory / "final_state.json").exists())
        self.assertIn("change.txt", (directory / "diff.patch").read_text(encoding="utf-8"))
        metadata = recorder.read_json(directory / "metadata.json")
        self.assertEqual("finished", metadata["status"])
        self.assertGreaterEqual(metadata["duration_ms"], 0)
        with self.assertRaisesRegex(recorder.RecorderError, "immutable"):
            recorder.append_event(self.root, run_id, "finding_created", {})

    def test_partial_run_detected(self):
        run_id = self.start()
        with self.assertRaisesRegex(recorder.RecorderError, "partial/interrupted"):
            recorder.validate_run(self.root, run_id)
        self.assertEqual("running", recorder.validate_run(self.root, run_id, require_finished=False)["status"])

    def test_finished_manifest_tamper_detected(self):
        run_id = self.start()
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        metadata_path = self.root / "runs" / run_id / "metadata.json"
        metadata = recorder.read_json(metadata_path)
        metadata["task_id"] = "TAMPERED"
        recorder.write_json(metadata_path, metadata)
        with self.assertRaisesRegex(recorder.RecorderError, "manifest hash mismatch"):
            recorder.validate_run(self.root, run_id)

    def test_finished_manifest_is_portable_across_crlf_checkout(self):
        run_id = self.start()
        recorder.cmd_finish_run(self.ns(run_id=run_id, result="PASS"), self.repo, self.root)
        directory = self.root / "runs" / run_id
        for name in ("metadata.json", "initial_state.json", "final_state.json", "events.jsonl", "diff.patch", "summary.json"):
            path = directory / name
            path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual("finished", recorder.validate_run(self.root, run_id)["status"])

    def test_human_decision_fixture_explicit(self):
        run_id = self.start(role="human")
        args = self.ns(run_id=run_id, decision_id=None, question="choose", alternatives_json='["A","B"]',
                       selected="B", reason="fixture reason", affected_authority=None, fixture=True)
        recorder.cmd_human_decision(args, self.repo, self.root)
        event = recorder.validate_events(self.root / "runs" / run_id / "events.jsonl", run_id)[-1]
        self.assertTrue(event["data"]["human_actor"])
        self.assertTrue(event["data"]["fixture"])

    def test_backfill_marks_unknowns_unavailable(self):
        recorder.cmd_backfill(self.ns(task_id="TEST-001"), self.repo, self.root)
        value = recorder.read_json(self.root / "backfill" / "TEST-001.json")
        self.assertTrue(value["backfilled"])
        self.assertEqual("retrospective_backfill", value["collection_mode"])
        for field in ("prompt", "model_calls", "token_usage", "tool_calls", "exact_timing", "reasoning", "context_size", "cost"):
            self.assertEqual("unavailable", value[field])

    def test_ci_ingestion_records_external_observation_only(self):
        run_id = self.start(role="ci")
        evidence_path = self.repo / "ci-evidence.json"
        evidence = {"provider": "fixture", "ci_run_id": "fixture-1", "commit_sha": "0" * 40,
                    "job_name": "fixture", "result": "FAIL", "failed_checks": ["unit"],
                    "duration_ms": 12, "evidence_reference": "fixture://ci/1"}
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        recorder.cmd_ingest_ci(self.ns(run_id=run_id, evidence=str(evidence_path)), self.repo, self.root)
        event = recorder.validate_events(self.root / "runs" / run_id / "events.jsonl", run_id)[-1]
        self.assertEqual("ci_finished", event["event_type"])
        self.assertEqual("FAIL", event["data"]["result"])

    def test_ci_ingestion_rejects_extra_secret_fields_without_persisting(self):
        run_id = self.start(role="ci")
        evidence_path = self.repo / "ci-secret-evidence.json"
        secret = "SYNTHETIC_CI_SECRET_VALUE"
        evidence = {"provider": "fixture", "ci_run_id": "fixture-1", "commit_sha": "0" * 40,
                    "job_name": "fixture", "result": "FAIL", "failed_checks": ["unit"],
                    "duration_ms": 12, "evidence_reference": "fixture://ci/1",
                    "password": secret, "raw_auth_headers": {"Authorization": secret}}
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        before = (self.root / "runs" / run_id / "events.jsonl").read_bytes()
        with self.assertRaisesRegex(recorder.RecorderError, "extra"):
            recorder.cmd_ingest_ci(self.ns(run_id=run_id, evidence=str(evidence_path)), self.repo, self.root)
        events_path = self.root / "runs" / run_id / "events.jsonl"
        self.assertEqual(before, events_path.read_bytes())
        self.assertNotIn(secret, events_path.read_text(encoding="utf-8"))

    def test_prospective_resume_trace_flags(self):
        run_id = self.start(capture="prospective_resume", pre=True)
        value = recorder.read_json(self.root / "runs" / run_id / "metadata.json")
        self.assertTrue(value["pre_recorder_work"])
        self.assertFalse(value["pre_recorder_trace_complete"])
        with self.assertRaisesRegex(recorder.RecorderError, "requires"):
            self.start(capture="prospective_resume", pre=False)

    def test_bootstrap_partial_is_never_trace_complete(self):
        run_id = self.start(capture="bootstrap_partial", role="bootstrap")
        value = recorder.read_json(self.root / "runs" / run_id / "metadata.json")
        self.assertFalse(value["pre_recorder_trace_complete"])

    def test_secret_redaction_and_no_environment_dump(self):
        prompt_id = self.prompt("API_KEY=supersecretvalue")
        prompt_text = (self.root / "prompts" / prompt_id / "prompt.txt").read_text(encoding="utf-8")
        self.assertNotIn("supersecretvalue", prompt_text)
        self.assertIn("[REDACTED]", prompt_text)
        run_id = self.start()
        result = self.cli("run-command", "--run-id", run_id, "--", sys.executable, "-c", "print('password=hunter2')")
        self.assertEqual(0, result.returncode)
        durable = "".join(p.read_text(encoding="utf-8") for p in (self.root / "runs" / run_id).rglob("*.txt"))
        self.assertNotIn("hunter2", durable)
        metadata = (self.root / "runs" / run_id / "metadata.json").read_text(encoding="utf-8")
        self.assertNotIn("environment", metadata.lower())

    def test_structured_secret_keys_and_quoted_json_prompt_are_redacted(self):
        secrets = ["SYNTHETIC_PASSWORD", "SYNTHETIC_API", "SYNTHETIC_TOKEN",
                   "SYNTHETIC_ACCESS", "SYNTHETIC_REFRESH", "SYNTHETIC_AUTH",
                   "SYNTHETIC_HEADERS"]
        structured = {"password": secrets[0], "api_key": secrets[1], "token": secrets[2],
                      "nested": {"ACCESS_TOKEN": secrets[3], "refresh-token": secrets[4],
                      "Authorization": secrets[5], "raw_auth_headers": secrets[6]}}
        safe, changed = recorder.redact_value(structured)
        self.assertTrue(changed)
        self.assertNotIn("SYNTHETIC_", json.dumps(safe))

        prompt_id = self.prompt(json.dumps(structured))
        prompt_dir = self.root / "prompts" / prompt_id
        prompt_text = (prompt_dir / "prompt.txt").read_text(encoding="utf-8")
        metadata = recorder.read_json(prompt_dir / "metadata.json")
        self.assertEqual("redacted", metadata["prompt_capture"])
        self.assertTrue(metadata["secret_redaction_applied"])
        for secret in secrets:
            self.assertNotIn(secret, prompt_text)

        run_id = self.start()
        recorder.cmd_record_event(self.ns(run_id=run_id, event_type="finding_created",
                                  data_json=json.dumps(structured)), self.repo, self.root)
        durable = (self.root / "runs" / run_id / "events.jsonl").read_text(encoding="utf-8")
        for secret in secrets:
            self.assertNotIn(secret, durable)

    def test_committed_repository_artifacts_validate(self):
        actual = Path(__file__).resolve().parents[2]
        recorder.cmd_validate_repository(self.ns(allow_partial=False), actual, actual / "research")

    def test_repository_safety_in_real_checkout(self):
        actual = Path(__file__).resolve().parents[2]
        changed = subprocess.run(["git", "-C", str(actual), "diff", "--name-only", "1e1523c127c5a0f3baf85d8b5eca11b7b34d80dc", "--"], capture_output=True, text=True, check=True).stdout.splitlines()
        forbidden = [p for p in changed if p.startswith(("backend/", "clients/", "plugins/", "contracts/", "spec/architecture/", "spec/domain/", "spec/invariants/", "spec/acceptance/"))]
        self.assertEqual([], forbidden)
        paused = actual / "spec/tasks/review/LOOP1-CONTRACT-001.md"
        self.assertTrue(paused.exists())
        text = paused.read_text(encoding="utf-8")
        self.assertIn("status: review", text)
        self.assertIn("owner: unassigned-independent-review-agent", text)


if __name__ == "__main__":
    unittest.main()

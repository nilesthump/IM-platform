#!/usr/bin/env python3
"""File-based Research Recorder v1. Records observable facts, never hidden reasoning."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

SCHEMA_VERSION = "1.0.0"
EVENT_TYPES = {
    "run_started", "run_finished", "prompt_registered", "task_state_observed",
    "git_state_observed", "command_started", "command_finished",
    "verification_result", "test_result", "review_started", "review_finished",
    "finding_created", "repair_started", "repair_finished", "ci_started",
    "ci_finished", "architecture_conflict", "human_decision", "external_blocker",
    "model_metadata", "instrumentation_warning",
}
ROLES = {"implementation", "review", "fix", "coordinator", "human", "ci", "bootstrap"}
CAPTURE_MODES = {"prospective", "prospective_resume", "retrospective_backfill", "bootstrap_partial"}
EXPERIMENT_GROUPS = {"vanilla", "spec_only", "full_governance", "unassigned"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization\s*:\s*(?:bearer\s+)?)[^\s]+"),
    re.compile(r"(?i)\b(api[_-]?key|password|passwd|secret|access[_-]?token|refresh[_-]?token)\b\s*[:=]\s*[^\s,;]+"),
    re.compile(r"\b(?:ghp|github_pat|sk)-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


class RecorderError(RuntimeError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecorderError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RecorderError(f"expected JSON object at {path}")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp-{uuid.uuid4().hex}")
    with temp.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def redact(text: str) -> tuple[str, bool]:
    changed = False
    for pattern in SECRET_PATTERNS:
        def replacement(match: re.Match[str]) -> str:
            nonlocal changed
            changed = True
            prefix = match.group(1) if match.lastindex else ""
            return prefix + "[REDACTED]"
        text = pattern.sub(replacement, text)
    return text, changed


def redact_value(value: object) -> tuple[object, bool]:
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        output, changed = [], False
        for item in value:
            safe, item_changed = redact_value(item)
            output.append(safe)
            changed = changed or item_changed
        return output, changed
    if isinstance(value, dict):
        output, changed = {}, False
        for key, item in value.items():
            safe, item_changed = redact_value(item)
            output[key] = safe
            changed = changed or item_changed
        return output, changed
    return value, False


def repo_root(explicit: str | None) -> Path:
    root = Path(explicit).resolve() if explicit else Path(__file__).resolve().parents[2]
    if not (root / ".git").exists():
        probe = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if probe.returncode != 0:
            raise RecorderError(f"not a Git repository: {root}")
        root = Path(probe.stdout.strip()).resolve()
    return root


def research_root(repo: Path, explicit: str | None) -> Path:
    return Path(explicit).resolve() if explicit else repo / "research"


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), "-c", "core.excludesFile=.git/info/exclude", *args], capture_output=True)
    if result.returncode != 0:
        raise RecorderError(f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout if binary else result.stdout.decode("utf-8", "replace")


def parse_current(repo: Path) -> dict:
    path = repo / "spec/progress/current.md"
    if not path.exists():
        return {"presence": "absent"}
    text = path.read_text(encoding="utf-8")
    result: dict[str, object] = {"presence": "present", "path": "spec/progress/current.md"}
    fields = {
        "task_id": r"(?m)^Current Task:\s*`?([^`\r\n]+)`?\s*$",
        "task_state": r"(?m)^Current Task State:\s*`?([^`\r\n]+)`?\s*$",
        "last_known_good_commit": r"(?ms)^## Last Known Good Commit\s*.*?`([0-9a-f]{40})`",
        "latest_checkpoint": r"(?ms)^## Latest Checkpoint\s*.*?`([^`]+)`",
    }
    for key, pattern in fields.items():
        match = re.search(pattern, text)
        result[key] = match.group(1).strip() if match else "unavailable"
    task_id = result["task_id"]
    matches = list((repo / "spec/tasks").glob(f"*/{task_id}.md")) if task_id != "unavailable" else []
    if len(matches) == 1:
        task_text = matches[0].read_text(encoding="utf-8")
        owner = re.search(r"(?m)^owner:\s*(.+?)\s*$", task_text)
        result.update({"task_queue": matches[0].parent.name, "task_owner": owner.group(1) if owner else "unavailable"})
    else:
        result.update({"task_queue": "unavailable", "task_owner": "unavailable"})
    return result


def capture_git(repo: Path) -> dict:
    status_text = str(git(repo, "status", "--porcelain=v1", "--untracked-files=all"))
    changed = []
    for line in status_text.splitlines():
        name = line[3:]
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        changed.append(name)
    branch = str(git(repo, "branch", "--show-current")).strip() or "detached"
    return {
        "repo_identifier": Path(str(git(repo, "rev-parse", "--show-toplevel")).strip()).name,
        "head_sha": str(git(repo, "rev-parse", "HEAD")).strip(),
        "branch": branch,
        "clean": not bool(status_text),
        "changed_paths": changed,
        "status_porcelain": status_text.splitlines(),
        "diff_stat": str(git(repo, "diff", "--stat", "HEAD")).splitlines(),
    }


def authority_snapshot(repo: Path, task_id: str) -> dict:
    candidates = ["AGENTS.md", "spec/handoff/agent-context.md", "spec/progress/current.md",
                  "spec/architecture/README.md", "spec/architecture/baseline.md", "scalable-distributed-im-architecture.pdf"]
    candidates += str(git(repo, "ls-files", "spec/architecture/decisions", "spec/domain", "spec/invariants", "spec/acceptance", "contracts")).splitlines()
    candidates += [p.relative_to(repo).as_posix() for p in (repo / "spec/tasks").glob(f"*/{task_id}.md")]
    files = {}
    for relative in sorted(set(candidates)):
        path = repo / relative
        if path.is_file():
            files[relative] = {"presence": "present", "sha256": sha256_bytes(path.read_bytes())}
        else:
            files[relative] = {"presence": "absent"}
    return {"hash_algorithm": "sha256", "files": files}


def run_dir(root: Path, run_id: str) -> Path:
    return root / "runs" / run_id


def validated_run_id(run_id: str) -> str:
    if not re.fullmatch(r"R-[A-Za-z0-9_.:-]+", run_id):
        raise RecorderError("invalid run_id")
    return run_id


def event_records(path: Path) -> list[dict]:
    if not path.exists():
        raise RecorderError(f"missing event stream: {path}")
    records = []
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.endswith("\n"):
                raise RecorderError(f"partial JSONL write at line {number}")
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RecorderError(f"malformed JSONL at line {number}: {exc}") from exc
            if not isinstance(value, dict):
                raise RecorderError(f"event line {number} is not an object")
            records.append(value)
    return records


def validate_events(path: Path, run_id: str) -> list[dict]:
    records = event_records(path)
    previous = "0" * 64
    for expected, item in enumerate(records, 1):
        required = {"schema_version", "seq", "timestamp", "run_id", "task_id", "role", "event_type", "data", "previous_event_hash", "event_hash"}
        if set(item) != required:
            raise RecorderError(f"event {expected} fields do not match schema")
        if item["seq"] != expected:
            raise RecorderError(f"duplicate or non-monotonic sequence: expected {expected}, got {item['seq']}")
        if item["run_id"] != run_id:
            raise RecorderError(f"event {expected} run_id mismatch")
        if item["schema_version"] != SCHEMA_VERSION or item["event_type"] not in EVENT_TYPES or item["role"] not in ROLES or not isinstance(item["data"], dict):
            raise RecorderError(f"event {expected} contains invalid enum or data")
        if item["previous_event_hash"] != previous:
            raise RecorderError(f"event {expected} hash chain predecessor mismatch")
        unsigned = dict(item)
        actual = unsigned.pop("event_hash")
        expected_hash = sha256_bytes(canonical(unsigned))
        if actual != expected_hash:
            raise RecorderError(f"event {expected} hash mismatch")
        previous = actual
    return records


def append_event(root: Path, run_id: str, event_type: str, data: dict, *, allow_finished: bool = False) -> dict:
    if event_type not in EVENT_TYPES:
        raise RecorderError(f"unsupported event_type: {event_type}")
    directory = run_dir(root, validated_run_id(run_id))
    metadata = read_json(directory / "metadata.json")
    if metadata.get("status") == "finished" and not allow_finished:
        raise RecorderError("finished runs are immutable")
    path = directory / "events.jsonl"
    lock = directory / ".events.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError as exc:
        raise RecorderError("event stream is locked; interrupted writer may require inspection") from exc
    try:
        records = validate_events(path, run_id)
        seq = len(records) + 1
        previous = records[-1]["event_hash"] if records else "0" * 64
        event = {"schema_version": SCHEMA_VERSION, "seq": seq, "timestamp": now(), "run_id": run_id,
                 "task_id": metadata["task_id"], "role": metadata["role"], "event_type": event_type,
                 "data": data, "previous_event_hash": previous}
        event["event_hash"] = sha256_bytes(canonical(event))
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(canonical(event).decode("utf-8") + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return event
    finally:
        lock.unlink(missing_ok=True)


def cmd_register_prompt(args: argparse.Namespace, repo: Path, root: Path) -> int:
    if args.file:
        content = Path(args.file).read_bytes().decode("utf-8")
    elif args.stdin_base64:
        content = base64.b64decode(sys.stdin.buffer.read(), validate=True).decode("utf-8")
    else:
        content = sys.stdin.read()
    safe, was_redacted = redact(content)
    prompt_id = args.prompt_id or f"P-{uuid.uuid4()}"
    if not re.fullmatch(r"P-[A-Za-z0-9_.:-]+", prompt_id):
        raise RecorderError("invalid prompt_id")
    digest = sha256_bytes(safe.encode("utf-8"))
    metadata = {"recorder_schema_version": SCHEMA_VERSION, "prompt_id": prompt_id, "prompt_sha256": digest,
                "prompt_capture": "redacted" if was_redacted else "full", "prompt_source": args.source,
                "template_version": args.template_version or "unavailable", "task_id": args.task_id,
                "associated_run_id": args.run_id or "unavailable", "registered_at": now(),
                "system_prompt_capture": "unavailable", "secret_redaction_applied": was_redacted}
    directory = root / "prompts" / prompt_id
    if directory.exists():
        raise RecorderError(f"prompt already exists: {prompt_id}")
    directory.mkdir(parents=True)
    (directory / "prompt.txt").write_text(safe, encoding="utf-8", newline="\n")
    write_json(directory / "metadata.json", metadata)
    if args.run_id:
        append_event(root, args.run_id, "prompt_registered", {"prompt_id": prompt_id, "prompt_sha256": digest,
                     "prompt_capture": metadata["prompt_capture"], "prompt_source": args.source})
    print(json.dumps(metadata, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_start_run(args: argparse.Namespace, repo: Path, root: Path) -> int:
    if args.role not in ROLES or args.capture_mode not in CAPTURE_MODES or args.experiment_group not in EXPERIMENT_GROUPS:
        raise RecorderError("invalid role, capture_mode, or experiment_group")
    if args.capture_mode == "prospective_resume" and not args.pre_recorder_work:
        raise RecorderError("prospective_resume requires --pre-recorder-work")
    run_id = args.run_id or f"R-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4()}"
    directory = run_dir(root, validated_run_id(run_id))
    current = parse_current(repo)
    task_id = args.task_id or str(current.get("task_id", "unavailable"))
    prompt_id = args.prompt_id or "unavailable"
    if prompt_id != "unavailable":
        prompt_meta_path = root / "prompts" / prompt_id / "metadata.json"
        prompt_meta = read_json(prompt_meta_path)
        if prompt_meta["task_id"] != task_id:
            raise RecorderError("prompt task_id does not match run task_id")
        associated = prompt_meta.get("associated_run_id", "unavailable")
        if associated not in {"unavailable", run_id}:
            raise RecorderError(f"prompt is already associated with run {associated}")
    directory.mkdir(parents=True, exist_ok=False)
    metadata = {"recorder_schema_version": SCHEMA_VERSION, "run_id": run_id, "task_id": task_id,
                "role": args.role, "parent_run_id": args.parent_run_id or "unavailable",
                "related_run_id": args.related_run_id or "unavailable", "experiment_group": args.experiment_group,
                "capture_mode": args.capture_mode, "prompt_id": prompt_id, "status": "running", "started_at": now(),
                "finished_at": "unavailable", "pre_recorder_work": bool(args.pre_recorder_work),
                "pre_recorder_trace_complete": args.capture_mode == "prospective" and not bool(args.pre_recorder_work), "agent_harness": args.agent_harness,
                "model_name": args.model_name, "model_version": "unavailable", "token_usage": "unavailable",
                "monetary_cost": "unavailable", "system_prompt_capture": "unavailable"}
    metadata.update({"fresh_context": args.fresh_context, "explicit_token_budget": args.explicit_token_budget,
                     "context_mode": args.context_mode, "public_reasoning_mode": args.public_reasoning_mode,
                     "baseline_id": args.baseline_id, "replicate_id": args.replicate_id,
                     "mutation_id": args.mutation_id, "model_condition": args.model_condition,
                     "budget_condition": args.budget_condition})
    initial = {"recorder_schema_version": SCHEMA_VERSION, "captured_at": now(), "git": capture_git(repo),
               "task": current, "authority_snapshot": authority_snapshot(repo, task_id)}
    write_json(directory / "metadata.json", metadata)
    write_json(directory / "initial_state.json", initial)
    (directory / "events.jsonl").touch(exist_ok=False)
    if prompt_id != "unavailable":
        prompt_meta["associated_run_id"] = run_id
        write_json(prompt_meta_path, prompt_meta)
    append_event(root, run_id, "run_started", {"capture_mode": args.capture_mode, "prompt_id": prompt_id,
                 "pre_recorder_work": bool(args.pre_recorder_work),
                 "pre_recorder_trace_complete": args.capture_mode == "prospective" and not bool(args.pre_recorder_work)})
    append_event(root, run_id, "task_state_observed", current)
    append_event(root, run_id, "git_state_observed", initial["git"])
    print(run_id)
    return 0


def command_data(argv: list[str]) -> tuple[list[str], bool]:
    safe, changed = redact("\n".join(argv))
    return safe.split("\n"), changed


def cmd_run_command(args: argparse.Namespace, repo: Path, root: Path) -> int:
    argv = list(args.command)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        raise RecorderError("command is required")
    safe_argv, command_redacted = command_data(argv)
    command_id = f"C-{uuid.uuid4()}"
    append_event(root, args.run_id, "command_started", {"command_id": command_id, "argv": safe_argv,
                 "cwd": ".", "secret_redaction_applied": command_redacted})
    started = time.monotonic_ns()
    result = subprocess.run(argv, cwd=repo, capture_output=True)
    duration_ms = (time.monotonic_ns() - started) / 1_000_000
    stdout_text = result.stdout.decode("utf-8", "replace")
    stderr_text = result.stderr.decode("utf-8", "replace")
    sys.stdout.write(stdout_text)
    sys.stderr.write(stderr_text)
    safe_out, out_redacted = redact(stdout_text)
    safe_err, err_redacted = redact(stderr_text)
    blob_dir = run_dir(root, args.run_id) / "blobs"
    blob_dir.mkdir(exist_ok=True)
    (blob_dir / f"{command_id}.stdout.txt").write_text(safe_out, encoding="utf-8", newline="\n")
    (blob_dir / f"{command_id}.stderr.txt").write_text(safe_err, encoding="utf-8", newline="\n")
    append_event(root, args.run_id, "command_finished", {"command_id": command_id, "exit_code": result.returncode,
                 "duration_ms": duration_ms, "result": "PASS" if result.returncode == 0 else "FAIL",
                 "stdout_sha256": sha256_bytes(result.stdout), "stderr_sha256": sha256_bytes(result.stderr),
                 "stdout_blob": f"blobs/{command_id}.stdout.txt", "stderr_blob": f"blobs/{command_id}.stderr.txt",
                 "secret_redaction_applied": command_redacted or out_redacted or err_redacted})
    return result.returncode


def cmd_record_event(args: argparse.Namespace, repo: Path, root: Path) -> int:
    data = json.loads(args.data_json)
    if not isinstance(data, dict):
        raise RecorderError("event data must be a JSON object")
    safe_data, redacted = redact_value(data)
    if args.event_type in {"verification_result", "test_result", "review_finished", "ci_finished"} and "result" not in safe_data:
        raise RecorderError(f"{args.event_type} requires an observed result")
    if redacted:
        safe_data["secret_redaction_applied"] = True
    event = append_event(root, args.run_id, args.event_type, safe_data)
    print(json.dumps(event, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_human_decision(args: argparse.Namespace, repo: Path, root: Path) -> int:
    alternatives = json.loads(args.alternatives_json)
    if not isinstance(alternatives, list) or not alternatives:
        raise RecorderError("alternatives must be a non-empty JSON list")
    data = {"decision_id": args.decision_id or f"HD-{uuid.uuid4()}", "question": args.question,
            "alternatives": alternatives, "selected": args.selected, "reason": args.reason,
            "affected_authority": args.affected_authority or "unavailable", "human_actor": True,
            "fixture": bool(args.fixture)}
    data, changed = redact_value(data)
    if changed:
        data["secret_redaction_applied"] = True
    append_event(root, args.run_id, "human_decision", data)
    print(data["decision_id"])
    return 0


def cmd_ingest_ci(args: argparse.Namespace, repo: Path, root: Path) -> int:
    evidence = read_json(Path(args.evidence))
    required = {"provider", "ci_run_id", "commit_sha", "job_name", "result", "failed_checks", "duration_ms", "evidence_reference"}
    missing = required - set(evidence)
    if missing or evidence.get("result") not in {"PASS", "FAIL"}:
        raise RecorderError(f"invalid CI evidence; missing={sorted(missing)}")
    evidence["observed_evidence_sha256"] = sha256_bytes(Path(args.evidence).read_bytes())
    append_event(root, args.run_id, "ci_finished", evidence)
    return 0


def cmd_finish_run(args: argparse.Namespace, repo: Path, root: Path) -> int:
    directory = run_dir(root, validated_run_id(args.run_id))
    metadata = read_json(directory / "metadata.json")
    if metadata.get("status") == "finished":
        raise RecorderError("run is already finished")
    final = {"recorder_schema_version": SCHEMA_VERSION, "captured_at": now(), "git": capture_git(repo),
             "task": parse_current(repo), "authority_snapshot": authority_snapshot(repo, metadata["task_id"])}
    initial = read_json(directory / "initial_state.json")
    diff_bytes = git(repo, "diff", "--binary", initial["git"]["head_sha"], "--", binary=True)
    diff_text = diff_bytes.decode("utf-8", "replace")
    untracked = [line[3:] for line in final["git"]["status_porcelain"] if line.startswith("?? ")]
    if untracked:
        diff_text += "\n# Untracked paths observed; content intentionally not captured\n"
        diff_text += "".join(f"# ?? {path}\n" for path in untracked)
    diff_text, redacted = redact(diff_text)
    (directory / "diff.patch").write_text(diff_text, encoding="utf-8", newline="\n")
    write_json(directory / "final_state.json", final)
    append_event(root, args.run_id, "run_finished", {"result": args.result, "final_head_sha": final["git"]["head_sha"],
                 "diff_sha256": sha256_bytes(diff_text.encode("utf-8")), "secret_redaction_applied": redacted})
    records = validate_events(directory / "events.jsonl", args.run_id)
    finished_at = now()
    started = dt.datetime.fromisoformat(metadata["started_at"].replace("Z", "+00:00"))
    finished = dt.datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    metadata.update({"status": "finished", "finished_at": finished_at,
                     "duration_ms": (finished - started).total_seconds() * 1000,
                     "pre_recorder_trace_complete": metadata["capture_mode"] == "prospective" and not metadata.get("pre_recorder_work", False)})
    summary = {"recorder_schema_version": SCHEMA_VERSION, "run_id": args.run_id, "status": "finished",
               "result": args.result, "event_count": len(records), "first_event_hash": records[0]["event_hash"],
               "final_event_hash": records[-1]["event_hash"], "manifest_hash": "unavailable"}
    manifest_inputs = {"metadata": metadata, "initial_state_sha256": sha256_bytes((directory / "initial_state.json").read_bytes()),
                       "final_state_sha256": sha256_bytes((directory / "final_state.json").read_bytes()),
                       "diff_sha256": sha256_bytes((directory / "diff.patch").read_bytes()),
                       "events_sha256": sha256_bytes((directory / "events.jsonl").read_bytes())}
    summary["manifest_hash"] = sha256_bytes(canonical(manifest_inputs))
    write_json(directory / "summary.json", summary)
    write_json(directory / "metadata.json", metadata)
    print(json.dumps(summary, sort_keys=True))
    return 0


def validate_run(root: Path, run_id: str, require_finished: bool = True) -> dict:
    directory = run_dir(root, validated_run_id(run_id))
    metadata = read_json(directory / "metadata.json")
    required_meta = {"recorder_schema_version", "run_id", "task_id", "role", "experiment_group", "capture_mode", "status"}
    if missing := required_meta - set(metadata):
        raise RecorderError(f"metadata missing fields: {sorted(missing)}")
    if metadata["run_id"] != run_id or metadata["role"] not in ROLES or metadata["capture_mode"] not in CAPTURE_MODES:
        raise RecorderError("invalid run metadata")
    records = validate_events(directory / "events.jsonl", run_id)
    if not records or records[0]["event_type"] != "run_started":
        raise RecorderError("run has no valid run_started event")
    if metadata["status"] == "finished":
        for name in ("final_state.json", "diff.patch", "summary.json"):
            if not (directory / name).exists():
                raise RecorderError(f"finished run missing {name}")
        if records[-1]["event_type"] != "run_finished":
            raise RecorderError("finished run does not end with run_finished")
        summary = read_json(directory / "summary.json")
        manifest_inputs = {"metadata": metadata,
                           "initial_state_sha256": sha256_bytes((directory / "initial_state.json").read_bytes()),
                           "final_state_sha256": sha256_bytes((directory / "final_state.json").read_bytes()),
                           "diff_sha256": sha256_bytes((directory / "diff.patch").read_bytes()),
                           "events_sha256": sha256_bytes((directory / "events.jsonl").read_bytes())}
        if summary.get("manifest_hash") != sha256_bytes(canonical(manifest_inputs)):
            raise RecorderError("finished run manifest hash mismatch")
    elif require_finished:
        raise RecorderError("partial/interrupted run: status is not finished")
    if metadata["capture_mode"] == "prospective_resume" and (not metadata.get("pre_recorder_work") or metadata.get("pre_recorder_trace_complete") is not False):
        raise RecorderError("invalid prospective_resume trace completeness")
    return {"run_id": run_id, "status": metadata["status"], "event_count": len(records)}


def cmd_validate_run(args: argparse.Namespace, repo: Path, root: Path) -> int:
    print(json.dumps(validate_run(root, args.run_id, not args.allow_partial), sort_keys=True))
    return 0


def cmd_validate_repository(args: argparse.Namespace, repo: Path, root: Path) -> int:
    failures = []
    for directory in sorted((root / "runs").glob("R-*")) if (root / "runs").exists() else []:
        try:
            validate_run(root, directory.name, not args.allow_partial)
        except RecorderError as exc:
            failures.append(f"{directory.name}: {exc}")
    epoch = root / "INSTRUMENTATION_EPOCH.json"
    if epoch.exists():
        value = read_json(epoch)
        required = {"timestamp", "recorder_schema_version", "accepted_recorder_commit_sha", "recorder_task_id", "acceptance_evidence", "prospective_trace_start"}
        if missing := required - set(value):
            failures.append(f"Instrumentation Epoch missing {sorted(missing)}")
    if failures:
        raise RecorderError("repository validation failed: " + "; ".join(failures))
    print("PASS: Research Recorder repository artifacts validated.")
    return 0


def cmd_backfill(args: argparse.Namespace, repo: Path, root: Path) -> int:
    task_paths = list((repo / "spec/tasks").glob(f"*/{args.task_id}.md"))
    if len(task_paths) != 1:
        raise RecorderError("backfill task must resolve exactly once")
    task_path = task_paths[0]
    text = task_path.read_text(encoding="utf-8")
    commits = sorted(set(re.findall(r"\b[0-9a-f]{40}\b", text)))
    evidence = [p.relative_to(repo).as_posix() for p in (repo / "spec/progress/evidence" / args.task_id).glob("*.md")]
    value = {"recorder_schema_version": SCHEMA_VERSION, "task_id": args.task_id,
             "collection_mode": "retrospective_backfill", "backfilled": True, "generated_at": now(),
             "sources": {"task_spec": task_path.relative_to(repo).as_posix(), "durable_evidence": sorted(evidence), "commits_mentioned": commits},
             "prompt": "unavailable", "model_calls": "unavailable", "token_usage": "unavailable", "tool_calls": "unavailable",
             "exact_timing": "unavailable", "reasoning": "unavailable", "context_size": "unavailable", "cost": "unavailable"}
    write_json(root / "backfill" / f"{args.task_id}.json", value)
    print(args.task_id)
    return 0


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo")
    common.add_argument("--research-root")
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="subcommand", required=True)
    p = sub.add_parser("register-prompt", parents=[common]); p.add_argument("--task-id", required=True); p.add_argument("--file"); p.add_argument("--stdin-base64", action="store_true"); p.add_argument("--source", default="human"); p.add_argument("--template-version"); p.add_argument("--run-id"); p.add_argument("--prompt-id")
    p = sub.add_parser("start-run", parents=[common]); p.add_argument("--task-id"); p.add_argument("--role", required=True); p.add_argument("--capture-mode", required=True); p.add_argument("--experiment-group", default="unassigned"); p.add_argument("--prompt-id"); p.add_argument("--parent-run-id"); p.add_argument("--related-run-id"); p.add_argument("--run-id"); p.add_argument("--pre-recorder-work", action="store_true"); p.add_argument("--agent-harness", default="unavailable"); p.add_argument("--model-name", default="unavailable"); p.add_argument("--fresh-context", default="unavailable"); p.add_argument("--explicit-token-budget", default="unavailable"); p.add_argument("--context-mode", default="unavailable"); p.add_argument("--public-reasoning-mode", default="unavailable"); p.add_argument("--baseline-id", default="unavailable"); p.add_argument("--replicate-id", default="unavailable"); p.add_argument("--mutation-id", default="unavailable"); p.add_argument("--model-condition", default="unavailable"); p.add_argument("--budget-condition", default="unavailable")
    p = sub.add_parser("run-command", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("command", nargs=argparse.REMAINDER)
    p = sub.add_parser("record-event", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("--event-type", required=True); p.add_argument("--data-json", required=True)
    p = sub.add_parser("record-human-decision", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("--decision-id"); p.add_argument("--question", required=True); p.add_argument("--alternatives-json", required=True); p.add_argument("--selected", required=True); p.add_argument("--reason", required=True); p.add_argument("--affected-authority"); p.add_argument("--fixture", action="store_true")
    p = sub.add_parser("ingest-ci", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("--evidence", required=True)
    p = sub.add_parser("finish-run", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("--result", choices=["PASS", "FAIL", "BLOCKED", "CANCELLED"], required=True)
    p = sub.add_parser("validate-run", parents=[common]); p.add_argument("--run-id", required=True); p.add_argument("--allow-partial", action="store_true")
    p = sub.add_parser("validate-repository", parents=[common]); p.add_argument("--allow-partial", action="store_true")
    p = sub.add_parser("backfill", parents=[common]); p.add_argument("--task-id", required=True)
    return top


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        repo = repo_root(args.repo)
        root = research_root(repo, args.research_root)
        root.mkdir(parents=True, exist_ok=True)
        commands = {"register-prompt": cmd_register_prompt, "start-run": cmd_start_run, "run-command": cmd_run_command,
                    "record-event": cmd_record_event, "record-human-decision": cmd_human_decision, "ingest-ci": cmd_ingest_ci,
                    "finish-run": cmd_finish_run, "validate-run": cmd_validate_run,
                    "validate-repository": cmd_validate_repository, "backfill": cmd_backfill}
        return commands[args.subcommand](args, repo, root)
    except (RecorderError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

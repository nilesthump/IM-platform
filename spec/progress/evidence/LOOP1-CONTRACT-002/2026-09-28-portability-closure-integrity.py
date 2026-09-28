"""Audit staged raw Recorder command outputs against recorded hashes."""

import hashlib
import json
import subprocess
from pathlib import Path

root = Path("research/runs/R-20260928T093047Z-78a476e3-1352-4f6b-844b-e06cf8a75bfb")
count = 0
for line in (root / "events.jsonl").read_text(encoding="utf-8").splitlines():
    event = json.loads(line)
    if event["event_type"] != "command_finished":
        continue
    data = event["data"]
    for stream in ("stdout", "stderr"):
        path = root / data[f"{stream}_blob"]
        staged = subprocess.check_output(["git", "show", f":{path.as_posix()}"])
        assert staged == path.read_bytes(), f"staged bytes differ: {path}"
        assert hashlib.sha256(staged).hexdigest() == data[f"{stream}_sha256"], path
        count += 1
print(f"PASS: {count}/{count} staged Recorder output blobs match event hashes")

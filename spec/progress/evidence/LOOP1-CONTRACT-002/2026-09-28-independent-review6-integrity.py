import hashlib
import json
from pathlib import Path
import subprocess

run = "R-20260928T050925Z-2cc0954c-0cd6-43fa-8b41-b014d633a5bb"
root = Path("research/runs") / run
count = 0
for raw in (root / "events.jsonl").read_text(encoding="utf-8").splitlines():
    event = json.loads(raw)
    if event["event_type"] != "command_finished":
        continue
    data = event["data"]
    for stream in ("stdout", "stderr"):
        path = root / data[f"{stream}_blob"]
        working = path.read_bytes()
        committed = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{path.as_posix()}"])
        assert working == committed
        assert hashlib.sha256(working).hexdigest() == data[f"{stream}_sha256"]
        count += 1
print(f"PASS: {count}/{count} Fix 5 output blobs equal committed bytes and event SHA-256")

review_run = "R-20260928T053447Z-5aa0c014-0381-4fba-9457-7acb7cf3da9a"
review_root = Path("research/runs") / review_run
staged_count = 0
for raw in (review_root / "events.jsonl").read_text(encoding="utf-8").splitlines():
    event = json.loads(raw)
    if event["event_type"] != "command_finished":
        continue
    data = event["data"]
    for stream in ("stdout", "stderr"):
        path = review_root / data[f"{stream}_blob"]
        working = path.read_bytes()
        staged = subprocess.check_output(["git", "show", f":{path.as_posix()}"])
        assert working == staged
        assert hashlib.sha256(staged).hexdigest() == data[f"{stream}_sha256"]
        staged_count += 1
print(f"PASS: {staged_count}/{staged_count} Review 6 output blobs equal staged bytes and event SHA-256")

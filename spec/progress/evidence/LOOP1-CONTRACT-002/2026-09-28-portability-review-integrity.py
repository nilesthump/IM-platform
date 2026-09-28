"""Audit a committed Recorder run's raw command output bytes."""
import hashlib
import json
import subprocess
from pathlib import Path

run_id = 'R-20260928T083213Z-9aaad4eb-0bfa-4998-9604-000a450420e6'
root = Path('research/runs') / run_id
count = 0
for line in (root / 'events.jsonl').read_text(encoding='utf-8').splitlines():
    event = json.loads(line)
    if event['event_type'] != 'command_finished':
        continue
    data = event['data']
    for stream in ('stdout', 'stderr'):
        path = root / data[f'{stream}_blob']
        working = path.read_bytes()
        committed = subprocess.check_output(['git', 'cat-file', 'blob', f'HEAD:{path.as_posix()}'])
        assert working == committed, f'working/committed bytes differ: {path}'
        assert hashlib.sha256(committed).hexdigest() == data[f'{stream}_sha256'], f'event hash differs: {path}'
        count += 1
print(f'PASS: {count}/{count} Fix portability output blobs match events and committed Git bytes')
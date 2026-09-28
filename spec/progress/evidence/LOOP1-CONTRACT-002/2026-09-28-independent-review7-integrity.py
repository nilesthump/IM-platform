"""Verify Fix 6 Recorder output bytes against event hashes and committed Git blobs."""
import hashlib
import json
from pathlib import Path
import subprocess

run = 'R-20260928T060018Z-0daae2f5-d6ee-4d1a-a688-39bb16513878'
root = Path('research/runs') / run
count = 0
for raw in (root / 'events.jsonl').read_text(encoding='utf-8').splitlines():
    event = json.loads(raw)
    if event['event_type'] != 'command_finished':
        continue
    data = event['data']
    for stream in ('stdout', 'stderr'):
        path = root / data[f'{stream}_blob']
        working = path.read_bytes()
        committed = subprocess.check_output(['git', 'cat-file', 'blob', f'HEAD:{path.as_posix()}'])
        assert working == committed, f'uncommitted output bytes: {path}'
        assert hashlib.sha256(working).hexdigest() == data[f'{stream}_sha256'], f'output hash mismatch: {path}'
        count += 1
print(f'PASS: {count}/{count} Fix 6 output blobs match events and committed bytes')

review_run = 'R-20260928T062353Z-39bc4b6e-2cc6-4610-940b-1e93949d211b'
review_root = Path('research/runs') / review_run
staged_count = 0
for raw in (review_root / 'events.jsonl').read_text(encoding='utf-8').splitlines():
    event = json.loads(raw)
    if event['event_type'] != 'command_finished':
        continue
    data = event['data']
    for stream in ('stdout', 'stderr'):
        path = review_root / data[f'{stream}_blob']
        working = path.read_bytes()
        staged = subprocess.check_output(['git', 'show', f':{path.as_posix()}'])
        assert working == staged, f'staged output bytes differ: {path}'
        assert hashlib.sha256(staged).hexdigest() == data[f'{stream}_sha256'], f'staged output hash mismatch: {path}'
        staged_count += 1
print(f'PASS: {staged_count}/{staged_count} Review 7 output blobs match events and staged bytes')

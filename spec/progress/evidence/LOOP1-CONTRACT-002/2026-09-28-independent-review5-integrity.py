import hashlib
import json
import pathlib
import subprocess
run = 'R-20260928T042440Z-2abf26e1-ad46-4d62-b224-42f747519427'
root = pathlib.Path('research/runs') / run
count = 0
for raw in (root/'events.jsonl').read_text(encoding='utf-8').splitlines():
    event = json.loads(raw)
    if event['event_type'] != 'command_finished':
        continue
    data = event['data']
    for stream in ('stdout', 'stderr'):
        rel = data[f'{stream}_blob']
        path = root / rel
        working = path.read_bytes()
        committed = subprocess.check_output(['git','cat-file','blob',f'HEAD:{path.as_posix()}'])
        digest = hashlib.sha256(working).hexdigest()
        assert working == committed and digest == data[f'{stream}_sha256'], str(path)
        count += 1
print(f'PASS: {count}/{count} Fix 4 output blobs equal committed bytes and event SHA-256')
review_run = 'R-20260928T044144Z-c2f35c2f-7072-4b31-bd49-5b84dd1c4654'
review_root = pathlib.Path('research/runs') / review_run
staged_count = 0
for raw in (review_root/'events.jsonl').read_text(encoding='utf-8').splitlines():
    event = json.loads(raw)
    if event['event_type'] != 'command_finished':
        continue
    data = event['data']
    for stream in ('stdout','stderr'):
        path = review_root / data[f'{stream}_blob']
        staged = subprocess.check_output(['git','show',f':{path.as_posix()}'])
        working = path.read_bytes()
        assert working == staged and hashlib.sha256(staged).hexdigest() == data[f'{stream}_sha256'], str(path)
        staged_count += 1
print(f'PASS: {staged_count}/{staged_count} Review 5 staged output blobs equal working bytes and event SHA-256')
import json
from pathlib import Path
root=Path('H:/.codex/evidence/s2-sqlite-fixed-independent-review-20261001/research/runs/R-SQLITE-FIXED-REVIEW-20261001')
events=[json.loads(l) for l in (root/'events.jsonl').read_text(encoding='utf-8').splitlines()]
for e in events:
 if e['event_type']=='command_finished':
  d=e['data']; print(d['command_id'],d['exit_code'],d['duration_ms'])
  for k in ('stdout_blob','stderr_blob'):
   blob=(root/d[k]).read_text(encoding='utf-8')
   for line in blob.splitlines():
    if line.startswith(('PASS:','Ran ','OK','FAIL:')): print(line)

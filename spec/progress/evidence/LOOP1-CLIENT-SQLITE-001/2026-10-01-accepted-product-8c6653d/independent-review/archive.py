import json,hashlib
from pathlib import Path
p=Path('H:/.codex/evidence/s2-sqlite-fixed-independent-review-20261001')
r=p/'research/runs/R-SQLITE-FIXED-REVIEW-20261001'
events=[json.loads(l) for l in (r/'events.jsonl').read_text(encoding='utf-8').splitlines()]
started={e['data']['command_id']:e['data'] for e in events if e['event_type']=='command_started'}
ledger=[{'started':started[e['data']['command_id']],'finished':e['data']} for e in events if e['event_type']=='command_finished']
(p/'command-results.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
files={str(f.relative_to(p)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and f.name!='manifest.json'}
(p/'manifest.json').write_text(json.dumps({'candidate_sha':'8c6653d36051a805ccd576806ffda8a6159edbd3','review_result':'PASS','reviewer':'/root/sqlite_fixed_independent_review','files':files},indent=2),encoding='utf-8')
for name in ('independent-review.md','manifest.json','command-results.json'): print(name,hashlib.sha256((p/name).read_bytes()).hexdigest())

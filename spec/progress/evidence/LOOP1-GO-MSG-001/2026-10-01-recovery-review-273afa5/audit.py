from pathlib import Path
import json,subprocess,hashlib
r=Path('H:/.codex/worktrees/s1-recovery-review-20261001-b'); o=Path('H:/.codex/evidence/s1-recovery-review-20261001-b'); original=Path('H:/IM-platform')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
e=r/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync'
a=json.loads((e/'archive-byte-manifest.json').read_text(encoding='utf-8-sig')); bad=[]; missing=[]
for row in a:
 p=r/row['archive']; s=Path(row['source'])
 if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=row['size']:bad.append({'kind':'archive','row':row})
 if s.is_file():
  if sha(s)!=row['sha256']:bad.append({'kind':'original-source','row':row})
 else:missing.append(row['source'])
inv=json.loads((e/'original-inventory.json').read_text(encoding='utf-8-sig')); rel=json.loads((e/'original-relocation.json').read_text(encoding='utf-8-sig'))
for row in inv['untracked']:
 p=original/row['path']
 if row['path']=='spec/progress/evidence/LOOP1-CI-001/review2-negative-probe.py':p=original/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync/preserved-original/review2-negative-probe.py'
 if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=row['size']:bad.append({'kind':'original605','row':row})
names=subprocess.check_output(['git','diff','--name-only','33b1522..273afa5'],cwd=r).decode().splitlines()
allowed=lambda p:p.startswith('research/prompts/P-MSG-SYNC-HANDOFF-20261001/') or p.startswith('research/runs/R-MSG-SYNC-HANDOFF-20261001/') or p.startswith('spec/progress/evidence/LOOP1-GO-MSG-001/') or p in ['spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-sync-handoff.md']
for p in names:
 if not allowed(p):bad.append({'kind':'scope','path':p})
oldpaths=subprocess.check_output(['git','ls-tree','-r','--name-only','33b1522'],cwd=r).decode().splitlines(); immutable=0
for p in oldpaths:
 if p.startswith(('research/','spec/progress/evidence/','spec/progress/checkpoints/')):
  old=subprocess.check_output(['git','rev-parse','33b1522:'+p],cwd=r).strip(); new=subprocess.check_output(['git','rev-parse','273afa5:'+p],cwd=r).strip()
  if old!=new:bad.append({'kind':'historical-mutation','path':p})
  immutable+=1
result={'archive301':len(a),'missing_external_source':missing,'original605':len(inv['untracked']),'historical_files_unchanged':immutable,'changed_paths':len(names),'bad':bad,'result':'FAIL' if bad else 'PASS'}
(o/'byte-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result));raise SystemExit(bool(bad))

from pathlib import Path
import subprocess,json,hashlib
from review import ROOT,OUT,run,PY,REC,RESEARCH,RID
r=ROOT;o=OUT;original=Path('H:/IM-platform');bad=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(ref):
 data=subprocess.check_output(['git','ls-tree','-r','-z',ref],cwd=r)
 return {z.split(b'\t',1)[1].decode():z.split(b'\t',1)[0].split()[2].decode() for z in data.split(b'\0') if z}
a=tree('273afa5');b=tree('b51e62a');names=[p for p in set(a)|set(b) if a.get(p)!=b.get(p)]
allowed=lambda p:p.startswith(('research/prompts/P-S1-RESUME-20261001-B/','research/runs/R-S1-RESUME-20261001-B/','spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-recovery-review-273afa5/')) or p in ['spec/progress/current.md','spec/tasks/done/LOOP1-GO-MSG-001.md','spec/progress/checkpoints/2026-10-01-loop1-go-msg-001-recovery-review.md']
for p in names:
 if not allowed(p):bad.append(dict(kind='scope',path=p))
immutable=[p for p in a if p.startswith(('research/','spec/progress/evidence/','spec/progress/checkpoints/'))]
for p in immutable:
 if a[p]!=b.get(p):bad.append(dict(kind='prior-immutable',path=p))
source=Path('H:/.codex/evidence/s1-recovery-review-20261001-b');archive=r/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-recovery-review-273afa5';external=list(source.rglob('*'));extfiles=[p for p in external if p.is_file()]
for p in extfiles:
 target=archive/p.relative_to(source)
 if not target.is_file() or p.read_bytes()!=target.read_bytes():bad.append(dict(kind='new-archive120',path=str(p)))
e=r/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync';old=json.loads((e/'archive-byte-manifest.json').read_text(encoding='utf-8-sig'))
for row in old:
 p=r/row['archive']
 if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=row['size']:bad.append(dict(kind='archive301',path=str(p)))
inv=json.loads((e/'original-inventory.json').read_text(encoding='utf-8-sig'))
for row in inv['untracked']:
 p=original/row['path']
 if row['path']=='spec/progress/evidence/LOOP1-CI-001/review2-negative-probe.py':p=original/'spec/progress/evidence/LOOP1-GO-MSG-001/2026-10-01-admin-closure-sync/preserved-original/review2-negative-probe.py'
 if not p.is_file() or sha(p)!=row['sha256'] or p.stat().st_size!=row['size']:bad.append(dict(kind='original605',path=str(p)))
for p in names:
 if p.endswith('/.gitattributes'):
  content=(r/p).read_text();assert content.strip()=='* -text',content
result=dict(result='FAIL' if bad else 'PASS',changed_paths=len(names),new_archive_files=len(extfiles),old_archive_files=len(old),original_files=len(inv['untracked']),prior_immutable_objects=len(immutable),bad=bad,scope=sorted(names))
(o/'byte-audit.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k!='scope'}));raise SystemExit(bool(bad))

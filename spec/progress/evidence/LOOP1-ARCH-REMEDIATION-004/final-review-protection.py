import subprocess,sys,hashlib,json
from pathlib import Path
R=Path(sys.argv[1]);G=lambda *a:subprocess.check_output(['git','-C',str(R),*a],encoding='utf-8').strip()
assert G('rev-parse','HEAD')=='b84cd0f05e675239d73c8e765c3689d8b2d17fa2'
assert not G('status','--porcelain')
for p in ['backend','contracts','deploy','ci','tools','tests','spec/architecture']:
 assert G('rev-parse','HEAD:'+p)==G('rev-parse','87c0ee2:'+p),p
old=G('show','6cdd981:spec/tasks/active/LOOP1-ARCH-REMEDIATION-004.md')
cur=(R/'spec/tasks/review/LOOP1-ARCH-REMEDIATION-004.md').read_text(encoding='utf-8')
for line in old.splitlines():
 if 'applicable \u00a7' in line or 'canonical \u00a7' in line: assert line in cur
assert cur.count('\u00a7')==7 and '\u6402' not in cur and '\ufffd' not in cur
for row in G('diff','--name-status','--no-renames','87c0ee2','HEAD').splitlines():
 kind,p=row.split('\t',1)
 if p.startswith('research/') or p.startswith('spec/progress/evidence/'): assert kind=='A',row
assert hashlib.sha256((R/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()=='83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'
print('PASS exact clean SHA, protected Git trees identical, prior evidence additions only, 7 exact approved section references')

import subprocess,sys,hashlib
from pathlib import Path
r=Path(sys.argv[1]); g=lambda *a:subprocess.check_output(['git','-C',str(r),*a],encoding='utf-8').strip()
assert g('rev-parse','HEAD')=='6339f8e7c0cb95820af19e69d1e2a4f0d9632acb'
assert not g('status','--porcelain')
for p in ['contracts','backend/java','deploy','ci','tools','tests','spec/architecture']:
 assert g('rev-parse','HEAD:'+p)==g('rev-parse','0fb1f60:'+p),p
expected={'backend/go/gateway/gateway.go','backend/go/gateway/session.go','backend/go/gateway/session_test.go','backend/go/tests/revocation_fallback_test.go'}
assert set(g('diff','--name-only','0fb1f60','HEAD','--','backend/go').splitlines())==expected
for row in g('diff','--name-status','--no-renames','0fb1f60','HEAD').splitlines():
 k,p=row.split(chr(9),1)
 if p.startswith(('research/','spec/progress/evidence/')):assert k=='A',row
t=(r/'spec/tasks/review/LOOP1-ARCH-REMEDIATION-004.md').read_text(encoding='utf-8')
assert t.count(chr(167))==7 and chr(0x6402) not in t and chr(0xfffd) not in t
c=(r/'spec/progress/current.md').read_text(encoding='utf-8'); assert c.count('Current Task: LOOP1-ARCH-REMEDIATION-004')==1 and 'Current Task State: review' in c
assert len(list((r/'spec/tasks').glob('*/LOOP1-ARCH-REMEDIATION-004.md')))==1
for p,h in [('spec/architecture/frozen-architecture.md','83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'),('scalable-distributed-im-architecture.pdf','546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510')]:assert hashlib.sha256((r/p).read_bytes()).hexdigest()==h
print('PASS exact clean SHA/protected trees/product four-file scope/history additions only/UTF8 seven section references/unique004 review/current hash/historical PDF')

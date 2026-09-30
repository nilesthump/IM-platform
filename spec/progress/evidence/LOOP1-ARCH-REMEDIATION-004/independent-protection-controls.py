import sys,subprocess,json,copy,hashlib
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve();sys.path.insert(0,str(ROOT))
from ci.classify import classify
from ci.check_gate import JOBS,check
protected=['contracts','spec/architecture','scalable-distributed-im-architecture.pdf','spec/domain','spec/invariants','spec/acceptance','backend/java','backend/go/go.mod','backend/go/go.sum','spec/tasks/done','spec/progress/checkpoints']
assert not subprocess.check_output(['git','diff','--name-only','6cdd981','87c0ee2','--']+protected,cwd=ROOT)
changed=subprocess.check_output(['git','diff','--name-status','--no-renames','6cdd981','87c0ee2'],cwd=ROOT,text=True)
for row in changed.splitlines():
 kind,path=row.split('\t',1)
 if path.startswith('research/') or path.startswith('spec/progress/evidence/'):
  assert kind=='A',row
selected=classify(['tests/go/live_role_smoke.py']);assert all(selected[x] for x in ['go','deploy','architecture','source_go']) and not selected['java']
full=classify(['.github/workflows/ci.yml','ci/classify.py']);assert all(full[x] for x in JOBS)
needs={x:{'result':'success' if selected[x] else 'skipped'} for x in JOBS};needs['classify']={'result':'success','outputs':{x:str(v).lower() for x,v in selected.items()}};check(needs)
for name in ['go','deploy','architecture','source_go']:
 for result in ['failure','cancelled','skipped']:
  v=copy.deepcopy(needs);v[name]['result']=result
  try:check(v)
  except ValueError:pass
  else:raise AssertionError((name,result))
 v=copy.deepcopy(needs);del v[name]
 try:check(v)
 except ValueError:pass
 else:raise AssertionError('missing '+name)
assert hashlib.sha256((ROOT/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()=='83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'
assert hashlib.sha256((ROOT/'scalable-distributed-im-architecture.pdf').read_bytes()).hexdigest()=='546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510'
a=json.loads((ROOT/'spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/capture-byte-audit.json').read_text(encoding='utf-8'));assert len(a)==54
for r in a:
 data=(ROOT/r['blob']).read_bytes();assert hashlib.sha256(data).hexdigest()==r['stored_sha256']
 assert r['raw_match'] or r['secret_redaction_applied']
 assert b'\xef\xbf\xbd' not in data
print('PASS protected authority/contracts/history/dependencies unchanged, final all-job selection,16 selected-job Gate negatives, v1.1/PDF hashes and54 previous capture stored-byte/redaction checks')

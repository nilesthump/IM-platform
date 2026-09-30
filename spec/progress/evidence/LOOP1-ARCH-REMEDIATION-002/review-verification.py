from pathlib import Path
import json, hashlib, subprocess
R=Path.cwd()
def git(*args): return subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude',*args],cwd=R)
assert git('rev-parse','HEAD').decode().strip()=='3b04904666530687705dfcb189b34337f3e3ae41'
assert not git('status','--porcelain=v1').strip()
paths=git('diff','--name-only','5ca5089','3b04904').decode().splitlines()
for p in paths:
 assert not p.startswith(('backend/','contracts/','spec/domain/','spec/invariants/','spec/tasks/done/','spec/progress/checkpoints/','spec/progress/evidence/LOOP1-ARCH-REMEDIATION-001/')),p
 assert p not in ['spec/architecture/frozen-architecture.md','scalable-distributed-im-architecture.pdf','CLAUDE.md']
 assert not ('ADR-0001' in p or 'ADR-0002' in p),p
r=R/'research/runs/R-20260930T124045Z-bb6d4855-0e9d-45ba-8b8c-62830da56365'; n=0
for line in (r/'events.jsonl').read_text(encoding='utf-8').splitlines():
 e=json.loads(line)
 if e['event_type']=='command_finished':
  for stream in ['stdout','stderr']:
   p=r/e['data'][stream+'_blob']; b=p.read_bytes()
   assert hashlib.sha256(b).hexdigest()==e['data'][stream+'_sha256'],str(p)
   assert git('show','3b04904:'+p.relative_to(R).as_posix())==b,str(p)
   n+=1
print('PASS exact clean candidate; unchanged product/contracts/domain/invariants/historical done/evidence/PDF/canonical/ADR0001-2; implementation Recorder raw hashes and committed bytes:',n)

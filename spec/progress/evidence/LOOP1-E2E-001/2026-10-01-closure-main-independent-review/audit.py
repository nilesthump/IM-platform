from pathlib import Path
import subprocess,json,hashlib
r=Path.cwd(); base='6346f39fc6786bba3cddbde7acc91bbad42446a1'; head='cb2cf431a59e0318a1163073a1c76432135c86d9'
def git(*a):return subprocess.check_output(['git',*a])
def tree(ref):return {x.split(None,3)[3]:x.split(None,3)[2] for x in git('ls-tree','-r',ref).decode().splitlines()}
a=tree(base);b=tree(head);changed=[p for p in set(a)|set(b) if a.get(p)!=b.get(p)]
allowed={'spec/progress/current.md','spec/tasks/review/LOOP1-E2E-001.md','spec/tasks/done/LOOP1-E2E-001.md','spec/progress/checkpoints/2026-10-01-loop1-e2e-001-s1-gate-pass.md'}
assert all(p in allowed or p.startswith('spec/progress/evidence/LOOP1-E2E-001/') for p in changed)
assert all(a[p]==b[p] for p in a if p not in allowed)
assert not git('status','--porcelain').strip()
e=r/'spec/progress/evidence/LOOP1-E2E-001';arc=e/'2026-10-01-independent-review-6346'
for p in [e/'2026-10-01-closure-archive-byte-audit.json',arc/'final-manifest.json']:
 print(p.name, p.exists());
 if p.exists():print(p.read_text(encoding='utf-8')[:1800])
print('Archive JSON files',[p.name for p in arc.glob('*.json')]); print('Bounded changes',len(changed),'priorobjects',len(a),'scopePASS')
for p in [r/'spec/progress/current.md',r/'spec/progress/checkpoints/2026-10-01-loop1-e2e-001-s1-gate-pass.md',e/'2026-10-01-closure-followup.md']:
 print(str(p),p.read_text(encoding='utf-8'))
print('TASK_DELTA');print(git('diff',base,head,'--','spec/tasks/done/LOOP1-E2E-001.md').decode().split('# Independent acceptance and administrative closure')[1])
json.dump({'candidate':head,'base':base,'changed':sorted(changed),'prior_objects_unchanged_excluding_governance':len(a)-2,'result':'PASS'},open('H:/.codex/evidence/s1-closure-review/scope.json','w'),indent=2)

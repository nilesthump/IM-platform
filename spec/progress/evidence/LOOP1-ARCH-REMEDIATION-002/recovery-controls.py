from pathlib import Path
import re, subprocess, hashlib, json
R=Path(__file__).resolve().parents[4]
def text(p):return (R/p).read_text(encoding='utf-8-sig')
def recover(current,tasks):
 tid=re.search(r'^Current Task:\s*(\S+)',current,re.M).group(1)
 state=re.search(r'^Current Task State:\s*(\S+)',current,re.M).group(1)
 matches=[(q,s) for q,s in tasks if re.search(r'^task_id:\s*'+re.escape(tid)+r'\s*$',s,re.M)]
 assert len(matches)==1,'current ID must resolve exactly once'
 q,s=matches[0]
 assert q==state and re.search(r'^status:\s*'+state+r'\s*$',s,re.M),'queue/status mismatch'
 for h in ('Goal','Inputs','Dependencies','Allowed Paths','Acceptance','Forbidden','Minimality','Verification','Evidence','Handoff','Next Action'):
  assert '# '+h in s,h
 return tid,state
tasks=[(q,p.read_text(encoding='utf-8')) for q in ['backlog','ready','active','review','done'] for p in (R/'spec/tasks'/q).glob('*.md')]
cur=text('spec/progress/current.md')
tid,state=recover(cur,tasks);assert tid=='LOOP1-ARCH-REMEDIATION-002'
for kind,c,ts in [
 ('duplicate',cur,tasks+[next(v for v in tasks if 'task_id: '+tid in v[1])]),
 ('missing',cur.replace(tid,'MISSING-TASK'),tasks),
 ('wrong queue',cur.replace('Current Task State: '+state,'Current Task State: done' if state!='done' else 'Current Task State: active'),tasks)]:
 try:recover(c,ts)
 except (AssertionError,AttributeError):print('Expected rejection:',kind)
 else:raise AssertionError('mutation accepted: '+kind)
for p in ['AGENTS.md','spec/handoff/agent-context.md','spec/tasks/TASK_TEMPLATE.md']:
 s=text(p);assert 'SRC-01 through SRC-07' in s,p
 assert 'execution-boundaries.md' in s and 'independent-review.md' in s,p
for tid2 in ['LOOP1-GO-SOCIAL-001','LOOP1-GO-MSG-001','LOOP1-E2E-001']:
 s=text('spec/tasks/backlog/'+tid2+'.md')
 assert 'Frozen Architecture v1.0' not in s
 assert 'LOOP1-ARCH-REMEDIATION batch PASS' in s
 assert 'backend/go/**' not in s
 assert 'before activation' in s.lower()
assert text('CLAUDE.md').count('AGENTS.md')==2
assert hashlib.sha256((R/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()=='83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'
assert hashlib.sha256((R/'scalable-distributed-im-architecture.pdf').read_bytes()).hexdigest()=='546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510'
print('PASS: unique current recovery, three isolated memory negative controls, actual execution inputs, narrow pending paths, unchanged canonical/PDF hashes')
print('Stage-two document/recovery control only; not stage-three source/import/trigger checker effectiveness or product compliance')


changed=subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','diff','--name-only','5ca5089','--'],cwd=R,text=True).splitlines()
changed+=subprocess.check_output(['git','-c','core.excludesFile=.git/info/exclude','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines()
exact={'AGENTS.md','README.md','spec/handoff/agent-context.md','spec/tasks/TASK_TEMPLATE.md','spec/progress/current.md','spec/architecture/baseline.md','spec/architecture/decisions/ADR-0003-architecture-conflict-resolution.md'}
for p in changed:
 assert p in exact or p.startswith(('spec/tasks/backlog/','spec/tasks/ready/','spec/batches/','spec/acceptance/','spec/governance/','spec/progress/evidence/LOOP1-ARCH-REMEDIATION-002/','research/prompts/P-cee6fb38-f577-472c-9833-9b0d0f396022/','research/runs/R-20260930T124045Z-bb6d4855-0e9d-45ba-8b8c-62830da56365/')) or p=='research/prompts/stage2-implementation-delegation.txt' or re.match(r'^spec/tasks/(active|review)/LOOP1-ARCH-REMEDIATION-002.md$',p), 'unauthorized delta: '+p
print('PASS: candidate scope anchored at actual inherited 5ca5089; no product/contracts/history/canonical body delta')

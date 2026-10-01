import json, subprocess, sys, time
from pathlib import Path
r=Path('H:/.codex/worktrees/s1-e2e-review-6346');e=Path('H:/.codex/evidence/s1-e2e-review-6346');gh='C:/Program Files/GitHub CLI/gh.exe';tag=str(time.time_ns())
required={'classify','architecture','source_go','source_java','go','java','web','desktop','mobile','shared','compatibility','deploy','gate'}
def api(key,url):
 p=subprocess.run([gh,'api',url],cwd=r,capture_output=True)
 (e/(key+'-'+tag+'.json')).write_bytes(p.stdout);(e/(key+'-'+tag+'-stderr.txt')).write_bytes(p.stderr)
 if p.returncode:raise RuntimeError(key+' API failed')
 return json.loads(p.stdout)
for label,rid in [('push',36831979992),('pr',36832052224)]:
 run=api(label+'-run',f'repos/nilesthump/IM-platform/actions/runs/{rid}');jobs=api(label+'-jobs',f'repos/nilesthump/IM-platform/actions/runs/{rid}/jobs?per_page=100')['jobs']
 assert run['head_sha']=='6346f39fc6786bba3cddbde7acc91bbad42446a1'
 print(label,run['status'],run['conclusion'],[(j['name'],j['status'],j['conclusion']) for j in jobs])
 if run['status']=='completed':
  assert {j['name'] for j in jobs}==required
  assert all(j['status']=='completed' and j['conclusion']=='success' for j in jobs)
  p=subprocess.run([gh,'run','view',str(rid),'--repo','nilesthump/IM-platform','--log'],cwd=r,capture_output=True)
  (e/(label+'-logs-'+tag+'.txt')).write_bytes(p.stdout);(e/(label+'-logs-'+tag+'-stderr.txt')).write_bytes(p.stderr)
  assert p.returncode==0
  lines=p.stdout.decode(errors='replace').splitlines()
  for l in lines:
   if 'Ran 29 tests' in l or 'OK (skipped' in l or 'PASS TLS:' in l or 'PASS fixtures:' in l or 'PASS revocation:' in l or 'PASS cleanup:' in l:print(l)
  assert any('Ran 29 tests' in l for l in lines)
  assert not any('OK (skipped' in l for l in lines)
  assert any('PASS TLS:' in l for l in lines)
pr=api('pr5', 'repos/nilesthump/IM-platform/pulls/5');virtual=api('virtual-merge','repos/nilesthump/IM-platform/commits/'+pr['merge_commit_sha'])
assert pr['head']['sha']=='6346f39fc6786bba3cddbde7acc91bbad42446a1';assert pr['base']['sha']=='b442acd26777c481620a6bd917863cebfaf79b35'
parents=[p['sha'] for p in virtual['parents']];assert parents==[pr['base']['sha'],pr['head']['sha']],parents
candidate_tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=r,text=True).strip();assert virtual['commit']['tree']['sha']==candidate_tree
print('virtualmerge',virtual['sha'],'parents',parents,'tree',candidate_tree,'candidate tree identical')
(e/('hosted-binding-'+tag+'.json')).write_text(json.dumps({'head':pr['head']['sha'],'base':pr['base']['sha'],'virtual_merge':virtual['sha'],'parents':parents,'tree':candidate_tree},indent=2),encoding='utf8')

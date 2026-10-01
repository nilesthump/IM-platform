import subprocess,time,json,pathlib,hashlib,sys,os
E=pathlib.Path('H:/.codex/worktrees/msg-admin-confirmation-20261001/evidence')
PY='C:/Users/21441/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
R=pathlib.Path.cwd(); results=[]
def run(name,args):
 start=time.time(); p=subprocess.run(args,capture_output=True); elapsed=time.time()-start
 (E/(name+'.stdout')).write_bytes(p.stdout); (E/(name+'.stderr')).write_bytes(p.stderr)
 results.append(dict(name=name,argv=args,exit_code=p.returncode,elapsed_seconds=elapsed,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest()))
 (E/'command-results.json').write_text(json.dumps(results,indent=2),encoding='utf8')
 print(name,p.returncode,round(elapsed,3),flush=True)
 assert p.returncode==0,(name,p.stderr.decode(errors='replace'))
 return p.stdout
def api(name,endpoint): return json.loads(run(name,['gh','api',endpoint]))
head=run('initial-head',['git','rev-parse','HEAD']).decode().strip(); assert head=='33b1522c7f315b7aeb25fc31c05756c2bc950a9c'
assert not run('initial-status',['git','status','--porcelain=v1']).strip()
run('acceptance',['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'])
run('frozen',['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'])
run('sourceall',[PY,'-B','ci/check_architecture.py','--scope','all','--json'])
run('admin-range',['git','diff','--name-status','183be639640cf652dc7a9f18152071c617f2ceac',head])
assert not run('unchanged-product',['git','diff','183be639640cf652dc7a9f18152071c617f2ceac',head,'--','backend','contracts','spec/architecture','ci','.github']).strip()
repo='repos/nilesthump/IM-platform/'
summary={}
for label,rid,selected in [('pr',36820491515,{'classify','source_go','source_java','architecture','go','gate'}),('push',36820486384,{'classify','source_go','source_java','architecture','gate'})]:
 r=api(label+'-run',repo+'actions/runs/'+str(rid)); assert r['head_sha']==head and r['status']=='completed' and r['conclusion']=='success'
 jobs=api(label+'-jobs',repo+'actions/runs/'+str(rid)+'/jobs?per_page=100'); assert jobs['total_count']==len(jobs['jobs'])
 observed={}
 for j in jobs['jobs']:
  d=api(label+'-job-'+str(j['id']),repo+'actions/jobs/'+str(j['id']))
  assert d['run_id']==rid and d['head_sha']==head and d['status']=='completed'
  assert d['conclusion']==('success' if d['name'] in selected else 'skipped'),(d['name'],d['conclusion'])
  observed[d['name']]=dict(id=d['id'],conclusion=d['conclusion'],completed_at=d['completed_at'])
 assert set(observed)&selected==selected
 summary[label]=dict(run_id=rid,head=head,selected=sorted(selected),jobs=observed)
prnum=api('pr-run-details',repo+'actions/runs/36820491515')['pull_requests'][0]['number']
pr=api('pull-request',repo+'pulls/'+str(prnum)); assert pr['head']['sha']==head
merge=api('pr-virtual-merge',repo+'git/commits/'+pr['merge_commit_sha'])
commit=api('candidate-commit',repo+'git/commits/'+head)
assert [p['sha'] for p in merge['parents']]==[pr['base']['sha'],head]
assert merge['tree']['sha']==commit['tree']['sha']
summary['binding']=dict(pr_number=prnum,base=pr['base']['sha'],head=head,virtual_merge=merge['sha'],parents=[p['sha'] for p in merge['parents']],tree=merge['tree']['sha'])
run('pr-classification',[PY,'-B','ci/classify.py','--base',pr['base']['sha'],'--head',head])
run('push-classification',[PY,'-B','ci/classify.py','--base','183be639640cf652dc7a9f18152071c617f2ceac','--head',head])
assert not run('final-status',['git','status','--porcelain=v1']).strip()
(E/'ci-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print('INDEPENDENT SUPPLEMENT PASS',flush=True)
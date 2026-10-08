from pathlib import Path
import subprocess,json,hashlib,datetime,re,importlib.util
r=Path('H:/.codex/worktrees/g/IM-platform');p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit');gh='C:/Program Files/GitHub CLI/gh.exe'
main='b14bf1070ba26ac368488e2c6ea15a7936e2de89';candidate='d37626427b96fc7040280a0fe5a5cda8a700cb16';old='7088ecd5c905dceadae8ed2f504d54d6585ca3dc'
def git(*a):return subprocess.check_output(['git',*a],cwd=r)
assert git('rev-parse','HEAD').decode().strip()==main
assert not git('status','--porcelain').strip()
parents=git('show','-s','--format=%P',main).decode().split();assert parents==[old,candidate]
a=git('rev-parse',main+'^{tree}').decode().strip();b=git('rev-parse',candidate+'^{tree}').decode().strip();assert a==b
assert not git('diff','--name-only',candidate,main).strip()
assert not git('diff','--name-only',old,main,'--','contracts','spec/architecture/frozen-architecture.md','scalable-distributed-im-architecture.pdf').strip()
s=importlib.util.spec_from_file_location('classify',r/'ci/classify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
paths=git('diff','--no-renames','--name-only',old,main).decode().splitlines();flags=m.classify(paths);assert all(flags.values())
result={'result':'PASS','exactActualMain':main,'reviewedProductCandidate':candidate,'parents':parents,'mainTree':a,'candidateTree':b,'treeByteIdentity':True,'changedPathsFromAcceptedMain':len(paths),'canonicalContractsPDFUnchanged':True,'expectedFlags':flags,'clean':True}
(p/'main-tree-binding.json').write_text(json.dumps(result,indent=2))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); folder=p/'hosted';folder.mkdir(exist_ok=True)
raws={}
for name,endpoint in [('run','actions/runs/37738345509'),('jobs','actions/runs/37738345509/jobs?per_page=100'),('pr24','pulls/24')]:
 x=subprocess.run([gh,'api','repos/nilesthump/IM-platform/'+endpoint],capture_output=True)
 f=folder/(stamp+'-'+name+'.json');f.write_bytes(x.stdout);(folder/(stamp+'-'+name+'.stderr.txt')).write_bytes(x.stderr);assert x.returncode==0,(name,x.returncode)
 raws[name]=json.loads(x.stdout)
run=raws['run'];jobs=raws['jobs']['jobs'];pr=raws['pr24']
assert run['head_sha']==main and run['event']=='push'
assert pr['merged'] and pr['merge_commit_sha']==main and pr['head']['sha']==candidate
snapshot={'capturedUTC':stamp,'headSHA':main,'run':37738345509,'status':run['status'],'conclusion':run['conclusion'],'jobs':[{'name':j['name'],'status':j['status'],'conclusion':j['conclusion'],'id':j['id']} for j in jobs],'PRMerged':True,'originalFiles':[{'path':str(f.relative_to(p)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(folder.glob(stamp+'*'))]}
(folder/(stamp+'-snapshot.json')).write_text(json.dumps(snapshot,indent=2));print(json.dumps(snapshot,indent=2))

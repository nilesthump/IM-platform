import hashlib,json,subprocess,sys,time
from pathlib import Path
r=Path('H:/.codex/worktrees/s1-e2e-review-6346');e=Path('H:/.codex/evidence/s1-e2e-review-6346')
def git(*args):return subprocess.check_output(['git','-C',str(r),*args])
base='0d4df7aa8a39426976a44ff0c42c94befe2e0b2e';head='6346f39fc6786bba3cddbde7acc91bbad42446a1'
old={p:oid for row in git('ls-tree','-r',base).decode().splitlines() for meta,p in [row.split('\t',1)] for mode,kind,oid in [meta.split()]}
new={p:oid for row in git('ls-tree','-r',head).decode().splitlines() for meta,p in [row.split('\t',1)] for mode,kind,oid in [meta.split()]}
changed=[p for p,oid in old.items() if new.get(p)!=oid]
preserved=[p for p in old if p.startswith(('research/','spec/progress/evidence/'))]
assert not changed or set(changed)<={'.github/workflows/ci.yml','ci/classify.py','tests/ci/test_classify.py','spec/progress/current.md','spec/tasks/active/LOOP1-E2E-001.md'},changed
assert all(new.get(p)==old[p] for p in preserved)
protected=['spec/architecture/frozen-architecture.md','scalable-distributed-im-architecture.pdf']
assert all(old[p]==new[p] for p in protected)
for directory in ['contracts','deploy','backend','spec/domain','spec/invariants','spec/acceptance','spec/architecture']:
 assert all(new.get(p)==oid for p,oid in old.items() if p.startswith(directory+'/'))
snapshot={'candidate':head,'base':base,'preserved_existing_history_blob_count':len(preserved),'changed_existing_paths':changed,'canonical_sha256':hashlib.sha256((r/protected[0]).read_bytes()).hexdigest(),'historical_pdf_sha256':hashlib.sha256((r/protected[1]).read_bytes()).hexdigest(),'original_h_unknown_preservation':'Coordinator external605byteaudit required; original unknown content not opened or modified by Reviewer'}
(e/'byte-preservation.json').write_text(json.dumps(snapshot,indent=2),encoding='utf8')
print(json.dumps(snapshot))
# Independent API observations, no mutations or secret output.
gh='C:/Program Files/GitHub CLI/gh.exe'
for key,endpoint in [('push-run','repos/nilesthump/IM-platform/actions/runs/36831979992'),('push-jobs','repos/nilesthump/IM-platform/actions/runs/36831979992/jobs?per_page=100'),('pr-run','repos/nilesthump/IM-platform/actions/runs/36832052224'),('pr-jobs','repos/nilesthump/IM-platform/actions/runs/36832052224/jobs?per_page=100'),('pr5','repos/nilesthump/IM-platform/pulls/5')]:
 p=subprocess.run([gh,'api',endpoint],capture_output=True,cwd=r)
 (e/(key+'.json')).write_bytes(p.stdout);(e/(key+'-stderr.txt')).write_bytes(p.stderr)
 assert p.returncode==0,(key,p.stderr.decode(errors='replace'))
 obj=json.loads(p.stdout)
 if 'jobs' in obj:print(key,[(j['name'],j['status'],j['conclusion']) for j in obj['jobs']])
 elif key=='pr5':print(key,obj['head']['sha'],obj['base']['sha'],obj.get('merge_commit_sha'),obj.get('mergeable_state'))
 else:print(key,obj['head_sha'],obj['event'],obj['status'],obj['conclusion'])

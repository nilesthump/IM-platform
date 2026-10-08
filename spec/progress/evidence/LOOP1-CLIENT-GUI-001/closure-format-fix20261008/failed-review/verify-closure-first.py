from pathlib import Path
import hashlib,json,subprocess,sys
r=Path('H:/.codex/worktrees/g/IM-platform');p=Path('H:/.codex/gui-handoffs/20261008-gui-closure-review');head='c1633901c82ee2295c4ffc1c1e608c62a9b40759';base='b14bf1070ba26ac368488e2c6ea15a7936e2de89'
def git(*args): return subprocess.check_output(['git',*args],cwd=r)
def blob(rel,rev=head):return git('show',rev+':'+str(rel).replace('\\','/'))
def sha(b):return hashlib.sha256(b).hexdigest()
assert git('rev-parse','--show-toplevel').decode().strip().replace('\\','/').lower()==str(r).lower()
assert git('rev-parse','HEAD').decode().strip()==head
assert not git('status','--porcelain').strip()
assert git('rev-parse',head+'^').decode().strip()==base
changed=git('diff','--name-only',base,head).decode().splitlines()
allowed=['spec/progress/evidence/LOOP1-CLIENT-GUI-001/closure20261008/','spec/progress/current.md','spec/progress/checkpoints/2026-10-08-loop1-client-gui-001-product-accepted.md','spec/tasks/review/LOOP1-CLIENT-GUI-001.md','spec/tasks/done/LOOP1-CLIENT-GUI-001.md']
assert all(any(f==a or a.endswith('/') and f.startswith(a) for a in allowed) for f in changed)
closure='spec/progress/evidence/LOOP1-CLIENT-GUI-001/closure20261008/'
bind=json.loads(blob(closure+'export-bindings.json'));checked=[]
for row in bind:
 original=Path(row['original']);rel=row['export'].replace('\\','/');b=blob(rel);o=original.read_bytes()
 assert b==o and len(b)==row['bytes'] and sha(b)==row['sha256'],rel
 checked.append({'path':rel,'sha256':sha(b),'bytes':len(b)})
for private,sub in [('20261008-mobile-diag-review','mobile-review'),('20261008-mobile-diag-hosted','full-ci-review'),('20261008-gui-actual-main-audit','actual-main-review')]:
 origin=Path('H:/.codex/gui-handoffs')/private
 manifest=json.loads((origin/'public-safe-allowlist.json').read_bytes())
 for row in manifest:
  assert row.get('public_safe') is True,row
  path=row['path'];rel=closure+sub+'/'+path.replace('\\','/')
  b=blob(rel);assert b==(origin/path).read_bytes() and sha(b)==row['sha256'] and len(b)==row['bytes'],rel
 assert len(manifest)=={'mobile-review':17,'full-ci-review':16,'actual-main-review':46}[sub]
 assert blob(closure+sub+'/public-safe-allowlist.json')==(origin/'public-safe-allowlist.json').read_bytes()
assert len(bind)==82
assert blob(closure+'prior-current.md')==blob('spec/progress/current.md',base)
assert sha(blob(closure+'actual-main-review/report.md'))=='565edad34a6cabd99bcd5a29538f515fa3cebec046309cbdb3b4aaae1678adce'
assert blob('spec/architecture/frozen-architecture.md')==blob('spec/architecture/frozen-architecture.md',base)
assert not git('diff',base,head,'--','clients','backend','contracts','spec/architecture','.github','ci','tools','tests').strip()
for task in ['LOOP1-CLIENT-SQLITE-001','LOOP1-CLIENT-UI-ARCH-001','LOOP1-CLIENT-SEND-001','LOOP1-SYNC-001','LOOP1-CLIENT-NATIVE-ARCH-001','LOOP1-CLIENT-GUI-001']:
 files=list((r/'spec/tasks').glob('*/'+task+'.md'));assert len(files)==1 and files[0].parent.name=='done';assert '\nstatus: done\n' in files[0].read_text()
web=list((r/'spec/tasks').glob('*/LOOP1-WEB-001.md'));assert len(web)==1 and web[0].parent.name=='backlog'
authored=['spec/progress/current.md','spec/tasks/done/LOOP1-CLIENT-GUI-001.md','spec/progress/checkpoints/2026-10-08-loop1-client-gui-001-product-accepted.md']
x=subprocess.run(['git','diff','--check',base,head,'--',*authored],cwd=r,capture_output=True);assert x.returncode==0
(p/'authored-diff.patch').write_bytes(git('diff',base,head,'--',*authored))
out={'result':'PASS','candidate':head,'base':base,'changedPathCount':len(changed),'exportOriginalCount':len(checked),'allowlistCounts':[17,16,46],'publicOriginalExportsMatch':True,'priorCurrentMatchesBaseBlob':True,'productAuthorityContractsWorkflowDeltaZero':True,'dependenciesUniqueDone':True,'webUniqueBacklog':True,'authoredDiffCheckExit':x.returncode,'wholeRangeDiffCheckNotClaimed':True,'verifiedExports':checked}
(p/'evidence-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='verifiedExports'},indent=2))
from pathlib import Path
import subprocess,json,hashlib,importlib.util
R=Path('H:/.codex/worktrees/g/IM-platform'); P=Path('H:/.codex/gui-handoffs/20261007-auth-final-review'); E=P/'metadata-extension'
OLD='1700cf0a3d3cc89d521c52fac2720a706827195f'; HEAD='6db3a60ece381ce5120b754beec4fb9edd4d9c2f'; BASE='ffd6b63ac9396e577f0bb5c3d3ac02ee4915d597'
def git(*a): return subprocess.check_output(['git',*a],cwd=R)
assert git('rev-parse','--show-toplevel').decode().strip().replace('\\','/')==R.as_posix()
assert git('rev-parse','HEAD').decode().strip()==HEAD
assert not git('status','--porcelain')
F='spec/progress/evidence/LOOP1-CLIENT-GUI-001/android-review-resume-20261007/'
index=json.loads((P/'report-hashes.json').read_text()); original=[]
for row in index:
 rel=F+'final-review/'+row['path']; b=(R/rel).read_bytes(); old=(P/row['path']).read_bytes()
 assert b==old and len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],rel
 assert git('show',HEAD+':'+rel)==old,rel+' git bytes'
 original.append(row)
assert (R/(F+'final-review/report-hashes.json')).read_bytes()==(P/'report-hashes.json').read_bytes()
assert git('show',HEAD+':'+F+'final-review/report-hashes.json')==(P/'report-hashes.json').read_bytes()
expected={F+'final-review/'+x['path'] for x in index}|{F+'final-review/report-hashes.json',F+'latest-candidate-readiness.json',F+'latest-hosted-head-query.json','spec/progress/current.md','spec/tasks/review/LOOP1-CLIENT-GUI-001.md','spec/progress/checkpoints/2026-10-07-loop1-client-gui-001-android-auth-reviewed.md'}
paths=git('diff','--name-only',OLD,HEAD).decode().splitlines(); assert len(paths)==14 and set(paths)==expected
crlf={}
for rel in ['spec/progress/current.md','spec/tasks/review/LOOP1-CLIENT-GUI-001.md']:
 b=(R/rel).read_bytes(); assert b'\r\n' in b and b'\n' not in b.replace(b'\r\n',b''); crlf[rel]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'CRLF':True}
assert len(list((R/'spec/tasks').glob('*/LOOP1-CLIENT-GUI-001.md')))==1
current=(R/'spec/progress/current.md').read_text(); task=(R/'spec/tasks/review/LOOP1-CLIENT-GUI-001.md').read_text()
assert 'Current Task State: review' in current and 'Gate Status: OPEN' in current and 'status: review' in task
assert 'Human-reported' in current and 'machine same-account Root/defaultTLS rollback proof pending' in current
assert '仅推迟被占用导致的验证' in current and 'Human-authorized unified' in current
assert 'former owned credential slot absent' in current and '5new +98' in current
readiness=json.loads((R/(F+'latest-candidate-readiness.json')).read_text()); assert readiness['candidate']==OLD
query=json.loads((R/(F+'latest-hosted-head-query.json')).read_text()); assert query['total_count']==0
full=git('diff','--name-only',BASE,HEAD).decode().splitlines()
spec=importlib.util.spec_from_file_location('classify',R/'ci/classify.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m); selectors=m.classify(full); assert all(selectors.values())
jobs=['classify','go','java','web','desktop','mobile','shared','compatibility','deploy','architecture','source_go','source_java','gate']
subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check',OLD,HEAD,'--','spec/progress/current.md','spec/tasks/review/LOOP1-CLIENT-GUI-001.md','spec/progress/checkpoints/2026-10-07-loop1-client-gui-001-android-auth-reviewed.md'],cwd=R,check=True)
result={'result':'PASS','head':HEAD,'sourceReviewHead':OLD,'captureSource':'3a5001228d6d3eb3f3b5dcbda468f270202554fb','metadataOnly14paths':paths,'original8ReportsExactCheckoutAndGitBytes':original,'indexSHA256':hashlib.sha256((P/'report-hashes.json').read_bytes()).hexdigest(),'CRLF':crlf,'fullAuthorityBase':BASE,'fullRangePaths':len(full),'classifier14':selectors,'requiredActual13jobs':jobs,'hostedSnapshotHead':OLD,'hostedSnapshotQuery':query,'currentCandidateHostedCI':'PENDING; old 1700 query is not 6db query','wholeTask':'review/S2OPEN; occupied Windows and machine CA proof pending; no merge/done/main sync','sourceAnd103ImageApproval':'unchanged product/tests/source from independently reviewed 1700; bounded prior cf476 source + twoAuth changes; 5 new +98 previously reviewed unaffected images; expiry pointer and former-owned credential slot, not two distinct sessions','finalStatus':git('status','--porcelain').decode()}
(E/'metadata-bindings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))



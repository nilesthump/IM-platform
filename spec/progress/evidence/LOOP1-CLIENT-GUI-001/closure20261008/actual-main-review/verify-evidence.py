from pathlib import Path
import json,hashlib,subprocess
r=Path('H:/.codex/worktrees/g/IM-platform'); p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit'); e=r/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/win20261008'
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def j(f):return json.loads(f.read_text(encoding='utf-8-sig'))
m=j(e/'manifest.json')
for x in m['files']:assert h(e/x['file'])==x['sha256'],x['file']
raw=[x for x in m['files'] if x['kind']=='approved raw screenshot'];assert len(raw)==43
assert not any('private-inspection' in x['file'] or 'baseline-private' in x['file'] for x in m['files'])
d=j(e/'convergence-derived.json')
for name,sha in d['source_hashes'].items():assert h(e/'receipts'/name)==sha
s=j(e/'receipts/sqlite-sending.json');f=j(e/'receipts/sqlite-failed.json');t=j(e/'receipts/sqlite-retried.json');u=j(e/'receipts/sqlite-reconnected.json')
rid=d['same_retry_request_id']
find=lambda v: next(row for row in v['rows'] if row['request_id']==rid)
assert find(s)['state']=='SENDING' and find(f)['state']=='FAILED' and find(t)['state']=='SENT'
assert t['rows']==u['rows'] and t['contiguous_seq']==u['contiguous_seq']==4
flatten=lambda v: [item for row in v['rows'] for item in (row['value'] if 'value' in row else [row])]
g=flatten(j(e/'receipts/postgres-after-retry.json'));z=flatten(j(e/'receipts/postgres-reconnected.json'))
assert g==z and len(g)==2 and len({row['request_id'] for row in g})==2
for row in g:
 local=next(v for v in t['rows'] if v['request_id']==row['request_id'])
 assert row['outbox_count']==1 and row['server_message_id']==local['server_message_id'] and row['seq']==local['server_seq']
assert j(e/'receipts/actual-root-rollback.json')['rollback_pass']
assert j(e/'receipts/actual-root-fresh-after-rollback.json')['complete_other_root_set_unchanged']
assert j(e/'receipts/cleanup.json')['cleanup_pass']
coverage=j(r/'spec/progress/evidence/LOOP1-CLIENT-GUI-001/android-review-resume-20261007/final-review/coverage.json')
for x in coverage['prior98Reused']:assert h(Path(x['path']))==x['sha256']
assert len(coverage['prior98Reused'])==98
for start in ['1700cf0a3d3cc89d521c52fac2720a706827195f','cc13ba1284e3c11a44203377b3ac7adb3d0e25d6']:
 out=subprocess.check_output(['git','diff','--name-only',start,'HEAD','--','clients/desktop','clients/mobile/app/src/main','clients/mobile/app/build.gradle.kts','clients/shared'],cwd=r,text=True)
 assert not out.strip(),(start,out)
result={'reviewedHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'windowsManifestFilesVerified':len(m['files']),'windowsApprovedRaw43':len(raw),'priorAndroidReferences98Verified':len(coverage['prior98Reused']),'sameRetryRIDAndServerIdentity':True,'reconnectNoDuplicate':True,'singleOutboxEach':True,'completeOtherRootRollbackAndCleanup':True,'clientProductSourceUnchanged':True,'result':'PASS'}
(p/'evidence-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


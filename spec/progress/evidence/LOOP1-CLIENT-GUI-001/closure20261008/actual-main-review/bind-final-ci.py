from pathlib import Path
import json,hashlib,re,base64,subprocess
p=Path('H:/.codex/gui-handoffs/20261008-gui-actual-main-audit');r=Path('H:/.codex/worktrees/g/IM-platform');h=p/'hosted'
snap=sorted(h.glob('*-snapshot.json'))[-1];snapshot=json.loads(snap.read_text());stamp=snapshot['capturedUTC'];run=json.loads((h/(stamp+'-run.json')).read_bytes());jobs=json.loads((h/(stamp+'-jobs.json')).read_bytes())['jobs'];pr=json.loads((h/(stamp+'-pr24.json')).read_bytes())
assert run['id']==37738345509 and run['head_sha']=='b14bf1070ba26ac368488e2c6ea15a7936e2de89' and run['event']=='push'
assert run['status']=='completed' and run['conclusion']=='success','Exact-main CI pending or failing'
expected={'classify','architecture','source_go','source_java','go','java','web','desktop (windows-latest)','desktop (ubuntu-latest)','mobile','shared','compatibility','deploy','gate'}
assert len(jobs)==14 and {j['name'] for j in jobs}==expected
allow={'desktop (windows-latest)':{'Native Tauri prerequisites and approved Rust compiler','Actual TypeScript Repository on SQLx SQLite'},'desktop (ubuntu-latest)':{'Approved Windows GUI assembly and auth controls'}};skips=[]
for j in jobs:
 assert j['status']=='completed' and j['conclusion']=='success',(j['name'],j['status'],j['conclusion'])
 for s in j['steps']:
  assert s['status']=='completed'
  if s['conclusion']=='skipped':assert s['name'] in allow.get(j['name'],set());skips.append({'job':j['name'],'step':s['name'],'reason':'existing mutually exclusive runner.os condition'})
  else:assert s['conclusion']=='success',(j['name'],s)
flags=json.loads((h/'classify-main-derived.json').read_text())['flags'];assert len(flags)==14 and all(flags.values())
text=(h/'mobile-main-safe-excerpt.txt').read_text();assert 'assertions=46' in text and 'sdkInt=34' in text and 'engine=actual anonymous/registration UI and Android Keystore/SharedPreferences' in text and 'INSTRUMENTATION_CODE: -1' in text
workflow=(r/'.github/workflows/ci.yml').read_text();assert "if: runner.os == 'Windows'" in workflow or "runner.os == 'Windows'" in workflow;assert 'old_client' in workflow and 'plugin' in workflow and 'migration' in workflow
raw=(h/'classify-main.log').read_bytes();assert not re.search(rb'(?:ghp_|github_pat_|-----BEGIN .*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}\.)',raw)
archive={'kind':'byte-exact original log archive','source':'classify-main.log','sourceSHA256':hashlib.sha256(raw).hexdigest(),'sourceBytes':len(raw),'base64':base64.b64encode(raw).decode()};(h/'classify-main-original.archive.json').write_text(json.dumps(archive,indent=2))
assert base64.b64decode(archive['base64'])==raw
result={'result':'PASS','actualMainSHA':run['head_sha'],'exactPushRun':run['id'],'event':'push','expectedBaseSHA':'7088ecd5c905dceadae8ed2f504d54d6585ca3dc','fullLogicalGroups':13,'fullActualInstances':14,'allRequiredJobsAndStepsSuccess':True,'expectedOSConditionalSkips':skips,'all14FlagsTrue':flags,'MobileActualAPI34Anonymous46':True,'MobileWholeLogPrivateSHA256':hashlib.sha256((h/'mobile-main-PRIVATE.log').read_bytes()).hexdigest(),'originalMetadataSnapshot':stamp,'treeEqualReviewedCandidate':json.loads((p/'main-tree-binding.json').read_text())['treeByteIdentity'],'cleanHEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'cleanStatus':not subprocess.check_output(['git','status','--porcelain'],cwd=r,text=True).strip(),'mainWorkspaceSynchronization':'NOT_PERFORMED_BY_REVIEWER','TaskState':'review','S2Gate':'OPEN'}
(p/'hosted-binding-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

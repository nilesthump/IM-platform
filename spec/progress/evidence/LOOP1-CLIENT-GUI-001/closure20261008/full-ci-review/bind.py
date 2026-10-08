from pathlib import Path
import json,re,hashlib
p=Path('H:/.codex/gui-handoffs/20261008-mobile-diag-hosted');sha='d37626427b96fc7040280a0fe5a5cda8a700cb16';base='7088ecd5c905dceadae8ed2f504d54d6585ca3dc'
pr=json.loads((p/'pr-1791441125.stdout.txt').read_bytes());push=json.loads((p/'push-1791441127.stdout.txt').read_bytes());info=json.loads((p/'pr24-final.stdout.txt').read_bytes())
assert info['headRefOid']==sha and info['baseRefOid']==base and info['isDraft'] and info['state']=='OPEN'
expected={'classify','architecture','source_go','source_java','go','java','web','desktop (windows-latest)','desktop (ubuntu-latest)','mobile','shared','compatibility','deploy','gate'}
assert pr['headSha']==push['headSha']==sha;assert pr['databaseId']==37737318185 and push['databaseId']==37737314493
assert pr['status']==push['status']=='completed' and pr['conclusion']==push['conclusion']=='success'
assert len(pr['jobs'])==14 and {j['name'] for j in pr['jobs']}==expected
allow={'desktop (windows-latest)':{'Native Tauri prerequisites and approved Rust compiler','Actual TypeScript Repository on SQLx SQLite'},'desktop (ubuntu-latest)':{'Approved Windows GUI assembly and auth controls'}}
step_skips=[]
for j in pr['jobs']:
 assert j['status']=='completed' and j['conclusion']=='success'
 for s in j['steps']:
  assert s['status']=='completed'
  if s['conclusion']=='skipped':assert s['name'] in allow.get(j['name'],set());step_skips.append({'job':j['name'],'step':s['name'],'reason':'existing mutually exclusive runner.os condition'})
  else:assert s['conclusion']=='success',(j['name'],s)
selected={'classify','architecture','source_go','source_java','mobile','gate'};inactive={'go','deploy','java','shared','compatibility','web','desktop'}
assert len(push['jobs'])==13 and {j['name'] for j in push['jobs']}==selected|inactive
assert all(j['conclusion']==('success' if j['name'] in selected else 'skipped') for j in push['jobs'])
def flags(file):
 s=(p/file).read_text();lines=[x for x in s.splitlines() if '\tClassify full diff, including deletions\t' in x]
 f={}
 for l in lines:
  m=re.search(r'"([a-z_]+)": (true|false)',l)
  if m:f[m[1]]=m[2]=='true'
 return f,s
pf,ps=flags('classify-pr-final.stdout.txt');sf,ss=flags('classify-push.stdout.txt')
assert len(pf)==len(sf)==14 and all(pf.values());assert {k for k,v in sf.items() if v}=={'mobile','architecture','source_go','source_java'}
assert ('BASE_SHA: '+base) in ps and ('HEAD_SHA: '+sha) in ps;assert 'BASE_SHA: 6f21e00f8731020e6344545e1383854a5354b6e9' in ss and ('HEAD_SHA: '+sha) in ss
for file in ['mobile-pr-safe-excerpt.txt','mobile-push-safe-excerpt.txt']:
 s=(p/file).read_text();assert 'assertions=46' in s and 'sdkInt=34' in s and 'engine=actual anonymous/registration UI and Android Keystore/SharedPreferences' in s and 'INSTRUMENTATION_CODE: -1' in s
 assert 'result=FAIL' not in s
result={'result':'PASS','exactHeadSHA':sha,'PRBaseSHA':base,'fullPRRun':37737318185,'pushRun':37737314493,'fullActualInstances':14,'fullLogicalGroups':13,'fullJobsAllSuccess':True,'fullSelectionFlags':pf,'pushSelectionFlags':sf,'pushSelectedSuccess':6,'pushClassifierFalseInactive':7,'expectedOSConditionalStepSkips':step_skips,'MobileActualAPI34Anonymous46BothRuns':True,'wholeMobileLogPrivateOnly':True,'TaskState':'review','S2Gate':'OPEN','mainSynchronization':'pending'}
(p/'binding-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

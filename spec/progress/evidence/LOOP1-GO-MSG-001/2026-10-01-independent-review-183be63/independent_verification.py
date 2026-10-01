import os,sys,subprocess,time,json
from pathlib import Path
ROOT=Path.cwd(); E=ROOT.parent/'evidence'; RE=E/'research'; R='R-MSG-REREVIEW-20261001'
PG='loop1-msg-rereview-pg-20261001'; NATS='loop1-msg-rereview-nats-20261001'
os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55642',PGUSER='postgres',PGDATABASE='msg_rereview',NATS_URL='nats://127.0.0.1:42642',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
os.environ['PATH']=r'H:\go\bin;C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell;'+os.environ['PATH']
results=[]
def rec(argv,allow=False):
 st=time.monotonic(); cmd=[sys.executable,'-B','tools/research/recorder.py','run-command','--research-root',str(RE),'--run-id',R,'--']+argv
 p=subprocess.run(cmd,text=True,capture_output=True,encoding='utf-8',errors='replace'); ix=len(results); (E/f'{sys.argv[1]}-{ix}-stdout.txt').write_text(p.stdout,encoding='utf-8'); (E/f'{sys.argv[1]}-{ix}-stderr.txt').write_text(p.stderr,encoding='utf-8'); results.append(dict(argv=argv,exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-st,3),go_skips=p.stdout.count('--- SKIP:'))); print(json.dumps(results[-1]),flush=True)
 if p.returncode and not allow: raise RuntimeError('failed command, see staged raw output')
 return p
try:
 phase=sys.argv[1]
 if phase=='baseline':
  rec([sys.executable,'-B','contracts/websocket/verify.py']); rec([sys.executable,'-B','ci/check_architecture.py','--scope','all','--json']); rec(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'])
  rec(['docker','run','-d','--name',PG,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner='+R,'-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=msg_rereview','-p','127.0.0.1:55642:5432','postgres:16']); rec(['docker','run','-d','--name',NATS,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner='+R,'-p','127.0.0.1:42642:4222','nats:2.10'])
  for _ in range(60):
   p=rec(['docker','exec',PG,'pg_isready','-U','postgres','-d','msg_rereview'],True)
   if p.returncode==0: break
   time.sleep(.5)
  else: raise RuntimeError('PG not ready')
  rec(['docker','cp',str(ROOT/'contracts/database/migrations/0001_initial.up.sql'),PG+':/tmp/review0001.sql']); rec(['docker','exec',PG,'psql','-U','postgres','-d','msg_rereview','-v','ON_ERROR_STOP=1','-f','/tmp/review0001.sql'])
  for ex in [[],['-race']]:
   p=rec(['go','-C','backend/go','test']+ex+['-count=1','-v','./...'])
   if '--- SKIP:' in p.stdout: raise RuntimeError('Go integration skipped')
 elif phase=='probes':
  for pkg,ov,pattern in [('tests','reviewer-live-overlay.go.json','TestReviewerLiveConflictRetryMustNotEraseOrigin|TestLiveConflictingRetryDelayedOrigin'),('gateway','reviewer-message-overlay.go.json','TestReviewer'),('core','reviewer-sync-overlay.json','TestReviewerRequiredAfterSeqNegativesAndZero|TestHistoryRequiresPresentIntegerAfterSeq')]:
   for race in [[],['-race']]:
    p=rec(['go','-C','backend/go','test','-overlay',str(E/ov)]+race+['-count=1','-v','./'+pkg,'-run',pattern]); assert '--- SKIP:' not in p.stdout
 elif phase=='checks':
  for argv in [['go','-C','backend/go','build','./...'],['go','-C','backend/go','vet','./...'],[sys.executable,'-B','-m','unittest','discover','-s','tests/architecture','-v'],[sys.executable,'-B','-m','unittest','discover','-s','tests/ci','-v'],['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'],[sys.executable,'-B','tools/research/recorder.py','validate-repository','--allow-partial']]: rec(argv)
  files=[str(p) for p in (ROOT/'backend/go').rglob('*.go')]; p=rec(['gofmt','-l']+files); assert not p.stdout.strip()
 elif phase=='hosted':
  for run in ['36819292528','36819288126']:
   p=rec(['gh','run','view',run,'--json','headSha,headBranch,status,conclusion,event,url,jobs']); obj=json.loads(p.stdout); (E/('hosted-'+run+'.json')).write_text(p.stdout,encoding='utf-8'); assert obj['headSha']=='183be639640cf652dc7a9f18152071c617f2ceac' and obj['conclusion']=='success'
   selected={'classify','source_java','architecture','go','source_go','gate'}
   assert all(j['conclusion']=='success' for j in obj['jobs'] if j['name'] in selected)
   assert {j['name'] for j in obj['jobs'] if j['conclusion']=='success'}==selected
   for job in obj['jobs']:
    if job['name'] in {'classify','go','architecture','source_go','source_java','gate'}:
     q=rec(['gh','run','view',run,'--job',str(job['databaseId']),'--log']); (E/('hosted-'+run+'-'+job['name']+'.log')).write_text(q.stdout,encoding='utf-8')
  p=rec(['gh','pr','view','4','--json','headRefOid,baseRefOid,url,state']); (E/'pr4.json').write_text(p.stdout,encoding='utf-8'); assert json.loads(p.stdout)['headRefOid']=='183be639640cf652dc7a9f18152071c617f2ceac'
 elif phase=='audit':
  rec([sys.executable,'-B',str(E/'raw_audit.py')])
  rec(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain=v1']); rec(['git','rev-parse','HEAD']); rec(['git','diff','--name-status','b442acd..HEAD']); rec(['git','diff','84b7a63..HEAD','--','backend/go'])
  for rid in ['R-MSG-FIX-20261001','R-MSG-IMPLEMENTATION-20261001']:
   rec([sys.executable,'-B','tools/research/recorder.py','validate-run','--run-id',rid])
  rec([sys.executable,'-B','tools/research/recorder.py','validate-repository'],True)
  rec(['go','-C','backend/go','test','-count=1','-v','./tests','-run','TestLiveConflictingRetryDelayedOrigin']); rec(['go','-C','backend/go','test','-race','-count=1','-v','./tests','-run','TestLiveConflictingRetryDelayedOrigin'])
 elif phase=='binding':
  p=rec(['gh','api','repos/nilesthump/IM-platform/git/commits/74bef3082293d80d416da679a225ab4967a90c99']); merge=json.loads(p.stdout); (E/'pr-virtual-merge.json').write_text(p.stdout,encoding='utf-8')
  p=rec(['gh','api','repos/nilesthump/IM-platform/git/commits/183be639640cf652dc7a9f18152071c617f2ceac']); head=json.loads(p.stdout); (E/'remote-candidate-commit.json').write_text(p.stdout,encoding='utf-8')
  p=rec(['git','rev-parse','HEAD^{tree}']); local=p.stdout.strip(); assert merge['tree']['sha']==head['tree']['sha']==local
  assert [p['sha'] for p in merge['parents']]==['b442acd26777c481620a6bd917863cebfaf79b35','183be639640cf652dc7a9f18152071c617f2ceac']
  (E/'pr-tree-binding.json').write_text(json.dumps(dict(virtual_merge=merge['sha'],parents=[p['sha'] for p in merge['parents']],candidate=head['sha'],local_candidate='183be639640cf652dc7a9f18152071c617f2ceac',equal_tree=local,result='PASS'),indent=2),encoding='utf-8')
 elif phase=='cleanup':
  for name in [PG,NATS]:
   p=rec(['docker','inspect',name]); obj=json.loads(p.stdout)[0]; assert obj['Config']['Labels']['im.owner']==R; rec(['docker','rm','-fv',name])
finally:
 (E/f'{sys.argv[1]}-commands.json').write_text(json.dumps(dict(owner=R,phase=sys.argv[1],enable=dict(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55642',PGUSER='postgres',PGDATABASE='msg_rereview',NATS_URL='nats://127.0.0.1:42642'),commands=results),indent=2),encoding='utf-8')

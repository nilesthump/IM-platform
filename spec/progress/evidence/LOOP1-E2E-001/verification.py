import os,sys,subprocess,time,json,hashlib
from pathlib import Path
ROOT=Path.cwd(); E=ROOT/'spec/progress/evidence/LOOP1-E2E-001'; R='R-E2E-IMPLEMENTATION-20261001'
PG='loop1-e2e-impl-pg-20261001'; NATS='loop1-e2e-impl-nats-20261001'
os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55651',PGUSER='postgres',PGDATABASE='s1_e2e_regression',NATS_URL='nats://127.0.0.1:42651',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
os.environ['PATH']=str(Path(sys.executable).parent)+os.pathsep+r'H:\go\bin;C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell;'+os.environ['PATH']
results=[]
attempt=sys.argv[1]+"-"+str(time.time_ns())
def rec(argv,allow=False):
 st=time.monotonic(); p=subprocess.run([sys.executable,'-B','tools/research/recorder.py','run-command','--run-id',R,'--']+argv,text=True,capture_output=True,encoding='utf8',errors='replace'); item=dict(argv=argv,exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-st,3),go_runtime_skips=p.stdout.count('--- SKIP:'));results.append(item); print(json.dumps(item),flush=True)
 (E/(attempt+'-'+str(len(results))+'-stdout.txt')).write_text(p.stdout,encoding='utf8');(E/(attempt+'-'+str(len(results))+'-stderr.txt')).write_text(p.stderr,encoding='utf8')
 if p.returncode and not allow:raise RuntimeError('command failed: see immutable raw output')
 return p
try:
 phase=sys.argv[1]
 if phase=='startup':
  for p in ['spec/handoff/agent-context.md','spec/progress/current.md','spec/tasks/active/LOOP1-E2E-001.md','spec/architecture/README.md','spec/architecture/baseline.md','spec/governance/minimality.md','spec/governance/execution-boundaries.md','spec/governance/independent-review.md','research/README.md']:
   rec([sys.executable,'-B','-c',"from pathlib import Path;import json;print(json.dumps(Path("+repr(p)+").read_text(encoding='utf8'),ensure_ascii=True))"])
  matches=list((ROOT/'spec/tasks').glob('*/LOOP1-E2E-001.md'));assert len(matches)==1 and matches[0].parent.name=='active'
  assert hashlib.sha256((ROOT/'spec/architecture/frozen-architecture.md').read_bytes()).hexdigest()=='83d124bba4b9c605ae29b637e1ea6f8aa55ec4fb7cc6f631f7c069c6f1f77c2e'
  assert hashlib.sha256((ROOT/'scalable-distributed-im-architecture.pdf').read_bytes()).hexdigest()=='546915f639f30cd294f11390da3ade2ce6a85b620bf55727c2a90ca6017d7510'
  rec(['git','-c','core.excludesFile=.git/info/exclude','status','--short']);rec(['git','diff']);rec(['git','log','-5','--oneline'])
  rec([sys.executable,'-B','tools/research/recorder.py','record-event','--run-id',R,'--event-type','instrumentation_warning','--data-json',json.dumps({'reason':'Preparation and isolated-worktree creation occurred before run start; trace incomplete. Prior read-only startup command failures, quoting, wrong guessed paths and truncated/GBK output were disclosed; immutable inputs hash-confirmed and UTF8 supplemented. No product writes or services before baseline.','pre_recorder_trace_complete':False})])
 if phase in ('baseline','checks'):
  for args in [[sys.executable,'-B','contracts/websocket/verify.py'],[sys.executable,'-B','ci/check_architecture.py','--scope','all','--json'],['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'],['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1']]:rec(args)
 if phase=='baseline':
  rec(['docker','run','-d','--name',PG,'--label','im.task=LOOP1-E2E-001','--label','im.owner='+R,'-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=s1_e2e_regression','-p','127.0.0.1:55651:5432','postgres:16'])
  rec(['docker','run','-d','--name',NATS,'--label','im.task=LOOP1-E2E-001','--label','im.owner='+R,'-p','127.0.0.1:42651:4222','nats:2.10'])
  for _ in range(60):
   p=rec(['docker','exec',PG,'pg_isready','-U','postgres','-d','s1_e2e_regression'],True)
   if p.returncode==0:break
   time.sleep(.5)
  else:raise RuntimeError('PG unavailable')
  rec([sys.executable,'-B','-c',"from pathlib import Path;import subprocess;subprocess.run(['docker','exec','-i','"+PG+"','psql','-U','postgres','-d','s1_e2e_regression','-v','ON_ERROR_STOP=1'],input=Path('contracts/database/migrations/0001_initial.up.sql').read_bytes(),check=True)"])
 if phase in ('baseline','final'):
  for extra in [[],['-race']]:
   p=rec(['go','-C','backend/go','test']+extra+['-count=1','-v','./...']);assert '--- SKIP:' not in p.stdout,'Live runtime skipped'
 if phase=='checks':
  for argv in [['go','-C','backend/go','build','./...'],['go','-C','backend/go','vet','./...'],['pwsh','-NoProfile','-File','contracts/http/verify-auth-user-friend.ps1'],[sys.executable,'-B','-m','unittest','discover','-s','tests/architecture','-v'],[sys.executable,'-B','-m','unittest','discover','-s','tests/ci','-v']]:rec(argv)
  p=rec(['gofmt','-l']+[str(p) for p in (ROOT/'backend/go').rglob('*.go')]);assert not p.stdout.strip()
 if phase=='e2e':rec([sys.executable,'-B','tests/e2e/go_tls_messaging.py'])
 if phase=='cleanup':
  for name in [PG,NATS]:
   p=rec(['docker','inspect',name]);obj=json.loads(p.stdout)[0];assert obj['Config']['Labels']['im.owner']==R
   for mount in obj.get('Mounts',[]):
    if mount['Type']=='volume':
     volume=mount['Name'];q=rec(['docker','volume','inspect',volume]);assert json.loads(q.stdout)[0]['Name']==volume
     q=rec(['docker','ps','-aq','--no-trunc','--filter','volume='+volume]);assert set(q.stdout.split())=={obj['Id']},'volume shared with unknown container'
   rec(['docker','rm','-fv',name])
finally:
 (E/(attempt+'-commands.json')).write_text(json.dumps(dict(owner=R,phase=sys.argv[1],enable={k:os.environ[k] for k in ('DB_TEST_ENABLE','PGHOST','PGPORT','PGUSER','PGDATABASE','NATS_URL')},containers=[PG,NATS],commands=results),indent=2)+'\n',encoding='utf8')

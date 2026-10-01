import os,sys,subprocess,time,json
from pathlib import Path
ROOT=Path.cwd();E=ROOT/'spec/progress/evidence/LOOP1-GO-MSG-001';R='R-MSG-FIX-20261001'
PG='loop1-msg-fix-pg-20261001';NATS='loop1-msg-fix-nats-20261001'
os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55634',PGUSER='postgres',PGDATABASE='msg_fix_test',NATS_URL='nats://127.0.0.1:42634',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
os.environ['PATH']=str(Path(sys.executable).parent)+os.pathsep+r'H:\go\bin;C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\node;'+os.environ['PATH']
results=[]
def rec(argv,expected=0):
 start=time.monotonic();p=subprocess.run([sys.executable,'-B','tools/research/recorder.py','run-command','--run-id',R,'--']+argv,text=True,capture_output=True,encoding='utf-8',errors='replace');results.append(dict(argv=argv,exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-start,3),go_runtime_skips=p.stdout.count('--- SKIP:')));print(p.stdout);print(p.stderr,file=sys.stderr)
 if expected is not None and p.returncode!=expected:raise SystemExit(p.returncode or 1)
 return p
try:
 phase=sys.argv[1]
 if phase=='setup':
  rec(['docker','run','-d','--name',PG,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner=message_fix','-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=msg_fix_test','-p','127.0.0.1:55634:5432','postgres:16'])
  rec(['docker','run','-d','--name',NATS,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner=message_fix','-p','127.0.0.1:42634:4222','nats:2.10'])
  rec([sys.executable,'-B','-c',"import subprocess,time; name='"+PG+"'; ready=False\nfor _ in range(60):\n if subprocess.run(['docker','exec',name,'pg_isready','-U','postgres','-d','msg_fix_test'],capture_output=True).returncode==0: ready=True;break\n time.sleep(.5)\nassert ready,'PG readiness failed'"])
  rec([sys.executable,'-B','-c',"import subprocess,pathlib;subprocess.run(['docker','exec','-i','"+PG+"','psql','-U','postgres','-d','msg_fix_test','-v','ON_ERROR_STOP=1'],input=pathlib.Path('contracts/database/migrations/0001_initial.up.sql').read_bytes(),check=True)"])
 if phase in ('setup','final'):
  for extra in ([],['-race']):
   p=rec(['go','-C','backend/go','test']+extra+['-count=1','-v','./...'])
   if '--- SKIP:' in p.stdout:raise RuntimeError('live suite runtime skip')
 if phase=='setup':
  rec([sys.executable,'-B','contracts/websocket/verify.py']);rec([sys.executable,'-B','ci/check_architecture.py','--scope','all','--json']);rec(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'])
 if phase=='checks':
  for args in (['go','-C','backend/go','build','./...'],['go','-C','backend/go','vet','./...'],[sys.executable,'-B','contracts/websocket/verify.py'],[sys.executable,'-B','ci/check_architecture.py','--scope','all','--json'],[sys.executable,'-B','-m','unittest','discover','-s','tests/architecture','-v'],[sys.executable,'-B','-m','unittest','discover','-s','tests/ci','-v'],['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'],['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development']):rec(args)
 if phase in ('red','green'):
  for pkg,pattern in (('./gateway','TestRejectedRetryPreservesCommittedOrigin'),('./core','TestHistoryRequiresPresentIntegerAfterSeq'),('./tests','TestLiveConflictingRetryDelayedOrigin')):
   p=rec(['go','-C','backend/go','test','-count=1','-v',pkg,'-run',pattern],expected=1 if phase=='red' else 0)
   if '--- SKIP:' in p.stdout:raise RuntimeError('targeted test skip')
 if phase=='cleanup':
  for name in (PG,NATS):
   p=rec(['docker','inspect','--format','{{index .Config.Labels "im.owner"}}',name]);assert p.stdout.strip()=='message_fix'
   rec(['docker','rm','-fv',name])
finally:
 (E/('2026-10-01-fix-'+sys.argv[1]+'-commands.json')).write_text(json.dumps(dict(owner=R,phase=sys.argv[1],enable={k:os.environ[k] for k in ('DB_TEST_ENABLE','PGHOST','PGPORT','PGUSER','PGDATABASE','NATS_URL')},containers=[PG,NATS],commands=results),indent=2)+'\n',encoding='utf-8')

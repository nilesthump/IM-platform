import os,sys,subprocess,time,json
from pathlib import Path
ROOT=Path.cwd(); E=ROOT.parent/'evidence'; RE=E/'research'; R='R-MSG-INDEPENDENT-REVIEW-20261001'
PG='loop1-msg-review-pg-20261001'; NATS='loop1-msg-review-nats-20261001'
os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55641',PGUSER='postgres',PGDATABASE='msg_review',NATS_URL='nats://127.0.0.1:42641',PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1')
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
  rec(['docker','run','-d','--name',PG,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner='+R,'-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=msg_review','-p','127.0.0.1:55641:5432','postgres:16']); rec(['docker','run','-d','--name',NATS,'--label','im.task=LOOP1-GO-MSG-001','--label','im.owner='+R,'-p','127.0.0.1:42641:4222','nats:2.10'])
  for _ in range(60):
   p=rec(['docker','exec',PG,'pg_isready','-U','postgres','-d','msg_review'],True)
   if p.returncode==0: break
   time.sleep(.5)
  else: raise RuntimeError('PG not ready')
  rec(['docker','cp',str(ROOT/'contracts/database/migrations/0001_initial.up.sql'),PG+':/tmp/review0001.sql']); rec(['docker','exec',PG,'psql','-U','postgres','-d','msg_review','-v','ON_ERROR_STOP=1','-f','/tmp/review0001.sql'])
  for ex in [[],['-race']]:
   p=rec(['go','-C','backend/go','test']+ex+['-count=1','-v','./...'])
   if '--- SKIP:' in p.stdout: raise RuntimeError('Go integration skipped')
 elif phase=='checks':
  for argv in [['go','-C','backend/go','build','./...'],['go','-C','backend/go','vet','./...'],[sys.executable,'-B','-m','unittest','discover','-s','tests/architecture','-v'],[sys.executable,'-B','-m','unittest','discover','-s','tests/ci','-v'],['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'],[sys.executable,'-B','tools/research/recorder.py','validate-repository']]: rec(argv)
  files=[str(p) for p in (ROOT/'backend/go').rglob('*.go')]; p=rec(['gofmt','-l']+files); assert not p.stdout.strip()
 elif phase=='cleanup':
  for name in [PG,NATS]:
   p=rec(['docker','inspect',name]); obj=json.loads(p.stdout)[0]; assert obj['Config']['Labels']['im.owner']==R; rec(['docker','rm','-fv',name])
finally:
 (E/f'{sys.argv[1]}-commands.json').write_text(json.dumps(dict(owner=R,phase=sys.argv[1],enable=dict(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55641',PGUSER='postgres',PGDATABASE='msg_review',NATS_URL='nats://127.0.0.1:42641'),commands=results),indent=2),encoding='utf-8')

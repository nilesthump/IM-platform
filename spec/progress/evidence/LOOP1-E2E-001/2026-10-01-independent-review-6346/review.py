import json, os, subprocess, sys, time, hashlib
from pathlib import Path
REPO=Path('H:/.codex/worktrees/s1-e2e-review-6346')
E=Path('H:/.codex/evidence/s1-e2e-review-6346')
PY=sys.executable
REC=REPO/'tools/research/recorder.py'
COMMON=['--repo',str(REPO),'--research-root',str(E/'research'),'--run-id','R-E2E-REVIEW-6346']
ledger=[]
def run(argv, required=True):
 t=time.monotonic(); n=len(ledger)+1
 p=subprocess.run([PY,'-B',str(REC),'run-command']+COMMON+['--']+list(map(str,argv)),cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (E/f'command-{n:02}-stdout.txt').write_bytes(p.stdout); (E/f'command-{n:02}-stderr.txt').write_bytes(p.stderr)
 item={'argv':list(map(str,argv)),'exit_code':p.returncode,'elapsed_seconds':round(time.monotonic()-t,3),'stdout':f'command-{n:02}-stdout.txt','stderr':f'command-{n:02}-stderr.txt','go_runtime_skips':p.stdout.count(b'--- SKIP:')}
 ledger.append(item); (E/'commands.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
 print(f'{n}: exit={p.returncode} duration={item["elapsed_seconds"]} skips={item["go_runtime_skips"]} {argv[0]} {argv[1:]}',flush=True)
 if required and p.returncode: raise RuntimeError(f'command {n} failed')
 return p

def event(kind,data):
 p=subprocess.run([PY,'-B',str(REC),'record-event']+COMMON+['--event-type',kind,'--data-json',json.dumps(data)],cwd=REPO,capture_output=True)
 if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))

event('instrumentation_warning',{'decision':'Expose initial register-prompt exit2: --run-id cross-link referenced a run not yet created. Prompt bytes persisted; subsequent start-run succeeded and associated metadata now agree. No evidence edited. Earlier read-only preparation and formal startup reads remain incomplete pre-Recorder.'})
event('review_started',{'candidate':'6346f39fc6786bba3cddbde7acc91bbad42446a1','base':'b442acd26777c481620a6bd917863cebfaf79b35','independence':'fresh /root/s1_e2e_review neither implemented nor fixed','method':'clean detached exact committed Git worktree; external evidence only'})
run(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain=v1','--untracked-files=all'])
run(['git','rev-parse','HEAD'])
run(['git','diff','--name-status','0d4df7a..HEAD'])
run([PY,'-B','contracts/websocket/verify.py'])
run([PY,'-B','ci/check_architecture.py','--scope','all','--json'])
run(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Acceptance'])
run(['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'])
run([PY,'-B','-m','unittest','discover','-s','tests/architecture','-v'])
run([PY,'-B','-m','unittest','discover','-s','tests/ci','-v'])
run(['pwsh','-NoProfile','-File','contracts/http/verify-auth-user-friend.ps1'])
run(['go','-C','backend/go','build','./...'])
run(['go','-C','backend/go','vet','./...'])
run(['gofmt','-l','backend/go'])
run([PY,'-B','tests/e2e/go_tls_messaging.py'])
# Own isolated disposable live regression services; no product configuration changes.
pg='loop1-e2e-review-pg-6346'; nt='loop1-e2e-review-nats-6346'; owner='R-E2E-REVIEW-6346'
volumes=[]
try:
 run(['docker','run','-d','--name',pg,'--label','im.task=LOOP1-E2E-001','--label','im.owner='+owner,'-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=s1_e2e_review','-p','127.0.0.1:55661:5432','postgres:16'])
 run(['docker','run','-d','--name',nt,'--label','im.task=LOOP1-E2E-001','--label','im.owner='+owner,'-p','127.0.0.1:42661:4222','nats:2.10-alpine'])
 for _ in range(30):
  p=subprocess.run(['docker','exec',pg,'pg_isready','-U','postgres','-d','s1_e2e_review'],capture_output=True)
  if p.returncode==0: break
  time.sleep(.5)
 else: raise RuntimeError('PostgreSQL not ready')
 run(['docker','cp','contracts/database/migrations/0001_initial.up.sql',pg+':/tmp/canonical0001.sql'])
 run(['docker','exec',pg,'psql','-U','postgres','-d','s1_e2e_review','-v','ON_ERROR_STOP=1','-f','/tmp/canonical0001.sql'])
 os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55661',PGUSER='postgres',PGDATABASE='s1_e2e_review',NATS_URL='nats://127.0.0.1:42661',PYTHONDONTWRITEBYTECODE='1')
 run(['go','-C','backend/go','test','-count=1','-v','./...'])
 run(['go','-C','backend/go','test','-race','-count=1','-v','./...'])
finally:
 for name in (pg,nt):
  p=run(['docker','inspect',name],required=False)
  if p.returncode: continue
  obj=json.loads(p.stdout)[0]
  if obj['Config']['Labels'].get('im.owner')!=owner: raise RuntimeError('ownership mismatch')
  for m in obj.get('Mounts',[]):
   if m['Type']=='volume':
    v=m['Name']; vi=run(['docker','volume','inspect',v]); users=run(['docker','ps','-aq','--filter','volume='+v]).stdout.decode().split()
    if users != [obj['Id']]: raise RuntimeError('volume not exclusive')
    volumes.append(v)
  run(['docker','rm','-f',name])
 for v in volumes: run(['docker','volume','rm',v])
run(['docker','ps','-aq','--filter','label=im.owner='+owner])
run(['git','-c','core.excludesFile=.git/info/exclude','status','--porcelain=v1','--untracked-files=all'])
event('verification_result',{'result':'PASS','candidate':'6346f39fc6786bba3cddbde7acc91bbad42446a1','evidence':str(E/'commands.json'),'boundary':'local checks only; hosted exact job acceptance pending'})
print('LOCAL CHECKS COMPLETE, hosted acceptance pending',flush=True)

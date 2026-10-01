import os,sys,subprocess,time,json
from pathlib import Path
ROOT=Path.cwd(); E=ROOT/'spec/progress/evidence/LOOP1-GO-MSG-001'; R='R-MSG-IMPLEMENTATION-20261001'
PG='loop1-msg-impl-pg-20261001'; NATS='loop1-msg-impl-nats-20261001'
os.environ.update(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55631',PGUSER='postgres',PGDATABASE='msg_test',NATS_URL='nats://127.0.0.1:42631',PYTHONDONTWRITEBYTECODE='1')
os.environ['PATH']=r'H:\go\bin;C:\Users\21441\.cache\codex-runtimes\codex-primary-runtime\dependencies\node;'+os.environ['PATH']
results=[]
def command(argv,input=None):
    start=time.monotonic(); p=subprocess.run(argv,input=input,text=True,capture_output=True,encoding='utf-8',errors='replace'); results.append(dict(argv=argv,exit_code=p.returncode,elapsed_seconds=round(time.monotonic()-start,3),skips=p.stdout.count('--- SKIP:')))
    print(p.stdout);print(p.stderr,file=sys.stderr)
    if p.returncode: raise SystemExit(p.returncode)
    return p

def rec(argv):
    return command([sys.executable,'-B','tools/research/recorder.py','run-command','--run-id',R,'--']+argv)
try:
    phase=sys.argv[1]
    if phase=='baseline':
        rec(['docker','run','-d','--name',PG,'--label','im.task=LOOP1-GO-MSG-001','-e','POSTGRES_HOST_AUTH_METHOD=trust','-e','POSTGRES_DB=msg_test','-p','127.0.0.1:55631:5432','postgres:16'])
        rec(['docker','run','-d','--name',NATS,'--label','im.task=LOOP1-GO-MSG-001','-p','127.0.0.1:42631:4222','nats:2.10'])
        for _ in range(60):
            if subprocess.run(['docker','exec',PG,'pg_isready','-U','postgres','-d','msg_test'],capture_output=True).returncode==0: break
            time.sleep(.5)
        else: raise RuntimeError('disposable PG readiness failed')
        command(['docker','exec','-i',PG,'psql','-U','postgres','-d','msg_test','-v','ON_ERROR_STOP=1'],(ROOT/'contracts/database/migrations/0001_initial.up.sql').read_text())
        rec(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'])
    if phase in ['baseline','final']:
        for extra in [[],['-race']]:
            result=rec(['go','-C','backend/go','test']+extra+['-count=1','-v','./...'])
            if '--- SKIP:' in result.stdout: raise RuntimeError('runtime integration skipped')
    elif phase=='checks':
        rec(['go','-C','backend/go','build','./...']);rec(['go','-C','backend/go','vet','./...'])
        rec([sys.executable,'-B','contracts/websocket/verify.py'])
        rec([sys.executable,'-B','ci/check_architecture.py','--scope','all','--json'])
        rec([sys.executable,'-B','-m','unittest','discover','-s','tests/architecture','-v'])
        rec([sys.executable,'-B','-m','unittest','discover','-s','tests/ci','-v'])
        rec(['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'])
        rec(['pwsh','-NoProfile','-File','tools/verify-loop1-ctrl-002.ps1','-Mode','Development'])
    elif phase=='cleanup':
        for name in [PG,NATS]:
            label=command(['docker','inspect','--format','{{index .Config.Labels "im.task"}}',name]).stdout.strip()
            assert label=='LOOP1-GO-MSG-001'
            rec(['docker','rm','-fv',name])
finally:
    (E/('2026-10-01-'+sys.argv[1]+'-commands.json')).write_text(json.dumps(dict(owner=R,phase=sys.argv[1],enable=dict(DB_TEST_ENABLE='1',PGHOST='127.0.0.1',PGPORT='55631',PGUSER='postgres',PGDATABASE='msg_test',NATS_URL='nats://127.0.0.1:42631'),containers=[PG,NATS],commands=results),indent=2)+'\n')

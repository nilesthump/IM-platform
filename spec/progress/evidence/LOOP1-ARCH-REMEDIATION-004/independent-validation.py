import os,sys,subprocess,tempfile,time,secrets,json,importlib.util
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve()
PY=sys.executable
def run(argv,env=None,cwd=ROOT,timeout=600):
    print('RUN '+str(argv),flush=True)
    subprocess.run(argv,cwd=cwd,env=env,check=True,timeout=timeout)
def static():
    run(['pwsh','-NoProfile','-File','tools/verify-frozen-architecture.ps1'])
    run([PY,'ci/check_architecture.py','--scope','all','--json'])
    run([PY,'-m','unittest','discover','-s','tests/ci','-v'])
    files=[str(p) for p in (ROOT/'backend/go').rglob('*.go')]
    dirty=subprocess.check_output(['gofmt','-l']+files,cwd=ROOT,text=True)
    assert not dirty,dirty
    print('PASS recursivefmt '+str(len(files)))
    run(['go','-C','backend/go','build','./...'])
    run(['go','-C','backend/go','vet','./...'])
def live():
    env=os.environ.copy();env['DOCKER_CONTEXT']='default'
    env['POSTGRES_PASSWORD']=secrets.token_hex(24);env['PGPASSWORD']=env['POSTGRES_PASSWORD']
    pg='im-arch4-review-pg-'+str(os.getpid());nt='im-arch4-review-nats-'+str(os.getpid())
    created=[]
    def dock(*argv):return subprocess.check_output(['docker']+list(argv),env=env,text=True).strip()
    try:
        dock('run','-d','--name',pg,'-e','POSTGRES_PASSWORD','-e','POSTGRES_DB=im_review','-p','127.0.0.1::5432','postgres:16-alpine');created.append(pg)
        dock('run','-d','--name',nt,'-p','127.0.0.1::4222','nats:2.10-alpine');created.append(nt)
        for i in range(60):
            result=subprocess.run(['docker','exec',pg,'pg_isready','-U','postgres','-d','im_review'],env=env,capture_output=True)
            if result.returncode==0:break
            time.sleep(.5)
        else:raise RuntimeError('review PG unavailable')
        env.update(PGHOST='127.0.0.1',PGUSER='postgres',PGDATABASE='im_review',PGPORT='5432',DB_TEST_ENABLE='1')
        run(['docker','run','--rm','--network','container:'+pg,'-e','PGHOST','-e','PGUSER','-e','PGDATABASE','-e','PGPORT','-e','PGPASSWORD','-v',str(ROOT)+':/repo','-w','/repo','im-db-review-runtime','python3','contracts/database/migrate.py','up'],env)
        env['PGPORT']=dock('port',pg,'5432/tcp').split(':')[-1]
        env['NATS_URL']='nats://127.0.0.1:'+dock('port',nt,'4222/tcp').split(':')[-1]
        print('Independent disposable PostgreSQL16/NATS2.10; DB_TEST_ENABLE=1; canonical0001_initial, no skipped integration permitted',flush=True)
        for race in [False,True]:
            cmd=['go','-C','backend/go','test']+(['-race'] if race else [])+['-count=1','-v','./...']
            out=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=180)
            print(out.stdout);print(out.stderr);assert out.returncode==0 and '--- SKIP' not in out.stdout
        run([PY,'spec/progress/evidence/LOOP1-ARCH-REMEDIATION-004/message-cache-negative.py'],env)
        run([PY,'contracts/websocket/verify.py'],env)
        run(['pwsh','-NoProfile','-File','contracts/http/verify-auth-user-friend.ps1'],env)
        print('PASS independent live unit/race/auth/session/fixtures/rollback/cache negative, zero integration skips')
    finally:
        for name in reversed(created):subprocess.run(['docker','rm','-f','-v',name],env=env,check=True)
def eof():
    with tempfile.TemporaryDirectory(prefix='im-review-eof-') as d:
        d=Path(d)
        (d/'main.go').write_text('package main\nimport("fmt";"net/http";"net/http/httptest";"os")\nfunc main(){s:=httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){c,_,e:=w.(http.Hijacker).Hijack();if e==nil{c.Close()}}));defer s.Close();fmt.Println(s.URL);var b [1]byte;os.Stdin.Read(b[:])}\n',encoding='utf-8')
        run(['go','build','-o',str(d/'eof.exe'),str(d/'main.go')])
        proc=subprocess.Popen([str(d/'eof.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        try:
            url=proc.stdout.readline().strip();port=url.rsplit(':',1)[-1];assert port.isdigit()
            code="import importlib.util,sys,time; s=importlib.util.spec_from_file_location('smoke',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.PORT=int(sys.argv[2]);orig=m.socket.create_connection;m.socket.create_connection=lambda a,timeout=10:orig(('127.0.0.1',a[1]),timeout);t=time.monotonic()\ntry:m.WS();raise AssertionError('EOF accepted')\nexcept EOFError:assert time.monotonic()-t<2;print('PASS real TLS remote upgrade EOF exits under2s')"
            run([PY,'-c',code,str(ROOT/'tests/go/live_role_smoke.py'),port],timeout=5)
        finally:proc.terminate();proc.wait(timeout=5)
if __name__=='__main__':
    mode=sys.argv[2]
    {'static':static,'live':live,'eof':eof}[mode]()

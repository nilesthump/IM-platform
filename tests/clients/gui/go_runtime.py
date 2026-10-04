"""Owned actual Go/PG/NATS GUI fixture. No product edits or host trust install."""
from pathlib import Path
import importlib.util,json,os,secrets,ssl,subprocess,sys,time,urllib.request,uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PRIVATE=Path(os.environ.get('IM_GUI_PRIVATE_RUNTIME','H:/IM-platform/.git/worktrees/IM-platform3/gui-runtime')).resolve()
TLS=PRIVATE/'tls-v2';WORK=PRIVATE/('go-'+str(os.getpid()))
project='im-gui-product-20261004-'+str(os.getpid())
docker='C:/Program Files/Docker/Docker/resources/bin/docker.exe'
env=os.environ.copy();env.update(IM_HTTPS_PORT='18443',IM_GO_CONFIG_DIR=str(WORK/'config'),COMPOSE_PROGRESS='quiet')
base=[docker,'compose','-f',str(ROOT/'deploy/compose.yaml'),'-f',str(WORK/'override.yaml'),'-p',project,'--profile','go']
def execute(argv,data=None):
    r=subprocess.run(list(map(str,argv)),env=env,input=data,capture_output=True,timeout=600)
    if r.returncode:raise RuntimeError('Owned fixture command failed (private output withheld); exit='+str(r.returncode))
    return r.stdout
def compose(*args):return execute(base+list(args))
def sql(query):return compose('exec','-T','postgres','psql','-U','im','-d','im','-v','ON_ERROR_STOP=1','-Atc',query).decode().strip()
def cleanup():
    for kind,listing in [('container',[docker,'ps','-aq','--filter','label=com.docker.compose.project='+project]),('volume',[docker,'volume','ls','-q','--filter','label=com.docker.compose.project='+project])]:
        for name in execute(listing).decode().split():
            obj=json.loads(execute([docker,kind,'inspect',name]))[0]
            labels=obj['Config']['Labels'] if kind=='container' else obj['Labels']
            if labels.get('com.docker.compose.project')!=project:raise RuntimeError('Owned cleanup identity mismatch')
    compose('down','--volumes','--remove-orphans')
    if execute([docker,'ps','-aq','--filter','label=com.docker.compose.project='+project]).strip():raise RuntimeError('Owned container cleanup incomplete')
    print('PASS owned fixture cleanup; no unrelated container/volume operation',flush=True)
def main():
    if WORK.exists():raise RuntimeError('New exact private runtime directory required')
    (WORK/'config').mkdir(parents=True)
    identity=os.environ['USERDOMAIN']+'\\'+os.environ['USERNAME']
    execute(['icacls.exe',str(WORK),'/inheritance:r','/grant:r',identity+':(OI)(CI)F','SYSTEM:(OI)(CI)F'])
    (WORK/'config/config.json').write_bytes((ROOT/'backend/go/config.example.json').read_bytes())
    (WORK/'config/pg_password').write_bytes(b'local-development-only')
    (WORK/'config/jwt_key').write_bytes(secrets.token_urlsafe(48).encode())
    (WORK/'Caddyfile').write_text('https://localhost:443 {\n  tls /gui-cert/server.pem /gui-cert/server.key\n  reverse_proxy gateway-go:8080\n}\n')
    override='services:\n  tls-go:\n    ports: !override\n      - "127.0.0.1:18443:443"\n    volumes:\n      - type: bind\n        source: '+json.dumps(str(WORK/'Caddyfile'))+'\n        target: /etc/caddy/Caddyfile\n        read_only: true\n      - type: bind\n        source: '+json.dumps(str(TLS))+'\n        target: /gui-cert\n        read_only: true\n'
    (WORK/'override.yaml').write_text(override)
    configured=json.loads(compose('config','--format','json'))
    ports=configured['services']['tls-go']['ports']
    if len(ports)!=1 or ports[0].get('host_ip')!='127.0.0.1' or str(ports[0]['published'])!='18443':raise RuntimeError('Loopback-only owned endpoint required')
    started=False;ws=None
    try:
        started=True;print('Starting owned actual Go/PG/NATS project '+project,flush=True);compose('up','-d','--build')
        context=ssl.create_default_context(cafile=str(TLS/'ca.pem'))
        def call(method,path,body=None,token=None):
            headers={'Content-Type':'application/json'}
            if token:headers['Authorization']='Bearer '+token
            req=urllib.request.Request('https://localhost:18443'+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
            with urllib.request.urlopen(req,context=context,timeout=15) as response:return json.loads(response.read() or b'{}')
        for _ in range(120):
            try:urllib.request.urlopen('https://localhost:18443/__infra/health',context=context,timeout=2).close();break
            except OSError:time.sleep(.5)
        else:raise RuntimeError('Actual accepted Go TLS endpoint unavailable')
        accounts=[];logins=[]
        for i,label in enumerate(['Avery','Morgan','Riley']):
            username='gui_'+label.lower()+'_'+secrets.token_hex(3)
            password='fixture-password-not-a-real-secret'
            user=call('POST','/v1/auth/register',{'username':username,'password':password,'displayName':'GUI Fixture '+label})['user']
            accounts.append({'username':username,'userId':user['userId'],'displayName':user['displayName']})
            logins.append(call('POST','/v1/auth/login',{'username':username,'password':password,'clientType':'DESKTOP','deviceId':'gui-fixture-seed','clientVersion':'0.1.0','protocolVersion':'1'}))
        token=logins[0]['tokens']['accessToken'];conversation=call('PUT','/v1/friends/'+accounts[1]['userId'],{},token)['directConversationId']
        spec=importlib.util.spec_from_file_location('gui_actual_ws',ROOT/'tests/e2e/go_tls_messaging.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
        ws=h.WS(context,18443);ws.send(h.frame('auth.bind',{'accessToken':token}));check=ws.read()
        if check['payload']['status']!='bound':raise RuntimeError('Actual seed session binding failed')
        for text in ['Welcome to the GUI fixture. This message crossed the actual Go services.','History stays with this account, even when the connection is quiet.']:
            frame=h.frame('message.send',{'conversationId':conversation,'content':{'kind':'TEXT','text':text}});ws.send(frame)
            for _ in range(20):
                result=ws.read()
                if result['type']=='message.ack' and result['requestId']==frame['requestId']:
                    if result['payload']['status']!='committed':raise RuntimeError('Actual seed message not committed')
                    break
            else:raise RuntimeError('Actual seed ACK absent')
        ws.close();ws=None;logins.clear();token=None
        public={'status':'actual owned Go/PG/NATS, no system trust installed','project':project,'endpoint':'https://localhost:18443','accounts':accounts,'conversationId':conversation,'privateRuntime':str(WORK),'password':'unavailable in public evidence; owned fixture input only'}
        (WORK/'public.json').write_text(json.dumps(public,indent=2)+'\n')
        print(json.dumps(public,indent=2),flush=True)
        print('READY owned actual runtime; stdin accepts status, expire Avery/Morgan/Riley, stop',flush=True)
        for line in sys.stdin:
            action=line.strip()
            if action=='stop':break
            if action=='status':print('READY actual owned endpoint',flush=True)
            elif action.startswith('expire '):
                label=action.split(' ',1)[1];account=next((u for u in accounts if u['displayName']=='GUI Fixture '+label),None)
                if account is None:raise RuntimeError('Unknown owned fixture identity')
                uid=str(uuid.UUID(account['userId']));sql("UPDATE sessions SET expires_at=now()-interval '1 second' WHERE user_id='"+uid+"'");print('Applied owned fixture session expiry',flush=True)
            else:raise RuntimeError('Unknown owned fixture action')
    finally:
        if ws:ws.close()
        if started:cleanup()
if __name__=='__main__':main()

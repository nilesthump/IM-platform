"""Current Desktop application -> actual Go WSS/TLS -> PostgreSQL durable smoke."""
from pathlib import Path
import json, os, secrets, socket, ssl, subprocess, sys, tempfile, time, urllib.request, uuid
ROOT=Path(__file__).resolve().parents[3]
def main():
    probe=Path(sys.argv[1]).resolve()
    project='im-client-send-'+str(os.getpid())+'-'+secrets.token_hex(4)
    docker=os.environ.get('IM_CLIENT_DOCKER','docker');env=os.environ.copy()
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    env.update(IM_HTTPS_PORT=str(port),COMPOSE_PROGRESS='quiet')
    command=[docker,'compose','-f',str(ROOT/'deploy/compose.yaml'),'-p',project,'--profile','go']
    def execute(argv):
        r=subprocess.run(argv,env=env,capture_output=True,timeout=300)
        if r.returncode:raise RuntimeError('Go smoke infrastructure command failed')
        return r.stdout
    def compose(*argv):return execute(command+list(argv))
    with tempfile.TemporaryDirectory(prefix='im-send-go-config-') as tmp:
        tmp=Path(tmp);config=tmp/'config';config.mkdir();env['IM_GO_CONFIG_DIR']=str(config)
        (config/'config.json').write_bytes((ROOT/'backend/go/config.example.json').read_bytes())
        (config/'pg_password').write_bytes(b'local-development-only')
        (config/'jwt_key').write_bytes(secrets.token_urlsafe(48).encode())
        try:
            print('Starting isolated actual Go/PostgreSQL/NATS/TLS profile',flush=True)
            compose('up','-d','--build')
            tls=compose('ps','-q','tls-go').decode().strip();ca=tmp/'root.crt'
            for _ in range(120):
                try:execute([docker,'cp',tls+':/data/caddy/pki/authorities/local/root.crt',str(ca)]);break
                except RuntimeError:time.sleep(.5)
            else:raise RuntimeError('Actual Go public CA unavailable')
            context=ssl.create_default_context(cafile=str(ca))
            def call(method,path,body=None,token=None):
                headers={'Content-Type':'application/json'}
                if token:headers['Authorization']='Bearer '+token
                r=urllib.request.Request('https://localhost:'+str(port)+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
                with urllib.request.urlopen(r,context=context,timeout=10) as response:return json.loads(response.read() or b'{}')
            for _ in range(120):
                try:
                    urllib.request.urlopen('https://localhost:'+str(port)+'/__infra/health',context=context,timeout=2).close();break
                except OSError:time.sleep(.5)
            else:raise RuntimeError('Actual Go gateway unavailable')
            users=[];logins=[]
            for index in range(2):
                name='send'+secrets.token_hex(8);password='fixture-password-not-a-real-secret'
                user=call('POST','/v1/auth/register',{'username':name,'password':password,'displayName':name})['user'];users.append(user['userId'])
                login=call('POST','/v1/auth/login',{'username':name,'password':password,'clientType':'DESKTOP' if index==0 else 'MOBILE','deviceId':'send-smoke-'+str(index),'clientVersion':'1.0.0','protocolVersion':'1'});logins.append(login)
            friendship=call('PUT','/v1/friends/'+users[1],token=logins[0]['tokens']['accessToken']);conversation=friendship['directConversationId']
            login=logins[0];state=login['session'];private={'probe':str(probe),'endpoint':'wss://localhost:'+str(port)+'/v1/ws','conversationId':conversation,'session':{'userId':users[0],'sessionId':state['sessionId'],'sessionEpoch':state['sessionEpoch'],'accessToken':login['tokens']['accessToken']}}
            nodeenv=env.copy();nodeenv['NODE_EXTRA_CA_CERTS']=str(ca)
            result=subprocess.run(['node','tests/clients/send/go_client.mjs'],cwd=ROOT,env=nodeenv,input=json.dumps(private),capture_output=True,text=True,timeout=60)
            if result.returncode:raise RuntimeError('Actual Desktop Go SEND application failed')
            outcome=json.loads(result.stdout);request=str(uuid.UUID(outcome['requestId']));message=str(uuid.UUID(outcome['messageId']));conversation=str(uuid.UUID(conversation))
            query=f"SELECT json_build_object('messages',(SELECT count(*) FROM messages WHERE conversation_id='{conversation}' AND request_id='{request}' AND server_message_id='{message}'),'outbox',(SELECT count(*) FROM outbox_events WHERE conversation_id='{conversation}' AND event_type='message.created'),'nextSeq',(SELECT next_seq FROM conversations WHERE conversation_id='{conversation}'))"
            rows=json.loads(compose('exec','-T','postgres','psql','-U','im','-d','im','-v','ON_ERROR_STOP=1','-Atc',query))
            if rows!={'messages':1,'outbox':1,'nextSeq':2} or outcome['seq']!='1':raise RuntimeError('Client SENT lacks exact committed PostgreSQL Message/Outbox/sequence rows')
            print('PASS: actual Desktop TS application + SQLx + Go WSS verified TLS + PostgreSQL durable Message/Outbox; restart same-ID retry and terminal SENT',flush=True)
        finally:
            # Never touch an unrelated Docker resource.
            ids=execute([docker,'ps','-aq','--filter','label=com.docker.compose.project='+project]).decode().split()
            for ident in ids:
                labels=json.loads(execute([docker,'inspect',ident]))[0]['Config']['Labels']
                if labels.get('com.docker.compose.project')!=project:raise RuntimeError('Go smoke container ownership mismatch')
            volumes=execute([docker,'volume','ls','-q','--filter','label=com.docker.compose.project='+project]).decode().split()
            for name in volumes:
                if json.loads(execute([docker,'volume','inspect',name]))[0]['Labels'].get('com.docker.compose.project')!=project:raise RuntimeError('Go smoke volume ownership mismatch')
            compose('down','--volumes','--remove-orphans')
            print('PASS: only inspected task-owned Go smoke containers/volumes removed',flush=True)
if __name__=='__main__':main()

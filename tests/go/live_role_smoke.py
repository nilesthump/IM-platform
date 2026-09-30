"""Disposable real Go Compose roles and HTTPS/WSS Auth/NATS smoke.
No credentials or tokens are printed or committed. Does not replace full tests.
"""
import base64,hashlib,json,os,secrets,socket,ssl,struct,subprocess,tempfile,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PORT=19443
CTX=ssl._create_unverified_context() # only generated local smoke CA

def call(path,body=None,token=None):
    data=json.dumps(body).encode() if body is not None else None
    h={'Content-Type':'application/json'}
    if token:h['Authorization']='Bearer '+token
    with urllib.request.urlopen(urllib.request.Request(f'https://localhost:{PORT}'+path,data=data,headers=h),context=CTX,timeout=10) as r:
        return r.status,json.loads(r.read() or b'{}')

class WS:
    def __init__(self):
        self.s=CTX.wrap_socket(socket.create_connection(('localhost',PORT),timeout=10),server_hostname='localhost')
        self.s.settimeout(5)
        key=base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET /v1/ws HTTP/1.1\r\nHost: localhost:{PORT}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        head=b''
        while not head.endswith(b'\r\n\r\n'):
            chunk=self.s.recv(1)
            if not chunk:raise EOFError('WebSocket upgrade closed before headers')
            head+=chunk
        assert b' 101 ' in head
        expected=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        assert expected in head
    def send(self,typ,payload):
        b=json.dumps({'protocolVersion':'1.0','type':typ,'requestId':str(uuid.uuid4()),'payload':payload}).encode()
        mask=os.urandom(4);n=len(b)
        head=bytes([0x81,0x80|n]) if n<126 else bytes([0x81,0xfe])+struct.pack('!H',n)
        self.s.sendall(head+mask+bytes(x^mask[i%4] for i,x in enumerate(b)))
    def exact(self,n):
        b=b''
        while len(b)<n:
            x=self.s.recv(n-len(b))
            if not x:raise EOFError()
            b+=x
        return b
    def read(self):
        a,n=self.exact(2);n&=127
        if n==126:n=struct.unpack('!H',self.exact(2))[0]
        if n==127:n=struct.unpack('!Q',self.exact(8))[0]
        b=self.exact(n)
        if a&15==8:raise EOFError()
        return json.loads(b)
    def close(self):self.s.close()

def main():
    env=os.environ.copy();env['IM_HTTPS_PORT']=str(PORT)
    project='im-arch4-live-'+str(os.getpid())
    command=['docker','compose','-f',str(ROOT/'deploy/compose.yaml'),'-p',project,'--profile','go']
    def compose(*args):subprocess.run(command+list(args),env=env,check=True,timeout=300)
    with tempfile.TemporaryDirectory(prefix='im-arch4-config-') as d:
        d=Path(d);env['IM_GO_CONFIG_DIR']=str(d)
        (d/'config.json').write_bytes((ROOT/'backend/go/config.example.json').read_bytes())
        (d/'pg_password').write_text('local-development-only',encoding='utf-8')
        (d/'jwt_key').write_text(secrets.token_urlsafe(48),encoding='utf-8')
        try:
            compose('config','--quiet');compose('up','-d','--build')
            for attempt in range(60):
                try:
                    with urllib.request.urlopen(f'https://localhost:{PORT}/__infra/health',context=CTX,timeout=2) as r:assert r.read().strip()==b'profile=go role=gateway'
                    break
                except (OSError,AssertionError):time.sleep(1)
            else:raise RuntimeError('TLS gateway did not become ready')
            for role in ['core','gateway','plugin-host']:
                result=subprocess.check_output(command+['exec','-T',role+'-go','wget','-qO-','http://localhost:8080/__infra/health'],env=env)
                assert result.strip()==f'profile=go role={role}'.encode()
            username='roles'+secrets.token_hex(6);password='smoke-password-not-real-secret'
            status,_=call('/v1/auth/register',{'username':username,'password':password,'displayName':'Role Smoke'});assert status==201
            def login(typ):
                status,v=call('/v1/auth/login',{'username':username,'password':password,'clientType':typ,'deviceId':'smoke-'+typ,'clientVersion':'1.0.0','protocolVersion':'1'});assert status==200;return v
            first=login('WEB');desktop=login('DESKTOP');mobile=login('MOBILE')
            ws=WS();ws.send('auth.bind',{'accessToken':first['tokens']['accessToken']});assert ws.read()['payload']['status']=='bound'
            replacement=login('WEB');assert replacement['session']['sessionEpoch']==first['session']['sessionEpoch']+1
            event=ws.read();assert event['type']=='session.revoked' and event['payload']['reason']=='REPLACED'
            try:ws.read();raise AssertionError('revoked socket remained open')
            except EOFError:pass
            finally:ws.close()
            stale=WS();stale.send('auth.bind',{'accessToken':first['tokens']['accessToken']});assert stale.read()['payload']['status']=='rejected';stale.close()
            for v in [desktop,mobile]:assert call('/v1/users/me',token=v['tokens']['accessToken'])[0]==200
            current=WS();current.send('auth.bind',{'accessToken':desktop['tokens']['accessToken']});assert current.read()['payload']['status']=='bound'
            assert call('/v1/auth/logout',{},desktop['tokens']['accessToken'])[0]==204
            event=current.read();assert event['type']=='session.revoked' and event['payload']['reason']=='LOGOUT'
            try:current.read();raise AssertionError('logout socket remained open')
            except EOFError:pass
            finally:current.close()
            print('PASS: actual3 Go roles/HTTP forwarding/TLS/WSS3slots/replacementepoch/oldtokenreject/CoreOutboxNATSGatewayrevocation/logoutclose; no skips')
        finally:compose('down','--volumes','--remove-orphans')
if __name__=='__main__':main()

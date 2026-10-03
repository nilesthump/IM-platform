"""Controlled TLS/WSS behavior fixture; NOT proof of Go/PostgreSQL durability."""
import base64, hashlib, json, socket, ssl, struct, threading, time, uuid
USER="10000000-0000-4000-8000-000000000001"
SESSION="20000000-0000-4000-8000-000000000001"
class Fixture:
    def __init__(self,cert,key):
        self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);self.context.load_cert_chain(cert,key)
        self.server=socket.socket();self.server.bind(('127.0.0.1',0));self.server.listen()
        self.port=self.server.getsockname()[1];self.messages={};self.lock=threading.Lock();self.errors=[];self.sends=0
        threading.Thread(target=self.accept,daemon=True).start()
    def accept(self):
        while True:
            try: conn,_=self.server.accept()
            except OSError:return
            threading.Thread(target=self.connection,args=(conn,),daemon=True).start()
    def connection(self,conn):
        try:
            with self.context.wrap_socket(conn,server_side=True) as s:
                s.settimeout(20);header=b''
                while not header.endswith(b'\r\n\r\n'):
                    header+=s.recv(1)
                    if len(header)>16384:raise ValueError('header too large')
                lines=header.decode('ascii').split('\r\n');path=lines[0].split()[1]
                if '?' in path:raise ValueError('query forbidden')
                headers=dict(line.split(':',1) for line in lines[1:] if ':' in line)
                key=next(v.strip() for k,v in headers.items() if k.lower()=='sec-websocket-key')
                accept=base64.b64encode(hashlib.sha1((key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
                s.sendall(('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: '+accept+'\r\n\r\n').encode())
                def receive():
                    def exact(n):
                        out=b''
                        while len(out)<n:
                            part=s.recv(n-len(out))
                            if not part:raise EOFError()
                            out+=part
                        return out
                    first,second=exact(2);op=first&15;n=second&127
                    if n==126:n=struct.unpack('!H',exact(2))[0]
                    elif n==127:n=struct.unpack('!Q',exact(8))[0]
                    if n>131072:raise ValueError('frame too large')
                    if not second&128:raise ValueError('unmasked client')
                    mask=exact(4);body=exact(n);body=bytes(v^mask[i%4] for i,v in enumerate(body))
                    if op==8:raise EOFError()
                    if op!=1:raise ValueError('text expected')
                    return json.loads(body)
                def send(type,r,p):
                    raw=json.dumps({'protocolVersion':'1.0','type':type,'requestId':r,'payload':p},separators=(',',':')).encode()
                    prefix=bytes([0x81,len(raw)]) if len(raw)<126 else bytes([0x81,126])+struct.pack('!H',len(raw))
                    s.sendall(prefix+raw)
                auth=receive()
                if set(auth)!= {'protocolVersion','type','requestId','payload'} or auth['type']!='auth.bind' or set(auth['payload'])!={'accessToken'}:raise ValueError('bad bind')
                token=auth['payload']['accessToken']
                client='MOBILE' if token=='fixture-mobile' else 'DESKTOP'
                if token not in ('fixture-mobile','fixture-desktop'):raise ValueError('unexpected fixture credential')
                p={'status':'bound','userId':USER,'sessionId':SESSION,'clientType':client,'sessionEpoch':1}
                if path=='/wrong-session':p['sessionId']=str(uuid.uuid4())
                send('auth.ack',auth['requestId'],p)
                while True:
                    e=receive()
                    if e['type']=='pong':continue
                    if e['type']!='message.send' or set(e['payload'])!={'conversationId','content'}:raise ValueError('bad send')
                    r=e['requestId'];c=e['payload']['conversationId'];content=e['payload']['content']
                    with self.lock:
                        self.sends+=1;k=(USER,c,r);old=self.messages.get(k)
                        if old is None:
                            old={'conversationId':c,'messageId':str(uuid.uuid4()),'senderId':USER,'seq':9007199254740993+len(self.messages),'createdAt':'2026-10-03T00:00:00Z','content':content};self.messages[k]=old
                        elif old['content']!=content:raise ValueError('retry changed identity/content')
                    if path=='/revoked':send('session.revoked',str(uuid.uuid4()),{'sessionId':SESSION,'reason':'LOGOUT'});return
                    if path=='/timeout':continue
                    if path=='/reject':send('message.ack',r,{'status':'rejected','error':{'code':'AUTHORIZATION_DENIED','message':'Denied'}});continue
                    if path=='/late':time.sleep(.8)
                    ack={key:old[key] for key in ('conversationId','messageId','seq','createdAt')};ack['status']='committed'
                    if path=='/invalid':ack['unexpected']=True
                    if path=='/realtime':send('message.created',r,old)
                    else:send('message.ack',r,ack)
                    if path not in ('/invalid',):send('message.created',r,old)
        except (EOFError,ConnectionError,OSError,ssl.SSLError):pass
        except Exception as e:self.errors.append(type(e).__name__+': '+str(e))
    def close(self):self.server.close()

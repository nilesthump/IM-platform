"""Controlled actual HTTPS/WSS client fixture, never a PostgreSQL durability claim."""
import base64,hashlib,json,socket,ssl,struct,threading,time
USER="10000000-0000-4000-8000-000000000001"
SESSION="20000000-0000-4000-8000-000000000001"
C="30000000-0000-4000-8000-000000000001"
D="30000000-0000-4000-8000-000000000002"
DENIED="30000000-0000-4000-8000-000000000003"
def uid(n):return "50000000-0000-4000-8000-"+str(n).zfill(12)
def message(n,c=C):
    offset=10000 if c==D else 0
    return dict(conversationId=c,seq=n,messageId=uid(n+offset),senderId=USER,requestId=uid(n+offset+1000),createdAt="2026-10-03T00:00:00Z",content=dict(kind="TEXT",text="message-"+str(n)))
class Fixture:
    def __init__(self,cert,key):
        self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);self.context.load_cert_chain(cert,key)
        self.server=socket.socket();self.server.bind(("127.0.0.1",0));self.server.listen()
        self.port=self.server.getsockname()[1];self.errors=[];self.requests=[];self.head=205;self.ws=[];self.frames=0;self.user_count=205
        threading.Thread(target=self.accept,daemon=True).start()
    def accept(self):
        while True:
            try:conn,_=self.server.accept()
            except OSError:return
            threading.Thread(target=self.connection,args=(conn,),daemon=True).start()
    def frame(self,s,m):
        raw=json.dumps(dict(protocolVersion="1.0",type="message.created",requestId=m["requestId"],payload={k:v for k,v in m.items() if k!="requestId"}),separators=(",",":")).encode()
        s.sendall(bytes([129,126])+struct.pack("!H",len(raw))+raw);self.frames+=1
    def connection(self,conn):
        try:
            with self.context.wrap_socket(conn,server_side=True) as s:
                s.settimeout(20);header=b""
                while not header.endswith(b"\r\n\r\n"):
                    part=s.recv(1)
                    if not part:return
                    header+=part
                    if len(header)>16384:raise ValueError("header bound")
                lines=header.decode().split("\r\n");method,path,_=lines[0].split();headers={k.lower():v.strip() for k,v in (l.split(":",1) for l in lines[1:] if ":" in l)}
                if "?" in path:raise ValueError("query")
                if headers.get("upgrade","").lower()=="websocket":
                    key=headers["sec-websocket-key"];accept=base64.b64encode(hashlib.sha1((key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
                    s.sendall(("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: "+accept+"\r\n\r\n").encode())
                    def exact(n):
                        data=b""
                        while len(data)<n:
                            part=s.recv(n-len(data))
                            if not part:raise EOFError()
                            data+=part
                        return data
                    first,second=exact(2);n=second&127
                    if n==126:n=struct.unpack("!H",exact(2))[0]
                    if n>131072 or not second&128:raise ValueError("client frame")
                    mask=exact(4);raw=exact(n);auth=json.loads(bytes(v^mask[i%4] for i,v in enumerate(raw)));token=auth["payload"]["accessToken"]
                    if token not in ("fixture-mobile","fixture-desktop"):raise ValueError("credential")
                    payload=dict(status="bound",userId=USER,sessionId=SESSION,clientType="MOBILE" if token=="fixture-mobile" else "DESKTOP",sessionEpoch=1)
                    raw=json.dumps(dict(protocolVersion="1.0",type="auth.ack",requestId=auth["requestId"],payload=payload),separators=(",",":")).encode();s.sendall(bytes([129,126])+struct.pack("!H",len(raw))+raw)
                    self.ws.append(s);time.sleep(.1)
                    for m in [message(203),message(205),message(203),message(2,D)]:self.frame(s,m)
                    while s.recv(1024):pass
                    return
                if path=="/fixture/append":
                    self.head=208;self.user_count=206
                    for ws in list(self.ws):
                        try:self.frame(ws,message(208))
                        except OSError:pass
                    result={"ok":True};status=200
                elif path=="/fixture/redirect":
                    s.sendall(b"HTTP/1.1 302 Found\r\nLocation: https://example.invalid/\r\nContent-Length: 0\r\n\r\n");return
                elif path.startswith("/v1/sync/"):
                    if method!="POST" or headers.get("authorization") not in ("Bearer fixture-desktop","Bearer fixture-mobile"):raise ValueError("authenticated POST")
                    n=int(headers["content-length"]);raw=b""
                    while len(raw)<n:raw+=s.recv(n-len(raw))
                    body=json.loads(raw);self.requests.append((path,body))
                    if body["limit"]!=100:raise ValueError("page limit")
                    id=body["requestId"];status=200
                    if path=="/v1/sync/user":
                        start=0 if body["cursor"]=="0" else int(body["cursor"].split("-")[1]);events=[]
                        for n in range(start+1,min(start+100,self.user_count)+1):
                            kind="conversation.changed" if n==1 else "membership.changed" if n in (2,3) else "friend.changed" if n%2 else "plugin.changed"
                            subject=C if n==1 else D if n==2 else DENIED if n==3 else uid(30000+n)
                            events.append(dict(eventId=uid(20000+n),cursor="u-"+str(n),kind=kind,subjectId=subject,revision=n))
                        result=dict(syncVersion="1.0",type="sync.user.page",requestId=id,events=events,nextCursor=events[-1]["cursor"] if events else body["cursor"],hasMore=start+len(events)<self.user_count)
                    else:
                        c=body["conversationId"];after=body["afterSeq"]
                        if c==DENIED:status=403;result=dict(requestId=id,error=dict(code="AUTHORIZATION_DENIED",message="Denied"))
                        else:
                            head=self.head if c==C else 2;messages=[message(n,c) for n in range(after+1,min(after+100,head)+1)]
                            result=dict(syncVersion="1.0",type="sync.conversation.page",requestId=id,conversationId=c,messages=messages,hasMore=after+len(messages)<head)
                else:raise ValueError("path")
                raw=json.dumps(result,separators=(",",":")).encode()
                s.sendall(("HTTP/1.1 "+str(status)+" OK\r\nContent-Type: application/json\r\nCache-Control: no-store\r\nContent-Length: "+str(len(raw))+"\r\nConnection: close\r\n\r\n").encode()+raw)
        except (EOFError,ConnectionError,OSError,ssl.SSLError):pass
        except Exception as error:self.errors.append(type(error).__name__+": "+str(error))
    def close(self):self.server.close()

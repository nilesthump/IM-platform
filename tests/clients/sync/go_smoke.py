"""Real accepted public Sync client integration, optional actual Desktop SQLx."""
from pathlib import Path
import argparse,importlib.util,json,os,secrets,socket,ssl,subprocess,tempfile,time,urllib.request,uuid
ROOT=Path(__file__).resolve().parents[3]
def main():
    p=argparse.ArgumentParser();p.add_argument("--probe");a=p.parse_args()
    project="im-client-sync-"+str(os.getpid())+"-"+secrets.token_hex(4);env=os.environ.copy()
    with socket.socket() as s:s.bind(("127.0.0.1",0));port=s.getsockname()[1]
    env.update(IM_HTTPS_PORT=str(port),COMPOSE_PROGRESS="quiet");docker=os.environ.get("IM_CLIENT_DOCKER","docker")
    command=[docker,"compose","-f",str(ROOT/"deploy/compose.yaml"),"-p",project,"--profile","go"]
    def execute(argv,data=None):
        r=subprocess.run(argv,env=env,input=data,capture_output=True,timeout=600)
        if r.returncode:raise RuntimeError("Owned actual Go fixture command failed")
        return r.stdout
    def compose(*args):return execute(command+list(args))
    def sql(query):return compose("exec","-T","postgres","psql","-U","im","-d","im","-v","ON_ERROR_STOP=1","-Atc",query).decode().strip()
    npm="npm.cmd" if os.name=="nt" else "npm"
    for package in ["clients/shared/protocol-sdk"]+(["clients/desktop"] if a.probe else []):
        subprocess.run([npm,"--prefix",package,"ci","--ignore-scripts","--no-audit","--no-fund"],cwd=ROOT,check=True);subprocess.run([npm,"--prefix",package,"run","build"],cwd=ROOT,check=True)
    spec=importlib.util.spec_from_file_location("client_go_tls",ROOT/"tests/e2e/go_tls_messaging.py");h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    ws=None
    with tempfile.TemporaryDirectory(prefix="im-client-sync-go-") as temp:
        temp=Path(temp);config=temp/"config";config.mkdir();env["IM_GO_CONFIG_DIR"]=str(config)
        (config/"config.json").write_bytes((ROOT/"backend/go/config.example.json").read_bytes());(config/"pg_password").write_bytes(b"local-development-only");(config/"jwt_key").write_bytes(secrets.token_urlsafe(48).encode())
        try:
            print("Starting bounded owned actual Go/PostgreSQL/TLS client Sync fixture",flush=True);compose("up","-d","--build")
            tls=compose("ps","-q","tls-go").decode().strip();ca=temp/"root.crt"
            for _ in range(120):
                try:execute([docker,"cp",tls+":/data/caddy/pki/authorities/local/root.crt",str(ca)]);break
                except RuntimeError:time.sleep(.5)
            else:raise RuntimeError("Trusted CA unavailable")
            context=ssl.create_default_context(cafile=str(ca))
            def call(method,path,body=None,token=None):
                headers={"Content-Type":"application/json"}
                if token:headers["Authorization"]="Bearer "+token
                request=urllib.request.Request("https://localhost:"+str(port)+path,data=None if body is None else json.dumps(body).encode(),headers=headers,method=method)
                with urllib.request.urlopen(request,context=context,timeout=20) as response:return json.loads(response.read() or b"{}")
            for _ in range(120):
                try:urllib.request.urlopen("https://localhost:"+str(port)+"/__infra/health",context=context,timeout=2).close();break
                except OSError:time.sleep(.5)
            else:raise RuntimeError("Go TLS unavailable")
            users=[];logins=[]
            for i in range(2):
                name="clientsync"+secrets.token_hex(8);password="fixture-password-not-a-real-secret"
                users.append(call("POST","/v1/auth/register",{"username":name,"password":password,"displayName":name})["user"]["userId"])
                logins.append(call("POST","/v1/auth/login",{"username":name,"password":password,"clientType":"DESKTOP" if i==0 else "MOBILE","deviceId":"sync-smoke-"+str(i),"clientVersion":"1.0.0","protocolVersion":"1"}))
            token=logins[0]["tokens"]["accessToken"];c=call("PUT","/v1/friends/"+users[1],{},token)["directConversationId"]
            def event_fixture(count):
                sql(f"""DO $$ DECLARE n bigint; e uuid; k text; BEGIN
                PERFORM user_id FROM users WHERE user_id='{users[0]}' FOR UPDATE;
                FOR i IN 1..{count} LOOP k := (ARRAY['friend.changed','conversation.changed','membership.changed','plugin.changed'])[(i-1)%4+1];e:=gen_random_uuid();
                INSERT INTO user_sync_events(user_id,event_type,payload) VALUES('{users[0]}',k,'{{}}') RETURNING cursor_id INTO n;
                UPDATE user_sync_events SET payload=jsonb_build_object('eventId',e,'cursor',n::text,'kind',k,'subjectId','{c}','revision',1) WHERE cursor_id=n;
                END LOOP; END $$;""")
            event_fixture(205);ws=h.WS(context,port);ws.send(h.frame("auth.bind",{"accessToken":token}));assert ws.read()["payload"]["status"]=="bound"
            first=None
            def send_message(n):
                frame=h.frame("message.send",{"conversationId":c,"content":{"kind":"TEXT","text":"actual-sync-"+str(n-1)}});ws.send(frame)
                for _ in range(10):
                    result=ws.read()
                    if result["type"]=="message.ack" and result["requestId"]==frame["requestId"]:
                        assert result["payload"]["status"]=="committed" and result["payload"]["seq"]==n;return frame["requestId"]
                raise RuntimeError("Durable ACK absent")
            for n in range(1,206):
                rid=send_message(n)
                if first is None:first=rid
            private={"endpoint":"https://localhost:"+str(port),"conversationId":c,"firstRequestId":first,"session":{"userId":users[0],"sessionId":logins[0]["session"]["sessionId"],"sessionEpoch":logins[0]["session"]["sessionEpoch"],"accessToken":token}}
            if a.probe:private.update(probe=str(Path(a.probe).resolve()),localRoot=str(temp/"sqlite"))
            nodeenv=env.copy();nodeenv["NODE_EXTRA_CA_CERTS"]=str(ca)
            def client(phase):
                before=sql("SELECT (SELECT count(*) FROM messages)||','||(SELECT count(*) FROM outbox_events)")
                private.update(phase=phase,expected=205 if phase==1 else 206)
                r=subprocess.run(["node","tests/clients/sync/go_client.mjs"],cwd=ROOT,env=nodeenv,input=json.dumps(private),capture_output=True,text=True,timeout=180)
                if r.returncode:raise RuntimeError("Actual client Sync integration failed: "+r.stderr[:1000])
                result=json.loads(r.stdout);assert result["result"]=="PASS"
                assert sql("SELECT (SELECT count(*) FROM messages)||','||(SELECT count(*) FROM outbox_events)")==before
                private.update(cursor=result["cursor"],afterSeq="205");return result
            first_result=client(1);send_message(206);event_fixture(1);second_result=client(2)
            assert first_result["cursor"]!=second_result["cursor"]
            print("PASS: actual "+("Desktop SQLx orchestration" if a.probe else "shared Sync HTTPS adapter")+" -> trusted TLS/Gateway/Core/PG;208metadata205durableMessages,continuous pages/terminal/restart/new206th/read-only",flush=True)
        finally:
            if ws:ws.close()
            for kind,listing in (("container",[docker,"ps","-aq","--filter","label=com.docker.compose.project="+project]),("volume",[docker,"volume","ls","-q","--filter","label=com.docker.compose.project="+project])):
                for name in execute(listing).decode().split():
                    obj=json.loads(execute([docker,kind,"inspect",name]))[0];labels=obj["Config"]["Labels"] if kind=="container" else obj["Labels"]
                    if labels.get("com.docker.compose.project")!=project:raise RuntimeError("Owned cleanup mismatch")
            compose("down","--volumes","--remove-orphans")
            assert not execute([docker,"ps","-aq","--filter","label=com.docker.compose.project="+project]).strip()
            assert not execute([docker,"volume","ls","-q","--filter","label=com.docker.compose.project="+project]).strip()
            print("PASS: inspected only task-owned Compose containers/volumes cleanup",flush=True)
if __name__=="__main__":main()

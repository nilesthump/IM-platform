from pathlib import Path
import re
R=Path('backend/go')
def put(p,s):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
a=(R/'auth.go').read_text(encoding='utf-8');g=(R/'gateway.go').read_text(encoding='utf-8')
def fn(s,name):
 m=re.search(r'^func '+re.escape(name)+r'\b',s,re.M)
 if not m: raise ValueError(name)
 n=re.search(r'^func ',s[m.end():],re.M)
 return s[m.start():m.end()+n.start()] if n else s[m.start():]
def method(s,name):
 m=re.search(r'^func \(s \*authService\) '+name+r'\(',s,re.M)
 n=re.search(r'^func ',s[m.end():],re.M)
 return s[m.start():m.end()+n.start()] if n else s[m.start():]
claims=a[a.index('type claims struct'):a.index('type apiError struct')].replace('type claims','type Claims')
err=a[a.index('type apiError struct'):a.index('func randomToken')].replace('apiError','Error').replace('status  int','Status  int').replace('code    string','Code    string').replace('message string','Message string').replace('e.code','e.Code').replace('func fail(','func Fail(')
sec='package shared\n\nimport ("crypto/hmac";"crypto/rand";"crypto/sha256";"encoding/base64";"encoding/hex";"encoding/json";"strings";"time")\n\n'+claims+err+'type Codec struct {Key []byte; Now func() time.Time}\n\n'
for name in ['randomToken','uuid','hashToken']:
 sec+=fn(a,name).replace('func '+name,'func '+{'randomToken':'RandomToken','uuid':'UUID','hashToken':'HashToken'}[name])
for name in ['sign','parse']:
 sec+=method(a,name).replace('*authService','*Codec').replace(') '+name+'(',') '+name.title()+'(').replace('claims','Claims').replace('s.key','s.Key').replace('s.now','s.Now').replace('fail(','Fail(').replace('validClient(','ValidClient(')
sec+='func ValidClient(t string) bool { return t == "WEB" || t == "DESKTOP" || t == "MOBILE" }\n'
put(Path('shared/security.go'),sec)
# Core private writes and read authorization preserved, crypto support delegated.
for text in [a[a.index('type claims struct'):a.index('func randomToken')],fn(a,'randomToken'),fn(a,'uuid'),fn(a,'hashToken'),method(a,'sign'),method(a,'parse')]:a=a.replace(text,'')
a=a.replace('package main','package core',1).replace('"crypto/hmac"\n','').replace('"crypto/rand"\n','').replace('"encoding/base64"\n','')
a=a.replace('"golang.org/x/crypto/bcrypt"','"golang.org/x/crypto/bcrypt"\n "im-platform/backend/go/shared"')
a=a.replace('key    []byte','codec *shared.Codec').replace('revoke func(string, string)','')
a=a.replace('s.parse(','s.codec.Parse(').replace('s.sign(','s.codec.Sign(')
a=a.replace('if replaced && s.revoke != nil {\n\t\ts.revoke(oldID, "REPLACED")\n\t}', '').replace('if s.revoke != nil {\n\t\ts.revoke(sid, "LOGOUT")\n\t}', '')
a=a.replace('e.status','e.Status').replace('e.code','e.Code').replace('e.message','e.Message')
a+='\ntype claims = shared.Claims\ntype apiError = shared.Error\nfunc fail(status int,code,message string) error { return shared.Fail(status,code,message) }\nfunc uuid()(string,error){return shared.UUID()}\nfunc randomToken(n int)(string,error){return shared.RandomToken(n)}\nfunc hashToken(t string)string{return shared.HashToken(t)}\n'
put(Path('core/auth.go'),a)
put(Path('core/outbox.go'),(R/'outbox.go').read_text().replace('package main','package core',1).replace('func relaySessionRevocations','func RelaySessionRevocations'))
put(Path('shared/config.go'),(R/'config.go').read_text().replace('package main','package shared',1).replace('runtimeConfig','RuntimeConfig').replace('readConfig','ReadConfig'))
# Gateway owns independent read-only Session authority. It never signs or writes.
v=method((R/'auth.go').read_text(), 'authenticate').replace('*authService','*validator').replace('claims','shared.Claims').replace('s.parse(token)','s.codec.Parse(token)').replace('fail(','shared.Fail(')
put(Path('gateway/session.go'),'package gateway\nimport("context";"errors";"time";"github.com/jackc/pgx/v5";"github.com/jackc/pgx/v5/pgxpool";"im-platform/backend/go/shared")\ntype validator struct {db *pgxpool.Pool;codec *shared.Codec;now func()time.Time}\n'+v)
g=g.replace('package main','package gateway',1).replace('"github.com/gorilla/websocket"','"github.com/gorilla/websocket"\n "im-platform/backend/go/shared"')
g=g.replace('*authService','*validator').replace('*claims','*shared.Claims').replace('cl claims','cl shared.Claims').replace('uuid()','shared.UUID()').replace('apiError','shared.Error').replace('ae.code','ae.Code').replace('ae.message','ae.Message')
g=g.replace('bound *shared.Claims','bound *shared.Claims\n token string')
g=g.replace('c.bound = &cl','c.bound = &cl\n c.token = p.AccessToken').replace('h.auth.mustSign(*c.bound)','c.token').replace('h.auth.mustSign(cl)','c.token')
g=re.sub(r'^func \(s \*validator\) mustSign[^\n]*\n','',g,flags=re.M)
g=g.replace('writeError(w, r, fail(','writeError(w, r, shared.Fail(')
g+='\nfunc writeError(w http.ResponseWriter,r *http.Request,err error){e:=shared.Error{Status:500,Code:"INTERNAL_ERROR",Message:"Internal server error."};if v,ok:=err.(shared.Error);ok{e=v};id,_:=shared.UUID();w.Header().Set("Content-Type","application/json");w.WriteHeader(e.Status);_ = json.NewEncoder(w).Encode(map[string]any{"error":map[string]string{"code":e.Code,"message":e.Message},"requestId":id})}\n'
put(Path('gateway/gateway.go'),g)
# Runtime APIs are consumed by root assembly; no full business service exported.
put(Path('core/http.go'),'''package core
import("net/http";"time";"github.com/jackc/pgx/v5/pgxpool";"im-platform/backend/go/shared")
func NewHandler(db *pgxpool.Pool,key []byte) http.Handler {
 s:=&authService{db:db,codec:&shared.Codec{Key:key,Now:time.Now},now:time.Now}
 m:=shared.InfraMux("core");m.Handle("/v1/",s.handler());return m
}
''')
put(Path('gateway/http.go'),'''package gateway
import("encoding/json";"net/http";"net/http/httputil";"net/url";"time";"github.com/jackc/pgx/v5/pgxpool";"github.com/nats-io/nats.go";"im-platform/backend/go/shared")
func NewHandler(db *pgxpool.Pool,key []byte,nc *nats.Conn,coreURL string)(http.Handler,error){
 h:=newHub(&validator{db:db,codec:&shared.Codec{Key:key,Now:time.Now},now:time.Now})
 if nc!=nil{if _,err:=nc.Subscribe("session.revoked",func(m *nats.Msg){var v struct{SessionID string `json:"sessionId"`;Reason string `json:"reason"`};if json.Unmarshal(m.Data,&v)==nil{h.revoke(v.SessionID,v.Reason)}});err!=nil{return nil,err};if err:=nc.Flush();err!=nil{return nil,err}}
 m:=shared.InfraMux("gateway");m.HandleFunc("GET /v1/ws",h.serve)
 u,err:=url.Parse(coreURL);if err!=nil{return nil,err};m.Handle("/v1/",httputil.NewSingleHostReverseProxy(u));return m,nil
}
''')
put(Path('shared/infra.go'),'''package shared
import("crypto/sha1";"encoding/base64";"fmt";"net/http";"strings")
// InfraMux is the existing non-business role health and transport probe.
func InfraMux(role string)*http.ServeMux{
 m:=http.NewServeMux();m.HandleFunc("/__infra/health",func(w http.ResponseWriter,r *http.Request){if r.Method!="GET"{http.Error(w,"method not allowed",405);return};w.Header().Set("Content-Type","text/plain; charset=utf-8");fmt.Fprintf(w,"profile=go role=%s\\n",role)})
 m.HandleFunc("/__infra/ws",func(w http.ResponseWriter,r *http.Request){if role!="gateway"||!strings.EqualFold(r.Header.Get("Upgrade"),"websocket")||r.Header.Get("Sec-WebSocket-Key")==""{http.NotFound(w,r);return};sum:=sha1.Sum([]byte(r.Header.Get("Sec-WebSocket-Key")+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"));w.Header().Set("Upgrade","websocket");w.Header().Set("Connection","Upgrade");w.Header().Set("Sec-WebSocket-Accept",base64.StdEncoding.EncodeToString(sum[:]));w.WriteHeader(101)});return m
}
''')
put(Path('plugin-host/http.go'),'''package pluginhost
import("net/http";"im-platform/backend/go/shared")
// No plugin business is introduced in this Auth remediation.
func NewHandler()http.Handler{return shared.InfraMux("plugin-host")}
''')
put(Path('main.go'),'''package main
import("context";"log";"net/http";"os";"time";"github.com/jackc/pgx/v5/pgxpool";"github.com/nats-io/nats.go";"im-platform/backend/go/core";"im-platform/backend/go/gateway";pluginhost "im-platform/backend/go/plugin-host";"im-platform/backend/go/shared")
func main(){
 if len(os.Args)!=2{log.Fatal("expected gateway, core, or plugin-host role")};role:=os.Args[1];if role!="gateway"&&role!="core"&&role!="plugin-host"{log.Fatal("unknown role")}
 if role=="plugin-host"{log.Fatal(http.ListenAndServe(":8080",pluginhost.NewHandler()))}
 path:=os.Getenv("IM_CONFIG_FILE");if path==""{path="/run/im-config/config.json"};cfg,key,pg,err:=shared.ReadConfig(path);if err!=nil{log.Fatal("Go runtime configuration unavailable")}
 db,err:=pgxpool.NewWithConfig(context.Background(),pg);if err!=nil{log.Fatal("database configuration failed")};defer db.Close();ctx,cancel:=context.WithTimeout(context.Background(),10*time.Second);err=db.Ping(ctx);cancel();if err!=nil{log.Fatal("database unavailable")}
 nc,err:=nats.Connect(cfg.NATSURL,nats.MaxReconnects(-1));if err!=nil{log.Fatal("NATS unavailable")};defer nc.Close()
 var h http.Handler
 if role=="core"{ctx,stop:=context.WithCancel(context.Background());defer stop();go core.RelaySessionRevocations(ctx,db,nc);h=core.NewHandler(db,key)}else{h,err=gateway.NewHandler(db,key,nc,cfg.CoreURL);if err!=nil{log.Fatal("gateway configuration failed")}}
 log.Fatal(http.ListenAndServe(":8080",h))
}
''')
for name in ['auth.go','config.go','gateway.go','outbox.go']:(R/name).unlink()

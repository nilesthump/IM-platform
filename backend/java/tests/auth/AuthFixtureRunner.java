package im.platform.tests.auth;

import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.*;
import im.platform.shared.authsupport.*;
import java.net.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.sql.*;

/** The same real-endpoint assertions run unchanged against both deployed role implementations. */
public final class AuthFixtureRunner {
    static final ObjectMapper JSON=new ObjectMapper();
    final HttpClient http=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(5)).build();
    final String base,profile; final Path root; final Config config; final Tokens codec;
    final Map<String,JsonNode> positive,negative,wss;
    final Set<String> passed=new LinkedHashSet<>();
    AuthFixtureRunner(String base,String profile,Path root,Config config)throws Exception{
        this.base=base;this.profile=profile;this.root=root;this.config=config;codec=new Tokens(config.signingKey());
        positive=fixtures("auth-user-friend/positive.json");negative=fixtures("auth-user-friend/negative.json");wss=fixtures("websocket/golden.json");
    }
    Map<String,JsonNode> fixtures(String path)throws Exception{Map<String,JsonNode> result=new LinkedHashMap<>();for(JsonNode s:JSON.readTree(root.resolve("contracts/fixtures/"+path).toFile()).get("scenarios")){if(result.put(s.get("id").textValue(),s)!=null)throw new AssertionError("Duplicate fixture");}return result;}
    static void require(boolean value,String message){if(!value)throw new AssertionError(message);}
    static boolean uuid(String value){return value.matches("[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}");}
    static final class Normalize{
        final String username;final Map<String,String> values=new HashMap<>();
        Normalize(String username){this.username=username;}
        void check(JsonNode expected,JsonNode actual,String path){
            require(actual!=null,"Missing "+path);
            if(expected.isObject()){require(actual.isObject(),"Object "+path);expected.fields().forEachRemaining(e->check(e.getValue(),actual.get(e.getKey()),path+"."+e.getKey()));}
            else if(expected.isArray()){require(actual.isArray()&&expected.size()==actual.size(),"Array "+path);for(int i=0;i<expected.size();i++)check(expected.get(i),actual.get(i),path+"["+i+"]");}
            else if(expected.isTextual()){
                require(actual.isTextual(),"Text "+path);String e=expected.textValue(),a=actual.textValue();
                if(path.equals("body.requestId")){require(uuid(a),"Request UUID");return;}
                if(uuid(e)||e.startsWith("<")&&e.endsWith(">")){
                    require(!a.isEmpty()&&(!uuid(e)||uuid(a)),"Generated value "+path);
                    String old=values.putIfAbsent(e,a);require(old==null||old.equals(a),"Inconsistent generated value "+path);
                    if(old==null)for(var pair:values.entrySet())require(pair.getKey().equals(e)||!pair.getValue().equals(a),"Generated value collision "+path);
                }else require((e.equals("alice")?username:e).equals(a),"Fixture mismatch "+path+" expected="+e);
            }else if(expected.isNumber())require(actual.isNumber()&&expected.decimalValue().compareTo(actual.decimalValue())==0,"Number "+path);
            else require(expected.equals(actual),"Fixture mismatch "+path);
        }
    }
    record Reply(int status,JsonNode body,HttpHeaders headers){String token(){return body.path("tokens").path("accessToken").textValue();}String refresh(){return body.path("tokens").path("refreshToken").textValue();}String cookie(){return headers.firstValue("set-cookie").orElseThrow().split(";",2)[0];}}
    Reply call(String method,String path,JsonNode body,String token,String cookie)throws Exception{
        Map<String,String> headers=new LinkedHashMap<>();if(token!=null)headers.put("Authorization","Bearer "+token);if(cookie!=null)headers.put("Cookie",cookie);
        return callHeaders(method,path,body,headers);
    }
    Reply callHeaders(String method,String path,JsonNode body,Map<String,String> headers)throws Exception{
        var request=HttpRequest.newBuilder(URI.create(base+path)).timeout(Duration.ofSeconds(10));
        headers.forEach(request::header);
        if(body!=null)request.header("Content-Type","application/json");
        request.method(method,body==null?HttpRequest.BodyPublishers.noBody():HttpRequest.BodyPublishers.ofString(JSON.writeValueAsString(body)));
        var response=http.send(request.build(),HttpResponse.BodyHandlers.ofString());
        return new Reply(response.statusCode(),response.body().isBlank()?NullNode.instance:JSON.readTree(response.body()),response.headers());
    }
    static ObjectNode body(JsonNode source,String username){ObjectNode b=source==null?JSON.createObjectNode():source.deepCopy();if(b.path("username").asText().equalsIgnoreCase("alice")){String old=b.get("username").textValue();b.put("username",old.equals(old.toUpperCase(Locale.ROOT))?username.toUpperCase(Locale.ROOT):username);}return b;}
    Reply step(JsonNode step,Normalize n,String token,String cookie,ObjectNode override)throws Exception{
        JsonNode r=step.get("request"),expected=step.get("expected");String path=r.get("path").textValue();
        if(r.has("query")){StringJoiner query=new StringJoiner("&");r.get("query").fields().forEachRemaining(e->query.add(URLEncoder.encode(e.getKey(),java.nio.charset.StandardCharsets.UTF_8)+"="+URLEncoder.encode(e.getValue().asText().equalsIgnoreCase("alice")?n.username:e.getValue().asText(),java.nio.charset.StandardCharsets.UTF_8)));path+="?"+query;}
        ObjectNode b=body(r.get("body"),n.username);if(override!=null)b.setAll(override);
        Map<String,String> headers=new LinkedHashMap<>();
        if(r.has("headers"))r.get("headers").fields().forEachRemaining(e->{String value=e.getValue().textValue();if(value.contains("<")){if(e.getKey().equals("Authorization")){require(token!=null,"Missing fixture access token");value=value.replaceAll("<[^>]+>",java.util.regex.Matcher.quoteReplacement(token));}else if(e.getKey().equals("Cookie")){require(cookie!=null,"Missing fixture cookie");value=value.replaceAll("<[^>]+>",java.util.regex.Matcher.quoteReplacement(cookie.split("=",2)[1]));}else throw new AssertionError("Unresolved fixture header");}headers.put(e.getKey(),value);});
        Reply reply=callHeaders(r.get("method").textValue(),path,r.has("body")||override!=null?b:null,headers);
        require(reply.status==expected.get("status").intValue(),path+" status="+reply.status+" expected="+expected.get("status"));
        if(expected.has("body"))n.check(expected.get("body"),reply.body,"body");
        if(expected.path("headers").has("Set-Cookie")){
            Map<String,String> attributes=new HashMap<>();for(String part:reply.headers.firstValue("set-cookie").orElseThrow().split(";")){String[] pair=part.strip().split("=",2);attributes.put(pair[0].toLowerCase(Locale.ROOT),pair.length==1?"":pair[1]);}
            for(String part:expected.get("headers").get("Set-Cookie").textValue().split(";")){String[] pair=part.strip().split("=",2);String actual=attributes.get(pair[0].toLowerCase(Locale.ROOT));require(actual!=null,"Missing cookie attribute "+pair[0]);n.check(JSON.valueToTree(pair.length==1?"":pair[1]),JSON.valueToTree(actual),"header.Set-Cookie."+pair[0]);}
        }
        if(reply.body.has("tokens")){Tokens.Claims claims=codec.parse(reply.token());JsonNode session=reply.body.get("session");require(claims.userId().equals(session.get("userId").textValue())&&claims.sessionId().equals(session.get("sessionId").textValue())&&claims.clientType().equals(session.get("clientType").textValue())&&claims.epoch()==session.get("sessionEpoch").longValue()&&claims.expires()-claims.issued()==reply.body.get("tokens").get("accessTokenExpiresInSeconds").longValue(),"Response JWT claims disagree with Session");}
        return reply;
    }
    static JsonNode step(Map<String,JsonNode> source,String id,int index){return Objects.requireNonNull(source.get(id),"Missing fixture "+id).get("steps").get(index);}
    static ObjectNode override(String key,String value){return JSON.createObjectNode().put(key,value);}
    Reply login(ObjectNode body)throws Exception{Reply r=call("POST","/v1/auth/login",body,null,null);require(r.status==200,"Setup login "+r.status);return r;}
    String signed(String token,String change)throws Exception{
        Tokens.Claims c=codec.parse(token);return codec.sign(new Tokens.Claims(c.userId(),change.equals("binding")?UUID.randomUUID().toString():c.sessionId(),change.equals("client")?"DESKTOP":c.clientType(),c.epoch(),change.equals("expired")?Instant.now().minusSeconds(7200).getEpochSecond():c.issued(),change.equals("expired")?Instant.now().minusSeconds(3600).getEpochSecond():c.expires()));
    }
    void httpFixtures()throws Exception{
        String username="jfixture"+UUID.randomUUID().toString().replace("-","");Normalize n=new Normalize(username);
        String register="registration-and-authorized-user-search",slots="same-slot-login-replaces-only-that-slot";
        step(step(positive,register,0),n,null,null,null);
        ObjectNode login=body(step(positive,slots,0).get("request").get("body"),username);
        Reply web1=step(step(positive,slots,0),n,null,null,null);
        step(step(positive,register,1),n,web1.token(),null,null);passed.add(register);
        Reply desktop=step(step(positive,slots,1),n,null,null,null),web2=step(step(positive,slots,2),n,null,null,null);
        step(step(positive,slots,3),n,web2.token(),null,null);step(step(positive,slots,4),n,desktop.token(),null,null);passed.add(slots);
        String user=web2.body.path("session").path("userId").textValue();
        try(var db=config.database().getConnection();var q=db.prepareStatement("SELECT count(*) FROM sessions WHERE user_id=? AND status='ACTIVE'")){q.setObject(1,UUID.fromString(user));try(var rs=q.executeQuery()){require(rs.next()&&rs.getInt(1)==2,"Slot count");}}
        ObjectNode mobileBody=body(step(positive,slots,1).get("request").get("body"),username).put("clientType","MOBILE").put("deviceId","mobile-1");
        Reply mobile=null;for(int i=0;i<4;i++)mobile=login(mobileBody);String oldRefresh=mobile.refresh();
        String nativeID="native-refresh-rotates-current-session-credential";Reply nativeRefresh=step(step(positive,nativeID,0),n,null,null,override("refreshToken",oldRefresh));require(!oldRefresh.equals(nativeRefresh.refresh()),"Native rotation");passed.add(nativeID);
        login.put("deviceId","browser-5");for(int i=0;i<3;i++)web2=login(login);
        String webID="web-refresh-rotates-secure-cookie";Reply refreshed=step(step(positive,webID,0),n,null,web2.cookie(),null);require(!web2.cookie().equals(refreshed.cookie()),"Cookie rotation");passed.add(webID);
        for(String id:List.of("invalid-credentials","token-in-query-rejected","invalid-client-type","refresh-client-type-mismatch","unsupported-protocol-version","missing-authentication","authorization-binding-mismatch","invalid-access-token","expired-access-token","username-already-exists","web-refresh-missing-cookie","native-refresh-missing-token","stale-session-epoch-rejected","revoked-refresh-token-rejected")){
            String token=switch(id){case "authorization-binding-mismatch"->signed(refreshed.token(),"binding");case "invalid-access-token"->refreshed.token()+"x";case "expired-access-token"->signed(refreshed.token(),"expired");case "stale-session-epoch-rejected"->web1.token();default->null;};
            ObjectNode extra=switch(id){case "refresh-client-type-mismatch"->override("refreshToken",desktop.refresh());case "revoked-refresh-token-rejected"->override("refreshToken",oldRefresh);default->null;};
            step(step(negative,id,0),n,token,null,extra);passed.add(id);
        }
        try(Socket socket=socket()){
            socket.send(frame("auth.bind",Map.of("accessToken",desktop.token())));require(socket.next().path("payload").path("status").asText().equals("bound"),"Logout socket bind");
            String id="logout-revokes-session-refresh-and-connection";step(step(positive,id,0),n,desktop.token(),null,null);
            JsonNode event=socket.next();require(event.path("type").asText().equals("session.revoked")&&event.path("payload").path("reason").asText().equals("LOGOUT"),"Logout notification");socket.closed();passed.add(id);
        }
        step(step(negative,"revoked-session-token",0),n,desktop.token(),null,null);passed.add("revoked-session-token");
        try(var db=config.database().getConnection();var q=db.prepareStatement("SELECT status,refresh_token_hash FROM sessions WHERE user_id=? AND client_type='DESKTOP'")){q.setObject(1,UUID.fromString(user));try(var rs=q.executeQuery()){require(rs.next()&&rs.getString(1).equals("REVOKED")&&rs.getString(2)==null,"Logout persistence");}}
        concurrent(login,user);
        if(profile.equals("java")){
            // Persisted corruption is an internal invariant failure, never an
            // ordinary wrong-password outcome. Restore the fixture row exactly.
            try(var db=config.database().getConnection();var read=db.prepareStatement("SELECT password_hash FROM users WHERE user_id=?")){
                read.setObject(1,UUID.fromString(user));String original;try(var rows=read.executeQuery()){require(rows.next(),"Corruption probe user");original=rows.getString(1);}
                try(var update=db.prepareStatement("UPDATE users SET password_hash=? WHERE user_id=?")){
                    update.setString(1,"invalid-stored-bcrypt");update.setObject(2,UUID.fromString(user));require(update.executeUpdate()==1,"Corruption setup");
                    try{Reply failure=call("POST","/v1/auth/login",login,null,null);require(failure.status==500,"Persisted hash corruption was hidden as credential rejection");}
                    finally{update.setString(1,original);require(update.executeUpdate()==1,"Corruption restoration");}
                }
            }
            System.out.println("INVARIANT java malformed persisted BCrypt produces HTTP500 PASS");
        }
        // Exercise the real transport with mutations to canonical expected data
        // and input. A runner that merely enumerates fixture IDs cannot pass.
        ObjectNode changedExpected=step(negative,"invalid-credentials",0).deepCopy();
        ((ObjectNode)changedExpected.get("expected").get("body").get("error")).put("code","MUTATED_EXPECTATION");
        boolean rejected=false;try{step(changedExpected,n,null,null,null);}catch(AssertionError mismatch){require(mismatch.getMessage().contains("body.error.code"),"Mutation failed for unrelated reason");rejected=true;}
        require(rejected,"Changed canonical expectation was ignored");
        ObjectNode changedInput=step(positive,register,0).deepCopy();((ObjectNode)changedInput.get("request").get("body")).put("username","!");
        rejected=false;try{step(changedInput,n,null,null,null);}catch(AssertionError mismatch){require(mismatch.getMessage().contains("status=400"),"Input mutation failed for unrelated reason");rejected=true;}
        require(rejected,"Changed canonical input was ignored");
        System.out.println("FIXTURE_MUTATION "+profile+" expected-code and request-username detected");
    }
    static ObjectNode frame(String type,Object payload){ObjectNode n=JSON.createObjectNode();n.put("protocolVersion","1.0").put("type",type).put("requestId",UUID.randomUUID().toString());n.set("payload",JSON.valueToTree(payload));return n;}
    final class Socket implements WebSocket.Listener,AutoCloseable{
        final BlockingQueue<Object> messages=new LinkedBlockingQueue<>();final StringBuilder text=new StringBuilder();WebSocket ws;
        public void onOpen(WebSocket ws){ws.request(1);}
        public CompletionStage<?> onText(WebSocket ws,CharSequence data,boolean last){text.append(data);if(last){messages.add(text.toString());text.setLength(0);}ws.request(1);return null;}
        public CompletionStage<?> onClose(WebSocket ws,int status,String reason){messages.add(Integer.valueOf(status));return null;}
        public void onError(WebSocket ws,Throwable error){messages.add(error);}
        void send(JsonNode value)throws Exception{ws.sendText(JSON.writeValueAsString(value),true).get(5,TimeUnit.SECONDS);}
        Object receive()throws Exception{Object value=messages.poll(5,TimeUnit.SECONDS);require(value!=null,"WSS timeout");if(value instanceof Throwable t)throw new AssertionError("WSS transport",t);return value;}
        JsonNode next()throws Exception{Object value=receive();require(value instanceof String,"WSS closed before event");return JSON.readTree((String)value);}
        void closed()throws Exception{Object terminal=messages.poll(5,TimeUnit.SECONDS);require(terminal!=null,"WSS close timeout inputClosed="+ws.isInputClosed()+" outputClosed="+ws.isOutputClosed());if(terminal instanceof java.io.IOException transport){require(ws.isInputClosed()&&ws.isOutputClosed(),"Transport error without terminal socket");return;}if(terminal instanceof Throwable t)throw new AssertionError("WSS close transport",t);require(terminal instanceof Integer,"Expected WSS close after revocation");}
        void afterRevoke(JsonNode input)throws Exception{try{send(input);}catch(ExecutionException failure){if(!(failure.getCause() instanceof java.io.IOException)||!ws.isOutputClosed())throw failure;}closed();}
        public void close(){ws.abort();}
    }
    Socket socket()throws Exception{Socket s=new Socket();s.ws=http.newWebSocketBuilder().connectTimeout(Duration.ofSeconds(5)).buildAsync(URI.create(base.replaceFirst("^http","ws")+"/v1/ws"),s).get(10,TimeUnit.SECONDS);return s;}
    void wsStep(Socket socket,String id,Normalize n,String token)throws Exception{JsonNode step=step(wss,id,0);ObjectNode sent=step.get("in").deepCopy();if(token!=null)((ObjectNode)sent.get("payload")).put("accessToken",token);socket.send(sent);for(JsonNode e:step.get("out")){JsonNode actual=socket.next();require(actual.get("requestId").equals(sent.get("requestId")),"WSS requestId echo");n.check(e,actual,"wss");}passed.add(id);}
    void socketFixtures()throws Exception{
        String username="jws"+UUID.randomUUID().toString().replace("-","");Normalize n=new Normalize(username);
        ObjectNode reg=JSON.createObjectNode().put("username",username).put("password","fixture-password-not-a-real-secret").put("displayName","Alice");require(call("POST","/v1/auth/register",reg,null,null).status==201,"WSS setup register");
        ObjectNode login=body(step(positive,"same-slot-login-replaces-only-that-slot",0).get("request").get("body"),username);Reply first=login(login);
        for(String id:List.of("ping-before-bind","unauthenticated-send","invalid-signature-bind","expired-token-bind"))try(Socket s=socket()){wsStep(s,id,n,id.equals("invalid-signature-bind")?"not-a-valid-JWT":id.equals("expired-token-bind")?signed(first.token(),"expired"):null);}
        try(Socket bound=socket()){
            wsStep(bound,"bind-valid-session",n,first.token());Reply second=login(login);
            try(Socket stale=socket()){wsStep(stale,"stale-epoch-bind",n,first.token());}
            try(Socket wrong=socket()){wsStep(wrong,"wrong-client-type-bind",n,signed(second.token(),"client"));}
            n.check(step(wss,"revoked-socket",0).get("out").get(0),bound.next(),"wss");
            long[] before=messageCounts();bound.afterRevoke(step(wss,"revoked-socket",1).get("in"));
            require(Arrays.equals(before,messageCounts()),"Post-revocation message changed persistence");passed.add("revoked-socket");
        }
        Reply reconnect=login(login);
        // Simulate a committed revocation whose optimization event was lost.
        // Reconnect must consult Session persistence, never cached bind state.
        try(var db=config.database().getConnection();var q=db.prepareStatement("UPDATE sessions SET status='REVOKED',refresh_token_hash=NULL WHERE session_id=?")){q.setObject(1,UUID.fromString(reconnect.body.path("session").path("sessionId").textValue()));require(q.executeUpdate()==1,"Lost-event setup");}
        try(Socket s=socket()){s.send(frame("auth.bind",Map.of("accessToken",reconnect.token())));JsonNode ack=s.next();require(ack.path("payload").path("error").path("code").asText().equals("AUTH_SESSION_REVOKED"),"Reconnect ignored authoritative revoked Session");s.closed();}
        System.out.println("SESSION "+profile+" lost-notification reconnect rejects persisted revocation PASS");
    }
    long[] messageCounts()throws Exception{try(var db=config.database().getConnection();var q=db.createStatement();var rows=q.executeQuery("SELECT (SELECT count(*) FROM messages),(SELECT count(*) FROM outbox_events WHERE event_type LIKE 'message.%')")){require(rows.next(),"Message state query");return new long[]{rows.getLong(1),rows.getLong(2)};}}
    void concurrent(ObjectNode login,String user)throws Exception{
        try(var pool=Executors.newFixedThreadPool(4)){
            List<Future<Reply>> jobs=new ArrayList<>();for(int i=0;i<4;i++)jobs.add(pool.submit(()->login(login)));Set<Long> epochs=new HashSet<>();for(var job:jobs)epochs.add(job.get(15,TimeUnit.SECONDS).body.path("session").path("sessionEpoch").longValue());require(epochs.size()==4,"Concurrent login epochs");
        }
        try(var db=config.database().getConnection();var q=db.prepareStatement("SELECT count(*) FROM sessions WHERE user_id=? AND client_type='WEB'")){q.setObject(1,UUID.fromString(user));try(var rs=q.executeQuery()){require(rs.next()&&rs.getInt(1)==1,"Concurrent slot uniqueness");}}
    }
    void credentials(String mode,Path state)throws Exception{
        String username;
        if(mode.equals("create")){username="switch"+UUID.randomUUID().toString().replace("-","");ObjectNode b=JSON.createObjectNode().put("username",username).put("password","profile-switch-password-"+"X".repeat(90)).put("displayName","Switch");require(call("POST","/v1/auth/register",b,null,null).status==201,"Cross-profile register");Files.writeString(state,username);}
        else{username=Files.readString(state);ObjectNode b=body(step(positive,"same-slot-login-replaces-only-that-slot",0).get("request").get("body"),username).put("password","profile-switch-password-"+"X".repeat(90));login(b);}
        System.out.println("PROFILE_CREDENTIAL "+profile+" "+mode+" PASS");
    }
    public static void main(String[] args)throws Exception{
        require(args.length>=4,"base profile repository config required");AuthFixtureRunner run=new AuthFixtureRunner(args[0],args[1],Path.of(args[2]),Config.read(args[3]));
        if(args.length==6){run.credentials(args[4],Path.of(args[5]));return;}
        run.httpFixtures();run.socketFixtures();require(run.passed.size()==28,"Expected all 28 Auth fixtures");for(String id:run.passed)System.out.println("FIXTURE "+run.profile+" "+id+" PASS");
        System.out.println("LIVE_AUTH "+run.profile+" PASS 28 fixtures; slot concurrency, rotation, logout, real NATS revocation");
    }
}

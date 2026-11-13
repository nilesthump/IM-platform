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
    final Set<String> secrets=ConcurrentHashMap.newKeySet();
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
            if(expected.isObject()){require(actual.isObject(),"Object "+path);require(actual.size()==expected.size(),"Unexpected response fields "+path);expected.fields().forEachRemaining(e->check(e.getValue(),actual.get(e.getKey()),path+"."+e.getKey()));}
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
    void collect(JsonNode node){
        if(node==null)return;
        if(node.isObject())node.fields().forEachRemaining(e->{if(Set.of("password","accessToken","refreshToken").contains(e.getKey())&&e.getValue().isTextual())secrets.add(e.getValue().textValue());else collect(e.getValue());});
        else if(node.isArray())node.forEach(this::collect);
    }
    void noLeak(String value){for(String secret:secrets)if(!secret.isEmpty())require(!value.contains(secret),"Credential material leaked");}
    void checkDisclosure(JsonNode reply,HttpHeaders headers){
        JsonNode copy=reply.deepCopy();
        if(copy.has("tokens")){
            JsonNode tokens=copy.get("tokens");boolean web="WEB".equals(copy.path("session").path("clientType").asText());
            Set<String> allowed=web?Set.of("accessToken","accessTokenExpiresInSeconds","refreshTokenDelivery"):Set.of("accessToken","accessTokenExpiresInSeconds","refreshTokenDelivery","refreshToken","refreshTokenExpiresInSeconds");
            require(tokens.isObject()&&tokens.size()==allowed.size(),"Unexpected token response fields");tokens.fieldNames().forEachRemaining(k->require(allowed.contains(k),"Unexpected token response fields"));
            ((ObjectNode)tokens).remove(List.of("accessToken","refreshToken"));
        }
        noLeak(copy.toString());headers.map().forEach((key,values)->{
            if(key.equalsIgnoreCase("set-cookie"))for(String cookie:values){
                require("WEB".equals(reply.path("session").path("clientType").asText())&&cookie.startsWith("__Host-im_refresh="),"Unexpected credential cookie");
                noLeak(cookie.substring(cookie.indexOf(';')));
            }else values.forEach(this::noLeak);
        });
    }
    Reply callHeaders(String method,String path,JsonNode body,Map<String,String> headers)throws Exception{
        collect(body);headers.forEach((key,value)->{if(key.equalsIgnoreCase("Authorization"))secrets.add(value.replaceFirst("^Bearer ",""));if(key.equalsIgnoreCase("Cookie"))secrets.add(value.split("=",2)[1]);});
        var request=HttpRequest.newBuilder(URI.create(base+path)).timeout(Duration.ofSeconds(10));
        headers.forEach(request::header);
        if(body!=null)request.header("Content-Type","application/json");
        request.method(method,body==null?HttpRequest.BodyPublishers.noBody():HttpRequest.BodyPublishers.ofString(JSON.writeValueAsString(body)));
        var response=http.send(request.build(),HttpResponse.BodyHandlers.ofString());
        JsonNode result=response.body().isBlank()?NullNode.instance:JSON.readTree(response.body());collect(result);
        response.headers().allValues("set-cookie").forEach(cookie->secrets.add(cookie.split(";",2)[0].split("=",2)[1]));
        checkDisclosure(result,response.headers());return new Reply(response.statusCode(),result,response.headers());
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
        for(String key:List.of("password","refreshToken")){
            ObjectNode leaked=refreshed.body.deepCopy();if(key.equals("refreshToken"))((ObjectNode)leaked.get("tokens")).put(key,oldRefresh);else leaked.put("extra",login.get("password").textValue());
            boolean detected=false;try{checkDisclosure(leaked,refreshed.headers);}catch(AssertionError expected){detected=true;}require(detected,"Response disclosure mutation undetected");
        }
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
    // A synchronous RFC6455 test client observes TCP EOF directly. The JDK
    // async client intermittently never delivered EOF after Go's abrupt close.
    final class Socket implements AutoCloseable {
        final java.net.Socket tcp; final java.io.InputStream input; final java.io.OutputStream output;
        Socket()throws Exception{
            URI uri=URI.create(base);tcp=new java.net.Socket();tcp.connect(new InetSocketAddress(uri.getHost(),uri.getPort()),5000);tcp.setSoTimeout(5000);
            input=tcp.getInputStream();output=tcp.getOutputStream();
            String key=Base64.getEncoder().encodeToString(new byte[16]);
            output.write(("GET /v1/ws HTTP/1.1\r\nHost: "+uri.getAuthority()+"\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: "+key+"\r\n\r\n").getBytes(java.nio.charset.StandardCharsets.US_ASCII));output.flush();
            java.io.ByteArrayOutputStream headers=new java.io.ByteArrayOutputStream();int state=0;
            while(state<4){int b=input.read();require(b>=0&&headers.size()<8192,"Incomplete WSS upgrade");headers.write(b);state=b==new int[]{13,10,13,10}[state]?state+1:(b==13?1:0);}
            String response=headers.toString(java.nio.charset.StandardCharsets.US_ASCII);
            require(response.startsWith("HTTP/1.1 101 "),"WSS upgrade rejected");
            String accept=Base64.getEncoder().encodeToString(java.security.MessageDigest.getInstance("SHA-1").digest((key+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").getBytes(java.nio.charset.StandardCharsets.US_ASCII)));
            require(response.toLowerCase(Locale.ROOT).contains("sec-websocket-accept: "+accept.toLowerCase(Locale.ROOT)+"\r\n"),"WSS upgrade accept mismatch");
        }
        void send(JsonNode value)throws Exception{
            byte[] payload=JSON.writeValueAsBytes(value);require(payload.length<65536,"Test frame too large");
            output.write(0x81);if(payload.length<126)output.write(0x80|payload.length);else{output.write(0xfe);output.write(payload.length>>8);output.write(payload.length);}
            byte[] mask=new byte[4];new java.security.SecureRandom().nextBytes(mask);output.write(mask);
            for(int i=0;i<payload.length;i++)output.write(payload[i]^mask[i%4]);output.flush();
        }
        Object receive()throws Exception{
            int first=input.read();if(first<0)return Integer.valueOf(1006);
            int second=input.read();require(second>=0&&(first&0x70)==0&&(first&0x80)!=0&&(second&0x80)==0,"Invalid server frame");
            int length=second&127;if(length==126){byte[] size=input.readNBytes(2);require(size.length==2,"Truncated frame length");length=((size[0]&255)<<8)|(size[1]&255);}require(length!=127,"Oversize server frame");
            byte[] data=input.readNBytes(length);require(data.length==length,"Truncated server frame");
            int opcode=first&15;if(opcode==8)return Integer.valueOf(1000);require(opcode==1,"Unexpected server frame");return new String(data,java.nio.charset.StandardCharsets.UTF_8);
        }
        JsonNode next()throws Exception{Object value=receive();require(value instanceof String,"WSS closed before event");return JSON.readTree((String)value);}
        void closed()throws Exception{
            try{require(receive() instanceof Integer,"Expected WSS close after event");}
            catch(java.net.SocketException reset){require(!tcp.isClosed(),"Test closed socket before server closure");}
        }
        void afterRevoke(JsonNode frame)throws Exception{try{send(frame);}catch(java.net.SocketException disconnected){/* Read must independently observe terminal EOF/close. */}closed();}
        public void close()throws java.io.IOException{tcp.close();}
    }
    Socket socket()throws Exception{return new Socket();}
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
        for(String field:List.of("protocolVersion","requestId","type","payload"))try(Socket malformed=socket()){
            ObjectNode sent=frame("ping",Map.of());sent.put(field,1.0);malformed.send(sent);malformed.closed();
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
    void durations()throws Exception{
        String username="ttl"+UUID.randomUUID().toString().replace("-","");
        ObjectNode registration=JSON.createObjectNode().put("username",username).put("password","duration-test-password").put("displayName","TTL");
        require(call("POST","/v1/auth/register",registration,null,null).status==201,"TTL setup");
        for(String type:List.of("WEB","DESKTOP")){
            ObjectNode request=body(step(positive,"same-slot-login-replaces-only-that-slot",0).get("request").get("body"),username).put("password","duration-test-password").put("clientType",type);
            Reply reply=login(request);
            for(int i=0;i<2;i++){
                Tokens.Claims claims=codec.parse(reply.token());require(claims.expires()-claims.issued()==config.accessTokenSeconds,"Configured JWT lifetime");
                require(reply.body.path("tokens").path("accessTokenExpiresInSeconds").asInt()==config.accessTokenSeconds,"Configured advertised access lifetime");
                if(type.equals("WEB"))require(reply.headers.firstValue("set-cookie").orElseThrow().contains("Max-Age="+config.refreshTokenSeconds+";"),"Configured cookie lifetime");
                else require(reply.body.path("tokens").path("refreshTokenExpiresInSeconds").asInt()==config.refreshTokenSeconds,"Configured advertised refresh lifetime");
                try(var db=config.database().getConnection();var q=db.prepareStatement("SELECT extract(epoch FROM expires_at-now()) FROM sessions WHERE session_id=?")){q.setObject(1,UUID.fromString(claims.sessionId()));try(var rows=q.executeQuery()){require(rows.next(),"TTL session missing");double remaining=rows.getDouble(1);require(remaining>config.refreshTokenSeconds-10&&remaining<=config.refreshTokenSeconds,"Configured database expiry");}}
                ObjectNode refresh=request.deepCopy();refresh.remove(List.of("username","password"));if(!type.equals("WEB"))refresh.put("refreshToken",reply.refresh());
                reply=call("POST",type.equals("WEB")?"/v1/auth/refresh/web":"/v1/auth/refresh/native",refresh,null,type.equals("WEB")?reply.cookie():null);require(reply.status==200,"TTL refresh");
            }
        }
        System.out.println("CONFIG nondefault token durations across login/refresh/claims/cookie/database PASS");
    }
    public static void main(String[] args)throws Exception{
        require(args.length>=4,"base profile repository config required");AuthFixtureRunner run=new AuthFixtureRunner(args[0],args[1],Path.of(args[2]),Config.read(args[3]));
        if(args.length==5){try{run.durations();}finally{Files.writeString(Path.of(args[3]).getParent().resolve("sensitive-values.json"),JSON.writeValueAsString(run.secrets));}return;}
        if(args.length==6){try{run.credentials(args[4],Path.of(args[5]));}finally{Files.writeString(Path.of(args[3]).getParent().resolve("sensitive-values.json"),JSON.writeValueAsString(run.secrets));}return;}
        try{run.execute();}finally{Files.writeString(Path.of(args[3]).getParent().resolve("sensitive-values.json"),JSON.writeValueAsString(run.secrets));}
    }
    void execute()throws Exception{
        AuthFixtureRunner run=this;
        run.httpFixtures();run.socketFixtures();require(run.passed.size()==28,"Expected all 28 Auth fixtures");for(String id:run.passed)System.out.println("FIXTURE "+run.profile+" "+id+" PASS");
        System.out.println("LIVE_AUTH "+run.profile+" PASS 28 fixtures; slot concurrency, rotation, logout, real NATS revocation");
    }
}

package im.platform.client.sync
import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle
import im.platform.client.send.SendSession
import im.platform.client.send.SendViewModel
import im.platform.client.send.Wss
import im.platform.client.send.SendSocket
import im.platform.client.storage.Repository
import im.platform.client.storage.UserEvent
import im.platform.client.storage.ServerMessage
import im.platform.client.storage.LocalMessage
import kotlinx.coroutines.*
import java.math.BigInteger
import java.util.UUID
import java.io.*
import java.net.URL
import java.security.KeyStore
import java.security.cert.CertificateFactory
import java.security.cert.Certificate
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import javax.net.ssl.*
import org.json.JSONObject
import org.json.JSONArray

class SyncInstrumentation:Instrumentation() {
    private lateinit var args:Bundle
    private var assertions=0
    private var phase="wire"
    private val u="10000000-0000-4000-8000-000000000001"
    private val sid="20000000-0000-4000-8000-000000000001"
    private val c="30000000-0000-4000-8000-000000000001"
    private val d="30000000-0000-4000-8000-000000000002"
    private val denied="30000000-0000-4000-8000-000000000003"
    private fun uid(n:Int)="50000000-0000-4000-8000-"+n.toString().padStart(12,'0')
    private fun session(user:String=u)=SendSession(user,sid,BigInteger.ONE,"fixture-mobile")
    private fun equal(a:Any?,b:Any?){check(a==b){"Assertion $assertions phase=$phase actual=$a expected=$b"};assertions++}
    private fun reject(action:()->Unit){var failed=false;try{action()}catch(_:Exception){failed=true};check(failed);assertions++}
    private suspend fun until(test:()->Boolean){repeat(1000){if(test())return;delay(10)};error("Condition timed out in $phase")}
    private fun event(id:String=uid(1),token:String="opaque")=JSONObject().put("eventId",id).put("cursor",token).put("kind","conversation.changed").put("subjectId",c).put("revision",1)
    private fun userPage(id:String,token:String="opaque")=JSONObject().put("syncVersion","1.0").put("type","sync.user.page").put("requestId",id).put("events",JSONArray().put(event(token=token))).put("nextCursor",token).put("hasMore",false)
    private fun message(n:Int,text:String="x")=JSONObject().put("conversationId",c).put("seq",n).put("messageId",uid(n)).put("senderId",u).put("requestId",uid(n+1000)).put("createdAt","2026-10-03T00:00:00Z").put("content",JSONObject().put("kind","TEXT").put("text",text))
    private fun conversationPage(id:String,messages:JSONArray)=JSONObject().put("syncVersion","1.0").put("type","sync.conversation.page").put("requestId",id).put("conversationId",c).put("messages",messages).put("hasMore",false)
    private fun wire() {
        val id=uid(4000)
        equal(Wire.user(userPage(id).toString(),id,"0").events.single().revision,1L)
        for(n in listOf("9007199254740993","9007199254740993.0","90071992547409930e-1"))equal(Wire.user(userPage(id).toString().replace("\"revision\":1","\"revision\":$n"),id,"0").events.single().revision,9007199254740993L)
        reject {Wire.user(userPage(id).put("nextCursor","wrong").toString(),id,"0")}
        reject {Wire.user(userPage(id).put("events",JSONArray()).put("hasMore",true).toString(),id,"0")}
        reject {Wire.user(userPage(id).toString().replace("\"revision\":1","\"revision\":1,\"revision\":2"),id,"0")}
        reject {Wire.user(userPage(id).toString(),uid(5000),"0")}
        reject {Wire.user(userPage(id).put("events",JSONArray().put(event()).put(event())).toString(),id,"0")}
        reject {Wire.user(userPage(id).put("events",JSONArray().put(event().put("kind","message.created"))).toString(),id,"0")}
        val started=System.nanoTime()
        for(n in listOf("1e100000000","1e-100000000","100000000000000000000","1e2147483647","1e-2147483647")) reject {Wire.user(userPage(id).toString().replace("\"revision\":1","\"revision\":$n"),id,"0")}
        check(System.nanoTime()-started<2_000_000_000L) {"Hostile numeric Sync response was not bounded"}
        val text="😀".repeat(4096);val messages=JSONArray();(1..100).forEach {messages.put(message(it,text))}
        val raw=conversationPage(id,messages).toString()
        equal(Wire.conversation(raw,id,c,0).messages.size,100)
        val escaped=raw.replace("😀","\\ud83d\\ude00");check(escaped.toByteArray().size<MAX_RESPONSE)
        equal(Wire.conversation(escaped,id,c,0).messages.last().text,text)
        reject {Wire.conversation(conversationPage(id,JSONArray().put(message(2))).toString(),id,c,0)}
        reject {Wire.conversation(conversationPage(id,JSONArray().put(message(1)).put(message(1))).toString(),id,c,0)}
        reject {Wire.conversation(conversationPage(id,JSONArray()).put("hasMore",true).toString(),id,c,0)}
        reject {Wire.conversation(conversationPage(id,JSONArray().put(message(1,"😀".repeat(4097)))).toString(),id,c,0)}
        equal(Wire.conversation(conversationPage(id,JSONArray().put(message(1))).toString().replace("\"seq\":1","\"seq\":9007199254740993"),id,c,9007199254740992L).messages.single().seq,9007199254740993L)
        for(endpoint in listOf("http://localhost/","https://user@localhost/","https://localhost/?token=x","https://localhost/sub"))reject {SyncHttps(endpoint,session())}
    }
    private fun tls():SSLContext {
        val certificate=CertificateFactory.getInstance("X.509").generateCertificate(ByteArrayInputStream(java.util.Base64.getDecoder().decode(args.getString("certificate"))))
        val store=KeyStore.getInstance(KeyStore.getDefaultType());store.load(null);store.setCertificateEntry("fixture",certificate)
        val trust=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());trust.init(store)
        return SSLContext.getInstance("TLS").also {it.init(null,trust.trustManagers,null)}
    }
    private suspend fun actual() {
        phase="actual-TLS-WSS-pagination"
        val endpoint=args.getString("endpoint") ?: error("endpoint missing");val tls=tls()
        targetContext.deleteDatabase("im-$u.sqlite");val repo=Repository(targetContext,u);repo.initialize()
        fun send()=SendViewModel(repo,session(),{url,open,message,end->Wss(url,open,message,end,tls.socketFactory)},100,{uid(1001)})
        fun http()=SyncHttps(endpoint,session(),{url->(url.openConnection() as HttpsURLConnection).also {it.sslSocketFactory=tls.socketFactory}})
        var sender=send();sender.openConversation(c);equal(sender.send(c,"message-1"),uid(1001));equal(repo.messages(c).single()[3],"FAILED")
        var sync=SyncViewModel(sender,repo,http());sender.connect(endpoint.replace("https:","wss:")+"/ws")
        until {sender.state.value.connection=="ready"};until {repo.contiguous(c)==205L && sync.state.value.status=="idle"}
        equal(repo.cursor(),"u-205");equal(repo.messages(c).size,205);equal(repo.messages(c).first {it[0]==uid(1001)}[3],"SENT")
        equal(repo.contiguous(d),2L);equal(repo.conversationIds(),listOf(c,d,denied));check(denied in sync.state.value.unavailable);equal(sender.state.value.messages.size,205)
        val append=(URL(endpoint+"/fixture/append").openConnection() as HttpsURLConnection);append.sslSocketFactory=tls.socketFactory;append.inputStream.use {it.readBytes()};append.disconnect()
        until {repo.contiguous(c)==208L && repo.cursor()=="u-206" && sync.state.value.status=="idle"};equal(repo.messages(c).size,208)
        sender.disconnect();sender.connect(endpoint.replace("https:","wss:")+"/ws");until {sender.state.value.connection=="ready"};delay(200);sync.synchronize();equal(repo.contiguous(c),208L)
        sync.dispose();equal(sender.state.value.messages.size,0);repo.close()
        val reopened=Repository(targetContext,u);reopened.initialize();sender=SendViewModel(reopened,session());sync=SyncViewModel(sender,reopened,http());sync.openConversation(c)
        equal(sender.state.value.messages.size,208);equal(reopened.cursor(),"u-206");sync.dispose();reopened.close()
        phase="untrusted-CA";var failed=false;try {SyncHttps(endpoint,session()).user("0")}catch(e:SyncFailure){equal(e.kind,"transport");failed=true};check(failed)
        targetContext.deleteDatabase("im-$u.sqlite")
    }
    private class Fake(private val reply:()->String,private val status:Int=200,private val gate:CountDownLatch?=null):HttpsURLConnection(URL("https://localhost/")) {
        val input=ByteArrayOutputStream()
        override fun connect(){}
        override fun disconnect(){gate?.countDown()}
        override fun usingProxy()=false
        override fun getCipherSuite()="fixture-only"
        override fun getLocalCertificates():Array<Certificate>?=null
        override fun getServerCertificates():Array<Certificate> = emptyArray()
        override fun getOutputStream():OutputStream=input
        override fun getResponseCode()=status
        override fun getHeaderField(name:String?)=if(name.equals("Cache-Control",true))"no-store" else null
        override fun getContentType()="application/json"
        override fun getInputStream():InputStream {gate?.await(30,TimeUnit.SECONDS);return ByteArrayInputStream(reply().toByteArray())}
        override fun getErrorStream():InputStream=getInputStream()
    }
    private suspend fun storageLifecycle() {
        phase="native-rollback-lifecycle"
        val account=UUID.randomUUID().toString();val other=UUID.randomUUID().toString();val repo=Repository(targetContext,account);repo.initialize()
        val creds=session(account);val sender=SendViewModel(repo,creds)
        var failed=false
        try {sender.mergeUserPage(listOf(UserEvent("conversation.changed",c,1)),"rollback","0",{true},true)}catch(_:Exception){failed=true}
        check(failed);equal(repo.cursor(),"0");equal(repo.conversationIds(),emptyList<String>())
        val request=uid(1001);repo.localSend(LocalMessage(c,request,account,"rollback"));repo.markFailed(c,request)
        failed=false;val m=ServerMessage(c,request,account,"rollback",uid(1),1,"2026-10-03T00:00:00Z")
        try {sender.mergeMessages(listOf(m),{true},true)}catch(_:Exception){failed=true};check(failed);equal(repo.contiguous(c),0L);equal(repo.messages(c).single()[3],"FAILED")
        sender.mergeMessages(listOf(m));equal(repo.contiguous(c),1L);equal(repo.messages(c).single()[3],"SENT")
        val otherRepo=Repository(targetContext,other);otherRepo.initialize();equal(otherRepo.messages(c).size,0);reject {SyncViewModel(sender,otherRepo,SyncHttps("https://localhost/",creds))};otherRepo.close()
        val id=uid(4000);val gate=CountDownLatch(1);var started=false
        val http=SyncHttps("https://localhost/",creds,{Fake({userPage(id,"retired").toString()},gate=gate).also {started=true}},{id})
        val sync=SyncViewModel(sender,repo,http);val job=CoroutineScope(currentCoroutineContext()).launch {sync.synchronize()};until {started};sync.dispose();job.join()
        equal(repo.cursor(),"0");equal(sync.state.value.status,"retired")
        var calls=0
        val unauthorized=SyncHttps("https://localhost/",creds,{Fake({JSONObject().put("requestId",id).put("error",JSONObject().put("code","AUTH_SESSION_REVOKED").put("message","Revoked")).toString()},401).also {calls++}},{id})
        val sender2=SendViewModel(repo,creds);val stopped=SyncViewModel(sender2,repo,unauthorized)
        failed=false;try {stopped.synchronize()}catch(_:SyncFailure){failed=true};check(failed);equal(stopped.state.value.error,"authentication");stopped.synchronize();equal(calls,1);stopped.dispose()
        val sender3=SendViewModel(repo,creds);reject {SyncViewModel(sender3,repo,SyncHttps("https://localhost/",session(other)))};sender3.dispose()
        repo.close();targetContext.deleteDatabase("im-$account.sqlite");targetContext.deleteDatabase("im-$other.sqlite")
        val clearedAccount=UUID.randomUUID().toString();val clearedRepo=Repository(targetContext,clearedAccount);clearedRepo.initialize()
        val clearedCreds=session(clearedAccount);val clearedSender=SendViewModel(clearedRepo,clearedCreds,ownsRepository=true)
        val clearedGate=CountDownLatch(1);var clearedStarted=false
        val clearedHttp=SyncHttps("https://localhost/",clearedCreds,{Fake({userPage(id,"after-clear").toString()},gate=clearedGate).also {clearedStarted=true}},{id})
        val cleared=SyncViewModel(clearedSender,clearedRepo,clearedHttp);val clearedJob=CoroutineScope(currentCoroutineContext()).launch {cleared.synchronize()}
        until {clearedStarted};SyncViewModel::class.java.getDeclaredMethod("onCleared").apply {isAccessible=true}.invoke(cleared);clearedJob.join()
        until {try {clearedRepo.cursor();false}catch(_:Exception){true}}
        val restart=Repository(targetContext,clearedAccount);restart.initialize();equal(restart.cursor(),"0");restart.close();targetContext.deleteDatabase("im-$clearedAccount.sqlite")
    }

    private suspend fun discovery() {
        phase="FAILED-only-empty-selected-discovery"
        for(local in listOf(true,false)){
            val account=UUID.randomUUID().toString();val repo=Repository(targetContext,account);repo.initialize();val creds=session(account)
            val chosen=uid(if(local)91002 else 91003);val request=uid(if(local)91004 else 91005);val id=uid(4300)
            if(local){repo.localSend(LocalMessage(chosen,request,account,"discovery"));repo.markFailed(chosen,request)}
            var pulled=0
            val http=SyncHttps("https://localhost/",creds,{url->
                if(url.path.endsWith("user"))Fake({JSONObject().put("syncVersion","1.0").put("type","sync.user.page").put("requestId",id).put("events",JSONArray()).put("nextCursor","0").put("hasMore",false).toString()})
                else Fake({pulled++;conversationPage(id,JSONArray().put(message(1,"discovery").put("conversationId",chosen).put("requestId",request).put("senderId",account))).put("conversationId",chosen).toString()})
            },{id})
            val owner=SendViewModel(repo,creds);val sync=SyncViewModel(owner,repo,http)
            if(local)sync.synchronize() else sync.openConversation(chosen)
            equal(pulled,1);equal(repo.contiguous(chosen),1L);equal(repo.messages(chosen).single()[3],"SENT");equal(repo.cursor(),"0")
            sync.dispose();repo.close();targetContext.deleteDatabase("im-$account.sqlite")
        }
    }

    override fun onCreate(arguments:Bundle?){args=arguments ?: Bundle();super.onCreate(arguments);start()}
    override fun onStart(){
        val result=Bundle()
        try {runBlocking {wire();actual();storageLifecycle();discovery()};result.putString("result","PASS");result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putInt("assertions",assertions);finish(Activity.RESULT_OK,result)}
        catch(error:Throwable){result.putString("result","FAIL");result.putString("phase",phase);result.putString("failure",error.javaClass.simpleName+": "+error.message);finish(Activity.RESULT_CANCELED,result)}
    }
}

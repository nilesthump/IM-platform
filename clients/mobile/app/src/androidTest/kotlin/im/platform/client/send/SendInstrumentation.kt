package im.platform.client.send
import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle
import im.platform.client.storage.Repository
import im.platform.client.storage.ServerMessage
import kotlinx.coroutines.*
import java.math.BigInteger
import java.util.UUID
import java.io.ByteArrayInputStream
import java.security.KeyStore
import java.security.cert.CertificateFactory
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManagerFactory
import org.json.JSONObject

class SendInstrumentation: Instrumentation() {
    private lateinit var args:Bundle
    private var assertions=0
    private var phase="wire"
    private val user="10000000-0000-4000-8000-000000000001"
    private val session="20000000-0000-4000-8000-000000000001"
    private val conversation="30000000-0000-4000-8000-000000000001"
    private fun equal(actual:Any?,expected:Any?) {check(actual==expected) { "Assertion $assertions failed" };assertions++}
    private suspend fun until(test:()->Boolean) { repeat(500) {if(test())return;delay(10)};error("Condition timed out") }
    private fun credentials()=SendSession(user,session,BigInteger.ONE,"fixture-mobile")
    private fun fakeFrame(type:String,id:String,p:JSONObject)=Wire.envelope(type,id,p)
    private class Fake:SendSocket {
        var open:(()->Unit)?=null;var message:((String)->Unit)?=null;var end:(()->Unit)?=null
        val frames=mutableListOf<JSONObject>()
        override fun send(text:String){frames.add(JSONObject(text))}
        override fun close(){}
        fun bound(user:String,session:String){val auth=frames.last();message!!(Wire.envelope("auth.ack",auth.getString("requestId"),JSONObject().put("status","bound").put("userId",user).put("sessionId",session).put("clientType","MOBILE").put("sessionEpoch",1)))}
    }
    private fun committed(c:String,id:String,seq:Long=9007199254740993L)=JSONObject().put("status","committed").put("conversationId",c).put("messageId",id).put("seq",seq).put("createdAt","2026-10-03T00:00:00Z")
    private suspend fun actualTls() {
        phase="TLS/offline"
        targetContext.deleteDatabase("im-$user.sqlite")
        val certificate=CertificateFactory.getInstance("X.509").generateCertificate(ByteArrayInputStream(java.util.Base64.getDecoder().decode(args.getString("certificate"))))
        val store=KeyStore.getInstance(KeyStore.getDefaultType());store.load(null);store.setCertificateEntry("fixture",certificate)
        val trust=TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());trust.init(store)
        val tls=SSLContext.getInstance("TLS");tls.init(null,trust.trustManagers,null)
        val endpoint=args.getString("endpoint") ?: error("TLS fixture endpoint required")
        val repo=Repository(targetContext,user);repo.initialize()
        fun app()=SendViewModel(repo,credentials(),{url,open,message,end->Wss(url,open,message,end,tls.socketFactory)},300)
        suspend fun connect(vm:SendViewModel,mode:String="normal") {vm.connect("$endpoint/$mode");until {vm.state.value.connection=="ready"};vm.openConversation(conversation)}
        var vm=app();vm.openConversation(conversation);val offline=vm.send(conversation,"mobile-offline");equal(repo.messages(conversation).first {it[0]==offline}[3],"FAILED")
        connect(vm);vm.retry(conversation,offline);until {vm.state.value.messages.firstOrNull {it[0]==offline}?.get(3)=="SENT"};equal(repo.messages(conversation).first {it[0]==offline}[5],"9007199254740993");vm.dispose()
        phase="TLS/restart";vm=app();connect(vm,"timeout");val retry=vm.send(conversation,"mobile-restart");until {vm.state.value.messages.firstOrNull {it[0]==retry}?.get(3)=="FAILED"};vm.dispose();repo.close()
        val reopened=Repository(targetContext,user);reopened.initialize()
        vm=SendViewModel(reopened,credentials(),{url,open,message,end->Wss(url,open,message,end,tls.socketFactory)},300);connect(vm);vm.retry(conversation,retry);until {vm.state.value.messages.firstOrNull {it[0]==retry}?.get(3)=="SENT"};equal(reopened.messages(conversation).count {it[0]==retry},1);vm.dispose()
        for(mode in listOf("late","realtime","reject","invalid","revoked")) {
            phase="TLS/$mode"
            vm=SendViewModel(reopened,credentials(),{url,open,message,end->Wss(url,open,message,end,tls.socketFactory)},300);connect(vm,mode)
            val request=vm.send(conversation,"mobile-$mode")
            if(mode=="late") {until {vm.state.value.messages.firstOrNull {it[0]==request}?.get(3)=="FAILED"};until {vm.state.value.messages.firstOrNull {it[0]==request}?.get(3)=="SENT"}}
            if(mode=="realtime") {until {vm.state.value.messages.firstOrNull {it[0]==request}?.get(3)=="SENT"};equal(reopened.messages(conversation).count {it[0]==request},1)}
            if(mode=="reject") {until {vm.state.value.messages.firstOrNull {it[0]==request}?.get(3)=="FAILED"};vm.mergeMessages(listOf(ServerMessage(conversation,request,user,"mobile-$mode",UUID.randomUUID().toString(),99,"2026-10-03T00:00:00Z")));equal(vm.state.value.messages.first {it[0]==request}[3],"SENT");vm.retry(conversation,request);equal(vm.state.value.messages.first {it[0]==request}[3],"SENT")}
            if(mode=="revoked") {until {vm.state.value.connection=="offline" && vm.state.value.messages.firstOrNull {it[0]==request}?.get(3)=="FAILED"};equal(reopened.messages(conversation).first {it[0]==request}[3],"FAILED");val offline=vm.send(conversation,"after revoked");equal(reopened.messages(conversation).first {it[0]==offline}[3],"FAILED")}
            if(mode=="invalid") {until {vm.state.value.connection=="offline" && vm.state.value.error=="protocol"};equal(reopened.messages(conversation).first {it[0]==request}[3],"FAILED");equal(vm.state.value.error,"protocol")}
            vm.dispose();equal(vm.state.value.messages.size,0)
        }
        vm=SendViewModel(reopened,credentials(),{url,open,message,end->Wss(url,open,message,end,tls.socketFactory)});vm.connect("$endpoint/wrong-session");until {vm.state.value.error=="protocol"};equal(vm.state.value.connection,"offline");vm.dispose()
        // The platform default trust store must reject the private fixture CA.
        vm=SendViewModel(reopened,credentials());vm.connect("$endpoint/normal");until {vm.state.value.connection=="offline"};equal(vm.state.value.connection,"offline");vm.dispose()
        reopened.close();targetContext.deleteDatabase("im-$user.sqlite")
    }
    private suspend fun racesAndStorage() {
        phase="races/storage"
        val account=UUID.randomUUID().toString();val other=UUID.randomUUID().toString()
        val repo=Repository(targetContext,account);repo.initialize()
        val creds=credentials().copy(userId=account);val sockets=mutableListOf<Fake>()
        val vm=SendViewModel(repo,creds,{_,open,message,end->Fake().also {it.open=open;it.message=message;it.end=end;sockets.add(it)}},100)
        vm.openConversation(conversation);vm.connect("wss://localhost/");var socket=sockets.last();socket.open!!();until {socket.frames.isNotEmpty()};socket.bound(account,session);until {vm.state.value.connection=="ready"}
        val request=vm.send(conversation,"generation");equal(vm.state.value.messages.first {it[0]==request}[3],"SENDING");equal(repo.messages(conversation).first {it[0]==request}[3],"SENDING")
        delay(50);vm.retry(conversation,request);delay(70);equal(vm.state.value.messages.first {it[0]==request}[3],"SENDING")
        val oldMessage=socket.message!!;vm.disconnect();vm.connect("wss://localhost/");socket=sockets.last();socket.open!!();until {socket.frames.isNotEmpty()};socket.bound(account,session);until {vm.state.value.connection=="ready"}
        oldMessage(fakeFrame("message.ack",request,committed(conversation,UUID.randomUUID().toString())));delay(50);equal(repo.messages(conversation).first {it[0]==request}[3],"FAILED")
        vm.retry(conversation,request);val messageId=UUID.randomUUID().toString();socket.message!!(fakeFrame("message.ack",request,committed(conversation,messageId)));until {vm.state.value.messages.first {it[0]==request}[3]=="SENT"};delay(150);equal(vm.state.value.messages.first {it[0]==request}[3],"SENT")
        val bad=vm.send(conversation,"persist failure");repo.close();socket.message!!(fakeFrame("message.ack",bad,committed(conversation,UUID.randomUUID().toString(),12)));until {vm.state.value.error=="storage"};equal(vm.state.value.messages.first {it[0]==bad}[3],"SENDING")
        delay(180);equal(vm.state.value.error,"storage");equal(vm.state.value.messages.first {it[0]==bad}[3],"SENDING")
        val count=socket.frames.size;try {vm.send(conversation,"before commit");error("Expected storage error")} catch(_:IllegalStateException){};equal(socket.frames.size,count)
        // Closed Repository deliberately remains a failed storage fixture; retire
        // via lifecycle to avoid attempting another transaction on closed DB.
        val clear=SendViewModel::class.java.getDeclaredMethod("onCleared");clear.isAccessible=true;clear.invoke(vm);equal(vm.state.value.messages.size,0)
        Repository(targetContext,account).use {it.initialize();equal(it.messages(conversation).count {row->row[0]==request},1);equal(it.messages(conversation).first {row->row[0]==bad}[3],"SENDING")}
        Repository(targetContext,other).use {it.initialize();equal(it.messages(conversation).size,0)}
        targetContext.deleteDatabase("im-$account.sqlite");targetContext.deleteDatabase("im-$other.sqlite")
    }
    private fun wire() {
        val request=UUID.randomUUID().toString();val message=UUID.randomUUID().toString();val base=fakeFrame("message.ack",request,committed(conversation,message))
        for(number in listOf("9007199254740993","9007199254740993.0","90071992547409930e-1","9223372036854775808")) {
            val frame=base.replace("9007199254740993",number);val expected=if(number=="9223372036854775808") BigInteger(number) else BigInteger("9007199254740993")
            equal(Wire.decode(frame).payload["seq"],expected)
        }
        for(frame in listOf(base.replace("9007199254740993","0"),base.replace("9007199254740993","\"1\""),base.replace("9007199254740993","1.5"),base.replace("message.ack","hello"),base.dropLast(1)+",\"extra\":1}",base.replace("\"seq\":9007199254740993","\"seq\":1,\"seq\":2"))) {
            var rejected=false;try {Wire.decode(frame)} catch(_:IllegalArgumentException) {rejected=true};equal(rejected,true)
        }
    }
    override fun onCreate(arguments:Bundle?) {super.onCreate(arguments);args=arguments ?: Bundle();start()}
    override fun onStart() {
        val result=Bundle()
        try {runBlocking {wire();actualTls();racesAndStorage()};result.putString("result","PASS");result.putInt("assertions",assertions);result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putString("engine","actual Android SDK SQLite + standard verified TLS WSS + StateFlow");finish(Activity.RESULT_OK,result)}
        catch(error:Throwable) {result.putString("phase",phase);result.putString("failure",error.javaClass.simpleName+": "+error.message);result.putString("result","FAIL");result.putInt("assertions",assertions);finish(Activity.RESULT_CANCELED,result)}
    }
}

package im.platform.client.group
import android.app.Application
import android.app.Instrumentation
import android.os.Bundle
import im.platform.client.ui.*
import im.platform.client.send.SendSession
import im.platform.client.storage.Repository
import kotlinx.coroutines.*
import java.net.*
import java.io.*
import java.math.BigInteger
import java.util.UUID
import java.util.concurrent.atomic.AtomicReference
import javax.net.ssl.HttpsURLConnection
import kotlin.coroutines.*

class FriendLoadInstrumentation:Instrumentation(){
 private val account=UUID.randomUUID().toString()
 private val friend=UUID.randomUUID().toString()
 private val conversation=UUID.randomUUID().toString()
 private var puts=0;private var gets=0
 @Volatile private var entered:java.util.concurrent.CountDownLatch?=null
 @Volatile private var release:java.util.concurrent.CountDownLatch?=null
 @Volatile private var fault:Throwable?=IOException("owned list read failure")
 private fun field(o:Any,name:String,value:Any?){o.javaClass.getDeclaredField(name).apply{isAccessible=true}.set(o,value)}
 private class Peer(url:URL,val response:()->String):HttpsURLConnection(url){
  override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
  override fun getCipherSuite()="owned-test-only";override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null;override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
  override fun getResponseCode()=200;override fun getContentType()="application/json"
  override fun getInputStream():InputStream=response().byteInputStream()
 }
 override fun onCreate(args:Bundle?){super.onCreate(args);start()}
 // This instrumentation owns reporting: cleanup must not replace a failed assertion.
 internal fun runChecks(result:Bundle,checks:()->Unit,cancelScope:()->Unit,closeRepository:()->Unit):Int {
  var failure:Throwable?=null
  try{checks()}catch(e:Throwable){failure=e}
  finally{
   try{cancelScope()}catch(e:Throwable){val primary=failure;if(primary==null)failure=e else if(primary!==e)primary.addSuppressed(e)}
   try{closeRepository()}catch(e:Throwable){val primary=failure;if(primary==null)failure=e else if(primary!==e)primary.addSuppressed(e)}
  }
  failure?.let{result.putString("result","FAIL");result.putString("failure",it.stackTraceToString())}
  return if(result.getString("result")=="PASS")android.app.Activity.RESULT_OK else android.app.Activity.RESULT_CANCELED
 }
 override fun onStart(){val result=Bundle();var vm:WorkspaceViewModel?=null;var scope:CoroutineScope?=null;var repo:Repository?=null
  val code=runChecks(result,{URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL):URLConnection{
   check(url.host=="friend-load-r5.invalid"){"unexpected host"}
   return Peer(url){if(url.path=="/v1/friends/$friend"){puts++;"{\"friendshipId\":\"$friend\",\"normalizedPair\":[],\"directConversationId\":\"$conversation\",\"memberUserIds\":[],\"created\":true}"}else{check(url.path=="/v1/friends");gets++;entered?.countDown();release?.await();fault?.let{throw it};"{\"friends\":[]}"}}
  }}else null}
   val escaped=AtomicReference<Throwable?>()
   val ownedScope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate+CoroutineExceptionHandler{_,e->escaped.set(e)});scope=ownedScope
   val model=WorkspaceViewModel(targetContext.applicationContext as Application);vm=model
   field(model,"scope",ownedScope)
   val auth=Auth("https://friend-load-r5.invalid",Preferences(targetContext));field(auth,"session",SendSession(account,UUID.randomUUID().toString(),BigInteger.ONE,"owned-test-only"));field(model,"auth",auth)
   val storage=Repository(targetContext,account);storage.initialize();repo=storage
   runBlocking {
    withContext(Dispatchers.Main){model.add(friend)}
    withTimeout(10000){while(model.state.value.busy)delay(10)}
    check(puts==1&&gets==1){"actual PUT/GET path not exercised"}
    check(model.state.value.friendsStatus=="error"){"GET failure left status=${model.state.value.friendsStatus}"}
    check(escaped.get()==null)
    fault=null
    suspend fun readAgain(){suspendCoroutine<Unit>{continuation->
      val m=model.javaClass.getDeclaredMethod("refreshFriends",Repository::class.java,java.lang.Long.TYPE,Continuation::class.java);m.isAccessible=true
      val returned=try{m.invoke(model,storage,0L,continuation)}catch(e:java.lang.reflect.InvocationTargetException){throw e.cause!!}
      if(returned!==kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED)continuation.resume(Unit)
    }}
    withContext(Dispatchers.Main){readAgain()}
    check(model.state.value.friendsStatus=="ready"&&model.state.value.friends.isEmpty());check(puts==1&&gets==2){"read recovery repeated PUT"}
    val unknown=IllegalStateException("owned unknown read");fault=unknown
    withContext(Dispatchers.Main){model.add(friend)}
    withTimeout(10000){while(model.state.value.busy||escaped.get()==null)delay(10)}
    check(escaped.get()===unknown){"unknown did not propagate unchanged"};check(model.state.value.friendsStatus=="error")
    // Refresh-list caller must also publish error before an unknown escapes.
    field(model,"friendCursor","")
    val readError=try{withContext(Dispatchers.Main){readAgain()};null}catch(e:Throwable){e}
    check(readError===unknown);check(model.state.value.friendsStatus=="error")
    // A retired generation's known GET failure must not replace the current state.
    escaped.set(null);fault=IOException("owned stale failure")
    entered=java.util.concurrent.CountDownLatch(1);release=java.util.concurrent.CountDownLatch(1)
    withContext(Dispatchers.Main){model.add(friend)}
    check(entered!!.await(10,java.util.concurrent.TimeUnit.SECONDS))
    withContext(Dispatchers.Main){field(model,"generation",1L);field(model,"friendRevision",100L)
      val f=model.javaClass.getDeclaredField("mutable").apply{isAccessible=true}
      @Suppress("UNCHECKED_CAST") val flow=f.get(model) as kotlinx.coroutines.flow.MutableStateFlow<WorkspaceState>
      flow.value=flow.value.copy(friendsStatus="ready",busy=false,error=null)
    }
    release!!.countDown();withTimeout(10000){ownedScope.coroutineContext[Job]!!.children.toList().forEach{it.join()}};check(gets==5)
    check(model.state.value.friendsStatus=="ready"&&model.state.value.error==null);check(escaped.get()==null)

   }
   result.putString("result","PASS");result.putString("scope","actual VM.add PUT then GET, terminal error, GET-only empty recovery, unknown propagation; controlled transport, not TLS acceptance")
  },{scope?.cancel()},{repo?.close()})
  finish(code,result)
 }
}

package im.platform.client.group

import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity
import im.platform.client.send.SendSession
import im.platform.client.ui.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import org.json.JSONArray
import org.json.JSONObject
import java.io.*
import java.math.BigInteger
import java.net.*
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import javax.net.ssl.HttpsURLConnection
import kotlin.coroutines.*

/** Actual Activity/Compose/WorkspaceViewModel; only HTTPS transport is controlled. */
class GroupCloseInstrumentation:Instrumentation(){
 private lateinit var activity:MainActivity
 private lateinit var model:WorkspaceViewModel
 private lateinit var flow:MutableStateFlow<WorkspaceState>
 private var ownedScope:CoroutineScope?=null
 private val escaped=AtomicReference<Throwable?>()
 private val account=UUID.randomUUID().toString()
 private val friend=UUID.randomUUID().toString()
 private val conversation=UUID.randomUUID().toString()
 private val session=SendSession(account,UUID.randomUUID().toString(),BigInteger.ONE,"owned-test-only")
 private val friends=listOf(Friend(User(friend,"close_fixture","Close Friend"),UUID.randomUUID().toString(),UUID.randomUUID().toString()))
 private val posts=java.util.Collections.synchronizedList(mutableListOf<String>())
 @Volatile private var mutationFault:Throwable?=null
 @Volatile private var readFault:Throwable?=null
 @Volatile private var readEntered=CountDownLatch(1)
 @Volatile private var readRelease=CountDownLatch(1)
 @Volatile private var postEntered:CountDownLatch?=null
 @Volatile private var postRelease:CountDownLatch?=null
 private fun field(o:Any,name:String)=o.javaClass.getDeclaredField(name).apply{isAccessible=true}
 private inner class Peer(url:URL):HttpsURLConnection(url){
  private val body=ByteArrayOutputStream()
  override fun connect(){};override fun disconnect(){};override fun usingProxy()=false
  override fun getCipherSuite()="owned-test-only"
  override fun getLocalCertificates():Array<java.security.cert.Certificate>?=null
  override fun getServerCertificates():Array<java.security.cert.Certificate> = emptyArray()
  override fun getOutputStream():OutputStream=body
  override fun getContentType()="application/json"
  override fun getHeaderField(name:String):String?=if(name=="Cache-Control")"no-store"else null
  override fun getResponseCode()=if(requestMethod=="POST"&&url.path=="/v1/groups")201 else 200
  override fun getInputStream():InputStream {
   val value=if(requestMethod=="POST"){
    check(url.path=="/v1/groups"||url.path=="/v1/groups/$conversation/members")
    val request=JSONObject(body.toString("UTF-8"));posts.add(request.toString())
    postEntered?.countDown();check(postRelease?.await(15,TimeUnit.SECONDS)!=false){"post release timed out"}
    mutationFault?.let{throw it}
    JSONObject().put("requestId",request.getString("requestId")).put("conversationId",conversation)
     .put("addedMemberUserIds",JSONArray(if(url.path=="/v1/groups")listOf(account,friend).sorted()else listOf(friend)))
     .put("createdAt","2026-10-29T00:00:00Z")
   }else{
    check(url.path=="/v1/conversations");readEntered.countDown()
    check(readRelease.await(15,TimeUnit.SECONDS)){"member release timed out"};readFault?.let{throw it}
    val request=url.query.split('&').single{it.startsWith("requestId=")}.substringAfter('=')
    JSONObject().put("requestId",request).put("items",JSONArray()).put("hasMore",false)
     .put("next",JSONObject().put("afterConversationId","").put("afterMemberUserId",""))
   }
   return value.toString().byteInputStream()
  }
 }
 private fun root():AccessibilityNodeInfo?{uiAutomation.clearCache();return uiAutomation.rootInActiveWindow}
 private fun find(n:AccessibilityNodeInfo?,label:String):AccessibilityNodeInfo? {
  if(n==null)return null
  if(n.text?.toString()==label||n.contentDescription?.toString()==label)return n
  for(i in 0 until n.childCount)find(n.getChild(i),label)?.let{return it}
  return null
 }
 private fun settled(test:()->Boolean){repeat(150){if(test())return;Thread.sleep(40)};error("Actual Compose/VM state did not converge")}
 private fun click(label:String){
  repeat(150){if(find(root(),label)==null)Thread.sleep(40)};var n=find(root(),label)
  while(n!=null&&!n.isClickable)n=n.parent
  check(n!=null&&n.isEnabled&&n.performAction(AccessibilityNodeInfo.ACTION_CLICK)){"Control disabled: $label"}
  waitForIdleSync();Thread.sleep(150)
 }
 private fun set(change:(WorkspaceState)->WorkspaceState){runOnMainSync{flow.value=change(flow.value)};waitForIdleSync();Thread.sleep(100)}
 private fun idle(){runBlocking{withTimeout(10000){ownedScope!!.coroutineContext[Job]!!.children.toList().forEach{it.join()}}};waitForIdleSync()}
 private fun stop(keep:Boolean){runOnMainSync{runBlocking{suspendCoroutine<Unit>{c->
  val m=field(model,"generation");check(m.getLong(model)>=0)
  val method=model.javaClass.getDeclaredMethod("stop",Boolean::class.javaPrimitiveType,Continuation::class.java).apply{isAccessible=true}
  val result=try{method.invoke(model,keep,c)}catch(e:java.lang.reflect.InvocationTargetException){throw e.cause!!}
  if(result!==kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED)c.resume(Unit)
 }}};waitForIdleSync()}
 private fun prepare(){
  readRelease.countDown();postRelease?.countDown();idle();stop(false)
  mutationFault=null;readFault=null;postEntered=null;postRelease=null;escaped.set(null)
  readEntered=CountDownLatch(1);readRelease=CountDownLatch(1)
  val auth=Auth("https://group-close.invalid",Preferences(targetContext));field(auth,"session").set(auth,session)
  runOnMainSync{field(model,"auth").set(model,auth)}
  set{WorkspaceState(session=session,friends=friends,friendsStatus="ready")}
 }
 private fun selector(){click("+ New chat");click("Create group");click("Close Friend")}
 private fun confirmed(before:Long){
  check(readEntered.await(10,TimeUnit.SECONDS)){"No actual follow-up member GET"}
  settled{model.state.value.groupStatus=="success"}
  check(model.state.value.groupSuccessRevision==before+1){"Confirmed mutation still waits for member GET to close selector"}
  check(model.state.value.selected==conversation){"Confirmed conversation not opened before member GET"}
  settled{find(root(),"Search friends")==null}
  check(model.state.value.groupPending==null&&!model.state.value.groupBusy)
 }
 override fun onCreate(args:Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=Bundle()
  val code=FriendLoadInstrumentation().runChecks(result,{
   URL.setURLStreamHandlerFactory{scheme->if(scheme=="https")object:URLStreamHandler(){override fun openConnection(url:URL):URLConnection{check(url.host=="group-close.invalid");return Peer(url)}}else null}
   activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) as MainActivity
   val key=activity.viewModelStore.keys().single{it.endsWith("WorkspaceViewModel")}
   model=androidx.lifecycle.ViewModelProvider(activity)[key,WorkspaceViewModel::class.java]
   @Suppress("UNCHECKED_CAST") val mutable=field(model,"mutable").get(model) as MutableStateFlow<WorkspaceState>;flow=mutable
   val original=field(model,"scope").get(model) as CoroutineScope
   runBlocking{original.coroutineContext[Job]!!.children.toList().forEach{it.join()}};original.cancel()
   ownedScope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate+CoroutineExceptionHandler{_,e->escaped.set(e)})
   field(model,"scope").set(model,ownedScope)

   // First CREATE: mutation confirmation closes real selector before deferred read.
   prepare();selector();val count=posts.size;click("Confirm");confirmed(0)
   check(posts.size==count+1)
   // Open a later selector while old metadata read is still pending.
   click("Back to chats");click("+ New chat");click("Create group")
   readRelease.countDown();idle();check(find(root(),"Search friends")!=null){"Old read closed a new picker"}
   check(model.state.value.groupSuccessRevision==1L&&posts.size==count+1)
   click("Cancel")

   // First ADD, using actual member-management controls, closes before unknown read.
   prepare();set{it.copy(selected=conversation,groups=listOf(MemberRow(conversation,"GROUP",account,"2026-10-29T00:00:00Z",GroupUser(account,"close_actor","Actor"),"OWNER","2026-10-29T00:00:00Z")))}
   click("Members");click("+ Add members");click("Close Friend")
   val unknown=IllegalStateException("owned unknown member read");readFault=unknown
   click("Confirm");confirmed(0);readRelease.countDown();idle()
   check(escaped.get()===unknown){"Unknown member failure did not escape unchanged"}
   check(model.state.value.groupStatus=="success"&&model.state.value.groupSuccessRevision==1L)

   // Lost response retains original operation across actual stop(true), locale/reopen.
   prepare();mutationFault=IOException("owned response loss");selector();click("Confirm")
   settled{model.state.value.groupStatus=="unconfirmed"};val pending=checkNotNull(model.state.value.groupPending)
   check(model.state.value.groupSuccessRevision==0L&&find(root(),"Search friends")!=null)
   click("Cancel");stop(true);set{it.copy(session=session,friends=friends,friendsStatus="ready",language="zh-CN")}
   set{it.copy(language="en")};click("+ New chat");click("Create group")
   check(find(root(),"Close Friend")?.isChecked==true){"Original selection was lost"}
   mutationFault=null;val oldCount=posts.size;click("Retry original request");confirmed(0)
   check(posts.size==oldCount+1&&JSONObject(posts.last()).getString("requestId")==pending.requestId)
   check(JSONObject(posts.last()).getJSONArray("memberUserIds").getString(0)==friend)
   readRelease.countDown();idle();check(escaped.get()==null)

   // Retired account's delayed successful mutation cannot close/open new account UI.
   prepare();postEntered=CountDownLatch(1);postRelease=CountDownLatch(1);selector();click("Confirm")
   check(postEntered!!.await(10,TimeUnit.SECONDS));stop(false)
   set{it.copy(session=session.copy(userId=UUID.randomUUID().toString()),friends=friends,friendsStatus="ready")}
   click("+ New chat");click("Create group");postRelease!!.countDown();idle()
   check(find(root(),"Search friends")!=null&&model.state.value.selected.isEmpty()&&model.state.value.groupSuccessRevision==0L)
   check(readEntered.count==1L&&escaped.get()==null)
   result.putString("result","PASS")
   result.putString("scope","Actual Compose/VM first CREATE/ADD; delayed/unknown member reads; original-ID same-account retry/reopen; old-read/new-picker and retired-account safety. Controlled transport, not TLS/DB acceptance.")
  },{readRelease.countDown();postRelease?.countDown();ownedScope?.cancel()}, {if(::activity.isInitialized)runOnMainSync{activity.finish()}})
  finish(code,result)
 }
}

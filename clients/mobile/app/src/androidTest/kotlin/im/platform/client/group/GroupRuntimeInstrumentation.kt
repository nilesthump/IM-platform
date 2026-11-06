package im.platform.client.group
import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity
import im.platform.client.ui.WorkspaceViewModel
import org.json.JSONObject
import java.io.File
/** Owned real-Compose/default SDK TLS entry checks. Credentials are read only from app-private test input. */
class GroupRuntimeInstrumentation:Instrumentation(){
 private lateinit var activity:Activity
 private lateinit var output:File
 private var args=Bundle()
 private fun vm():WorkspaceViewModel {val owner=activity as MainActivity;val key=owner.viewModelStore.keys().single{it.endsWith("WorkspaceViewModel")};return androidx.lifecycle.ViewModelProvider(owner)[key,WorkspaceViewModel::class.java]}
 private fun root():AccessibilityNodeInfo? {uiAutomation.clearCache();return uiAutomation.rootInActiveWindow}
 private fun find(n:AccessibilityNodeInfo?,label:String):AccessibilityNodeInfo? {if(n==null)return null;if(n.text?.toString()==label||n.contentDescription?.toString()==label)return n;for(i in 0 until n.childCount)find(n.getChild(i),label)?.let{return it};return null}
 private fun await(label:String):AccessibilityNodeInfo {repeat(300){find(root(),label)?.let{return it};Thread.sleep(100)};error("Missing actual control: "+label)}
 private fun click(label:String){
  fun actionable(n:AccessibilityNodeInfo?,parent:AccessibilityNodeInfo?):AccessibilityNodeInfo? {if(n==null)return null;val owner=if(n.isClickable)n else parent;if((n.text?.toString()==label||n.contentDescription?.toString()==label)&&owner!=null)return owner;for(i in 0 until n.childCount)actionable(n.getChild(i),owner)?.let{return it};return null}
  var target:AccessibilityNodeInfo?=null;repeat(300){if(target==null){target=actionable(root(),null)?.takeIf{it.isEnabled};if(target==null){if(label=="Sign out"){fun scroll(n:AccessibilityNodeInfo?):Boolean{if(n==null)return false;if(n.isScrollable&&n.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD))return true;for(i in 0 until n.childCount)if(scroll(n.getChild(i)))return true;return false};scroll(root())};Thread.sleep(100)}}};val n=target?:error("Missing clickable control: "+label);check(n.isEnabled&&n.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();Thread.sleep(350)
 }
 private fun checkbox(label:String):AccessibilityNodeInfo {fun find(n:AccessibilityNodeInfo?):AccessibilityNodeInfo?{if(n==null)return null;if(n.isCheckable&&n.isVisibleToUser&&n.contentDescription?.toString()==label)return n;for(i in 0 until n.childCount){val found=find(n.getChild(i));if(found!=null)return found};return null};return find(root())?:error("Missing actual friend checkbox: $label")}
 private fun choose(label:String,checked:Boolean=true){val box=checkbox(label);check(box.isChecked!=checked);check(box.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();settled{checkbox(label).isChecked==checked}}
 private fun fill(label:String,value:String){Thread.sleep(750);var n:AccessibilityNodeInfo?=await(label);while(n!=null&&n.actionList.none{it.id==AccessibilityNodeInfo.ACTION_SET_TEXT})n=n.parent
  if(n==null&&label=="Message"){val candidates=mutableListOf<AccessibilityNodeInfo>();fun collect(v:AccessibilityNodeInfo?){if(v==null)return;if(v.isVisibleToUser&&v.isEditable&&v.isEnabled)candidates.add(v);for(i in 0 until v.childCount)collect(v.getChild(i))};collect(root());if(candidates.size==1)n=candidates.single()}
  val edit=n?:error("Not editable: "+label);check(edit.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,Bundle().apply{putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,value)}));waitForIdleSync()
 }
 private fun settled(test:()->Boolean){repeat(400){if(test())return;Thread.sleep(100)};error("Actual group state did not converge")}
 private fun capture(name:String){waitForIdleSync();Thread.sleep(250);val bitmap=checkNotNull(uiAutomation.takeScreenshot());File(output,name+".png").outputStream().use{check(bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it))};val s=vm().state.value;File(output,name+".json").writeText(JSONObject().put("sourceSHA",args.getString("sourceSHA")).put("locale",s.language).put("theme",s.appearance.theme).put("fontSize",s.appearance.fontSize).put("density",s.appearance.density).put("width",bitmap.width).put("height",bitmap.height).put("groupStatus",s.groupStatus).put("groupRows",s.groups.size).put("conversationId",s.selected).put("messageCount",s.messages.size).toString(2));bitmap.recycle()}
 private fun refreshOffline(){
  activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));Thread.sleep(1000)
  val v=vm();@Suppress("UNCHECKED_CAST") val f=v.javaClass.getDeclaredField("mutable").apply{isAccessible=true}.get(v) as kotlinx.coroutines.flow.MutableStateFlow<im.platform.client.ui.WorkspaceState>
  val a="10000000-0000-4000-8000-000000000001";val b="10000000-0000-4000-8000-000000000002"
  val session=im.platform.client.send.SendSession(a,"20000000-0000-4000-8000-000000000001",java.math.BigInteger.ONE,"offline")
  val friends=listOf(im.platform.client.ui.Friend(im.platform.client.ui.User(b,"fixture","Refresh Friend"),"30000000-0000-4000-8000-000000000001","40000000-0000-4000-8000-000000000001"))
  fun set(s:im.platform.client.ui.WorkspaceState){runOnMainSync{f.value=s};waitForIdleSync();Thread.sleep(300)}
  fun stop(keep:Boolean){runOnMainSync{kotlinx.coroutines.runBlocking{kotlin.coroutines.suspendCoroutine<Unit>{c->val m=v.javaClass.getDeclaredMethod("stop",Boolean::class.javaPrimitiveType,kotlin.coroutines.Continuation::class.java).apply{isAccessible=true};if(m.invoke(v,keep,c)!==kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED)c.resumeWith(Result.success(Unit))}}};waitForIdleSync();Thread.sleep(300)}
  set(im.platform.client.ui.WorkspaceState(groupSuccessRevision=1,session=session));click("+ New chat");click("Create group")
  await("Loading friends…");check(find(root(),"Add a friend to start a group.")==null);capture("friends-loading")
  set(f.value.copy(friendsStatus="error"));await("Could not load friends. Retry.");check(find(root(),"Add a friend to start a group.")==null);capture("friends-error")
  set(f.value.copy(friendsStatus="ready"));await("Add a friend to start a group.");capture("friends-empty")
  set(f.value.copy(friends=friends));fill("Search friends","Refresh");choose("Refresh Friend")
  click("Confirm");val op=v.javaClass.getDeclaredField("groupOperation").apply{isAccessible=true}.get(v) as GroupOperation;check(op.account==a&&op.targets==listOf(b))
  set(f.value.copy(groupPending=op,groupStatus="unconfirmed"));stop(true);check(f.value.session==null&&f.value.groupPending==op);set(f.value.copy(session=session,friends=friends))
  set(f.value.copy(friendsStatus="error"));await("Could not load friends. Retry.");check(await("Retry original request").isEnabled);check(await("Cancel").isEnabled);capture("friends-error-unconfirmed");await("Search friends");check(find(root(),"Refresh")!=null){"Search cleared by refresh"};check(checkbox("Refresh Friend").isChecked);check(f.value.groupPending==op)
  set(f.value.copy(groupStatus="success",groupPending=null,groupSuccessRevision=f.value.groupSuccessRevision+1));check(find(root(),"Search friends")==null){"Confirmed success did not close selector"}
  stop(false);check(f.value.groupPending==null);set(im.platform.client.ui.WorkspaceState(session=session.copy(userId="10000000-0000-4000-8000-000000000003"),friends=friends))
  click("+ New chat");click("Create group");await("Search friends");check(find(root(),"Refresh")==null);check(!checkbox("Refresh Friend").isChecked)
 }
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);args=arguments?:Bundle();start()}
 // Keep both actual check and owned fixture cleanup failures in the final report.
 internal fun runChecks(result:Bundle,checks:()->Unit,cleanup:()->Unit):Int {
  var failure:Throwable?=null
  try{checks()}catch(e:Throwable){failure=e
   if(::output.isInitialized&&::activity.isInitialized)try{capture("failure")}catch(captureError:Throwable){if(captureError!==e)e.addSuppressed(captureError);result.putString("captureFailure",captureError.toString())}
  }finally{try{cleanup()}catch(e:Throwable){val primary=failure;if(primary==null)failure=e else if(primary!==e)primary.addSuppressed(e)}}
  failure?.let{result.putString("result","FAIL");result.putString("failure",it.stackTraceToString())}
  return if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED
 }
 override fun onStart(){val result=Bundle();val input=File(targetContext.filesDir,"group-runtime-fixture.json");val code=runChecks(result,{
  if(args.getString("mode")=="refresh-offline"){output=File(targetContext.getExternalFilesDir(null),"group-runtime/"+checkNotNull(args.getString("runId")));check(output.mkdirs());refreshOffline();result.putString("result","PASS")}else{
  val accounts=JSONObject(input.readText());val run=checkNotNull(args.getString("runId"));require(Regex("[A-Za-z0-9-]+").matches(run));output=File(targetContext.getExternalFilesDir(null),"group-runtime/"+run);check(output.mkdirs());
  activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));settled{vm().state.value.language=="en"}
  val a=accounts.getJSONObject("A");fill("Username",a.getString("username"));fill("Password",a.getString("password"));runOnMainSync{(activity.getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager).hideSoftInputFromWindow(activity.window.decorView.windowToken,0)};click("Sign in");settled{vm().state.value.session?.userId==a.getString("userId")&&vm().state.value.friends.isNotEmpty()};
  click("+ New chat");click("Create group");
  val beforeCancel=vm().state.value;fill("Search friends","Group Fixture B");choose("Group Fixture B");
  runOnMainSync{vm().language("zh-CN")};await("取消");check(checkbox("Group Fixture B").isChecked);runOnMainSync{vm().language("en")};await("Cancel");check(checkbox("Group Fixture B").isChecked);choose("Group Fixture B",false);click("Cancel");
  check(vm().state.value.selected==beforeCancel.selected&&vm().state.value.groupPending==null&&vm().state.value.groupSuccessRevision==beforeCancel.groupSuccessRevision);
  click("+ New chat");click("Create group");capture("android-friend-selection");choose("Group Fixture B");click("Confirm");settled{vm().state.value.groupStatus=="success"&&vm().state.value.groups.size>=2};capture("android-created-members");val conversation=vm().state.value.selected;check(conversation.isNotEmpty());click("Members");await(conversation);capture("android-member-management");click("← Cancel");
  settled{vm().state.value.selected==conversation};fill("Message","GROUP Android actual "+run);runOnMainSync{(activity.getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager).hideSoftInputFromWindow(activity.window.decorView.windowToken,0)};click("Send ↑");settled{vm().state.value.messages.any{it[2]=="GROUP Android actual "+run&&it[3]=="SENT"}};capture("android-group-sent");
  click("Back to chats");click("Settings");click("Sign out");settled{vm().state.value.session==null&&!vm().state.value.busy}
  val b=accounts.getJSONObject("B");fill("Username",b.getString("username"));fill("Password",b.getString("password"));runOnMainSync{(activity.getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager).hideSoftInputFromWindow(activity.window.decorView.windowToken,0)};click("Sign in");settled{vm().state.value.session?.userId==b.getString("userId")&&vm().state.value.groups.any{it.conversationId==conversation}};click("Chat");click("Conversation "+conversation.take(8));settled{vm().state.value.selected==conversation};click("Members");click("+ Add members");choose("Group Fixture C");click("Confirm");settled{vm().state.value.groupStatus=="success"&&vm().state.value.groups.count{it.conversationId==conversation}==3};capture("android-b-added-c");click("Back to chats");click("Settings");click("Sign out");settled{vm().state.value.session==null&&!vm().state.value.busy}
  val c=accounts.getJSONObject("C");fill("Username",c.getString("username"));fill("Password",c.getString("password"));runOnMainSync{(activity.getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager).hideSoftInputFromWindow(activity.window.decorView.windowToken,0)};click("Sign in");settled{vm().state.value.session?.userId==c.getString("userId")&&vm().state.value.groups.count{it.conversationId==conversation}==3};click("Chat");click("Conversation "+conversation.take(8));settled{vm().state.value.selected==conversation};fill("Message","GROUP Android C "+run);runOnMainSync{(activity.getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager).hideSoftInputFromWindow(activity.window.decorView.windowToken,0)};click("Send ↑");settled{vm().state.value.messages.any{it[2]=="GROUP Android C "+run&&it[3]=="SENT"}};capture("android-c-group-sent");
  result.putString("result","PASS");result.putString("conversationId",conversation);result.putInt("targetProcessId",android.os.Process.myPid());result.putString("scope","Real Compose create/members/group send through default SDK TLS; G06/G07/G08/G09 full matrix still separate")
 }},{if(args.getString("mode")!="refresh-offline"&&input.exists()&&!input.delete())throw IllegalStateException("Owned private fixture cleanup failed")});finish(code,result)}
}

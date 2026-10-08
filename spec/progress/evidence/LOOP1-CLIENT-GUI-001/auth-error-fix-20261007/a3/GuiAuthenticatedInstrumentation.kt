package im.platform.client.ui
import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity
import java.net.URL
import javax.net.ssl.HttpsURLConnection

/** Real Compose UI/default SDK TLS against task-owned actual Go fixture. */
class GuiAuthenticatedInstrumentation:Instrumentation(){
 private val deliveries=mutableListOf<String>()
 private var args=Bundle();private var activity:Activity?=null;private var count=0
 private val captureRun=System.currentTimeMillis().toString()
 private val sentText="GUI Android actual send "+captureRun
 private val retryText="GUI Android retry identity "+captureRun
 private val sendingText="GUI Android controlled sending "+captureRun
 private fun verify(v:Boolean){check(v){"Actual GUI assertion "+count+" failed"};count++}
 private fun headerAbsent(themeInSettings:Boolean=false){
  verify(find(actualRoot(),"IM+ logo")==null&&find(actualRoot(),"IM+")==null)
  verify((find(actualRoot(),"Cold AI")!=null||find(actualRoot(),"Warm Creative")!=null)==themeInSettings)
 }
 private fun actualRoot():AccessibilityNodeInfo?{uiAutomation.clearCache();return uiAutomation.rootInActiveWindow}
 private fun find(n:AccessibilityNodeInfo?,text:String,prefix:Boolean=false):AccessibilityNodeInfo?{
  if(n==null)return null;val v=n.text?.toString()?:n.contentDescription?.toString()
  if(v==text || prefix&&v?.startsWith(text)==true)return n
  for(i in 0 until n.childCount)find(n.getChild(i),text,prefix)?.let{return it};return null
 }
 private fun await(text:String,prefix:Boolean=false):AccessibilityNodeInfo{
  repeat(300){find(actualRoot(),text,prefix)?.let{return it};Thread.sleep(100)}
  error("Actual control missing: "+text)
 }
 private fun scroll(n:AccessibilityNodeInfo?,direction:Int=AccessibilityNodeInfo.ACTION_SCROLL_FORWARD):Boolean{
  fun collection(v:AccessibilityNodeInfo?):Boolean{
   if(v==null)return false
   if(v.collectionInfo!=null&&v.isScrollable&&v.performAction(direction))return true
   for(i in 0 until v.childCount)if(collection(v.getChild(i)))return true
   return false
  }
  if(collection(n))return true
  if(n==null)return false;if(n.isScrollable&&n.performAction(direction))return true
  for(i in 0 until n.childCount)if(scroll(n.getChild(i),direction))return true;return false
 }
 private fun click(text:String,prefix:Boolean=false){
  fun actionable(n:AccessibilityNodeInfo?,parent:AccessibilityNodeInfo?):AccessibilityNodeInfo?{
   if(n==null)return null
   val next=if(n.isClickable)n else parent
   val value=n.text?.toString()?:n.contentDescription?.toString()
   if(value==text||prefix&&value?.startsWith(text)==true)if(next!=null)return next
   for(i in 0 until n.childCount)actionable(n.getChild(i),next)?.let{return it}
   return null
  }
  var target:AccessibilityNodeInfo?=null
  repeat(300){if(target==null){target=actionable(actualRoot(),null);if(target==null)Thread.sleep(100)}}
  val n=target?:error("Actual clickable control missing "+text)
  verify(n.isEnabled);verify(n.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();Thread.sleep(650);uiAutomation.waitForIdle(200,5000)
 }
 private fun reach(text:String){
  var diagnostic="absent"
  repeat(10){
   var n=find(actualRoot(),text)
   while(n!=null){
    val r=android.graphics.Rect();n.getBoundsInScreen(r)
    val b=uiAutomation.takeScreenshot()
    if(b!=null){
     diagnostic="bounds="+r+" viewport="+b.width+"x"+b.height+" clickable="+n.isClickable
     val visible=r.width()>0&&r.height()>0&&r.left>=0&&r.top>=0&&r.right<=b.width&&r.bottom<=b.height
     b.recycle();if(visible)return
    }
    n=n.parent
   }
   scroll(actualRoot());waitForIdleSync();Thread.sleep(650);uiAutomation.waitForIdle(200,5000)
  }
  fun describe(n:AccessibilityNodeInfo?):String{
   if(n==null)return "root-null"
   val here=if(n.isPassword||n.isEditable) "[edit]" else "[text="+n.text+" desc="+n.contentDescription+" clickable="+n.isClickable+"]"
   return here+(0 until n.childCount).joinToString(""){describe(n.getChild(it))}
  }
  error("Control unreachable "+text+" "+diagnostic+" activityFinishing="+activity?.isFinishing+" activityDestroyed="+activity?.isDestroyed+" rootPackage="+actualRoot()?.packageName+" windows="+uiAutomation.windows.joinToString{it.id.toString()+":"+it.type+":"+it.isActive}+" tree="+describe(actualRoot()))
 }
 private fun fill(label:String,value:String){
  reach(label);var n=await(label);while(n.actionList.none{it.id==AccessibilityNodeInfo.ACTION_SET_TEXT})n=n.parent?:error("No edit "+label)
  val b=Bundle();b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,value)
  verify(n.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,b));waitForIdleSync();Thread.sleep(200)
 }
 private fun capture(name:String){
  Thread.sleep(250);val d=java.io.File(targetContext.getExternalFilesDir(null),"gui-auth/$captureRun").apply{mkdirs()}
  val b=checkNotNull(uiAutomation.takeScreenshot());java.io.File(d,name+".png").outputStream().use{check(b.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it))}
  if(args.getString("phase") in listOf("evidence-complete","auth-errors")){
   val s=actualViewModel().state.value
   java.io.File(d,name+".json").writeText(org.json.JSONObject().put("theme",s.appearance.theme).put("fontSize",s.appearance.fontSize).put("spacingDensity",s.appearance.density).put("busy",s.busy).put("error",s.error).put("connection",s.connection).put("sync",s.sync).put("conversationCount",s.conversations.size).put("friendCount",s.friends.size).put("resultCount",s.results.size).put("messageCount",s.messages.size).put("conversationSelected",s.selected.isNotEmpty()).put("sessionPresent",s.session!=null).put("offlineAccountPresent",s.offlineAccount!=null).put("secureCurrentPresent",Preferences(targetContext).read("https://localhost:8443/current")!=null).put("width",b.width).put("height",b.height).toString(2))
  };b.recycle()
 }
 private fun delivery(text:String,status:String):List<String?>{
  val account=checkNotNull(Auth("https://localhost:8443",Preferences(targetContext)).savedAccount())
  val file=targetContext.getDatabasePath("im-"+account.lowercase()+".sqlite");check(file.isFile)
  android.database.sqlite.SQLiteDatabase.openDatabase(file.path,null,android.database.sqlite.SQLiteDatabase.OPEN_READONLY).use{db->
   repeat(300){
    db.rawQuery("SELECT request_id,sender_id,content,state,server_message_id FROM messages WHERE content=? AND state=? ORDER BY local_id DESC LIMIT 1",arrayOf(text,status)).use{c->
     if(c.moveToFirst()){val row=(0 until c.columnCount).map{if(c.isNull(it))null else c.getString(it)};deliveries.add(text+"|"+status+"|"+row[0]+"|"+row[4]);return row}
    }
    Thread.sleep(100)
   }
  }
  val db=android.database.sqlite.SQLiteDatabase.openDatabase(file.path,null,android.database.sqlite.SQLiteDatabase.OPEN_READONLY)
  val observed=try{db.rawQuery("SELECT content,state FROM messages ORDER BY local_id DESC LIMIT 8",null).use{c->val rows=mutableListOf<String>();while(c.moveToNext()){val content=c.getString(0);if(content.startsWith("GUI Android"))rows.add(content+":"+c.getString(1))};rows.joinToString("|")}}finally{db.close()}
  error("Actual read-only repository delivery missing "+text+" "+status+" observed="+observed)
 }
 private fun actualViewModel():WorkspaceViewModel{
  val owner=activity as MainActivity;val key=owner.viewModelStore.keys().single{it.endsWith("WorkspaceViewModel")}
  return androidx.lifecycle.ViewModelProvider(owner)[key,WorkspaceViewModel::class.java]
 }
 private fun showMessage(text:String){
  fun list(n:AccessibilityNodeInfo?,composerTop:Int,minHeight:Int):AccessibilityNodeInfo?{
   if(n==null)return null;val r=android.graphics.Rect();n.getBoundsInScreen(r)
   if(n.isScrollable&&r.height()>minHeight&&r.bottom<=composerTop)return n
   for(i in 0 until n.childCount)list(n.getChild(i),composerTop,minHeight)?.let{return it};return null
  }
  repeat(40){
   val root=actualRoot();val composer=android.graphics.Rect();var editor=find(root,"Message")
   while(editor!=null){editor.getBoundsInScreen(composer);if(!composer.isEmpty)break;editor=editor.parent}
   val screen=checkNotNull(uiAutomation.takeScreenshot());val height=screen.height;screen.recycle()
   val viewport=android.graphics.Rect();val n=list(root,composer.top,height/6)
   val target=find(root,text);val r=android.graphics.Rect();target?.getBoundsInScreen(r)
   if(n==null){
    val heading=android.graphics.Rect();(find(root,"Messages sync automatically")?:find(root,"Offline · Showing saved history"))?.getBoundsInScreen(heading)
    check(target!=null&&!heading.isEmpty&&!r.isEmpty&&r.left>=0&&r.top>=heading.bottom&&r.bottom<=composer.top-36){"Actual complete non-scrolling message viewport unavailable"}
    return
   }
   n.getBoundsInScreen(viewport)
   if(target!=null&&!r.isEmpty&&r.top>=viewport.top+8&&r.bottom<=viewport.bottom-16)return
   val messages=actualViewModel().state.value.messages
   val targetIndex=messages.indexOfFirst{it[2]==text}
   val visible=messages.mapIndexedNotNull{index,row->val v=find(root,row[2]?:"");val bounds=android.graphics.Rect();v?.getBoundsInScreen(bounds);if(v!=null&&!bounds.isEmpty&&bounds.intersects(viewport.left,viewport.top,viewport.right,viewport.bottom))index else null}
   val above=visible.isNotEmpty()&&targetIndex>=0&&targetIndex<visible.min()
   val delta=if(above)viewport.height()/3 else if(target!=null&&!r.isEmpty&&r.top<viewport.top+8)kotlin.math.min(viewport.height()/3,kotlin.math.max(20,viewport.top+8-r.top))
    else -kotlin.math.min(viewport.height()/3,if(target==null||r.isEmpty)viewport.height()/3 else kotlin.math.max(20,r.bottom-(viewport.bottom-16)))
   val x=viewport.centerX().toFloat();val y=viewport.centerY().toFloat();val down=android.os.SystemClock.uptimeMillis()
   fun event(action:Int,step:Int){val e=android.view.MotionEvent.obtain(down,android.os.SystemClock.uptimeMillis(),action,x,y+delta*step/6f,0);e.source=android.view.InputDevice.SOURCE_TOUCHSCREEN;try{verify(uiAutomation.injectInputEvent(e,true))}finally{e.recycle()}}
   event(android.view.MotionEvent.ACTION_DOWN,0);for(i in 1..6){Thread.sleep(25);event(android.view.MotionEvent.ACTION_MOVE,i)};event(android.view.MotionEvent.ACTION_UP,6)
   Thread.sleep(250);uiAutomation.waitForIdle(100,3000)
  }
  error("Actual complete message viewport unavailable "+text)
 }
 private fun retryMessage(text:String){
  showMessage(text);val body=android.graphics.Rect();await(text).getBoundsInScreen(body)
  val candidates=mutableListOf<Pair<AccessibilityNodeInfo,android.graphics.Rect>>()
  fun scan(n:AccessibilityNodeInfo?,parent:AccessibilityNodeInfo?){
   if(n==null)return;val click=if(n.isClickable)n else parent
   if(n.text?.toString()=="Retry"&&click!=null){val r=android.graphics.Rect();click.getBoundsInScreen(r);if(r.top>=body.bottom)candidates.add(click to r)}
   for(i in 0 until n.childCount)scan(n.getChild(i),click)
  }
  scan(actualRoot(),null);val n=checkNotNull(candidates.minByOrNull{it.second.top}){"Current message Retry unavailable"}.first
  verify(n.isEnabled);verify(n.performAction(AccessibilityNodeInfo.ACTION_CLICK));Thread.sleep(650);uiAutomation.waitForIdle(200,5000)
 }
 private fun actualState():String{
  val owner=activity as MainActivity
  val keys=owner.viewModelStore.keys().filter{it.endsWith("WorkspaceViewModel")}
  val vm=androidx.lifecycle.ViewModelProvider(owner)[keys.single(),WorkspaceViewModel::class.java]
  val f=WorkspaceViewModel::class.java.getDeclaredField("sync").apply{isAccessible=true}
  val sync=f.get(vm) as? im.platform.client.sync.SyncViewModel
  val send=sync?.send
  fun read(name:String):Any?=send?.javaClass?.getDeclaredField(name)?.apply{isAccessible=true}?.get(send)
  return "keys="+keys.joinToString()+" workspaceConnection="+vm.state.value.connection+" messages="+vm.state.value.messages.size+" error="+vm.state.value.error+" sendConnection="+send?.state?.value?.connection+" sendError="+send?.state?.value?.error+" bound="+read("bound")+" socketPresent="+(read("socket")!=null)+" attempts="+((read("attempts") as? Map<*,*>)?.size)+" sentRequestCount="+((read("requestConversations") as? Map<*,*>)?.size)+" wssClosed="+read("socket")?.let{it.javaClass.getDeclaredField("closed").apply{isAccessible=true}.get(it)}
 }
 private fun mainNetworkProbe():String{
  val owner=activity as MainActivity;val key=owner.viewModelStore.keys().single{it.endsWith("WorkspaceViewModel")}
  val vm=androidx.lifecycle.ViewModelProvider(owner)[key,WorkspaceViewModel::class.java]
  val sync=WorkspaceViewModel::class.java.getDeclaredField("sync").apply{isAccessible=true}.get(vm) as im.platform.client.sync.SyncViewModel
  val socket=sync.send.javaClass.getDeclaredField("socket").apply{isAccessible=true}.get(sync.send) as im.platform.client.send.SendSocket
  var observed="unavailable"
  runOnMainSync{try{socket.send(im.platform.client.send.Wire.envelope("ping",java.util.UUID.randomUUID().toString(),org.json.JSONObject()));observed="NO_EXCEPTION"}catch(e:Throwable){observed=e.javaClass.name}}
  return observed
 }
 private fun backKeyboard(){uiAutomation.injectInputEvent(android.view.KeyEvent(0,android.view.KeyEvent.KEYCODE_BACK),true);uiAutomation.injectInputEvent(android.view.KeyEvent(1,android.view.KeyEvent.KEYCODE_BACK),true);Thread.sleep(650);uiAutomation.waitForIdle(200,5000)}
 private fun login(user:String){
  fill("Username",user);fill("Password","fixture-password-not-a-real-secret");backKeyboard();reach("Sign in");click("Sign in");await("Connected")
 }
 private fun navigate(page:String){
  if(find(actualRoot(),"←")!=null)click("←")
  fun selected(n:AccessibilityNodeInfo?):Boolean{
   if(n==null)return false
   if(n.isSelected&&find(n,page)!=null)return true
   for(i in 0 until n.childCount)if(selected(n.getChild(i)))return true;return false
  }
  if(!selected(actualRoot()))click(page)
 }
 private fun openMorgan(){navigate("Chat");if(find(actualRoot(),"←")!=null)click("←");click("GUI Fixture Morgan")}
 private fun settingsControl(name:String){navigate("Settings");reach(name);click(name)}
 private fun toggleTheme(){
  navigate("Settings")
  val current=if(actualViewModel().state.value.appearance.theme=="cold")"Cold AI" else "Warm Creative"
  repeat(10){if(scroll(actualRoot(),AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)){waitForIdleSync();Thread.sleep(100)}}
  reach(current);click(current)
 }
 private fun controlled(name:String){
  val directory=java.io.File(targetContext.getExternalFilesDir(null),"gui-auth/$captureRun").apply{mkdirs()}
  java.io.File(directory,name+"-ready").writeText(captureRun)
  val proceed=java.io.File(directory,name+"-continue");repeat(1200){if(!proceed.exists())Thread.sleep(50)};verify(proceed.exists())
 }
 private fun top(){repeat(10){if(scroll(actualRoot(),AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)){waitForIdleSync();Thread.sleep(100)}}}
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);args=arguments?:Bundle();start()}
 override fun onStart(){
  val result=Bundle();val prefs=Preferences(targetContext);val appearance=prefs.loadAppearance()
  try{
   verify(android.os.Build.VERSION.SDK_INT==34)
   val c=URL("https://localhost:8443/__infra/health").openConnection() as HttpsURLConnection
   c.connectTimeout=10000;c.readTimeout=10000;c.instanceFollowRedirects=false
   try{verify(c.responseCode==200);c.inputStream.close()}finally{c.disconnect()}
   result.putString("defaultSDKHTTPS","PASS")
   val plain=java.net.Socket();plain.connect(java.net.InetSocketAddress("127.0.0.1",8443),10000)
   val wrong=(javax.net.ssl.SSLSocketFactory.getDefault() as javax.net.ssl.SSLSocketFactory).createSocket(plain,"fixture-hostname-mismatch.invalid",8443,true) as javax.net.ssl.SSLSocket
   try{wrong.soTimeout=10000;val parameters=wrong.sslParameters;parameters.endpointIdentificationAlgorithm="HTTPS";wrong.sslParameters=parameters
    var rejected=false;try{wrong.startHandshake()}catch(_:javax.net.ssl.SSLHandshakeException){rejected=true};verify(rejected)
   }finally{wrong.close()}
   result.putString("defaultHostnameMismatch","PASS");prefs.saveAppearance(Appearance("cold",14,.8f))
   activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));await("Open your workspace")
   val phase=args.getString("phase")?:"matrix"
   if(phase=="auth-errors"){
    fun invalid(name:String){
     fill("Username",args.getString("avery")!!);fill("Password","wrong-fixture-password");backKeyboard();reach("Sign in");click("Sign in");await("Invalid username or password")
     val s=actualViewModel().state.value;verify(s.session==null&&s.offlineAccount==null&&!s.busy&&s.connection=="offline"&&s.error=="Invalid username or password")
     verify(prefs.read("https://localhost:8443/current")==null);verify(find(actualRoot(),"Session expired. Sign in again.")==null);top();reach("Invalid username or password");capture(name)
    }
    invalid("cold-auth-invalid-14")
    login(args.getString("avery")!!);navigate("Settings");top();repeat(8){click("+")};reach("Comfort");click("Comfort");verify(actualViewModel().state.value.appearance==Appearance("cold",22,1.2f));settingsControl("Sign out");await("Open your workspace")
    invalid("cold-auth-invalid-22")
    login(args.getString("avery")!!);toggleTheme();verify(actualViewModel().state.value.appearance==Appearance("warm",22,1.2f));settingsControl("Sign out");await("Open your workspace")
    invalid("warm-auth-invalid-22")
    login(args.getString("avery")!!);val slot=checkNotNull(prefs.read("https://localhost:8443/current"));verify(prefs.read(slot)!=null)
    settingsControl("Go offline");await("Offline");navigate("Settings");reach("Refresh session");verify(prefs.read(slot)!=null);capture("real-session-before-expiry");controlled("expiry");click("Refresh session");await("Session expired. Sign in again.")
    val expired=actualViewModel().state.value;verify(expired.session==null&&expired.offlineAccount==null&&!expired.busy&&expired.connection=="offline")
    verify(prefs.read("https://localhost:8443/current")==null&&prefs.read(slot)==null);top();reach("Session expired. Sign in again.");capture("real-session-expired-cleared")
    result.putString("expiredSecureSlotAbsent","PASS current and former owned session credential absent")
   }else if(phase=="evidence-complete"){
    fill("Username",args.getString("riley")!!);fill("Password","wrong-fixture-password");backKeyboard();reach("Sign in");click("Sign in");await("Invalid username or password");capture("auth-error")
    fill("Password","fixture-password-not-a-real-secret");backKeyboard();reach("Sign in");controlled("auth");click("Sign in");await("Please wait…");verify(actualViewModel().state.value.busy);capture("auth-loading");await("Connected")
    repeat(100){if(actualViewModel().state.value.busy||actualViewModel().state.value.sync!="idle")Thread.sleep(100)}
    verify(actualViewModel().state.value.conversations.isEmpty());await("Your next conversation starts here");capture("empty-chat-list")
    navigate("Friends");await("Your circle is waiting to grow.");capture("empty-friends")
    fill("Username","gui_absent_"+captureRun);backKeyboard();reach("Search");click("Search");repeat(300){if(actualViewModel().state.value.busy)Thread.sleep(100)};reach("No matching user shown.");verify(actualViewModel().state.value.results.isEmpty());capture("friend-not-found")
    fill("Username",args.getString("avery")!!);backKeyboard();reach("Search");controlled("search");click("Search");await("Searching…");verify(actualViewModel().state.value.busy);capture("friends-search-loading");await("GUI Fixture Avery");capture("friends-search-success");reach("Add friend");click("Add friend");repeat(300){if(actualViewModel().state.value.busy)Thread.sleep(100)}
    navigate("Chat");if(find(actualRoot(),"←")==null)click("GUI Fixture Avery");await("No messages yet. Say hello.");verify(actualViewModel().state.value.messages.isEmpty()&&actualViewModel().state.value.selected.isNotEmpty());capture("empty-conversation")
    settingsControl("Go offline");await("Offline");navigate("Friends");top();fill("Username",args.getString("avery")!!);backKeyboard();reach("Search");controlled("error");click("Search");await("Connection unavailable");verify(!actualViewModel().state.value.busy&&actualViewModel().state.value.results.isEmpty());capture("friends-transport-error");controlled("restore")
    navigate("Settings");reach("Reconnect");controlled("sync");click("Reconnect");await("Syncing…");verify(actualViewModel().state.value.sync=="syncing");capture("sync-reconnecting");await("Connected")
    toggleTheme();verify(actualViewModel().state.value.appearance.theme=="warm");navigate("AI");reach("No AI service is connected. Your conversations are not sent to an AI provider.");capture("warm-ai");navigate("Plugin");reach("No plugin runtime or installation service is connected in this release.");capture("warm-plugin")
    navigate("Settings");top();repeat(8){click("+")};reach("Comfort");click("Comfort");verify(actualViewModel().state.value.appearance==Appearance("warm",22,1.2f))
    for(theme in listOf("warm","cold")){
     if(actualViewModel().state.value.appearance.theme!=theme)toggleTheme()
     navigate("Settings");top();reach("Font size: 22px");capture(theme+"-settings-22-top");reach("Profile & session");capture(theme+"-profile-22");reach("Sign out");capture(theme+"-session-22-bottom")
     navigate("Friends");top();fill("Username",args.getString("avery")!!);backKeyboard();reach("Search");click("Search");await("GUI Fixture Avery");reach("Add friend");capture(theme+"-friends-22-search");reach("Your friends");reach("Message");capture(theme+"-friends-22-bottom")
     navigate("AI");top();capture(theme+"-ai-22-top");reach("No AI service is connected. Your conversations are not sent to an AI provider.");capture(theme+"-ai-22-bottom")
     navigate("Plugin");top();capture(theme+"-plugin-22-top");reach("No plugin runtime or installation service is connected in this release.");capture(theme+"-plugin-22-bottom")
    }
    settingsControl("Sign out");await("Open your workspace");click("New here? Create an account");fill("Username","gui_confirm_"+captureRun);fill("Password","fixture-password-not-a-real-secret");fill("Confirm password","different-fixture-password");backKeyboard();reach("Create account");click("Create account");await("Passwords do not match");capture("registration-mismatch-22");reach("Already have an account? Sign in");capture("registration-22-bottom")
   }else if(phase=="ui-revision"){

    verify(find(actualRoot(),"Friends")==null&&find(actualRoot(),"Settings")==null&&find(actualRoot(),"Server")==null);headerAbsent();capture("anonymous-login")
    click("New here? Create an account");fill("Username","gui_ui_"+captureRun);fill("Password","fixture-password-not-a-real-secret");fill("Confirm password","fixture-password-not-a-real-secret");backKeyboard();reach("Create account");capture("registration");click("Create account");await("Account created. Sign in to continue.");capture("registration-success")
    login(args.getString("avery")!!);await("GUI Fixture Morgan");verify(actualViewModel().state.value.selected.isEmpty());verify(find(actualRoot(),"Message")==null);headerAbsent();capture("cold-chat-list")
    click("Friends");await("Your friends");headerAbsent();capture("cold-friends");click("AI");headerAbsent();capture("cold-ai");click("Plugin");headerAbsent();capture("cold-plugin");click("Chat");click("GUI Fixture Morgan");await("Welcome to the GUI fixture. This message crossed the actual Go services.");verify(find(actualRoot(),"Friends")==null&&find(actualRoot(),"Settings")==null);headerAbsent();verify(find(actualRoot(),"←")!=null&&find(actualRoot(),"← Chat")==null&&find(actualRoot(),"Chat")==null);capture("cold-conversation")
    fill("Message",sentText);backKeyboard();click("Send ",true);delivery(sentText,"SENT");reach(sentText);capture("sent")
    click("←");await("GUI Fixture Morgan");verify(actualViewModel().state.value.selected.isEmpty());capture("back-to-chat-list")
    click("Settings");reach("Cold AI");headerAbsent(true);capture("cold-settings-theme");click("Cold AI");verify(actualViewModel().state.value.appearance.theme=="warm");headerAbsent(true);click("Warm Creative");verify(actualViewModel().state.value.appearance==Appearance("cold",14,.8f));click("Cold AI");verify(actualViewModel().state.value.appearance==Appearance("warm",14,.8f));click("Friends");await("Your friends");headerAbsent();capture("warm-friends");click("Settings");repeat(8){click("+")};reach("Comfort");click("Comfort");verify(actualViewModel().state.value.appearance==Appearance("warm",22,1.2f));headerAbsent(true);capture("warm-settings-22")
    click("Chat");await("GUI Fixture Morgan");headerAbsent();capture("warm-chat-list-22");click("GUI Fixture Morgan");reach(sentText);headerAbsent();verify(find(actualRoot(),"←")!=null&&find(actualRoot(),"← Chat")==null&&find(actualRoot(),"Chat")==null);capture("warm-conversation-22");click("←");click("Settings");reach("Sign out");click("Sign out");await("Open your workspace");verify(find(actualRoot(),"Friends")==null);headerAbsent();capture("logout-22")
   }else if(phase=="expiry"){
    backKeyboard();reach("Resume saved session");click("Resume saved session")
    await("Session expired. Sign in again.");verify(prefs.read("https://localhost:8443/current")==null)
    verify(actualViewModel().state.value.session==null&&actualViewModel().state.value.offlineAccount==null);capture("session-expired-cleared")
   }else if(phase=="diagnose"||phase=="diagnose-red"){
    login(args.getString("avery")!!);click("GUI Fixture Morgan");fill("Message",sentText);backKeyboard()
    result.putString("beforeSend",actualState());capture("diagnose-before-send")
    click("Send ",true);result.putString("afterSend",actualState());capture("diagnose-after-send")
    if(phase=="diagnose-red"){delivery(sentText,"FAILED");result.putString("mainThreadBenignPingException",mainNetworkProbe());error("Actual immediate FAILED; sentRequestCount distinguishes pre-ACK socket send failure")}
    delivery(sentText,"SENT");result.putString("afterCommitted",actualState());showMessage(sentText);capture("diagnose-sent")
   }else if(phase=="matrix"){
    capture("cold-login");login(args.getString("avery")!!);click("GUI Fixture Morgan");await("Welcome to the GUI fixture. This message crossed the actual Go services.");capture("cold-chat-history")
    navigate("Friends");await("Your friends");capture("cold-friends");fill("Username",args.getString("riley")!!);backKeyboard();reach("Search");click("Search");await("GUI Fixture Riley");capture("friend-search-result");click("Add friend");await("Connected")
    openMorgan();fill("Message",sentText);backKeyboard();click("Send ",true);delivery(sentText,"SENT");showMessage(sentText);capture("sent")
    settingsControl("Go offline");openMorgan();await("Offline");showMessage(sentText);capture("offline-history")
    fill("Message",retryText);backKeyboard();click("Send ",true);val retryId=delivery(retryText,"FAILED")[0];showMessage(retryText);capture("failed")
    click("Reconnect");await("Connected");retryMessage(retryText);verify(delivery(retryText,"SENT")[0]==retryId);showMessage(retryText);capture("retry-sent")
    settingsControl("Refresh session");await("GUI Fixture Avery");capture("profile-refreshed")
    toggleTheme();verify(actualViewModel().state.value.appearance.theme=="warm");openMorgan();showMessage(sentText);capture("warm-chat-history")
   }else{
    if(prefs.read("https://localhost:8443/current")==null)login(args.getString("avery")!!) else {backKeyboard();reach("Resume saved session");click("Resume saved session");await("Connected")}
    click("GUI Fixture Morgan");await("GUI Android actual send",true);capture("restart-resume")
    if(phase=="refresh"){
     val slot=checkNotNull(prefs.read("https://localhost:8443/current"));val before=prefs.read(slot)
     settingsControl("Refresh session");repeat(300){if(actualViewModel().state.value.busy)Thread.sleep(100)}
     verify(!actualViewModel().state.value.busy&&actualViewModel().state.value.connection=="ready")
     verify(prefs.read(slot)!=before);await("GUI Fixture Avery");capture("profile-refreshed")
    }else if(phase=="appearance"){
     toggleTheme();verify(actualViewModel().state.value.appearance.theme=="warm");await("Font size: 14px");capture("warm-settings-14-compact")
     repeat(8){click("+")};reach("Comfort");click("Comfort");verify(actualViewModel().state.value.appearance==Appearance("warm",22,1.2f));capture("warm-settings-22-comfort")
     openMorgan();val latest=actualViewModel().state.value.messages.firstOrNull{it[2]?.startsWith("GUI Android retry identity")==true&&it[3]=="SENT"}!![2]!!
     capture("warm-chat-22-comfort")
     toggleTheme();verify(actualViewModel().state.value.appearance==Appearance("cold",22,1.2f));openMorgan();capture("cold-chat-22-comfort")
     navigate("Settings");reach("−");repeat(6){click("−")};reach("Standard");click("Standard");verify(actualViewModel().state.value.appearance==Appearance("cold",16,1f));capture("cold-settings-16-standard")
     toggleTheme();verify(actualViewModel().state.value.appearance==Appearance("warm",16,1f));capture("warm-settings-16-standard")
    }else if(phase=="retry"||phase=="retry-existing"){
     val target=if(phase=="retry")retryText else args.getString("retryText")!!
     if(phase=="retry"){
      settingsControl("Go offline");openMorgan();await("Offline");fill("Message",target);backKeyboard();click("Send ",true)
      val request=delivery(target,"FAILED")[0];showMessage(target);capture("existing-failed")
      click("Reconnect");await("Connected");retryMessage(target);verify(delivery(target,"SENT")[0]==request)
     }
     val committed=delivery(target,"SENT")
     result.putString("retryRequestId",committed[0]);result.putString("retryServerMessageId",committed[4]);try{showMessage(target);capture("retry-sent")}catch(e:IllegalStateException){result.putString("retryCaptureGap",e.message);capture("retry-capture-gap")}
     val slot=checkNotNull(prefs.read("https://localhost:8443/current"));val before=prefs.read(slot)
     settingsControl("Refresh session");repeat(300){if(actualViewModel().state.value.busy)Thread.sleep(100)}
     verify(!actualViewModel().state.value.busy&&actualViewModel().state.value.connection=="ready")
     verify(prefs.read(slot)!=before);await("GUI Fixture Avery");capture("profile-refreshed")
     toggleTheme();verify(actualViewModel().state.value.appearance.theme=="warm");openMorgan();capture("warm-chat-history")
    }else if(phase=="isolation"){
     settingsControl("Sign out");await("Open your workspace");capture("logout");login(args.getString("riley")!!);Thread.sleep(1000);verify(find(actualRoot(),"GUI Android actual send",true)==null);verify(Auth("https://localhost:8443",prefs).savedAccount()==args.getString("rileyId"))
     val isolated=targetContext.getDatabasePath("im-"+args.getString("rileyId")+".sqlite")
     android.database.sqlite.SQLiteDatabase.openDatabase(isolated.path,null,android.database.sqlite.SQLiteDatabase.OPEN_READONLY).use{db->db.rawQuery("SELECT count(*) FROM messages WHERE content LIKE 'GUI Android%'",null).use{rows->verify(rows.moveToFirst()&&rows.getInt(0)==0)}}
     capture("second-account-isolated");settingsControl("Sign out");await("Open your workspace");verify(prefs.read("https://localhost:8443/current")==null);capture("second-account-logout")
     login(args.getString("avery")!!);capture("expiry-prepared")
    }else if(phase=="offline-logout"){
     val directory=java.io.File(targetContext.getExternalFilesDir(null),"gui-auth/$captureRun").apply{mkdirs()}
     java.io.File(directory,"logout-ready").writeText(captureRun)
     val proceed=java.io.File(directory,"logout-continue");repeat(1200){if(!proceed.exists())Thread.sleep(50)};verify(proceed.exists())
     settingsControl("Sign out");await("Open your workspace")
     repeat(300){if(actualViewModel().state.value.busy)Thread.sleep(100)}
     verify(!actualViewModel().state.value.busy&&actualViewModel().state.value.session==null&&actualViewModel().state.value.offlineAccount==null)
     verify(prefs.read("https://localhost:8443/current")==null);capture("offline-logout-cleared")
    }else if(phase=="sending"){
     navigate("Chat");click("GUI Fixture Riley");verify(actualViewModel().state.value.messages.isEmpty())
     fill("Message",sendingText);backKeyboard()
     val directory=java.io.File(targetContext.getExternalFilesDir(null),"gui-auth/$captureRun").apply{mkdirs()}
     java.io.File(directory,"send-ready").writeText(captureRun)
     val proceed=java.io.File(directory,"send-continue");repeat(1200){if(!proceed.exists())Thread.sleep(50)};verify(proceed.exists())
     click("Send ",true);val pending=delivery(sendingText,"SENDING");await(sendingText);await("Sending",true);capture("sending")
     verify(delivery(sendingText,"SENT")[0]==pending[0]);await(sendingText);capture("controlled-send-sent")
    }
   }
   result.putString("result","PASS");result.putInt("assertions",count);result.putString("phase",phase);result.putString("captureRun",captureRun);result.putStringArrayList("deliveries",java.util.ArrayList(deliveries))
  }catch(e:Throwable){try{capture("failure")}catch(_:Throwable){};result.putString("result","FAIL");result.putString("failure",e.toString());result.putInt("assertions",count);result.putString("captureRun",captureRun)}
  finally{activity?.let{runOnMainSync{it.finish()}};prefs.saveAppearance(appearance)}
  result.putStringArrayList("deliveries",java.util.ArrayList(deliveries))
  finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
 }
}

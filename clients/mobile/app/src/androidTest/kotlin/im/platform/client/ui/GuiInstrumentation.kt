package im.platform.client.ui

import android.app.Activity
import android.app.Instrumentation
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityNodeInfo
import im.platform.client.MainActivity

/** Actual Compose navigation and SDK secure storage; no fake server/ACK acceptance. */
class GuiInstrumentation:Instrumentation() {
    private var assertions=0
    private var capture=false
    private val captureRun=System.currentTimeMillis().toString()
    private fun capture(name:String){
        if(!capture)return
        Thread.sleep(650);uiAutomation.waitForIdle(200,5000)
        val directory=java.io.File(targetContext.getExternalFilesDir(null),"gui-captures/$captureRun").apply{mkdirs()}
        val file=java.io.File(directory,"$name.png");check(!file.exists()){"Capture already exists: $name"}
        val bitmap=checkNotNull(uiAutomation.takeScreenshot());file.outputStream().use{check(bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it))};bitmap.recycle()
    }
    private fun fill(label:String,value:String){
        var node=await(label)
        while(node.actionList.none{it.id==AccessibilityNodeInfo.ACTION_SET_TEXT})node=node.parent?:error("Editable control missing: $label")
        val args=Bundle();args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,value);verify(node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,args));waitForIdleSync();Thread.sleep(300)
    }
    private fun visible(text:String):Boolean {
        val node=find(uiAutomation.rootInActiveWindow,text)?:return false
        val bounds=android.graphics.Rect();node.getBoundsInScreen(bounds)
        val display=targetContext.resources.displayMetrics
        return !bounds.isEmpty && bounds.centerX() in 0 until display.widthPixels && bounds.top>=0 && bounds.bottom<=display.heightPixels
    }
    private fun scroll(node:AccessibilityNodeInfo?):Boolean {
        if(node==null)return false
        if(node.isScrollable && node.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD))return true
        for(i in 0 until node.childCount)if(scroll(node.getChild(i)))return true
        return false
    }
    private var activity:Activity?=null
    private fun verify(value:Boolean){check(value){"GUI assertion $assertions failed"};assertions++}
    private fun find(node:AccessibilityNodeInfo?,text:String):AccessibilityNodeInfo? {
        if(node==null)return null
        if(node.text?.toString()==text || node.contentDescription?.toString()==text)return node
        for(i in 0 until node.childCount)find(node.getChild(i),text)?.let{return it}
        return null
    }
    private fun await(text:String):AccessibilityNodeInfo {
        repeat(100){find(uiAutomation.rootInActiveWindow,text)?.let{return it};Thread.sleep(50)}
        error("Actual Compose control missing: $text")
    }
    private fun click(text:String){var node=await(text);while(!node.isClickable){node=node.parent?:error("Control not clickable: $text")};verify(node.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();Thread.sleep(650)}
    private fun launch(){activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));waitForIdleSync();await("Settings")}
    private fun close(){activity?.let{runOnMainSync{it.finish()}};activity=null;waitForIdleSync()}
    override fun onCreate(arguments:Bundle?){super.onCreate(arguments);capture=arguments?.getString("capture")=="true";start()}
    override fun onStart(){
        val result=Bundle();result.putString("captureRun",captureRun);val prefs=Preferences(targetContext);val baseline=prefs.loadAppearance();val slot="gui-instrumentation-owned-slot"
        try {
            verify(android.os.Build.VERSION.SDK_INT==34)
            prefs.write(slot,"fixture-only-secure-value");verify(prefs.read(slot)=="fixture-only-secure-value")
            val saved=targetContext.getSharedPreferences("secure-refresh",0).getString(slot,null)!!
            verify(!saved.contains("fixture-only-secure-value"));verify(saved.split(':').size==2)
            val store=java.security.KeyStore.getInstance("AndroidKeyStore");store.load(null);verify(store.getKey("im-platform-refresh",null).encoded==null)
            prefs.remove(slot);verify(prefs.read(slot)==null)
            prefs.saveAppearance(Appearance("cold",14,.8f));launch();click("Settings");await("Appearance");capture("cold-settings-14-compact");close();prefs.saveAppearance(Appearance("warm",16,1f));launch();click("Settings");await("Appearance");capture("warm-settings-16-standard");close();prefs.saveAppearance(Appearance("cold",16,1f));launch();click("Settings");await("Appearance");await("Color, type and spacing are independent.");capture("cold-settings-16-standard")
            click("AI");await("Intelligence, in conversation.");capture("cold-ai-unavailable");click("Plugin");await("Your workspace, extended.");capture("cold-plugin-unavailable");click("Chat");await("Open your workspace")
            close();prefs.saveAppearance(Appearance("warm",22,1.2f));launch();click("Settings");await("Appearance");await("Font size: 22px");verify(prefs.loadAppearance()==Appearance("warm",22,1.2f));capture("warm-settings-22-comfort");click("Cold AI");verify(prefs.loadAppearance()==Appearance("cold",22,1.2f));capture("cold-settings-22-comfort");click("Warm Creative");verify(prefs.loadAppearance()==Appearance("warm",22,1.2f))
            // Actual scroll accessibility verifies sign-in reachability at the largest approved appearance.
            click("Chat");await("Open your workspace");verify(uiAutomation.takeScreenshot()!=null);capture("warm-login-22-comfort");verify(scroll(uiAutomation.rootInActiveWindow));waitForIdleSync();Thread.sleep(650);fill("Username","local-ui-only");fill("Password","local-reachability-only");repeat(6){if(!visible("Sign in")){if(!scroll(uiAutomation.rootInActiveWindow)){val b=android.graphics.Rect();find(uiAutomation.rootInActiveWindow,"Sign in")?.getBoundsInScreen(b);error("Scroll ended; sign-in bounds=$b display="+targetContext.resources.displayMetrics.widthPixels+"x"+targetContext.resources.displayMetrics.heightPixels)};assertions++;waitForIdleSync();Thread.sleep(650)}};verify(visible("Sign in"));capture("warm-login-scrolled-22-comfort");click("Password");capture("warm-login-ime-22-comfort");uiAutomation.injectInputEvent(android.view.KeyEvent(android.view.KeyEvent.ACTION_DOWN,android.view.KeyEvent.KEYCODE_BACK),true);uiAutomation.injectInputEvent(android.view.KeyEvent(android.view.KeyEvent.ACTION_UP,android.view.KeyEvent.KEYCODE_BACK),true);Thread.sleep(650);close();prefs.saveAppearance(Appearance("warm",14,.8f));launch();click("Settings");await("Appearance");capture("warm-settings-14-compact")
            result.putString("result","PASS");result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putInt("assertions",assertions);result.putString("engine","actual Compose Navigation/Android Keystore/SharedPreferences")
        }catch(error:Throwable){capture("failure-state");result.putString("result","FAIL");result.putString("failure",error.toString())}
        finally{close();prefs.remove(slot);prefs.saveAppearance(baseline)}
        finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
    }
}

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
        if(node.text?.toString()?.trim()==text || node.contentDescription?.toString()?.trim()==text)return node
        for(i in 0 until node.childCount)find(node.getChild(i),text)?.let{return it}
        return null
    }
    private fun await(text:String):AccessibilityNodeInfo {
        repeat(100){find(uiAutomation.rootInActiveWindow,text)?.let{return it};Thread.sleep(50)}
        error("Actual Compose control missing: $text")
    }
    private fun click(text:String){var node=await(text);while(!node.isClickable){node=node.parent?:error("Control not clickable: $text")};verify(node.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync();Thread.sleep(650)}
    private fun launch(){activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));waitForIdleSync();await("Open your workspace")}
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
            for(theme in listOf("cold","warm"))for(font in listOf(14,16,22)){
                close();prefs.saveAppearance(Appearance(theme,font,if(font==22)1.2f else .8f));launch()
                verify(find(uiAutomation.rootInActiveWindow,"Settings")==null)
                verify(find(uiAutomation.rootInActiveWindow,"Friends")==null)
                verify(find(uiAutomation.rootInActiveWindow,"Server")==null)
                verify(find(uiAutomation.rootInActiveWindow,"IM+ logo")!=null)
                capture("$theme-login-$font")
                repeat(6){if(!visible("New here? Create an account")){scroll(uiAutomation.rootInActiveWindow);waitForIdleSync();Thread.sleep(200)}}
                click("New here? Create an account");repeat(4){if(find(uiAutomation.rootInActiveWindow,"Confirm password")==null){scroll(uiAutomation.rootInActiveWindow);waitForIdleSync();Thread.sleep(250)}};await("Confirm password");capture("$theme-register-$font")
                if(font==16){fill("Username","fixture-confirm-only");fill("Password","fixture-only-password-value");fill("Confirm password","mismatch");uiAutomation.injectInputEvent(android.view.KeyEvent(android.view.KeyEvent.ACTION_DOWN,android.view.KeyEvent.KEYCODE_BACK),true);uiAutomation.injectInputEvent(android.view.KeyEvent(android.view.KeyEvent.ACTION_UP,android.view.KeyEvent.KEYCODE_BACK),true);repeat(6){if(!visible("Create account"))scroll(uiAutomation.rootInActiveWindow)};click("Create account");await("Passwords do not match");verify(find(uiAutomation.rootInActiveWindow,"Settings")==null)}
            }
            result.putString("result","PASS");result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putInt("assertions",assertions);result.putString("engine","actual anonymous/registration UI and Android Keystore/SharedPreferences")
        }catch(error:Throwable){capture("failure-state");result.putString("result","FAIL");result.putString("failure",error.toString())}
        finally{close();prefs.remove(slot);prefs.saveAppearance(baseline)}
        finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
    }
}

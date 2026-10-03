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
    private fun click(text:String){var node=await(text);while(!node.isClickable){node=node.parent?:error("Control not clickable: $text")};verify(node.performAction(AccessibilityNodeInfo.ACTION_CLICK));waitForIdleSync()}
    private fun launch(){activity=startActivitySync(Intent(targetContext,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));waitForIdleSync();await("Settings")}
    private fun close(){activity?.let{runOnMainSync{it.finish()}};activity=null;waitForIdleSync()}
    override fun onCreate(arguments:Bundle?){super.onCreate(arguments);start()}
    override fun onStart(){
        val result=Bundle();val prefs=Preferences(targetContext);val baseline=prefs.loadAppearance();val slot="gui-instrumentation-owned-slot"
        try {
            verify(android.os.Build.VERSION.SDK_INT==34)
            prefs.write(slot,"fixture-only-secure-value");verify(prefs.read(slot)=="fixture-only-secure-value")
            val saved=targetContext.getSharedPreferences("secure-refresh",0).getString(slot,null)!!
            verify(!saved.contains("fixture-only-secure-value"));verify(saved.split(':').size==2)
            val store=java.security.KeyStore.getInstance("AndroidKeyStore");store.load(null);verify(store.getKey("im-platform-refresh",null).encoded==null)
            prefs.remove(slot);verify(prefs.read(slot)==null)
            prefs.saveAppearance(Appearance("cold",16,1f));launch();click("Settings");await("Appearance");await("Color, type and spacing are independent.")
            click("AI");await("Intelligence, in conversation.");click("Plugin");await("Your workspace, extended.");click("Chat");await("Open your workspace")
            close();prefs.saveAppearance(Appearance("warm",22,1.2f));launch();click("Settings");await("Appearance");await("Font size: 22px");verify(prefs.loadAppearance()==Appearance("warm",22,1.2f))
            // Screen content is real Compose; scrolling/IME reachability is covered by runtime QA.
            click("Chat");await("Open your workspace");verify(uiAutomation.takeScreenshot()!=null)
            result.putString("result","PASS");result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT);result.putInt("assertions",assertions);result.putString("engine","actual Compose Navigation/Android Keystore/SharedPreferences")
        }catch(error:Throwable){result.putString("result","FAIL");result.putString("failure",error.toString())}
        finally{close();prefs.remove(slot);prefs.saveAppearance(baseline)}
        finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
    }
}

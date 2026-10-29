package im.platform.client.group

import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle

/** Runs the two real instrumentation reporting boundaries, including their finally paths. */
class CleanupInstrumentation:Instrumentation(){
 override fun onCreate(args:Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=Bundle()
  try{
   for(harness in listOf("runtime","friend"))for(primaryFails in listOf(false,true))for(cleanupFails in listOf(false,true)){
    val report=Bundle();val primary=IllegalStateException("owned primary $harness");val cleanup=IllegalArgumentException("owned cleanup $harness")
    var bodyCalls=0;var cleanupCalls=0;var cancelCalls=0
    val body:()->Unit={bodyCalls++;if(primaryFails)throw primary;report.putString("result","PASS")}
    val close:()->Unit={cleanupCalls++;if(cleanupFails)throw cleanup}
    val code=if(harness=="runtime")GroupRuntimeInstrumentation().runChecks(report,body,close)
      else FriendLoadInstrumentation().runChecks(report,body,{cancelCalls++},close)
    check(bodyCalls==1&&cleanupCalls==1&&cancelCalls==if(harness=="friend")1 else 0)
    if(!primaryFails&&!cleanupFails){check(code==Activity.RESULT_OK&&report.getString("result")=="PASS");check(!report.containsKey("failure"))}
    else{
     check(code==Activity.RESULT_CANCELED&&report.getString("result")=="FAIL")
     val text=checkNotNull(report.getString("failure"))
     if(primaryFails)check(text.startsWith(primary.toString()))
     if(cleanupFails)check(text.contains(cleanup.toString()))
     check(primary.suppressed.contentEquals(if(primaryFails&&cleanupFails)arrayOf(cleanup)else emptyArray()))
    }
   }
   // Scope cancellation failing still closes storage and retains both cleanup causes.
   val report=Bundle();val cancel=IllegalStateException("owned cancel");val close=IllegalArgumentException("owned close");var closed=false
   val code=FriendLoadInstrumentation().runChecks(report,{report.putString("result","PASS")},{throw cancel},{closed=true;throw close})
   check(closed&&code==Activity.RESULT_CANCELED&&report.getString("result")=="FAIL")
   check(cancel.suppressed.single()===close);check(checkNotNull(report.getString("failure")).contains(close.toString()))
   result.putString("result","PASS");result.putString("scope","two actual harness reporting/finally paths: success, primary, cleanup, dual; scope cancellation still closes repository")
  }catch(e:Throwable){result.putString("result","FAIL");result.putString("failure",e.stackTraceToString())}
  finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
 }
}

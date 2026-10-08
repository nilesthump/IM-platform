package im.platform.client.ui
import android.app.Activity
import android.app.Instrumentation
import android.os.Bundle
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLHandshakeException
/** Rollback proof only: default SDK TLS must reject the approved fixture after CA removal. */
class GuiTrustRollbackInstrumentation:Instrumentation(){
 private var args=Bundle()
 override fun onCreate(arguments:Bundle?){super.onCreate(arguments);args=arguments?:Bundle();start()}
 override fun onStart(){val result=Bundle();try{
  check(android.os.Build.VERSION.SDK_INT==34)
  val caFile=args.getString("caFile")?:"132339d5.0";check(Regex("[0-9a-f]{8}\\.0").matches(caFile));check(!java.io.File("/apex/com.android.conscrypt/cacerts/"+caFile).exists())
  val port=args.getString("port")?:"18443";check(port=="8443"||port=="18443")
  val c=URL("https://localhost:"+port+"/__infra/health").openConnection() as HttpsURLConnection
  c.connectTimeout=10000;c.readTimeout=10000;c.instanceFollowRedirects=false
  try{c.inputStream.close();error("Default TLS unexpectedly accepted removed fixture")}
  catch(expected:SSLHandshakeException){result.putString("tlsRejection",expected.javaClass.simpleName)}finally{c.disconnect()}
  result.putString("result","PASS");result.putString("proof","fresh application namespace has no approved CA; SDK default TLS rejects fixture")
 }catch(error:Throwable){result.putString("result","FAIL");result.putString("failure",error.javaClass.simpleName+": "+error.message)}
 finish(if(result.getString("result")=="PASS")Activity.RESULT_OK else Activity.RESULT_CANCELED,result)
 }
}

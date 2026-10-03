package im.platform.client.sync
import im.platform.client.send.SendSession
import java.net.URI
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.UUID
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.*
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

class SyncHttps(endpoint:String,private val session:SendSession,
    private val connection:(URL)->HttpsURLConnection={it.openConnection() as HttpsURLConnection},
    private val id:()->String={UUID.randomUUID().toString()}) {
    private val base:String
    fun matchesSession(check:(SendSession)->Boolean)=check(session)
    init {
        val uri=try {URI(endpoint)} catch(_:Exception){throw SyncFailure("protocol")}
        if(uri.scheme!="https" || uri.host==null || uri.rawUserInfo!=null || uri.rawQuery!=null || uri.rawFragment!=null || uri.rawPath !in listOf("","/") || session.accessToken.isEmpty() || session.accessToken.any {it=='\r' || it=='\n'}) throw SyncFailure("protocol")
        base=URI("https",null,uri.host,uri.port,null,null,null).toString()
    }
    private suspend fun post(path:String,body:String,id:String):String=suspendCancellableCoroutine {continuation->
        val current=AtomicReference<HttpsURLConnection?>()
        val job=CoroutineScope(continuation.context).launch(Dispatchers.IO) {
            try {
                val c=connection(URL(base+path));current.set(c)
                if(!continuation.isActive) return@launch
                c.instanceFollowRedirects=false;c.requestMethod="POST";c.connectTimeout=15000;c.readTimeout=15000;c.useCaches=false;c.doOutput=true
                c.setRequestProperty("Authorization","Bearer "+session.accessToken);c.setRequestProperty("Content-Type","application/json")
                val bytes=body.toByteArray(Charsets.UTF_8);c.setFixedLengthStreamingMode(bytes.size);c.outputStream.use {it.write(bytes)}
                val status=c.responseCode
                if(c.getHeaderField("Cache-Control")!="no-store" || c.contentType?.matches(Regex("(?i)application/json(?:\\s*;.*)?"))!=true) throw SyncFailure(if(status>=500)"transport" else "protocol")
                val stream=(if(status==200)c.inputStream else c.errorStream) ?: throw SyncFailure("transport")
                val out=java.io.ByteArrayOutputStream()
                stream.use {val buffer=ByteArray(8192);while(true){val count=it.read(buffer);if(count<0)break;if(out.size()+count>MAX_RESPONSE)throw SyncFailure("protocol");out.write(buffer,0,count)}}
                val raw=Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(out.toByteArray())).toString()
                if(status!=200) throw if(status in setOf(400,401,403,426))Wire.error(raw,id,status,path.endsWith("conversation")) else SyncFailure("transport")
                if(continuation.isActive)continuation.resume(raw)
            } catch(error:Exception) {if(continuation.isActive)continuation.resumeWithException(if(error is SyncFailure)error else SyncFailure("transport"))}
            finally {current.getAndSet(null)?.disconnect()}
        }
        continuation.invokeOnCancellation {current.getAndSet(null)?.disconnect();job.cancel()}
    }
    suspend fun user(cursor:String):UserPage {val request=id();return Wire.user(post("/v1/sync/user",Wire.userRequest(request,cursor),request),request,cursor)}
    suspend fun conversation(c:String,after:Long):ConversationPage {val request=id();return Wire.conversation(post("/v1/sync/conversation",Wire.conversationRequest(request,c,after),request),request,c,after)}
}

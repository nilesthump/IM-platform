package im.platform.client.send
import androidx.lifecycle.ViewModel
import im.platform.client.storage.Repository
import im.platform.client.storage.LocalMessage
import im.platform.client.storage.ServerMessage
import im.platform.client.storage.Committed
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.math.BigInteger
import java.net.URI
import java.util.UUID
import org.json.JSONObject

data class SendSession(val userId:String,val sessionId:String,val sessionEpoch:BigInteger,val accessToken:String) {
    override fun toString()="SendSession(credentials redacted)"
}
data class SendState(val connection:String="offline",val messages:List<List<String?>> = emptyList(),val error:String?=null)
// One ViewModel belongs to one authenticated account. The supplied Repository
// uses that account's existing SDK SQLite; it remains the sole storage writer.
class SendViewModel(private val repo:Repository, private val session:SendSession,
    private val factory:(String,()->Unit,(String)->Unit,()->Unit)->SendSocket = { url,open,message,end -> Wss(url,open,message,end) },
    private val timeoutMs:Long=15000, private val id:()->String={UUID.randomUUID().toString()}, private val ownsRepository:Boolean=false): ViewModel() {
    private val scope=CoroutineScope(SupervisorJob()+Dispatchers.IO)
    private val lock=Mutex()
    private val mutableState=MutableStateFlow(SendState())
    val state:StateFlow<SendState> = mutableState.asStateFlow()
    private var socket:SendSocket?=null
    private var generation=0L
    private var binding=""
    private var bound=false
    private var retired=false
    private var conversation=""
    private data class Attempt(val message:LocalMessage,val generation:Long,var sent:Boolean=false,var timer:Job?=null)
    private val attempts=mutableMapOf<String,Attempt>()
    private val known=mutableSetOf<String>()
    // null means this RID has identified multiple Conversations on this socket;
    // retain that fact after ACK/timeout until the connection is retired.
    private val requestConversations=mutableMapOf<String,String?>()
    init { require(Wire.uuid(session.userId)==session.userId && Wire.uuid(session.sessionId)==session.sessionId && session.sessionEpoch.signum()>0 && session.accessToken.isNotEmpty() && timeoutMs>0) }
    private fun key(c:String,r:String)="$c/$r"
    private fun publish(value:SendState) { if(!retired) mutableState.value=value }
    private fun refresh() { publish(mutableState.value.copy(messages=if(conversation.isEmpty()) emptyList() else repo.messages(conversation))) }
    private suspend fun operation(action:suspend ()->Unit) { lock.withLock { try { action() } catch(_:Exception) { publish(mutableState.value.copy(error="storage")); throw IllegalStateException("Send storage operation failed") } } }
    private fun callback(action:suspend ()->Unit) { scope.launch { try { operation(action) } catch(_:Exception) {} } }
    suspend fun openConversation(c:String) = operation { if(!retired) { conversation=Wire.uuid(c); refresh() } }
    suspend fun connect(endpoint:String) = operation {
        check(!retired); val uri=URI(endpoint); require(uri.scheme=="wss" && uri.host!=null && uri.rawQuery==null && uri.rawFragment==null && uri.rawUserInfo==null) { "Invalid WSS endpoint" }
        disconnectNow(); generation++; val g=generation; binding=Wire.uuid(id()); val bind=binding
        publish(mutableState.value.copy(connection="binding"))
        socket=factory(endpoint,{callback { if(g==generation && !retired) socket?.send(Wire.envelope("auth.bind",bind,JSONObject().put("accessToken",session.accessToken))) }},
            {raw -> callback { if(g==generation && !retired) receive(raw,g) }},{callback { if(g==generation && !retired) disconnectNow() }})
    }
    private fun disconnectNow() {
        generation++; bound=false; requestConversations.clear(); val old=socket; socket=null; old?.close()
        publish(mutableState.value.copy(connection="offline"))
        val pending=attempts.values.toList(); attempts.clear(); pending.forEach { it.timer?.cancel(); repo.markFailed(it.message.conversationId,it.message.requestId) }; refresh()
    }
    suspend fun disconnect() = operation { disconnectNow() }
    suspend fun dispose() = lock.withLock {
        retired=true; mutableState.value=SendState(error=mutableState.value.error)
        try {
            try { disconnectNow() } finally { if(ownsRepository) repo.close() }
        } catch(_:Exception) {
            mutableState.value=SendState(error="storage"); throw IllegalStateException("Send storage operation failed")
        } finally {
            attempts.values.forEach { it.timer?.cancel() }; attempts.clear(); scope.cancel()
        }
    }
    override fun onCleared() {
        socket?.close(); retired=true; requestConversations.clear(); mutableState.value=SendState()
        scope.launch { try { lock.withLock { if(ownsRepository) repo.close() } } finally { scope.cancel() } }
    }
    suspend fun send(c:String,text:String):String {
        val r=Wire.uuid(id()); val m=LocalMessage(Wire.uuid(c),r,session.userId,Wire.text(text)); operation { begin(m) }; return r
    }
    suspend fun retry(c:String,r:String) = operation {
        check(!retired); val conversation=Wire.uuid(c); val request=Wire.uuid(r)
        val row=repo.messages(conversation).firstOrNull {it[0]==request} ?: error("Unknown send")
        require(row[1]==session.userId); if(row[3]!="SENT") begin(LocalMessage(conversation,request,session.userId,row[2]!!))
    }
    private fun begin(m:LocalMessage) {
        check(!retired); repo.localSend(m); known.add(key(m.conversationId,m.requestId)); refresh()
        val k=key(m.conversationId,m.requestId); attempts[k]?.timer?.cancel(); val a=Attempt(m,generation); attempts[k]=a
        if(!bound || socket==null) { fail(k,a); return }
        try { socket!!.send(Wire.envelope("message.send",m.requestId,JSONObject().put("conversationId",m.conversationId).put("content",JSONObject().put("kind","TEXT").put("text",m.text)))); a.sent=true }
        catch(_:Exception) { fail(k,a); return }
        val priorConversation=requestConversations[m.requestId]
        requestConversations[m.requestId]=if(!requestConversations.containsKey(m.requestId) || priorConversation==m.conversationId) m.conversationId else null
        a.timer=scope.launch { delay(timeoutMs); try { operation { fail(k,a) } } catch(_:Exception) { /* Storage error is already observable; never crash the application timer. */ } }
    }
    private fun fail(k:String,a:Attempt) { if(attempts[k]!==a) return; attempts.remove(k); repo.markFailed(a.message.conversationId,a.message.requestId); refresh() }
    private fun clear(c:String,r:String) { attempts.remove(key(c,r))?.timer?.cancel() }
    private fun protocolFailure() { disconnectNow(); publish(mutableState.value.copy(error="protocol")) }
    private fun receive(raw:String,g:Long) {
        val f=try {Wire.decode(raw)} catch(_:IllegalArgumentException) {protocolFailure(); return}; val p=f.payload
        if(f.type=="ping") { socket?.send(Wire.envelope("pong",f.requestId,JSONObject())); return }; if(f.type=="pong") return
        if(f.type=="auth.ack") {
            if(f.requestId!=binding || p["status"]!="bound" || p["userId"]!=session.userId || p["sessionId"]!=session.sessionId || p["sessionEpoch"]!=session.sessionEpoch || p["clientType"]!="MOBILE" || bound) {protocolFailure(); return}
            bound=true; publish(mutableState.value.copy(connection="ready")); return
        }
        if(!bound) {protocolFailure(); return}
        if(f.type=="session.revoked") { if(p["sessionId"]!=session.sessionId) protocolFailure() else disconnectNow(); return }
        if(f.type=="message.created") {
            val content=p["content"] as Map<*,*>
            val m=ServerMessage(p["conversationId"] as String,f.requestId,p["senderId"] as String,content["text"] as String,p["messageId"] as String,(p["seq"] as BigInteger).longValueExact(),p["createdAt"] as String)
            repo.syncMessages(listOf(m)); clear(m.conversationId,m.requestId!!); refresh(); return
        }
        if(f.type=="message.ack") {
            if(p["status"]=="rejected") {
                // No Conversation is present: leave ambiguous attempts to their own ACK/timer.
                val matches=attempts.filter { (_,a) -> a.message.requestId==f.requestId && a.sent && a.generation==g }
                if(matches.size==1) { val (k,a)=matches.entries.single(); if(requestConversations[f.requestId]==a.message.conversationId) fail(k,a) }
            }
            else { val c=p["conversationId"] as String; if(key(c,f.requestId) !in known) return
                repo.committedAck(f.requestId,Committed(c,p["messageId"] as String,(p["seq"] as BigInteger).longValueExact(),p["createdAt"] as String)); clear(c,f.requestId); refresh() }
        }
    }
    suspend fun mergeMessages(messages:List<ServerMessage>) = operation { if(!retired) {repo.syncMessages(messages); messages.forEach {clear(it.conversationId,it.requestId!!)}; refresh()} }
}

// Account binding is fixed by the authenticated session, never a selected path.
suspend fun accountSend(context:android.content.Context,session:SendSession):SendViewModel = withContext(Dispatchers.IO) {
    val repository=Repository(context,Wire.uuid(session.userId))
    try {repository.initialize();SendViewModel(repository,session,ownsRepository=true)} catch(error:Exception) {repository.close();throw IllegalStateException("Send initialization failed")}
}

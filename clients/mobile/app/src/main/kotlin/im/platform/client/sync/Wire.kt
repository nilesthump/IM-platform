package im.platform.client.sync
import im.platform.client.send.Wire as SendWire
import im.platform.client.storage.UserEvent
import im.platform.client.storage.ServerMessage
import java.math.BigInteger
import org.json.JSONObject
const val MAX_RESPONSE=6*1024*1024
class SyncFailure(val kind:String):Exception("Sync $kind failure")
data class UserPage(val events:List<UserEvent>,val nextCursor:String,val hasMore:Boolean)
data class ConversationPage(val messages:List<ServerMessage>,val hasMore:Boolean)
object Wire {
    private fun invalid():Nothing=throw SyncFailure("protocol")
    private fun cursor(v:Any?):String {val s=v as? String ?: invalid();if(s.isEmpty() || s.codePointCount(0,s.length)>256) invalid();return s}
    private fun list(v:Any?):List<*> {val l=v as? List<*> ?: invalid();if(l.size>100) invalid();return l}
    private fun base(raw:String,keys:Set<String>,requestId:String,type:String):Map<String,Any> {
        val p=SendWire.obj(SendWire.parse(raw,MAX_RESPONSE,19),keys)
        if(p["syncVersion"]!="1.0" || p["type"]!=type || SendWire.uuid(p["requestId"])!=requestId || p["hasMore"] !is Boolean) invalid();return p
    }
    fun user(raw:String,id:String,input:String):UserPage=try {
        val p=base(raw,setOf("syncVersion","type","requestId","events","nextCursor","hasMore"),id,"sync.user.page")
        val ids=mutableSetOf<String>();val tokens=mutableSetOf<String>();var last=input
        val events=list(p["events"]).map {v->
            val e=SendWire.obj(v,setOf("eventId","cursor","kind","subjectId","revision"))
            val eventId=SendWire.uuid(e["eventId"]);val token=cursor(e["cursor"]);val kind=e["kind"] as? String ?: invalid()
            if(!ids.add(eventId) || !tokens.add(token) || token==input || kind !in setOf("friend.changed","conversation.changed","membership.changed","plugin.changed")) invalid()
            last=token;UserEvent(kind,SendWire.uuid(e["subjectId"]),SendWire.integer(e["revision"]).longValueExact())
        }
        val next=cursor(p["nextCursor"]);val more=p["hasMore"] as Boolean
        if(if(events.isEmpty()) next!=input || more else next!=last || next==input) invalid()
        UserPage(events,next,more)
    }catch(_:Exception){invalid()}
    fun conversation(raw:String,id:String,c:String,after:Long):ConversationPage=try {
        val p=base(raw,setOf("syncVersion","type","requestId","conversationId","messages","hasMore"),id,"sync.conversation.page")
        if(SendWire.uuid(p["conversationId"])!=c) invalid()
        var next=BigInteger.valueOf(after).add(BigInteger.ONE)
        val ids=mutableSetOf<String>();val requests=mutableSetOf<String>()
        val messages=list(p["messages"]).map {v->
            val m=SendWire.obj(v,setOf("conversationId","seq","messageId","senderId","requestId","createdAt","content"))
            val seq=SendWire.integer(m["seq"]);val message=SendWire.uuid(m["messageId"]);val request=SendWire.uuid(m["requestId"])
            if(SendWire.uuid(m["conversationId"])!=c || seq!=next || !ids.add(message) || !requests.add(request)) invalid();next=next.add(BigInteger.ONE)
            val content=SendWire.obj(m["content"],setOf("kind","text"));if(content["kind"]!="TEXT") invalid()
            ServerMessage(c,request,SendWire.uuid(m["senderId"]),SendWire.text(content["text"]),message,seq.longValueExact(),SendWire.time(m["createdAt"]))
        }
        val more=p["hasMore"] as Boolean;if(more && messages.isEmpty()) invalid();ConversationPage(messages,more)
    }catch(_:Exception){invalid()}
    fun error(raw:String,id:String,status:Int,conversation:Boolean):SyncFailure=try {
        val p=SendWire.obj(SendWire.parse(raw,MAX_RESPONSE,19),setOf("requestId","error"));if(SendWire.uuid(p["requestId"])!=id) invalid()
        val e=p["error"] as? Map<*,*> ?: invalid();if(e.keys.any {it !in setOf("code","message","violations")} || e["message"] !is String || (e["message"] as String).isEmpty()) invalid()
        if(e.containsKey("violations")) {(e["violations"] as? List<*> ?: invalid()).forEach {v->val f=SendWire.obj(v,setOf("field","reason"));if(f.values.any {it !is String || it.isEmpty()}) invalid()}}
        when {
            status==401 && e["code"] in setOf("AUTH_REQUIRED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH")->SyncFailure("authentication")
            conversation && status==403 && e["code"]=="AUTHORIZATION_DENIED"->SyncFailure("unavailable")
            status==400 && e["code"]=="VALIDATION_FAILED" || status==426 && e["code"]=="PROTOCOL_VERSION_UNSUPPORTED"->SyncFailure("protocol")
            else->invalid()
        }
    }catch(_:Exception){SyncFailure("protocol")}
    fun userRequest(id:String,input:String)=JSONObject().put("syncVersion","1.0").put("type","sync.user.request").put("requestId",SendWire.uuid(id)).put("cursor",cursor(input)).put("limit",100).toString()
    fun conversationRequest(id:String,c:String,after:Long):String {if(after<0) invalid();return JSONObject().put("syncVersion","1.0").put("type","sync.conversation.request").put("requestId",SendWire.uuid(id)).put("conversationId",SendWire.uuid(c)).put("afterSeq",after).put("limit",100).toString()}
}

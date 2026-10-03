package im.platform.client.send
import java.math.BigDecimal
import java.math.BigInteger
import java.time.OffsetDateTime
import java.util.UUID
import org.json.JSONObject

// Strict subset of JSON used by canonical WSS objects. Integer lexemes never
// pass through Double; storage conversion happens separately at the Repo edge.
object Wire {
    data class Frame(val type: String, val requestId: String, val payload: Map<String,Any>)
    private fun invalid(): Nothing = throw IllegalArgumentException("Invalid WSS frame")
    fun uuid(v: Any?): String {
        val s=v as? String ?: invalid()
        if(!s.matches(Regex("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"))) invalid()
        return UUID.fromString(s).toString()
    }
    fun text(v: Any?): String {
        val s=v as? String ?: invalid()
        if(s.isEmpty() || s.codePointCount(0,s.length)>4096) invalid()
        return s
    }
    fun integer(v: Any?): BigInteger {
        val n=v as? BigInteger ?: invalid()
        if(n.signum()<=0) invalid()
        return n
    }
    private fun obj(v: Any?, keys: Set<String>): Map<String,Any> {
        if(v !is Map<*,*> || v.keys!=keys) invalid()
        return keys.associateWith { v[it] ?: invalid() }
    }
    private fun time(v: Any?): String {
        val s=v as? String ?: invalid()
        if(!s.matches(Regex("[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})"))) invalid()
        val normalized=s.replace(Regex("(\\.[0-9]{9})[0-9]+"),"$1")
        try { OffsetDateTime.parse(normalized) } catch(_: Exception) { invalid() }
        return s
    }
    private class Parser(val raw: String) {
        var at=0
        fun space() { while(at<raw.length && raw[at] in " \t\r\n") at++ }
        fun string(): String {
            if(at>=raw.length || raw[at++]!='"') invalid()
            val out=StringBuilder()
            while(at<raw.length) {
                val c=raw[at++]
                if(c=='"') return out.toString()
                if(c<' ') invalid()
                if(c!='\\') out.append(c) else {
                    if(at>=raw.length) invalid()
                    when(val e=raw[at++]) {
                        '"','\\','/' -> out.append(e)
                        'b' -> out.append('\b'); 'f' -> out.append('\u000c'); 'n' -> out.append('\n'); 'r' -> out.append('\r'); 't' -> out.append('\t')
                        'u' -> { if(at+4>raw.length) invalid(); val hex=raw.substring(at,at+4); if(!hex.matches(Regex("[0-9a-fA-F]{4}"))) invalid(); out.append(hex.toInt(16).toChar()); at+=4 }
                        else -> invalid()
                    }
                }
            }
            invalid()
        }
        fun value(depth: Int=0): Any {
            if(depth>32) invalid(); space(); if(at>=raw.length) invalid()
            if(raw[at]=='"') return string()
            if(raw[at]=='{') {
                at++; space(); val out=mutableMapOf<String,Any>()
                if(at<raw.length && raw[at]!='}') while(true) {
                    space(); val key=string(); if(out.containsKey(key)) invalid(); space()
                    if(at>=raw.length || raw[at++]!=':') invalid(); out[key]=value(depth+1); space()
                    if(at>=raw.length || raw[at]!=',') break; at++
                }
                if(at>=raw.length || raw[at++]!='}') invalid(); return out
            }
            val m=Regex("-?(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?").find(raw,at)
            if(m==null || m.range.first!=at) invalid(); at=m.range.last+1
            return try { BigDecimal(m.value).toBigIntegerExact() } catch(_:Exception) { invalid() }
        }
        fun parse(): Any { if(raw.length>131072) invalid(); val v=value(); space(); if(at!=raw.length) invalid(); return v }
    }
    private val authErrors=setOf("VALIDATION_FAILED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH","PROTOCOL_VERSION_UNSUPPORTED")
    private val sendErrors=setOf("VALIDATION_FAILED","AUTH_REQUIRED","AUTH_SESSION_REVOKED","AUTHORIZATION_DENIED","MESSAGE_REQUEST_CONFLICT","MESSAGE_COMMIT_FAILED")
    fun decode(raw: String): Frame {
        val e=obj(Parser(raw).parse(),setOf("protocolVersion","type","requestId","payload"))
        if(e["protocolVersion"]!="1.0") invalid()
        val type=e["type"] as? String ?: invalid(); val id=uuid(e["requestId"])
        fun rejected(codes: Set<String>): Map<String,Any> {
            val p=obj(e["payload"],setOf("status","error")); val error=obj(p["error"],setOf("code","message"))
            if(p["status"]!="rejected" || error["code"] !in codes || error["message"] !is String || (error["message"] as String).isEmpty()) invalid()
            return p
        }
        val status=(e["payload"] as? Map<*,*>)?.get("status")
        val p=when(type) {
            "auth.ack" -> if(status=="rejected") rejected(authErrors) else {
                val p=obj(e["payload"],setOf("status","userId","sessionId","clientType","sessionEpoch"))
                if(p["status"]!="bound" || p["clientType"] !in setOf("WEB","DESKTOP","MOBILE")) invalid()
                p+mapOf("userId" to uuid(p["userId"]),"sessionId" to uuid(p["sessionId"]),"sessionEpoch" to integer(p["sessionEpoch"]))
            }
            "message.ack" -> if(status=="rejected") rejected(sendErrors) else {
                val p=obj(e["payload"],setOf("status","conversationId","messageId","seq","createdAt")); if(p["status"]!="committed") invalid()
                p+mapOf("conversationId" to uuid(p["conversationId"]),"messageId" to uuid(p["messageId"]),"seq" to integer(p["seq"]),"createdAt" to time(p["createdAt"]))
            }
            "message.created" -> {
                val p=obj(e["payload"],setOf("conversationId","messageId","senderId","seq","createdAt","content"))
                val content=obj(p["content"],setOf("kind","text")); if(content["kind"]!="TEXT") invalid(); text(content["text"])
                p+mapOf("conversationId" to uuid(p["conversationId"]),"messageId" to uuid(p["messageId"]),"senderId" to uuid(p["senderId"]),"seq" to integer(p["seq"]),"createdAt" to time(p["createdAt"]))
            }
            "session.revoked" -> {
                val p=obj(e["payload"],setOf("sessionId","reason")); if(p["reason"] !in setOf("LOGOUT","REPLACED","REVOKED")) invalid()
                p+mapOf("sessionId" to uuid(p["sessionId"]))
            }
            "ping","pong" -> obj(e["payload"],emptySet())
            else -> invalid()
        }
        return Frame(type,id,p)
    }
    fun envelope(type: String,id: String,payload: JSONObject) = JSONObject().put("protocolVersion","1.0").put("type",type).put("requestId",uuid(id)).put("payload",payload).toString()
}

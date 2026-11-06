package im.platform.client.ui
import im.platform.client.send.SendSession
import im.platform.client.send.Wire
import java.net.URI
import java.net.URL
import javax.net.ssl.HttpsURLConnection
import java.net.URLEncoder
import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import org.json.JSONObject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
class ApiFailure(val kind:String,message:String=kind):Exception(message)
data class User(val userId:String,val username:String,val displayName:String)
data class Friend(val user:User,val friendshipId:String,val directConversationId:String)
fun serverOrigin(value:String):String {val u=URI(value);require(u.scheme=="https" && u.host!=null && u.rawUserInfo==null && u.rawQuery==null && u.rawFragment==null && u.rawPath in listOf("","/"));return URI("https",null,u.host,u.port,null,null,null).toString()}
class Auth(val endpoint:String,private val preferences:Preferences) {
    @Volatile var session:SendSession?=null;private set
    private var slot="";private var expires=0L;@Volatile private var generation=0L
    init{serverOrigin(endpoint)}
    private fun metadata()=JSONObject().put("clientType","MOBILE").put("deviceId","im-mobile").put("clientVersion","0.1.0").put("protocolVersion","1")
    private fun transportCleanup(error:Throwable):Boolean=error is java.io.IOException && error.suppressed.all(::transportCleanup)
    private fun groupError(value:Any,status:Int,request:String?,listing:Boolean):Nothing {
        val codes=mapOf(400 to setOf("VALIDATION_FAILED"),401 to setOf("AUTH_REQUIRED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH"),403 to setOf("AUTHORIZATION_DENIED"),409 to setOf("GROUP_REQUEST_CONFLICT"))
        if(status !in codes || listing && status !in listOf(400,401))throw ApiFailure("invalid_server_response")
        val p=Wire.obj(value,setOf("requestId","error"));if(p["requestId"]!=request)throw ApiFailure("invalid_server_response")
        val raw=p["error"] as? Map<*,*>?:throw ApiFailure("invalid_server_response")
        val e=Wire.obj(raw,if(raw.containsKey("violations"))setOf("code","message","violations")else setOf("code","message"))
        val code=e["code"] as? String?:throw ApiFailure("invalid_server_response")
        if(code !in codes.getValue(status)||(e["message"] as? String).isNullOrEmpty())throw ApiFailure("invalid_server_response")
        if(e.containsKey("violations")){val violations=e["violations"] as? List<*>?:throw ApiFailure("invalid_server_response");for(v in violations){val q=Wire.obj(v,setOf("field","reason"));if((q["field"] as? String).isNullOrEmpty()||(q["reason"] as? String).isNullOrEmpty())throw ApiFailure("invalid_server_response")}}
        throw ApiFailure(if(status==401)"session_expired"else code)
    }
    suspend fun request(path:String,method:String="GET",body:JSONObject?=null,authenticated:Boolean=true,accessToken:String?=null,groupExpected:Int?=null,groupRequest:String?=null):Any=withContext(Dispatchers.IO){
        val connection=URL(endpoint+path).openConnection() as HttpsURLConnection
        try {
            var primary:Throwable?=null
            try {
            connection.instanceFollowRedirects=false;connection.requestMethod=method;connection.connectTimeout=15000;connection.readTimeout=15000;connection.useCaches=false;connection.setRequestProperty("Content-Type","application/json")
            if(authenticated){val token=accessToken?:session?.accessToken?:throw ApiFailure("session_expired","Session expired");connection.setRequestProperty("Authorization","Bearer "+token)}
            if(body!=null){connection.doOutput=true;val bytes=body.toString().toByteArray(Charsets.UTF_8);connection.setFixedLengthStreamingMode(bytes.size);connection.outputStream.use {it.write(bytes)}}
            val status=connection.responseCode;if(groupExpected!=null && status>=500)throw ApiFailure("connection_unavailable");if(groupExpected!=null && (connection.getHeaderField("Cache-Control")!="no-store" || status in 200..299 && status!=groupExpected))throw ApiFailure("invalid_server_response");if(status==204)return@withContext emptyMap<String,Any>()
            if(status in 300..399 || connection.contentType?.matches(Regex("(?i)application/json(?:\\s*;.*)?"))!=true)throw ApiFailure("invalid_server_response","Invalid server response")
            val output=java.io.ByteArrayOutputStream();val stream=if(status in 200..299)connection.inputStream else connection.errorStream
            (stream?:throw ApiFailure("connection_unavailable","Connection unavailable")).use{val buffer=ByteArray(8192);while(true){val n=it.read(buffer);if(n<0)break;if(output.size()+n>1048576)throw ApiFailure("invalid_server_response","Invalid server response");output.write(buffer,0,n)}}
            val raw=Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(output.toByteArray())).toString();val result=Wire.parse(raw,1048576)
            if(groupExpected!=null){val correlated=Wire.obj(result,if(status in 200..299)if(path.startsWith("/v1/conversations?"))setOf("requestId","items","hasMore","next")else setOf("requestId","conversationId","addedMemberUserIds","createdAt")else setOf("requestId","error"));if(correlated["requestId"]!=groupRequest)throw ApiFailure("invalid_server_response")};if(groupExpected!=null && status !in 200..299)groupError(result,status,groupRequest,method=="GET");if(status !in 200..299){val code=((result as? Map<*,*>)?.get("error") as? Map<*,*>)?.get("code") as? String;throw ApiFailure(if(status==401 && code=="AUTH_INVALID_CREDENTIALS")"invalid_credentials" else if(status==401)"session_expired" else code?:"request_failed",if(status==401 && code=="AUTH_INVALID_CREDENTIALS")"Invalid username or password" else if(status==401)"Session expired" else code?:"Request failed")};result
            }catch(error:Throwable){primary=error;throw error}
            finally{try{connection.disconnect()}catch(cleanup:Throwable){val original=primary;if(original==null)throw cleanup;if(cleanup!==original)original.addSuppressed(cleanup)}}
        }catch(error:Exception){
            val known=error is ApiFailure || error is im.platform.client.send.WireFailure || error is java.io.IOException || error is kotlinx.coroutines.CancellationException
            if(known && !error.suppressed.all(::transportCleanup))throw IllegalStateException("HTTPS operation and cleanup failed",error)
            val failure=when(error){is ApiFailure->error;is im.platform.client.send.WireFailure,is java.nio.charset.CharacterCodingException->ApiFailure("invalid_server_response","Invalid server response").also{it.initCause(error)};is java.io.IOException->ApiFailure("connection_unavailable","Connection unavailable").also{it.initCause(error)};else->error}
            throw failure
        }
    }
    private fun user(v:Any?):User {val o=Wire.obj(v,setOf("userId","username","displayName"));return User(Wire.uuid(o["userId"]),o["username"] as String,o["displayName"] as String)}
    @Synchronized private fun accept(value:Any,g:Long):SendSession {
        if(g!=generation)throw ApiFailure("session_expired","Session expired")
        val o=Wire.obj(value,setOf("session","tokens","replacedExistingSession"));val s=Wire.obj(o["session"],setOf("sessionId","userId","clientType","sessionEpoch","status"));val t=Wire.obj(o["tokens"],setOf("accessToken","accessTokenExpiresInSeconds","refreshToken","refreshTokenExpiresInSeconds","refreshTokenDelivery"))
        require(s["clientType"]=="MOBILE" && s["status"]=="ACTIVE" && t["refreshTokenDelivery"]=="RESPONSE_BODY_FOR_OS_SECURE_STORAGE" && o["replacedExistingSession"] is Boolean)
        val next=SendSession(Wire.uuid(s["userId"]),Wire.uuid(s["sessionId"]),Wire.integer(s["sessionEpoch"]),t["accessToken"] as String);require(next.accessToken.isNotEmpty());val refresh=t["refreshToken"] as String;require(refresh.isNotEmpty());val seconds=Wire.integer(t["accessTokenExpiresInSeconds"]).longValueExact();Wire.integer(t["refreshTokenExpiresInSeconds"])
        val newSlot=endpoint+"/"+next.userId+"/"+next.sessionId
        try {preferences.write(newSlot,refresh);preferences.write(endpoint+"/current",newSlot);if(slot.isNotEmpty() && slot!=newSlot)preferences.remove(slot)}catch(error:Exception){session=null;throw error}
        slot=newSlot;session=next;expires=System.currentTimeMillis()+seconds*1000;return next
    }
    suspend fun register(username:String,password:String):User = user(Wire.obj(request("/v1/auth/register","POST",JSONObject().put("username",username).put("password",password).put("displayName",username),false),setOf("user"))["user"])
    suspend fun login(username:String,password:String):SendSession {val g=generation;return accept(request("/v1/auth/login","POST",metadata().put("username",username).put("password",password),false),g)}
    suspend fun restore():SendSession? {slot=preferences.read(endpoint+"/current")?:return null;return refresh()}
    @Synchronized fun savedAccount():String? {val saved=preferences.read(endpoint+"/current")?:return null;require(saved.startsWith(endpoint+"/"));val parts=saved.removePrefix(endpoint+"/").split('/');require(parts.size==2);Wire.uuid(parts[1]);slot=saved;return Wire.uuid(parts[0])}
    suspend fun refresh():SendSession {val g=generation;val refresh=preferences.read(slot)?:throw ApiFailure("session_expired","Session expired");try{return accept(request("/v1/auth/refresh/native","POST",metadata().put("refreshToken",refresh),false),g)}catch(e:ApiFailure){
        if(g==generation && e.kind=="session_expired")try{clear()}catch(cleanup:Throwable){
            if(cleanup===e)throw e
            val failure=if(transportCleanup(cleanup))java.io.IOException("Refresh cleanup failed",e) else IllegalStateException("Refresh cleanup failed",e)
            failure.addSuppressed(cleanup);throw failure
        }
        throw e
    }}
    fun needsRefresh()=session!=null && System.currentTimeMillis()>expires-60000
    @Synchronized fun clear(){generation++;session=null;if(slot.isNotEmpty())preferences.remove(slot);slot="";preferences.remove(endpoint+"/current")}
    suspend fun logout(){val token=session?.accessToken;clear();if(token!=null)request("/v1/auth/logout","POST",accessToken=token)}
    suspend fun profile()=user(Wire.obj(request("/v1/users/me"),setOf("user"))["user"])
    suspend fun friends():List<Friend> =(Wire.obj(request("/v1/friends"),setOf("friends"))["friends"] as List<*>).map{val f=Wire.obj(it,setOf("user","friendshipId","directConversationId"));Friend(user(f["user"]),Wire.uuid(f["friendshipId"]),Wire.uuid(f["directConversationId"]))}
    suspend fun search(query:String):List<User> =(Wire.obj(request("/v1/users/search?username="+URLEncoder.encode(query,"UTF-8")),setOf("users"))["users"] as List<*>).map(::user)
    suspend fun add(id:String):String {val result=Wire.obj(request("/v1/friends/"+Wire.uuid(id),"PUT"),setOf("friendshipId","normalizedPair","directConversationId","memberUserIds","created"));return Wire.uuid(result["directConversationId"])}
}

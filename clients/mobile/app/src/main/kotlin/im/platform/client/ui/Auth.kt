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
class ApiFailure(val kind:String):Exception(kind)
data class User(val userId:String,val username:String,val displayName:String)
data class Friend(val user:User,val friendshipId:String,val directConversationId:String)
fun serverOrigin(value:String):String {val u=URI(value);require(u.scheme=="https" && u.host!=null && u.rawUserInfo==null && u.rawQuery==null && u.rawFragment==null && u.rawPath in listOf("","/"));return URI("https",null,u.host,u.port,null,null,null).toString()}
class Auth(val endpoint:String,private val preferences:Preferences) {
    @Volatile var session:SendSession?=null;private set
    private var slot="";private var expires=0L;@Volatile private var generation=0L
    init{serverOrigin(endpoint)}
    private fun metadata()=JSONObject().put("clientType","MOBILE").put("deviceId","im-mobile").put("clientVersion","0.1.0").put("protocolVersion","1")
    suspend fun request(path:String,method:String="GET",body:JSONObject?=null,authenticated:Boolean=true,accessToken:String?=null):Any=withContext(Dispatchers.IO){
        val connection=URL(endpoint+path).openConnection() as HttpsURLConnection
        try {
            connection.instanceFollowRedirects=false;connection.requestMethod=method;connection.connectTimeout=15000;connection.readTimeout=15000;connection.useCaches=false;connection.setRequestProperty("Content-Type","application/json")
            if(authenticated){val token=accessToken?:session?.accessToken?:throw ApiFailure("Session expired");connection.setRequestProperty("Authorization","Bearer "+token)}
            if(body!=null){connection.doOutput=true;val bytes=body.toString().toByteArray(Charsets.UTF_8);connection.setFixedLengthStreamingMode(bytes.size);connection.outputStream.use {it.write(bytes)}}
            val status=connection.responseCode;if(status==204)return@withContext emptyMap<String,Any>()
            if(status in 300..399 || connection.contentType?.matches(Regex("(?i)application/json(?:\\s*;.*)?"))!=true)throw ApiFailure("Invalid server response")
            val output=java.io.ByteArrayOutputStream();val stream=if(status in 200..299)connection.inputStream else connection.errorStream
            (stream?:throw ApiFailure("Connection unavailable")).use{val buffer=ByteArray(8192);while(true){val n=it.read(buffer);if(n<0)break;if(output.size()+n>1048576)throw ApiFailure("Invalid server response");output.write(buffer,0,n)}}
            val raw=Charsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(output.toByteArray())).toString();val result=Wire.parse(raw,1048576)
            if(status !in 200..299){val code=((result as? Map<*,*>)?.get("error") as? Map<*,*>)?.get("code") as? String;throw ApiFailure(if(status==401)"Session expired" else code?:"Request failed")};result
        }catch(e:ApiFailure){throw e}catch(_:Exception){throw ApiFailure("Connection unavailable")}finally{connection.disconnect()}
    }
    private fun user(v:Any?):User {val o=Wire.obj(v,setOf("userId","username","displayName"));return User(Wire.uuid(o["userId"]),o["username"] as String,o["displayName"] as String)}
    @Synchronized private fun accept(value:Any,g:Long):SendSession {
        if(g!=generation)throw ApiFailure("Session expired")
        val o=Wire.obj(value,setOf("session","tokens","replacedExistingSession"));val s=Wire.obj(o["session"],setOf("sessionId","userId","clientType","sessionEpoch","status"));val t=Wire.obj(o["tokens"],setOf("accessToken","accessTokenExpiresInSeconds","refreshToken","refreshTokenExpiresInSeconds","refreshTokenDelivery"))
        require(s["clientType"]=="MOBILE" && s["status"]=="ACTIVE" && t["refreshTokenDelivery"]=="RESPONSE_BODY_FOR_OS_SECURE_STORAGE" && o["replacedExistingSession"] is Boolean)
        val next=SendSession(Wire.uuid(s["userId"]),Wire.uuid(s["sessionId"]),Wire.integer(s["sessionEpoch"]),t["accessToken"] as String);require(next.accessToken.isNotEmpty());val refresh=t["refreshToken"] as String;require(refresh.isNotEmpty());val seconds=Wire.integer(t["accessTokenExpiresInSeconds"]).longValueExact();Wire.integer(t["refreshTokenExpiresInSeconds"])
        val newSlot=endpoint+"/"+next.userId+"/"+next.sessionId
        try {preferences.write(newSlot,refresh);preferences.write(endpoint+"/current",newSlot);if(slot.isNotEmpty() && slot!=newSlot)preferences.remove(slot)}catch(_:Exception){session=null;throw ApiFailure("Secure credential storage unavailable")}
        slot=newSlot;session=next;expires=System.currentTimeMillis()+seconds*1000;return next
    }
    suspend fun register(username:String,password:String):User = user(Wire.obj(request("/v1/auth/register","POST",JSONObject().put("username",username).put("password",password).put("displayName",username),false),setOf("user"))["user"])
    suspend fun login(username:String,password:String):SendSession {val g=generation;return accept(request("/v1/auth/login","POST",metadata().put("username",username).put("password",password),false),g)}
    suspend fun restore():SendSession? {slot=preferences.read(endpoint+"/current")?:return null;return refresh()}
    @Synchronized fun savedAccount():String? {val saved=preferences.read(endpoint+"/current")?:return null;require(saved.startsWith(endpoint+"/"));val parts=saved.removePrefix(endpoint+"/").split('/');require(parts.size==2);Wire.uuid(parts[1]);slot=saved;return Wire.uuid(parts[0])}
    suspend fun refresh():SendSession {val g=generation;val refresh=preferences.read(slot)?:throw ApiFailure("Session expired");try{return accept(request("/v1/auth/refresh/native","POST",metadata().put("refreshToken",refresh),false),g)}catch(e:ApiFailure){if(g==generation && e.kind=="Session expired")clear();throw e}}
    fun needsRefresh()=session!=null && System.currentTimeMillis()>expires-60000
    @Synchronized fun clear(){generation++;session=null;if(slot.isNotEmpty())preferences.remove(slot);slot="";preferences.remove(endpoint+"/current")}
    suspend fun logout(){val token=session?.accessToken;clear();if(token!=null)request("/v1/auth/logout","POST",accessToken=token)}
    suspend fun profile()=user(Wire.obj(request("/v1/users/me"),setOf("user"))["user"])
    suspend fun friends():List<Friend> =(Wire.obj(request("/v1/friends"),setOf("friends"))["friends"] as List<*>).map{val f=Wire.obj(it,setOf("user","friendshipId","directConversationId"));Friend(user(f["user"]),Wire.uuid(f["friendshipId"]),Wire.uuid(f["directConversationId"]))}
    suspend fun search(query:String):List<User> =(Wire.obj(request("/v1/users/search?username="+URLEncoder.encode(query,"UTF-8")),setOf("users"))["users"] as List<*>).map(::user)
    suspend fun add(id:String):String {val result=Wire.obj(request("/v1/friends/"+Wire.uuid(id),"PUT"),setOf("friendshipId","normalizedPair","directConversationId","memberUserIds","created"));return Wire.uuid(result["directConversationId"])}
}

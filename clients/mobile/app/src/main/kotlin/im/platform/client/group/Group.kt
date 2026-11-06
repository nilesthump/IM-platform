package im.platform.client.group
import im.platform.client.send.Wire
import im.platform.client.send.WireFailure
import im.platform.client.ui.Auth
import org.json.JSONObject
import org.json.JSONArray
import java.util.UUID

data class GroupUser(val userId:String,val username:String,val displayName:String)
data class MemberRow(val conversationId:String,val kind:String,val createdBy:String,val createdAt:String,val user:GroupUser,val role:String,val joinedAt:String)
data class GroupOperation(val account:String,val requestId:String,val targets:List<String>,val conversation:String?=null)
data class MemberPage(val items:List<MemberRow>,val more:Boolean,val afterConversation:String,val afterMember:String)
object GroupWire {
 fun id(value:Any?):String {val result=Wire.uuid(value);if(result!=value)throw WireFailure();return result}
 fun timestamp(v:Any?):String = Wire.time(v)
 fun targets(values:List<String>,actor:String):List<String>{if(values.size !in 1..100)throw WireFailure();val result=values.map(::id).distinct().sorted();if(actor in result)throw WireFailure();return result}
 fun result(v:Any,op:GroupOperation):String {val p=Wire.obj(v,setOf("requestId","conversationId","addedMemberUserIds","createdAt"));if(id(p["requestId"])!=op.requestId)throw WireFailure();val c=id(p["conversationId"]);val added=(p["addedMemberUserIds"] as? List<*>)?.map(::id)?:throw WireFailure();timestamp(p["createdAt"])
  if(added.size>101||added!=added.distinct().sorted())throw WireFailure()
  if(op.conversation!=null){if(c!=op.conversation||added.any{it !in op.targets})throw WireFailure()}else if(added!=(op.targets+op.account).sorted())throw WireFailure();return c
 }
 fun page(v:Any,request:String,afterConversation:String="",afterMember:String=""):MemberPage {
  val p=Wire.obj(v,setOf("requestId","items","hasMore","next"));if(id(p["requestId"])!=request)throw WireFailure();val values=p["items"] as? List<*>?:throw WireFailure();if(values.size>100)throw WireFailure();val more=p["hasMore"] as? Boolean?:throw WireFailure();var prior=afterConversation+afterMember;val metadata=mutableMapOf<String,List<String>>()
  val rows=values.map{v->val r=Wire.obj(v,setOf("conversationId","kind","createdBy","createdAt","member"));val m=Wire.obj(r["member"],setOf("user","role","joinedAt"));val u=Wire.obj(m["user"],setOf("userId","username","displayName"));val c=id(r["conversationId"]);val user=id(u["userId"]);val kind=r["kind"] as? String?:throw WireFailure();val role=m["role"] as? String?:throw WireFailure();val username=u["username"] as? String?:throw WireFailure();val display=u["displayName"] as? String?:throw WireFailure();if(kind !in listOf("GROUP","DIRECT")||role !in listOf("OWNER","MEMBER")||!Regex("^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$").matches(username)||c+user<=prior)throw WireFailure();prior=c+user
   val creator=id(r["createdBy"]);val created=timestamp(r["createdAt"]);val meta=listOf(kind,creator,created);if(metadata.containsKey(c)&&metadata[c]!=meta)throw WireFailure();metadata[c]=meta
   MemberRow(c,kind,creator,created,GroupUser(user,username,display),role,timestamp(m["joinedAt"]))}
  val n=Wire.obj(p["next"],setOf("afterConversationId","afterMemberUserId"));val c=n["afterConversationId"] as? String?:throw WireFailure();val u=n["afterMemberUserId"] as? String?:throw WireFailure();if(more){val last=rows.lastOrNull()?:throw WireFailure();if(c!=last.conversationId||u!=last.user.userId)throw WireFailure()}else if(c!=""||u!="")throw WireFailure();return MemberPage(rows,more,c,u)
 }
}
class GroupHttp(private val auth:Auth){
 suspend fun mutate(op:GroupOperation):String {val body=JSONObject().put("requestId",op.requestId).put("memberUserIds",JSONArray(op.targets));val path=op.conversation?.let{"/v1/groups/"+GroupWire.id(it)+"/members"}?:"/v1/groups";return GroupWire.result(auth.request(path,"POST",body,groupExpected=if(op.conversation==null)201 else 200,groupRequest=op.requestId),op)}
 suspend fun members(afterConversation:String="",afterMember:String=""):MemberPage {val request=UUID.randomUUID().toString();val suffix=if(afterConversation.isEmpty()&&afterMember.isEmpty())""else "&afterConversationId="+GroupWire.id(afterConversation)+"&afterMemberUserId="+GroupWire.id(afterMember);return GroupWire.page(auth.request("/v1/conversations?requestId="+request+"&limit=100"+suffix,groupExpected=200,groupRequest=request),request,afterConversation,afterMember)}
}
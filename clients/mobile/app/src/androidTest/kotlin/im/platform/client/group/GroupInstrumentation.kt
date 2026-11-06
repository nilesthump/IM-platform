package im.platform.client.group
import im.platform.client.send.WireFailure
class GroupInstrumentation:android.app.Instrumentation(){
 override fun onCreate(args:android.os.Bundle?){super.onCreate(args);start()}
 override fun onStart(){val result=android.os.Bundle();try{runChecks();result.putString("result","PASS");result.putString("scope","Actual Kotlin GroupWire correlation, ordering, short continuation, duplicate and result binding");finish(android.app.Activity.RESULT_OK,result)}catch(e:Throwable){result.putString("result","FAIL");result.putString("failure",e.toString());finish(android.app.Activity.RESULT_CANCELED,result)}}
 private fun runChecks(){
  val a="10000000-0000-4000-8000-000000000001";val b="10000000-0000-4000-8000-000000000002";val c="30000000-0000-4000-8000-000000000001";val r="40000000-0000-4000-8000-000000000001";val time="2026-10-18T06:30:00Z"
  fun rejected(block:()->Unit){try{block()}catch(e:WireFailure){return};error("invalid group response accepted")}
  fun row(id:String):Map<String,Any> = mapOf("conversationId" to c,"kind" to "GROUP","createdBy" to a,"createdAt" to time,"member" to mapOf("user" to mapOf("userId" to id,"username" to "user","displayName" to "Same"),"role" to if(id==a)"OWNER"else"MEMBER","joinedAt" to time))
  fun page(rows:List<Map<String,Any>>,more:Boolean=false,next:Map<String,String> = mapOf("afterConversationId" to "","afterMemberUserId" to ""))=mapOf("requestId" to r,"items" to rows,"hasMore" to more,"next" to next)
  check(GroupWire.targets(listOf(b,b),a)==listOf(b));rejected{GroupWire.targets(listOf(a),a)}
  val valid=page(listOf(row(a),row(b)));check(GroupWire.page(valid,r).items.size==2)
  rejected{GroupWire.page(page(listOf(row(b),row(a))),r)};rejected{GroupWire.page(page(listOf(row(a),row(a))),r)};rejected{GroupWire.page(valid,a)}
  val next=mapOf("afterConversationId" to c,"afterMemberUserId" to a)
  check(GroupWire.page(page(listOf(row(a)),true,next),r).more)
  rejected{GroupWire.page(page(emptyList(),true,next),r)};rejected{GroupWire.page(valid,r,c,a)};rejected{GroupWire.page(page(listOf(row(a)),false,next),r)}
  val op=GroupOperation(a,r,listOf(b));val response=mapOf("requestId" to r,"conversationId" to c,"addedMemberUserIds" to listOf(a,b),"createdAt" to time)
  check(GroupWire.result(response,op)==c);rejected{GroupWire.result(response+mapOf("addedMemberUserIds" to listOf(b)),op)}
  check(GroupWire.result(response+mapOf("addedMemberUserIds" to emptyList<String>()),op.copy(conversation=c))==c)
 }
}

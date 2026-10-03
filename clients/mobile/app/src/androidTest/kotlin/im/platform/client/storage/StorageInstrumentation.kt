package im.platform.client.storage
import android.app.Instrumentation
import android.app.Activity
import android.os.Bundle
import android.database.sqlite.SQLiteDatabase
import org.json.JSONObject
import java.util.UUID

class StorageInstrumentation : Instrumentation() {
    private var assertions=0
    private var canonicalCases=0
    private fun equal(actual: Any?, expected: Any?) { check(actual==expected) { "Storage assertion $assertions failed: $actual != $expected" }; assertions++ }
    private fun reject(block: () -> Unit) {
        var rejected=false
        try { block() } catch(_: Exception) { rejected=true }
        check(rejected) { "Expected conflict or rollback" }; assertions++
    }
    private fun message(obj: JSONObject) = ServerMessage(obj.getString("conversationId"),obj.getString("requestId"),
        obj.getString("senderId"),obj.getJSONObject("content").getString("text"),obj.getString("messageId"),obj.getLong("seq"),obj.getString("createdAt"))
    private fun local(m: ServerMessage) = LocalMessage(m.conversationId,m.requestId!!,m.senderId,m.text)
    private fun map(obj: JSONObject): Map<String,String> = obj.keys().asSequence().associateWith { obj.get(it).toString() }
    private fun messageMap(repo: Repository,c: String) = repo.messages(c).filter { it[5]!=null }.associate { it[5]!! to it[4]!! }
    private fun fixtures() {
        val golden=JSONObject(context.assets.open("golden.json").bufferedReader().use { it.readText() })
        val cases=golden.getJSONArray("cases")
        for(i in 0 until cases.length()) {
            val case=cases.getJSONObject(i); val steps=case.getJSONArray("steps")
            if((0 until steps.length()).any { steps.getJSONObject(it).getString("op") !in listOf("sync.message","sync.user","local.failed") }) continue
            canonicalCases++
            val account=UUID.randomUUID().toString()
            Repository(targetContext,account).use { repo ->
                repo.initialize(); var error=false; var cursor="0"
                for(j in 0 until steps.length()) {
                    val step=steps.getJSONObject(j); val op=step.getString("op"); var last=""
                    val c=step.optJSONObject("message")?.getString("conversationId")?:step.optString("conversationId","30000000-0000-4000-8000-000000000001")
                    try {
                        when(op) {
                            "local.failed" -> {
                                val request=step.getString("requestId")
                                if(repo.messages(c).none { it[0]==request }) {
                                    val future=(0 until steps.length()).mapNotNull { steps.getJSONObject(it).optJSONObject("message") }.first { it.getString("requestId")==request }
                                    repo.localSend(local(message(future)))
                                }
                                repo.markFailed(c,request); last=repo.messages(c).first { it[0]==request }[3]!!
                            }
                            "sync.message" -> { repo.syncMessages(listOf(message(step.getJSONObject("message"))),step.optString("fault")=="before_commit"); last="APPLIED" }
                            "sync.user" -> {
                                val page=step.getJSONObject("page"); val events=page.getJSONArray("events")
                                val inputs=(0 until events.length()).map { k -> val e=events.getJSONObject(k); UserEvent(e.getString("kind"),e.getString("subjectId"),e.getLong("revision")) }
                                repo.userPage(inputs,page.getString("nextCursor"),cursor,step.optString("fault")=="before_commit")
                                cursor=page.getString("nextCursor"); last="APPLIED"
                            }
                        }
                    } catch(_: Exception) {
                        if(step.optString("fault")=="before_commit") last="ROLLED_BACK" else { error=true; break }
                    }
                    val expected=case.optJSONObject("expect")?.optJSONArray("timeline")?.getJSONObject(j)
                    if(expected!=null) {
                        equal(repo.cursor(),expected.getString("cursor")); equal(repo.contiguous(c),expected.getLong("contiguous"))
                        equal(messageMap(repo,c),map(expected.getJSONObject("messages")))
                        equal(repo.query("SELECT kind,subject_id,CAST(revision AS TEXT) FROM user_state").associate { (it[0]+"/"+it[1]) to it[2]!! },map(expected.getJSONObject("userState")))
                        equal(last,expected.getString("last"))
                    }
                    val le=case.optJSONObject("expect")?.optJSONArray("localTimeline")?.getJSONObject(j)
                    if(le!=null) {
                        val rows=repo.messages(c); equal(rows.size,le.getInt("itemCount"))
                        equal(rows.filter { it[0]!=null }.associate { (c+"/"+it[0]) to it[3]!! },map(le.getJSONObject("local")))
                        equal(last,le.getString("last"))
                    }
                }
                equal(error,case.optBoolean("expectError"))
                if(!error) {
                    val expect=case.getJSONObject("expect")
                    if(expect.has("contiguous")) {
                        val c=(0 until steps.length()).mapNotNull { steps.getJSONObject(it).optJSONObject("message") }.firstOrNull()?.getString("conversationId")?:"30000000-0000-4000-8000-000000000001"
                        equal(repo.contiguous(c),expect.getLong("contiguous"))
                    }
                    if(expect.has("cursor")) equal(repo.cursor(),expect.getString("cursor"))
                    val conversations=expect.optJSONObject("conversations")
                    conversations?.keys()?.asSequence()?.forEach { c ->
                        equal(repo.contiguous(c),conversations.getJSONObject(c).getLong("contiguous"))
                        equal(messageMap(repo,c),map(conversations.getJSONObject(c).getJSONObject("messages")))
                    }
                }
            }
            targetContext.deleteDatabase("im-$account.sqlite")
        }
    }
    private fun additional() {
        val account=UUID.randomUUID().toString(); val other=UUID.randomUUID().toString()
        val c="30000000-0000-4000-8000-000000000001"; val c2="30000000-0000-4000-8000-000000000002"
        val r="40000000-0000-4000-8000-000000000001"; val id="50000000-0000-4000-8000-000000000001"
        val file=targetContext.getDatabasePath("im-$account.sqlite"); file.parentFile!!.mkdirs()
        SQLiteDatabase.openOrCreateDatabase(file,null).use { db ->
            db.beginTransaction()
            try { context.assets.open("v1.sql").bufferedReader().use { it.readText() }.split(";").filter { it.isNotBlank() }.forEach { db.execSQL(it) }; db.setTransactionSuccessful() } finally { db.endTransaction() }
        }
        val m=LocalMessage(c,r,account,"durable")
        Repository(targetContext,account).use { repo ->
            repo.localSend(m); reject { repo.initialize(true) }
            equal(repo.query("PRAGMA user_version").single().single(),"1")
            equal(repo.query("SELECT name FROM sqlite_master WHERE name='user_state'").size,0)
            repo.initialize(); equal(repo.messages(c)[0][2],"durable")
            val server=ServerMessage(c,r,account,"durable",id,1,"2026-09-28T00:00:01Z")
            repo.realtime(server.copy(requestId=null)); equal(repo.messages(c).size,2)
            repo.committedAck(r,Committed(c,id,1,server.createdAt)); equal(repo.messages(c).size,1)
            repo.markFailed(c,r); repo.localSend(m); equal(repo.messages(c)[0][3],"SENT")
            repo.syncMessages(listOf(server,server)); equal(repo.messages(c).size,1)
            reject { repo.syncMessages(listOf(server.copy(text="changed"))) }
            reject { repo.localSend(m.copy(text="changed")) }
            reject { repo.syncMessages(listOf(server.copy(conversationId=c2))) }
            reject { repo.syncMessages(listOf(server.copy(messageId="50000000-0000-4000-8000-000000000009"))) }
            equal(repo.messages(c)[0][2],"durable"); equal(repo.contiguous(c),1L)
            val next=server.copy(requestId="40000000-0000-4000-8000-000000000002",messageId="50000000-0000-4000-8000-000000000002",seq=2)
            reject { repo.syncMessages(listOf(next),true) }; equal(repo.messages(c).size,1); equal(repo.contiguous(c),1L)
            repo.syncMessages(listOf(next)); equal(repo.contiguous(c),2L)
            val crossed=server.copy(conversationId=c2,messageId="50000000-0000-4000-8000-000000000003")
            repo.realtime(crossed.copy(requestId=null)); repo.localSend(m.copy(conversationId=c2)); repo.syncMessages(listOf(crossed))
            equal(repo.messages(c2).size,1); equal(repo.contiguous(c2),1L)
            repo.committedAck(r,Committed(c2,crossed.messageId,1,crossed.createdAt)); equal(repo.messages(c2).size,1)
        }
        Repository(targetContext,account).use { repo -> repo.initialize(); equal(repo.messages(c).size,2); equal(repo.contiguous(c),2L) }
        Repository(targetContext,other).use { repo -> repo.initialize(); equal(repo.messages(c).size,0) }
        targetContext.deleteDatabase("im-$account.sqlite"); targetContext.deleteDatabase("im-$other.sqlite")
    }
    private fun unicode() {
        val account=UUID.randomUUID().toString()
        val c="30000000-0000-4000-8000-000000000001"; val r="40000000-0000-4000-8000-000000000001"
        val id="50000000-0000-4000-8000-000000000001"
        val emoji="\uD83D\uDE00".repeat(4096)
        var durable: List<List<String?>> = emptyList()
        val cursor256="\uD83D\uDE00".repeat(256)
        val events=listOf(UserEvent("friend.changed",account,1))
        var userState: List<List<String?>> = emptyList()
        Repository(targetContext,account).use { repo ->
            repo.initialize()
            val local=LocalMessage(c,r,account,emoji)
            val server=ServerMessage(c,r,account,emoji,id,1,"2026-09-28T00:00:01Z")
            repo.localSend(local); repo.syncMessages(listOf(server))
            equal(repo.messages(c)[0][2],emoji); durable=repo.messages(c)
            reject { repo.localSend(local.copy(requestId="40000000-0000-4000-8000-000000000009",text=emoji+"\uD83D\uDE00")) }
            equal(repo.messages(c),durable)
            reject { repo.syncMessages(listOf(server.copy(requestId="40000000-0000-4000-8000-000000000009",messageId="50000000-0000-4000-8000-000000000009",seq=2,text=emoji+"\uD83D\uDE00"))) }
            equal(repo.messages(c),durable); equal(repo.contiguous(c),1L); equal(repo.cursor(),"0")
            repo.userPage(events,cursor256,"0"); equal(repo.cursor(),cursor256)
            userState=repo.query("SELECT kind,subject_id,CAST(revision AS TEXT) FROM user_state")
            equal(userState,listOf(listOf("friend.changed",account,"1")))
            reject { repo.userPage(listOf(events[0].copy(revision=2)),cursor256+"\uD83D\uDE00",cursor256) }
            reject { repo.userPage(listOf(events[0].copy(revision=2)),"stale","0") }
            equal(repo.cursor(),cursor256); equal(repo.query("SELECT kind,subject_id,CAST(revision AS TEXT) FROM user_state"),userState)
            equal(repo.messages(c),durable); equal(repo.contiguous(c),1L)
        }
        Repository(targetContext,account).use { repo -> repo.initialize(); equal(repo.messages(c),durable)
            equal(repo.cursor(),cursor256); equal(repo.query("SELECT kind,subject_id,CAST(revision AS TEXT) FROM user_state"),userState)
            equal(repo.contiguous(c),1L)
        }
        targetContext.deleteDatabase("im-$account.sqlite")
    }
    private fun largeIntegers() {
        val account=UUID.randomUUID().toString()
        val c="30000000-0000-4000-8000-000000000001"; val c2="30000000-0000-4000-8000-000000000002"
        val r="40000000-0000-4000-8000-000000000001"; val id="50000000-0000-4000-8000-000000000001"
        val boundary=9007199254740992L; val max=Long.MAX_VALUE
        Repository(targetContext,account).use { it.initialize() }
        // Imported gap-free historical prefix, no enormous artificial row allocation.
        SQLiteDatabase.openDatabase(targetContext.getDatabasePath("im-$account.sqlite").path,null,SQLiteDatabase.OPEN_READWRITE).use { db ->
            db.beginTransaction()
            try {
                db.execSQL("INSERT INTO conversations VALUES(?,?)",arrayOf(c,boundary-1))
                db.execSQL("INSERT INTO conversations VALUES(?,?)",arrayOf(c2,max-1))
                db.setTransactionSuccessful()
            } finally { db.endTransaction() }
        }
        var messages: List<List<String?>> = emptyList(); var top: List<List<String?>> = emptyList()
        val revision=listOf(listOf(max.toString()))
        Repository(targetContext,account).use { repo ->
            val high=ServerMessage(c,r,account,"durable",id,boundary,"2026-09-28T00:00:01Z")
            val odd=high.copy(requestId="40000000-0000-4000-8000-000000000002",messageId="50000000-0000-4000-8000-000000000002",seq=boundary+1)
            repo.localSend(LocalMessage(c,r,account,"durable")); repo.syncMessages(listOf(odd)); equal(repo.contiguous(c),boundary-1)
            repo.committedAck(r,Committed(c,id,boundary,high.createdAt)); equal(repo.contiguous(c),boundary+1)
            repo.realtime(high.copy(requestId=null)); repo.syncMessages(listOf(high,odd))
            equal(repo.messages(c).map { it[5] },listOf(boundary.toString(),(boundary+1).toString()))
            val highest=high.copy(conversationId=c2,messageId="50000000-0000-4000-8000-000000000003",seq=max)
            repo.syncMessages(listOf(highest,highest)); equal(repo.contiguous(c2),max)
            val event=UserEvent("friend.changed",account,max)
            repo.userPage(listOf(event),"large","0"); repo.userPage(listOf(event.copy(revision=max-1)),"large2","large")
            equal(repo.query("SELECT CAST(revision AS TEXT) FROM user_state"),revision)
            messages=repo.messages(c); top=repo.messages(c2)
            // Kotlin Long cannot express MAX+1; no fabricated beyond-Long input test.
            for(invalid in listOf(0L,-1L,Long.MIN_VALUE)) {
                reject { repo.syncMessages(listOf(odd.copy(seq=invalid))) }
                reject { repo.userPage(listOf(event.copy(revision=invalid)),"invalid","large2") }
            }
            equal(repo.messages(c),messages); equal(repo.messages(c2),top); equal(repo.cursor(),"large2")
            equal(repo.query("SELECT CAST(revision AS TEXT) FROM user_state"),revision)
        }
        Repository(targetContext,account).use { repo ->
            repo.initialize(); equal(repo.contiguous(c),boundary+1); equal(repo.contiguous(c2),max)
            equal(repo.messages(c),messages); equal(repo.messages(c2),top); equal(repo.cursor(),"large2")
            equal(repo.query("SELECT CAST(revision AS TEXT) FROM user_state"),revision)
        }
        targetContext.deleteDatabase("im-$account.sqlite")
    }
    override fun onCreate(arguments: Bundle?) { super.onCreate(arguments); start() }
    override fun onStart() {
        val result=Bundle()
        try {
            fixtures(); additional(); unicode(); largeIntegers()
            Repository(targetContext,UUID.randomUUID().toString()).use { repo ->
                repo.initialize(); result.putString("sqliteVersion",repo.query("SELECT sqlite_version()").single().single())
            }
            result.putInt("sdkInt",android.os.Build.VERSION.SDK_INT)
            result.putString("result","PASS"); result.putInt("canonicalCases",canonicalCases); result.putInt("assertions",assertions)
            result.putString("engine","actual Android SDK SQLite")
            finish(Activity.RESULT_OK,result)
        } catch(error: Throwable) {
            error.printStackTrace(); result.putString("result","FAIL"); result.putString("failure",error.toString())
            finish(Activity.RESULT_CANCELED,result)
        }
    }
}

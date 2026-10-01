package im.platform.client.storage
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import java.io.Closeable

class Repository(context: Context, accountId: String) : Closeable {
    private val db: SQLiteDatabase
    init {
        require(accountId.matches(Regex("[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")))
        val file = context.getDatabasePath("im-" + accountId.lowercase() + ".sqlite")
        file.parentFile!!.mkdirs()
        db = SQLiteDatabase.openOrCreateDatabase(file, null)
    }
    fun initialize(failMigration: Boolean = false) {
        val version = db.version
        require(version in 0..2) { "Unsupported schema version" }
        if (version == 2) return
        transaction {
            if (version == 0) Schema.v1.forEach { db.execSQL(it) }
            if (failMigration) db.execSQL("INSERT INTO __fault_missing_table VALUES(1)")
            Schema.v2.forEach { db.execSQL(it) }
        }
    }
    private fun transaction(block: () -> Unit) {
        db.beginTransaction()
        try { block(); db.setTransactionSuccessful() } finally { db.endTransaction() }
    }
    internal fun query(sql: String, args: Array<String> = emptyArray()): List<List<String?>> {
        db.rawQuery(sql,args).use { cursor ->
            val rows = mutableListOf<List<String?>>()
            while (cursor.moveToNext()) rows.add((0 until cursor.columnCount).map { if(cursor.isNull(it)) null else cursor.getString(it) })
            return rows
        }
    }
    private fun checkText(text: String) { require(text.isNotEmpty() && text.length <= 4096) }
    private fun execute(sql: String, args: Array<out Any?> = emptyArray()) { db.execSQL(sql,args) }
    private fun advance(c: String) {
        execute("INSERT INTO conversations(conversation_id) VALUES(?) ON CONFLICT DO NOTHING", arrayOf(c))
        execute("""WITH RECURSIVE prefix(n) AS (
            SELECT contiguous_seq FROM conversations WHERE conversation_id=?
            UNION ALL SELECT n+1 FROM prefix WHERE EXISTS(SELECT 1 FROM messages WHERE conversation_id=? AND server_seq=n+1)
            ) UPDATE conversations SET contiguous_seq=(SELECT MAX(n) FROM prefix) WHERE conversation_id=?""",arrayOf(c,c,c))
    }
    fun localSend(m: LocalMessage) {
        checkText(m.text)
        transaction {
            val old=query("SELECT sender_id,content FROM messages WHERE conversation_id=? AND request_id=?", arrayOf(m.conversationId,m.requestId))
            require(old.isEmpty() || old[0]==listOf(m.senderId,m.text)) { "Local identity/content conflict" }
            execute("""INSERT INTO messages(conversation_id,request_id,sender_id,content,state) VALUES(?,?,?,?,'SENDING')
                ON CONFLICT(conversation_id,request_id) DO UPDATE SET state=CASE WHEN messages.state='SENT' THEN 'SENT' ELSE 'SENDING' END""",
                arrayOf(m.conversationId,m.requestId,m.senderId,m.text))
        }
    }
    fun markFailed(c: String, requestId: String) {
        transaction {
            require(query("SELECT 1 FROM messages WHERE conversation_id=? AND request_id=?",arrayOf(c,requestId)).size==1)
            execute("UPDATE messages SET state=CASE WHEN state='SENT' THEN 'SENT' ELSE 'FAILED' END WHERE conversation_id=? AND request_id=?",arrayOf(c,requestId))
        }
    }
    private fun materialize(m: ServerMessage) {
        checkText(m.text); require(m.seq>0)
        // Android rawQuery binds selectionArgs as non-null strings. Realtime
        // has no request identity, so omit that predicate rather than fake one.
        val identity = if (m.requestId != null) "(conversation_id=? AND request_id=?) OR " else ""
        val binds = if (m.requestId != null) arrayOf(m.conversationId,m.requestId,m.messageId,m.conversationId,m.seq.toString())
            else arrayOf(m.messageId,m.conversationId,m.seq.toString())
        val rows = query("SELECT conversation_id,request_id,sender_id,content,server_message_id,server_seq,server_time " +
            "FROM messages WHERE " + identity + "server_message_id=? OR (conversation_id=? AND server_seq=?)", binds)
        rows.forEach { r ->
            require(r[0]==m.conversationId && r[2]==m.senderId && r[3]==m.text &&
                (r[1]==null || m.requestId==null || r[1]==m.requestId) &&
                (r[4]==null || r[4]==m.messageId) && (r[5]==null || r[5]==m.seq.toString()) &&
                (r[6]==null || r[6]==m.createdAt)) { "Durable identity/content conflict" }
        }
        if(m.requestId!=null) {
            execute("""DELETE FROM messages WHERE server_message_id=? AND request_id IS NULL AND
                EXISTS(SELECT 1 FROM messages WHERE conversation_id=? AND request_id=?)""",arrayOf(m.messageId,m.conversationId,m.requestId))
            execute("UPDATE messages SET request_id=? WHERE server_message_id=? AND request_id IS NULL",arrayOf(m.requestId,m.messageId))
        }
        execute("""INSERT INTO messages(conversation_id,request_id,sender_id,content,state,server_message_id,server_seq,server_time)
            VALUES(?,?,?,?,'SENT',?,?,?) ON CONFLICT DO UPDATE SET state='SENT',server_message_id=excluded.server_message_id,
            server_seq=excluded.server_seq,server_time=excluded.server_time,request_id=COALESCE(messages.request_id,excluded.request_id)""",
            arrayOf(m.conversationId,m.requestId,m.senderId,m.text,m.messageId,m.seq.toString(),m.createdAt))
    }
    fun syncMessages(messages: List<ServerMessage>, failBeforeAdvance: Boolean = false) {
        require(messages.all { it.requestId!=null })
        transaction {
            messages.forEach { materialize(it) }
            if(failBeforeAdvance) execute("INSERT INTO __fault_missing_table VALUES(1)")
            messages.map { it.conversationId }.distinct().forEach { advance(it) }
        }
    }
    fun realtime(m: ServerMessage, failBeforeAdvance: Boolean = false) {
        require(m.requestId==null) { "Realtime payload has no send request identity" }
        transaction {
            materialize(m)
            if(failBeforeAdvance) execute("INSERT INTO __fault_missing_table VALUES(1)")
            advance(m.conversationId)
        }
    }
    fun committedAck(requestId: String, ack: Committed) {
        require(ack.seq>0)
        transaction {
            val local=query("SELECT sender_id,content,server_message_id,server_seq,server_time FROM messages WHERE conversation_id=? AND request_id=?",
                arrayOf(ack.conversationId,requestId)).single()
            val rows=query("""SELECT conversation_id,request_id,sender_id,content,server_message_id,server_seq,server_time
                FROM messages WHERE server_message_id=? OR (conversation_id=? AND server_seq=?) OR (conversation_id=? AND request_id=?)""",
                arrayOf(ack.messageId,ack.conversationId,ack.seq.toString(),ack.conversationId,requestId))
            rows.forEach { r ->
                require(r[0]==ack.conversationId && r[2]==local[0] && r[3]==local[1] &&
                    (r[1]==null || r[1]==requestId) && (r[4]==null || r[4]==ack.messageId) &&
                    (r[5]==null || r[5]==ack.seq.toString()) && (r[6]==null || r[6]==ack.createdAt))
            }
            execute("DELETE FROM messages WHERE server_message_id=? AND request_id IS NULL",arrayOf(ack.messageId))
            execute("UPDATE messages SET state='SENT',server_message_id=?,server_seq=?,server_time=? WHERE conversation_id=? AND request_id=?",
                arrayOf(ack.messageId,ack.seq.toString(),ack.createdAt,ack.conversationId,requestId))
            advance(ack.conversationId)
        }
    }
    fun userPage(events: List<UserEvent>, nextCursor: String, expectedCursor: String, failBeforeAdvance: Boolean=false) {
        require(nextCursor.isNotEmpty() && nextCursor.length<=256)
        require(events.all { it.kind in listOf("friend.changed","conversation.changed","membership.changed","plugin.changed") && it.revision>0 })
        transaction {
            require(cursor()==expectedCursor) { "Stale user page" }
            events.forEach { execute("""INSERT INTO user_state VALUES(?,?,?) ON CONFLICT(kind,subject_id)
                DO UPDATE SET revision=MAX(user_state.revision,excluded.revision)""",arrayOf(it.kind,it.subjectId,it.revision.toString())) }
            if(failBeforeAdvance) execute("INSERT INTO __fault_missing_table VALUES(1)")
            execute("UPDATE user_cursor SET cursor=? WHERE singleton=1",arrayOf(nextCursor))
        }
    }
    fun messages(c: String) = query("""SELECT request_id,sender_id,content,state,server_message_id,CAST(server_seq AS TEXT),server_time
        FROM messages WHERE conversation_id=? ORDER BY server_seq IS NULL,server_seq,local_id""", arrayOf(c))
    fun contiguous(c: String) = query("SELECT contiguous_seq FROM conversations WHERE conversation_id=?",arrayOf(c)).firstOrNull()?.first()?.toLong() ?: 0L
    fun cursor() = query("SELECT cursor FROM user_cursor WHERE singleton=1").single().single()!!
    override fun close() { db.close() }
}

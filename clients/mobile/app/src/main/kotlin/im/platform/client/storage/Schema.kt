package im.platform.client.storage
object Schema {
    val v1 = listOf(
        """CREATE TABLE messages(local_id INTEGER PRIMARY KEY,conversation_id TEXT NOT NULL,request_id TEXT,
        sender_id TEXT NOT NULL,content TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('SENDING','SENT','FAILED')),
        server_message_id TEXT,server_seq INTEGER CHECK(server_seq IS NULL OR server_seq>0),server_time TEXT,
        CHECK((state='SENT')=(server_message_id IS NOT NULL)),
        CHECK((server_message_id IS NULL)=(server_seq IS NULL)),
        CHECK((server_message_id IS NULL)=(server_time IS NULL)),
        UNIQUE(conversation_id,request_id),UNIQUE(server_message_id),UNIQUE(conversation_id,server_seq))""",
        "CREATE TABLE conversations(conversation_id TEXT PRIMARY KEY,contiguous_seq INTEGER NOT NULL DEFAULT 0 CHECK(contiguous_seq>=0))",
        "PRAGMA user_version=1")
    val v2 = listOf(
        "CREATE TABLE user_state(kind TEXT NOT NULL,subject_id TEXT NOT NULL,revision INTEGER NOT NULL,PRIMARY KEY(kind,subject_id))",
        "CREATE TABLE user_cursor(singleton INTEGER PRIMARY KEY CHECK(singleton=1),cursor TEXT NOT NULL)",
        "INSERT INTO user_cursor VALUES(1,'0')", "PRAGMA user_version=2")
}

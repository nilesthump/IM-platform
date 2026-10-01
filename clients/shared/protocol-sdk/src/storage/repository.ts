import type { Bind, Committed, Database, LocalMessage, RealtimeMessage, ServerMessage, Statement, UserPage } from "./models.js";
import { v1, v2 } from "./schema.js";

function text(m: LocalMessage | RealtimeMessage): string {
  if (m.content.kind !== "TEXT" || !m.content.text || [...m.content.text].length > 4096) throw new Error("Invalid text");
  return m.content.text;
}
function seq(n: number): string {
  if (!Number.isSafeInteger(n) || n < 1) throw new Error("Invalid sequence");
  return String(n);
}
const step = (sql: string, binds: Bind[] = [], expected: number | null = null): Statement => [sql, binds, expected];
// An assertion is an UPDATE with a predicate over the SAME transaction snapshot.
// Every account has exactly one cursor row; no schema-level business trigger.
const assert = (condition: string, binds: Bind[]): Statement =>
  step("UPDATE user_cursor SET cursor=cursor WHERE singleton=1 AND (" + condition + ")", binds, 1);
function advance(conversationId: string): Statement[] {
  return [
    step("INSERT INTO conversations(conversation_id) VALUES(?) ON CONFLICT DO NOTHING", [conversationId]),
    step(`WITH RECURSIVE prefix(n) AS (
      SELECT contiguous_seq FROM conversations WHERE conversation_id=?
      UNION ALL SELECT n+1 FROM prefix WHERE EXISTS(
        SELECT 1 FROM messages WHERE conversation_id=? AND server_seq=n+1)
    ) UPDATE conversations SET contiguous_seq=(SELECT MAX(n) FROM prefix) WHERE conversation_id=?`,
    [conversationId, conversationId, conversationId], 1),
  ];
}
export class Repository {
  constructor(readonly db: Database) {}
  async initialize(): Promise<void> {
    const version = Number((await this.db.query("PRAGMA user_version", []))[0][0]);
    if (![0,1,2].includes(version)) throw new Error("Unsupported local schema version");
    if (version === 2) return;
    await this.db.transaction([...(version === 0 ? v1 : []), ...v2]);
  }
  async localSend(m: LocalMessage): Promise<void> {
    await this.db.transaction([step(`INSERT INTO messages(conversation_id,request_id,sender_id,content,state)
      VALUES(?,?,?,?,'SENDING') ON CONFLICT(conversation_id,request_id) DO UPDATE SET
      state=CASE WHEN messages.state='SENT' THEN 'SENT' ELSE 'SENDING' END
      WHERE messages.sender_id=excluded.sender_id AND messages.content=excluded.content`,
      [m.conversationId,m.requestId,m.senderId,text(m)],1)]);
  }
  async markFailed(conversationId: string, requestId: string): Promise<void> {
    await this.db.transaction([step(`UPDATE messages SET state=CASE WHEN state='SENT' THEN 'SENT' ELSE 'FAILED' END
      WHERE conversation_id=? AND request_id=?`, [conversationId,requestId],1)]);
  }
  private materialize(m: ServerMessage | RealtimeMessage, requestId: string | null): Statement[] {
    const values: Bind[] = [m.conversationId,requestId,m.senderId,text(m),m.messageId,seq(m.seq),m.createdAt];
    // Check every durable identity/content before an unknown realtime row can
    // be merged. No INSERT OR REPLACE may erase a conflicting committed row.
    const guards: Statement[] = [
      assert(`NOT EXISTS(SELECT 1 FROM messages WHERE
        ((conversation_id=? AND request_id=?) OR server_message_id=? OR (conversation_id=? AND server_seq=?))
        AND (conversation_id<>? OR sender_id<>? OR content<>? OR
          (request_id IS NOT NULL AND ? IS NOT NULL AND request_id<>?) OR
          (server_message_id IS NOT NULL AND server_message_id<>?) OR
          (server_seq IS NOT NULL AND server_seq<>?) OR
          (server_time IS NOT NULL AND server_time<>?)))`,
      [m.conversationId,requestId,m.messageId,m.conversationId,seq(m.seq),
       m.conversationId,m.senderId,text(m),requestId,requestId,m.messageId,seq(m.seq),m.createdAt]),
    ];
    if (requestId !== null) {
      guards.push(step("DELETE FROM messages WHERE server_message_id=? AND request_id IS NULL AND EXISTS(SELECT 1 FROM messages WHERE conversation_id=? AND request_id=?)",
        [m.messageId,m.conversationId,requestId]));
      // If no local row exists, first attach the request to an existing realtime row.
      guards.push(step("UPDATE messages SET request_id=? WHERE server_message_id=? AND request_id IS NULL",
        [requestId,m.messageId]));
    }
    guards.push(step(`INSERT INTO messages(conversation_id,request_id,sender_id,content,state,server_message_id,server_seq,server_time)
      VALUES(?,?,?,?,'SENT',?,?,?)
      ON CONFLICT DO UPDATE SET
        state='SENT', server_message_id=excluded.server_message_id,
        server_seq=excluded.server_seq, server_time=excluded.server_time,
        request_id=COALESCE(messages.request_id,excluded.request_id)`,values,1));
    return guards;
  }
  async syncMessages(messages: ServerMessage[], failBeforeAdvance = false): Promise<void> {
    const statements = messages.flatMap(m => this.materialize(m,m.requestId));
    if (failBeforeAdvance) statements.push(step("INSERT INTO __fault_injection_missing_table VALUES(1)"));
    for (const id of new Set(messages.map(m => m.conversationId))) statements.push(...advance(id));
    await this.db.transaction(statements);
  }
  async realtime(m: RealtimeMessage, failBeforeAdvance = false): Promise<void> {
    const statements = this.materialize(m,null);
    if (failBeforeAdvance) statements.push(step("INSERT INTO __fault_injection_missing_table VALUES(1)"));
    await this.db.transaction([...statements,...advance(m.conversationId)]);
  }
  async committedAck(requestId: string, ack: Committed): Promise<void> {
    if (ack.status !== "committed") throw new Error("Only durable committed ACK accepted");
    const c = ack.conversationId, id = ack.messageId, n = seq(ack.seq), time = ack.createdAt;
    await this.db.transaction([
      assert("EXISTS(SELECT 1 FROM messages WHERE conversation_id=? AND request_id=?)",[c,requestId]),
      assert(`NOT EXISTS(SELECT 1 FROM messages s JOIN messages l ON l.conversation_id=? AND l.request_id=?
        WHERE (s.server_message_id=? OR (s.conversation_id=? AND s.server_seq=?) OR s.local_id=l.local_id)
        AND (s.conversation_id<>? OR s.sender_id<>l.sender_id OR s.content<>l.content OR
          (s.request_id IS NOT NULL AND s.request_id<>?) OR
          (s.server_message_id IS NOT NULL AND s.server_message_id<>?) OR
          (s.server_seq IS NOT NULL AND s.server_seq<>?) OR
          (s.server_time IS NOT NULL AND s.server_time<>?)))`,
        [c,requestId,id,c,n,c,requestId,id,n,time]),
      step("DELETE FROM messages WHERE server_message_id=? AND request_id IS NULL",[id]),
      step("UPDATE messages SET state='SENT',server_message_id=?,server_seq=?,server_time=? WHERE conversation_id=? AND request_id=?",
        [id,n,time,c,requestId],1),
      ...advance(c),
    ]);
  }
  async userPage(page: UserPage, expectedCursor: string, failBeforeAdvance = false): Promise<void> {
    if (page.syncVersion !== "1.0" || page.type !== "sync.user.page" || !page.nextCursor || [...page.nextCursor].length > 256) throw new Error("Invalid user page");
    const statements: Statement[] = [assert("cursor=?", [expectedCursor])];
    for (const event of page.events) {
      if (!["friend.changed","conversation.changed","membership.changed","plugin.changed"].includes(event.kind)) throw new Error("Message in user cursor");
      const revision = seq(event.revision);
      statements.push(step(`INSERT INTO user_state VALUES(?,?,?) ON CONFLICT(kind,subject_id)
        DO UPDATE SET revision=MAX(user_state.revision,excluded.revision)`,[event.kind,event.subjectId,revision],1));
    }
    if (failBeforeAdvance) statements.push(step("INSERT INTO __fault_injection_missing_table VALUES(1)"));
    statements.push(step("UPDATE user_cursor SET cursor=? WHERE singleton=1 AND cursor=?", [page.nextCursor,expectedCursor],1));
    await this.db.transaction(statements);
  }
  async messages(conversationId: string): Promise<(string | null)[][]> {
    return this.db.query(`SELECT request_id,sender_id,content,state,server_message_id,CAST(server_seq AS TEXT),server_time
      FROM messages WHERE conversation_id=? ORDER BY server_seq IS NULL,server_seq,local_id`,[conversationId]);
  }
  async contiguous(conversationId: string): Promise<number> {
    const rows = await this.db.query("SELECT CAST(contiguous_seq AS TEXT) FROM conversations WHERE conversation_id=?",[conversationId]);
    return Number(rows[0]?.[0] ?? 0);
  }
  async cursor(): Promise<string> { return (await this.db.query("SELECT cursor FROM user_cursor WHERE singleton=1",[]))[0][0]!; }
}

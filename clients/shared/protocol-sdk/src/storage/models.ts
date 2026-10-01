// Internal materialized models; wire authority remains contracts/.
export type State = "SENDING" | "SENT" | "FAILED";
export interface LocalMessage {
  conversationId: string; requestId: string; senderId: string;
  content: { kind: "TEXT"; text: string };
}
export interface ServerMessage extends LocalMessage {
  messageId: string; seq: number; createdAt: string;
}
export interface RealtimeMessage extends Omit<ServerMessage, "requestId"> {}
export interface Committed {
  status: "committed"; conversationId: string; messageId: string;
  seq: number; createdAt: string;
}
export interface UserEvent {
  eventId: string; cursor: string;
  kind: "friend.changed" | "conversation.changed" | "membership.changed" | "plugin.changed";
  subjectId: string; revision: number;
}
export interface UserPage {
  syncVersion: "1.0"; type: "sync.user.page"; requestId: string;
  events: UserEvent[]; nextCursor: string; hasMore: boolean;
}
export type Bind = string | null;
// All steps go through ONE native transaction. expectedChanges is a generic
// row-count assertion; a mismatch rolls back the entire intent.
export type Statement = [sql: string, binds: Bind[], expectedChanges: number | null];
export interface Database {
  transaction(statements: Statement[]): Promise<void>;
  query(sql: string, binds: Bind[]): Promise<(string | null)[][]>;
}

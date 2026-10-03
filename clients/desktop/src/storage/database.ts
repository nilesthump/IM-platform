import { invoke } from "@tauri-apps/api/core";
import type { Bind, Database, Statement } from "../../../shared/protocol-sdk/src/storage/models.js";
export function accountDatabase(accountId: string): Database {
  // Account identity comes from the bound session, never a caller-selected path.
  return {
    transaction: statements => invoke<void>("database_transaction",{ accountId, statements }),
    query: (sql: string, binds: Bind[]) => invoke<(string|null)[][]>("database_query",{ accountId, sql, binds }),
  };
}

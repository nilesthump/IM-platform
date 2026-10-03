import {accountSend} from "../accountSend.js";
import type {Session} from "../send.js";
import {SyncHttp} from "../../../../shared/protocol-sdk/src/sync/http.js";
import {SyncApplication} from "./application.js";
// The existing account factory owns native SQLx binding and local-first loading.
export async function accountSync(session:Session,endpoint:string):Promise<SyncApplication>{
  const owner=Object.freeze({...session});const http=new SyncHttp(endpoint,owner);
  return new SyncApplication(await accountSend(owner),http);
}

import {parse,object,uuid,positive,timestamp,content} from "../send/wire.js";
import type {UserPage,UserEvent,ServerMessage} from "../storage/models.js";
export const MAX_RESPONSE=6*1024*1024;
export interface ConversationPage {messages:ServerMessage[];hasMore:boolean}
const invalid=():never=>{throw new Error("Invalid Sync response");};
const kinds=["friend.changed","conversation.changed","membership.changed","plugin.changed"];
export function cursor(v:unknown):string {if(typeof v!=="string" || [...v].length<1 || [...v].length>256) return invalid();return v;}
function list(v:unknown):unknown[] {if(!Array.isArray(v) || v.length>100) return invalid();return v;}
function base(raw:string,keys:string[],requestId:string,type:string) {const p=object(parse(raw,MAX_RESPONSE),keys);if(p.syncVersion!=="1.0" || p.type!==type || uuid(p.requestId)!==requestId || typeof p.hasMore!=="boolean") return invalid();return p;}
export function userPage(raw:string,requestId:string,inputCursor:string):UserPage {
  try {
    const p=base(raw,["syncVersion","type","requestId","events","nextCursor","hasMore"],requestId,"sync.user.page");
    const ids=new Set<string>(), cursors=new Set<string>();
    const events=list(p.events).map(v=>{const e=object(v,["eventId","cursor","kind","subjectId","revision"]);
      const eventId=uuid(e.eventId), token=cursor(e.cursor);
      if(ids.has(eventId) || cursors.has(token) || token===inputCursor || !kinds.includes(String(e.kind))) return invalid();
      ids.add(eventId);cursors.add(token);
      return {eventId,cursor:token,kind:e.kind,subjectId:uuid(e.subjectId),revision:positive(e.revision)} as UserEvent;
    });
    const nextCursor=cursor(p.nextCursor),hasMore=p.hasMore as boolean;
    if(events.length ? nextCursor!==events.at(-1)!.cursor || nextCursor===inputCursor : nextCursor!==inputCursor || hasMore) return invalid();
    return {syncVersion:"1.0",type:"sync.user.page",requestId,events,nextCursor,hasMore};
  } catch {return invalid();}
}
export function conversationPage(raw:string,requestId:string,conversationId:string,afterSeq:bigint):ConversationPage {
  try {
    const p=base(raw,["syncVersion","type","requestId","conversationId","messages","hasMore"],requestId,"sync.conversation.page");
    if(uuid(p.conversationId)!==conversationId) return invalid();
    let next=afterSeq+1n;const ids=new Set<string>(),requests=new Set<string>();
    const messages=list(p.messages).map(v=>{const m=object(v,["conversationId","seq","messageId","senderId","requestId","createdAt","content"]);
      const messageId=uuid(m.messageId),rid=uuid(m.requestId),seq=positive(m.seq);
      if(uuid(m.conversationId)!==conversationId || seq!==next++ || ids.has(messageId) || requests.has(rid)) return invalid();
      ids.add(messageId);requests.add(rid);
      return {conversationId,seq,messageId,senderId:uuid(m.senderId),requestId:rid,createdAt:timestamp(m.createdAt),content:content(m.content)};
    });
    if(p.hasMore && !messages.length) return invalid();
    return {messages,hasMore:p.hasMore as boolean};
  } catch {return invalid();}
}
export class SyncFailure extends Error {constructor(readonly kind:"authentication"|"unavailable"|"protocol"|"transport"|"storage") {super("Sync "+kind+" failure");}}
export function errorResponse(raw:string,requestId:string,status:number,conversation:boolean):SyncFailure {
  try {
    const p=object(parse(raw,MAX_RESPONSE),["requestId","error"]);if(uuid(p.requestId)!==requestId) return invalid();
    const e=p.error as Record<string,unknown>;if(!e || typeof e!=="object" || Array.isArray(e) || Object.keys(e).some(k=>!["code","message","violations"].includes(k)) || typeof e.message!=="string" || !e.message) return invalid();
    if(e.violations!==undefined) {if(!Array.isArray(e.violations)) return invalid();for(const v of e.violations){const f=object(v,["field","reason"]);if(typeof f.field!=="string" || !f.field || typeof f.reason!=="string" || !f.reason) return invalid();}}
    if(status===401 && ["AUTH_REQUIRED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH"].includes(String(e.code))) return new SyncFailure("authentication");
    if(conversation && status===403 && e.code==="AUTHORIZATION_DENIED") return new SyncFailure("unavailable");
    if(status===400 && e.code==="VALIDATION_FAILED" || status===426 && e.code==="PROTOCOL_VERSION_UNSUPPORTED") return new SyncFailure("protocol");
    return invalid();
  } catch {return new SyncFailure("protocol");}
}
export function userRequest(requestId:string,inputCursor:string):string {return JSON.stringify({syncVersion:"1.0",type:"sync.user.request",requestId:uuid(requestId),cursor:cursor(inputCursor),limit:100});}
export function conversationRequest(requestId:string,c:string,afterSeq:bigint):string {if(afterSeq<0n) return invalid();return JSON.stringify({syncVersion:"1.0",type:"sync.conversation.request",requestId:uuid(requestId),conversationId:uuid(c),afterSeq:"SEQ",limit:100}).replace('"SEQ"',afterSeq.toString());}

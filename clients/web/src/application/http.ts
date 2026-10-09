import {object,uuid,parse,positive} from '../../../shared/protocol-sdk/src/send/wire.js';
export interface User {userId:string;username:string;displayName:string}
export interface Friend {user:User;friendshipId:string;directConversationId:string}
export interface Session {userId:string;sessionId:string;sessionEpoch:bigint;accessToken:string;expires:number}
export class ApiFailure extends Error {constructor(readonly code:string,readonly status:number){super(code);}}
const invalid=():never=>{throw new ApiFailure('INVALID_RESPONSE',0);};
export function user(v:unknown):User {const p=object(v,['userId','username','displayName']);if(typeof p.username!=='string'||!/^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$/.test(p.username)||typeof p.displayName!=='string')return invalid();return {userId:uuid(p.userId),username:p.username,displayName:p.displayName};}
export function friends(v:unknown):Friend[]{const p=object(v,['friends']);if(!Array.isArray(p.friends))return invalid();const ids=new Set<string>();return p.friends.map(v=>{const f=object(v,['user','friendshipId','directConversationId']),u=user(f.user);if(ids.has(u.userId))return invalid();ids.add(u.userId);return {user:u,friendshipId:uuid(f.friendshipId),directConversationId:uuid(f.directConversationId)};});}
export function auth(v:unknown):Session {
  const p=object(v,['session','tokens','replacedExistingSession']),s=object(p.session,['sessionId','userId','clientType','sessionEpoch','status']),t=object(p.tokens,['accessToken','accessTokenExpiresInSeconds','refreshTokenDelivery']);
  if(s.clientType!=='WEB'||s.status!=='ACTIVE'||typeof p.replacedExistingSession!=='boolean'||t.refreshTokenDelivery!=='HTTP_ONLY_SECURE_COOKIE'||typeof t.accessToken!=='string'||!t.accessToken||/[\r\n]/.test(t.accessToken))return invalid();
  const seconds=positive(t.accessTokenExpiresInSeconds);if(seconds>2147483n)return invalid();
  return {userId:uuid(s.userId),sessionId:uuid(s.sessionId),sessionEpoch:positive(s.sessionEpoch),accessToken:t.accessToken,expires:Date.now()+Number(seconds)*1000};
}
export class Http {
  readonly origin:string;
  constructor(origin:string,private fetcher:typeof fetch=(input,init)=>fetch(input,init)){const u=new URL(origin);if(u.protocol!=='https:'||u.username||u.password||u.search||u.hash||u.pathname!=='/')throw new ApiFailure('HTTPS_REQUIRED',0);this.origin=u.origin;}
  async request(path:string,method:string,body:unknown,token:string|undefined,signal:AbortSignal):Promise<unknown>{
    let r:Response;try {r=await this.fetcher(this.origin+path,{method,body:body===undefined?undefined:JSON.stringify(body),headers:{'Content-Type':'application/json',...(token?{'Authorization':'Bearer '+token}:{})},credentials:'same-origin',redirect:'error',cache:'no-store',signal});}catch{throw new ApiFailure('CONNECTION_UNAVAILABLE',0);}
    if(path==='/v1/auth/logout'&&method==='POST'){
      if(r.redirected)return invalid();
      if(r.status===204){if(r.body!==null)return invalid();return undefined;}
      if(r.ok)return invalid();
    }
    if(r.redirected||!/^application\/json(?:\s*;|$)/i.test(r.headers.get('content-type')??'')||r.headers.get('cache-control')!=='no-store')return invalid();
    let raw='';const reader=r.body?.getReader();if(!reader)return invalid();const decoder=new TextDecoder('utf8',{fatal:true});let size=0;
    try {for(;;){const part=await reader.read();if(part.done)break;size+=part.value.byteLength;if(size>6*1024*1024)return invalid();raw+=decoder.decode(part.value,{stream:true});}raw+=decoder.decode();}finally{await reader.cancel().catch(()=>{});}
    const p=parse(raw,6*1024*1024);
    if(!r.ok){const e=object(p,['requestId','error']);uuid(e.requestId);const detail=e.error as Record<string,unknown>;if(!detail||typeof detail.code!=='string')return invalid();const allowed=['VALIDATION_FAILED','AUTH_REQUIRED','AUTH_TOKEN_INVALID','AUTH_TOKEN_EXPIRED','AUTH_SESSION_REVOKED','AUTH_SESSION_EPOCH_STALE','AUTH_CLIENT_TYPE_MISMATCH','AUTH_REFRESH_REVOKED','AUTH_INVALID_CREDENTIALS','AUTHORIZATION_DENIED','USER_NOT_FOUND','FRIEND_SELF_NOT_ALLOWED','FRIENDSHIP_STATE_CONFLICT','PROTOCOL_VERSION_UNSUPPORTED'];throw new ApiFailure(allowed.includes(detail.code)?detail.code:'REQUEST_FAILED',r.status);}
    return p;
  }
}

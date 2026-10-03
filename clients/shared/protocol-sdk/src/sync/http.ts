import {MAX_RESPONSE,SyncFailure,errorResponse,userRequest,conversationRequest,userPage,conversationPage} from "./wire.js";
export interface SyncSession {userId:string;sessionId:string;sessionEpoch:bigint;accessToken:string}
export class SyncHttp {
  private readonly session:Readonly<SyncSession>;
  matchesSession(check:(s:Readonly<SyncSession>)=>boolean):boolean{return check(this.session);}
  private readonly base:string;private readonly token:string;
  constructor(endpoint:string,session:SyncSession,private fetcher:typeof fetch=fetch,private id:()=>string=()=>crypto.randomUUID()) {
    this.session=Object.freeze({...session});const accessToken=this.session.accessToken;
    let url:URL;try{url=new URL(endpoint);}catch{throw new SyncFailure("protocol");}
    if(url.protocol!=="https:" || !url.hostname || url.username || url.password || url.search || url.hash || url.pathname!=="/" || !accessToken || /[\r\n]/.test(accessToken)) throw new SyncFailure("protocol");
    this.base=url.origin;this.token=accessToken;
  }
  private async post(path:string,body:string,requestId:string,signal:AbortSignal):Promise<string> {
    try {
      const response=await this.fetcher(this.base+path,{method:"POST",headers:{"Authorization":"Bearer "+this.token,"Content-Type":"application/json"},body,signal,redirect:"error",credentials:"omit",cache:"no-store"});
      if(response.redirected || response.headers.get("cache-control")!=="no-store" || !/^application\/json(?:\s*;|$)/i.test(response.headers.get("content-type")??"")) throw new SyncFailure(response.status>=500?"transport":"protocol");
      const reader=response.body?.getReader();if(!reader) throw new SyncFailure("transport");
      const decoder=new TextDecoder("utf-8",{fatal:true});let raw="",size=0;
      try {for(;;){const item=await reader.read();if(item.done) break;size+=item.value.byteLength;if(size>MAX_RESPONSE) throw new SyncFailure("protocol");raw+=decoder.decode(item.value,{stream:true});}raw+=decoder.decode();}
      finally {await reader.cancel().catch(()=>{});}
      if(response.status!==200) {if([400,401,403,426].includes(response.status)) throw errorResponse(raw,requestId,response.status,path.endsWith("conversation"));throw new SyncFailure("transport");}
      return raw;
    } catch(error) {if(error instanceof SyncFailure) throw error;throw new SyncFailure("transport");}
  }
  async user(inputCursor:string,signal:AbortSignal) {const requestId=this.id();return userPage(await this.post("/v1/sync/user",userRequest(requestId,inputCursor),requestId,signal),requestId,inputCursor);}
  async conversation(c:string,afterSeq:bigint,signal:AbortSignal) {const requestId=this.id();return conversationPage(await this.post("/v1/sync/conversation",conversationRequest(requestId,c,afterSeq),requestId,signal),requestId,c,afterSeq);}
}

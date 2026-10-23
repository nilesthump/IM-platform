import {parse,object,WireFailure} from '../send/wire.js';
import {id,targets,result,page,start,type Continuation} from './wire.js';
export class GroupFailure extends Error {
  constructor(readonly kind:'transport'|'protocol'|'rejected'|'authentication',readonly code='',options?:ErrorOptions){super('Group '+kind,options);}
}
export class GroupHttp {
  private readonly base:string;
  constructor(endpoint:string,private readonly actor:string,private readonly token:string,private readonly fetcher:typeof fetch=fetch,private readonly transport:(error:unknown)=>boolean=e=>e instanceof TypeError||e instanceof DOMException){
    const u=new URL(endpoint);id(actor);if(u.protocol!=='https:'||u.username||u.password||u.search||u.hash||u.pathname!=='/'||!token||/[\r\n]/.test(token))throw new WireFailure();this.base=u.origin;
  }
  private async request(path:string,expected:number,requestId:string,signal:AbortSignal,body?:string):Promise<unknown>{
    let response:Response;
    try{response=await this.fetcher(this.base+path,{method:body===undefined?'GET':'POST',body,headers:{'Content-Type':'application/json','Authorization':'Bearer '+this.token},signal,credentials:'omit',redirect:'error',cache:'no-store'});}
    catch(error){if(this.transport(error))throw new GroupFailure('transport','',{cause:error});throw error;}
    if(response.redirected)throw new GroupFailure('protocol');
    if(response.status>=500)throw new GroupFailure('transport');
    if(response.headers.get('cache-control')!=='no-store'||!/^application\/json(?:\s*;|$)/i.test(response.headers.get('content-type')??''))throw new GroupFailure('protocol');
    const reader=response.body?.getReader();if(!reader)throw new GroupFailure('transport');
    const decoder=new TextDecoder('utf-8',{fatal:true});let raw='',size=0;let primary:unknown;
    try{for(;;){let part:ReadableStreamReadResult<Uint8Array>;
      try{part=await reader.read();}catch(error){if(this.transport(error))throw new GroupFailure('transport','',{cause:error});throw error;}
      if(part.done)break;size+=part.value.byteLength;if(size>6*1024*1024)throw new GroupFailure('protocol');
      try{raw+=decoder.decode(part.value,{stream:true});}catch(error){if(error instanceof TypeError)throw new GroupFailure('protocol','',{cause:error});throw error;}
    }
    try{raw+=decoder.decode();}catch(error){if(error instanceof TypeError)throw new GroupFailure('protocol','',{cause:error});throw error;}
    }catch(error){primary=error;throw error;}finally{try{await reader.cancel();}catch(error){
      if(primary!==undefined){if(error===primary||primary instanceof Error&&error===primary.cause)throw primary;throw new AggregateError([primary,error],'Group response and cleanup failed');}
      if(this.transport(error))throw new GroupFailure('transport','',{cause:error});throw error;
    }}
    const value=parse(raw,6*1024*1024);
    if(response.status!==expected){
      const codes:Record<number,string[]>={400:['VALIDATION_FAILED'],401:['AUTH_REQUIRED','AUTH_TOKEN_INVALID','AUTH_TOKEN_EXPIRED','AUTH_SESSION_REVOKED','AUTH_SESSION_EPOCH_STALE','AUTH_CLIENT_TYPE_MISMATCH'],403:['AUTHORIZATION_DENIED'],409:['GROUP_REQUEST_CONFLICT']};
      if(!codes[response.status]||body===undefined&&![400,401].includes(response.status))throw new GroupFailure('protocol');
      const p=object(value,['error','requestId']);if(id(p.requestId)!==requestId)throw new GroupFailure('protocol');
      const e=p.error as Record<string,unknown>;if(!e||typeof e!=='object'||Array.isArray(e))throw new GroupFailure('protocol');
      object(e,Object.hasOwn(e,'violations')?['code','message','violations']:['code','message']);
      if(typeof e.code!=='string'||!codes[response.status].includes(e.code)||typeof e.message!=='string'||!e.message)throw new GroupFailure('protocol');
      if(Object.hasOwn(e,'violations')){if(!Array.isArray(e.violations))throw new GroupFailure('protocol');for(const v of e.violations){const q=object(v,['field','reason']);if(typeof q.field!=='string'||!q.field||typeof q.reason!=='string'||!q.reason)throw new GroupFailure('protocol');}}
      throw new GroupFailure(response.status===401?'authentication':'rejected',e.code);
    }
    return value;
  }
  async mutate(requestId:string,selected:readonly string[],signal:AbortSignal,conversation?:string){
    id(requestId);const memberUserIds=targets(selected,this.actor);const path=conversation?'/v1/groups/'+id(conversation)+'/members':'/v1/groups';
    return result(await this.request(path,conversation?200:201,requestId,signal,JSON.stringify({requestId,memberUserIds})),requestId,this.actor,memberUserIds,conversation);
  }
  async members(requestId:string,signal:AbortSignal,after:Continuation=start){
    id(requestId);const q=new URLSearchParams({requestId,limit:'100'});
    if(after.afterConversationId||after.afterMemberUserId){q.set('afterConversationId',id(after.afterConversationId));q.set('afterMemberUserId',id(after.afterMemberUserId));}
    return page(await this.request('/v1/conversations?'+q,200,requestId,signal),requestId,after);
  }
}
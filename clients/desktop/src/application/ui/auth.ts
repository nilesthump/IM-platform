import {object,parse,positive,uuid} from "../../../../shared/protocol-sdk/src/send/wire.js";
import type {Session} from "../send.js";
import {nativeFetch,secure} from "./native.js";
export interface User {userId:string;username:string;displayName:string}
export interface Friend {user:User;friendshipId:string;directConversationId:string}
export class ApiFailure extends Error {constructor(readonly kind:string){super(kind);}}
export function origin(value:string):string {const u=new URL(value);if(u.protocol!=="https:"||u.username||u.password||u.search||u.hash||u.pathname!=="/")throw new ApiFailure("Use an HTTPS server origin");return u.origin;}
function user(value:unknown):User {const o=object(value,["userId","username","displayName"]);if(typeof o.username!=="string"||typeof o.displayName!=="string")throw new ApiFailure("Invalid server response");return {userId:uuid(o.userId),username:o.username,displayName:o.displayName};}
const metadata={clientType:"DESKTOP",deviceId:"im-desktop",clientVersion:"0.1.0",protocolVersion:"1"};
export class Auth {
  session:Session|null=null;private slot="";private expires=0;private generation=0;private storage:Promise<void>=Promise.resolve();
  constructor(readonly endpoint:string) {origin(endpoint);}
  async request(path:string,method="GET",body?:unknown,authenticated=true):Promise<unknown>{
    const headers:Record<string,string>={"Content-Type":"application/json"};
    if(authenticated){if(!this.session)throw new ApiFailure("Session expired");headers.Authorization="Bearer "+this.session.accessToken;}
    let response:Response;try{response=await nativeFetch(this.endpoint+path,{method,headers,...(body===undefined?{}:{body:JSON.stringify(body)}),redirect:"error",cache:"no-store"});}catch{throw new ApiFailure("Connection unavailable");}
    if(response.status===204)return null;
    if(!/^application\/json(?:\s*;|$)/i.test(response.headers.get("content-type")??""))throw new ApiFailure("Invalid server response");
    const raw=await response.text();let data:unknown;try{data=parse(raw,1048576);}catch{throw new ApiFailure("Invalid server response");}
    if(!response.ok){const code=(data as {error?:{code?:unknown}})?.error?.code;throw new ApiFailure(response.status===401?"Session expired":typeof code==="string"?code:"Request failed");}
    return data;
  }
  private async accept(data:unknown,g:number):Promise<Session>{
    if(g!==this.generation)throw new ApiFailure("Session expired");
    const result=object(data,["session","tokens","replacedExistingSession"]),s=object(result.session,["sessionId","userId","clientType","sessionEpoch","status"]);
    const t=object(result.tokens,["accessToken","accessTokenExpiresInSeconds","refreshToken","refreshTokenExpiresInSeconds","refreshTokenDelivery"]);
    if(s.clientType!=="DESKTOP"||s.status!=="ACTIVE"||t.refreshTokenDelivery!=="RESPONSE_BODY_FOR_OS_SECURE_STORAGE"||typeof t.accessToken!=="string"||!t.accessToken||typeof t.refreshToken!=="string"||!t.refreshToken||typeof result.replacedExistingSession!=="boolean")throw new ApiFailure("Invalid server response");
    const next={userId:uuid(s.userId),sessionId:uuid(s.sessionId),sessionEpoch:positive(s.sessionEpoch),accessToken:t.accessToken};
    const slot=this.endpoint+"/"+next.userId+"/"+next.sessionId;
    const refreshToken=t.refreshToken,expires=Number(positive(t.accessTokenExpiresInSeconds));positive(t.refreshTokenExpiresInSeconds);
    const write=this.storage.then(async()=>{if(g!==this.generation)throw new ApiFailure("Session expired");await secure.write(slot,refreshToken);if(g!==this.generation){await secure.remove(slot);throw new ApiFailure("Session expired");}await secure.write(this.endpoint+"/current",slot);if(this.slot&&this.slot!==slot)await secure.remove(this.slot);this.slot=slot;});
    this.storage=write.catch(()=>{});try{await write;}catch(error){this.session=null;throw error instanceof ApiFailure?error:new ApiFailure("Secure credential storage unavailable");}
    if(g!==this.generation)throw new ApiFailure("Session expired");this.session=next;this.expires=Date.now()+expires*1000;return next;
  }
  async login(username:string,password:string){const g=this.generation;return this.accept(await this.request("/v1/auth/login","POST",{username,password,...metadata},false),g);}
  async restore():Promise<Session|null>{return await this.savedAccount()?this.refresh():null;}
  async savedAccount():Promise<string|null>{const g=this.generation,slot=await secure.read(this.endpoint+"/current");if(g!==this.generation)throw new ApiFailure("Session expired");if(!slot)return null;if(!slot.startsWith(this.endpoint+"/"))throw new ApiFailure("Secure credential metadata invalid");const parts=slot.slice(this.endpoint.length+1).split("/");if(parts.length!==2)throw new ApiFailure("Secure credential metadata invalid");uuid(parts[1]);this.slot=slot;return uuid(parts[0]);}
  async refresh():Promise<Session>{const g=this.generation;const token=await secure.read(this.slot);if(g!==this.generation)throw new ApiFailure("Session expired");if(!token){await this.clear();throw new ApiFailure("Session expired");}try{return await this.accept(await this.request("/v1/auth/refresh/native","POST",{refreshToken:token,...metadata},false),g);}catch(error){if(g===this.generation&&error instanceof ApiFailure&&error.kind==="Session expired")await this.clear();throw error;}}
  needsRefresh(){return !!this.session && Date.now()>this.expires-60000;}
  async clear(){this.generation++;this.session=null;await this.storage;const slot=this.slot;this.slot="";if(slot)await secure.remove(slot);await secure.remove(this.endpoint+"/current");}
  async logout(){const remote=this.session?this.request("/v1/auth/logout","POST",{}):Promise.resolve();await Promise.all([this.clear(),remote]);}
  async profile():Promise<User>{const o=object(await this.request("/v1/users/me"),["user"]);return user(o.user);}
  async friends():Promise<Friend[]>{const o=object(await this.request("/v1/friends"),["friends"]);if(!Array.isArray(o.friends))throw new ApiFailure("Invalid server response");return o.friends.map(v=>{const f=object(v,["user","friendshipId","directConversationId"]);return {user:user(f.user),friendshipId:uuid(f.friendshipId),directConversationId:uuid(f.directConversationId)};});}
  async search(query:string):Promise<User[]>{const o=object(await this.request("/v1/users/search?username="+encodeURIComponent(query)),["users"]);if(!Array.isArray(o.users))throw new ApiFailure("Invalid server response");return o.users.map(user);}
  async add(userId:string):Promise<string>{const result=object(await this.request("/v1/friends/"+uuid(userId),"PUT"),["friendshipId","normalizedPair","directConversationId","memberUserIds","created"]);return uuid(result.directConversationId);}
}

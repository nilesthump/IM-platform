import {Repository} from "../../../../shared/protocol-sdk/src/storage/repository.js";
import {SyncHttp} from "../../../../shared/protocol-sdk/src/sync/http.js";
import {decode} from "../../../../shared/protocol-sdk/src/send/wire.js";
import {accountDatabase} from "../../storage/database.js";
import {SendApplication,type Session,type Socket} from "../send.js";
import {SyncApplication} from "../sync/application.js";
import {Auth,ApiFailure,type Friend,type User,origin} from "./auth.js";
import {appearance,defaults,nativeFetch,notify,type Appearance} from "./native.js";
export interface WorkspaceState {appearance:Appearance;busy:boolean;error:string|null;session:Session|null;offlineAccount:string|null;profile:User|null;friends:Friend[];results:User[];conversations:string[];selected:string;messages:ReadonlyArray<ReadonlyArray<string|null>>;connection:string;sync:string;unavailable:readonly string[];page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings";endpoint:string;previews:Record<string,{text:string;time:number}>}
export class Workspace {
  state:WorkspaceState={appearance:defaults,busy:false,error:null,session:null,offlineAccount:null,profile:null,friends:[],results:[],conversations:[],selected:"",messages:[],connection:"offline",sync:"idle",unavailable:[],page:"Chat",endpoint:"https://localhost:8443",previews:{}};
  private listeners=new Set<()=>void>();private auth:Auth|null=null;private sync:SyncApplication|null=null;private offlineRepository:Repository|null=null;private generation=0;private operation=0;private detach: (()=>void)[]=[];private repository:Repository|null=null;private listRevision=0;private activity=new Map<string,number>();private refreshTimer:ReturnType<typeof setInterval>|null=null;
  observe=(fn:()=>void)=>{this.listeners.add(fn);return()=>{this.listeners.delete(fn);};};
  snapshot=()=>this.state;
  private publish(value:Partial<WorkspaceState>){this.state={...this.state,...value};for(const listener of this.listeners)listener();}
  async start(){try{this.publish({appearance:await appearance.load()});}catch{this.publish({error:"Appearance could not be loaded"});}}
  page(page:WorkspaceState["page"]){this.publish({page,error:null});}
  async testNotification(){try{await notify("IM+","Your workspace notifications are ready.");}catch{this.publish({error:"System notification unavailable"});}}
  private appearanceWrites:Promise<void>=Promise.resolve();
  preferences(value:Appearance){this.publish({appearance:value,error:null});this.appearanceWrites=this.appearanceWrites.then(async()=>{try{await appearance.save(value);}catch{this.publish({error:"Appearance could not be saved"});}});return this.appearanceWrites;}
  private async stop(){this.generation++;if(this.refreshTimer)clearInterval(this.refreshTimer);this.refreshTimer=null;this.detach.forEach(fn=>fn());this.detach=[];const old=this.sync;this.sync=null;this.offlineRepository=null;this.repository=null;this.listRevision++;this.activity.clear();this.publish({session:null,offlineAccount:null,profile:null,friends:[],results:[],conversations:[],selected:"",messages:[],connection:"offline",sync:"idle",unavailable:[],previews:{}});await old?.close();}
  private socket(url:string,expired:()=>void):Socket {
    const ws=new WebSocket(url);let onmessage:Socket["onmessage"]=null;
    ws.onmessage=event=>{try{const frame=decode(event.data);if(frame.type==="session.revoked"||frame.type==="auth.ack"&&frame.payload.status==="rejected"){expired();return;}}catch{/* Existing Send parser owns malformed frame handling. */}onmessage?.(event);};
    return {get onopen(){return ws.onopen;},set onopen(fn){ws.onopen=fn;},get onmessage(){return onmessage;},set onmessage(fn){onmessage=fn;},get onclose(){return ws.onclose;},set onclose(fn){ws.onclose=fn;},get onerror(){return ws.onerror;},set onerror(fn){ws.onerror=fn;},send:text=>ws.send(text),close:()=>ws.close()};
  }
  private async bind(session:Session,op:number){
    if(op!==this.operation)return;
    await this.stop();if(op!==this.operation)return;const owner=this.auth,g=this.generation,active=()=>g===this.generation&&op===this.operation,repo=new Repository(accountDatabase(session.userId));await repo.initialize();if(!active())return;
    const send=new SendApplication(repo,session,url=>this.socket(url,()=>{void this.expire();}));
    this.repository=repo;const sync=new SyncApplication(send,new SyncHttp(this.state.endpoint,session,nativeFetch));this.sync=sync;
    const conversations=await repo.conversationIds();if(!active())return;this.publish({session,conversations,error:null});
    this.detach.push(send.observe(s=>{if(active()){this.publish({connection:s.connection,...(s.error?{error:s.error==="storage"?"Local history unavailable":"Protocol error"}:{})});void this.updateList(repo,g);}}));
    this.detach.push(sync.observe(s=>{if(!active())return;this.publish({sync:s.status,unavailable:s.unavailable,...(s.error?{error:"Sync "+s.error}:{})});if(s.error==="authentication")void this.expire();if(s.status==="idle")void this.updateList(repo,g);}));
    this.detach.push(send.observeDelivery(()=>{if(active()&&document.visibilityState!=="visible")void notify("IM+","New activity in your conversations").catch(()=>{if(active())this.publish({error:"System notification unavailable"});});}));
    await this.updateList(repo,g);if(!active())return;
    this.publish({selected:"",messages:[]});send.connect(this.state.endpoint.replace(/^https:/,"wss:")+"/v1/ws");
    this.refreshTimer=setInterval(()=>{if(active()&&this.auth?.needsRefresh())void this.refresh();},30000);
    try{const profile=await owner!.profile();if(!active())return;const friends=await owner!.friends();if(active()){this.publish({profile,friends});await this.updateList(repo,g);}}catch(error){if(active())this.failure(error);}
  }
  private failure(error:unknown){this.publish({error:error instanceof ApiFailure?error.kind:"Operation unavailable"});if(error instanceof ApiFailure&&error.kind==="Session expired")void this.expire();}
  private async updateList(repo:Repository,g:number){
    const revision=++this.listRevision;
    try{const ids=[...new Set([...await repo.conversationIds(),...this.state.friends.map(f=>f.directConversationId)])];
      const entries=await Promise.all(ids.map(async id=>{const rows=await repo.messages(id);const last=rows.at(-1);const time=Math.max(0,...rows.map(m=>m[6]?Date.parse(m[6]):0),this.activity.get(id)??0);return [id,{text:last?.[2]??"No messages yet",time},rows] as const;}));
      if(g!==this.generation||revision!==this.listRevision)return;
      const previews=Object.fromEntries(entries.map(([id,preview])=>[id,preview]));ids.sort((a,b)=>previews[b].time-previews[a].time||a.localeCompare(b));this.publish({conversations:ids,previews,messages:entries.find(e=>e[0]===this.state.selected)?.[2]??[]});
    }catch{if(g===this.generation&&revision===this.listRevision)this.publish({error:"Conversation history unavailable"});}
  }
  async register(username:string,password:string,confirmation:string){
    if(this.state.busy)return false;
    if(password!==confirmation){this.publish({error:"Passwords do not match"});return false;}
    if(!/^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$/.test(username)||[...password].length<12||[...password].length>256){this.publish({error:"Use a 3–64 character username and a 12–256 character password"});return false;}
    const op=++this.operation;this.publish({busy:true,error:null});
    try{await new Auth(this.state.endpoint).register(username,password);if(op!==this.operation)return false;return true;}
    catch(error){if(op===this.operation)this.failure(error);return false;}finally{if(op===this.operation)this.publish({busy:false});}
  }
  async login(endpoint:string,username:string,password:string){if(this.state.busy)return;const op=++this.operation;this.publish({busy:true,error:null});await this.stop();const g=this.generation;try{await this.auth?.clear();if(op!==this.operation)return;const base=origin(endpoint);this.publish({endpoint:base});const owner=new Auth(base);this.auth=owner;const session=await owner.login(username,password);if(op===this.operation)await this.bind(session,op);}catch(error){if(op===this.operation)this.failure(error);}finally{if(op===this.operation)this.publish({busy:false});}}
  async restore(endpoint:string){if(this.state.busy)return;const op=++this.operation;this.publish({busy:true,error:null});try{await this.stop();const g=this.generation,base=origin(endpoint);this.publish({endpoint:base});const auth=new Auth(base);this.auth=auth;const account=await auth.savedAccount();if(op!==this.operation)return;if(!account){this.publish({error:"No saved session for this server"});return;}const repo=new Repository(accountDatabase(account));await repo.initialize();const ids=await repo.conversationIds(),selected="",messages:ReadonlyArray<ReadonlyArray<string|null>>=[];if(op!==this.operation)return;this.offlineRepository=repo;this.publish({offlineAccount:account,conversations:ids,selected,messages,error:"Showing saved history while the secure session resumes"});await this.updateList(repo,this.generation);const session=await auth.refresh();if(op===this.operation)await this.bind(session,op);}catch(error){if(op===this.operation)this.failure(error);}finally{if(op===this.operation)this.publish({busy:false});}}
  async refresh(){if(this.state.busy||!this.auth)return;const op=++this.operation;const owner=this.auth,g=this.generation;this.publish({busy:true,error:null});try{const session=await owner.refresh();if(op===this.operation)await this.bind(session,op);}catch(error){if(op===this.operation)this.failure(error);}finally{if(op===this.operation)this.publish({busy:false});}}
  async expire(){const op=++this.operation,owner=this.auth;this.auth=null;await this.stop();try{await owner?.clear();}catch{/* Surface secure cleanup failure. */if(op===this.operation)this.publish({busy:false,error:"Session expired; secure credential cleanup failed"});return;}if(op===this.operation)this.publish({busy:false,error:"Session expired. Sign in again."});}
  async logout(){const op=++this.operation;this.publish({busy:true});const auth=this.auth;this.auth=null;const request=auth?.logout();await this.stop();const g=this.generation;try{await request;if(op===this.operation)this.publish({error:null});}catch(error){if(op===this.operation)this.failure(error);}finally{if(op===this.operation)this.publish({busy:false});}}
  closeConversation(){this.publish({selected:"",messages:[]});}
  async open(id:string){if(this.state.page==="Chat"&&this.state.selected===id){this.closeConversation();return;}const g=this.generation;this.publish({selected:id,page:"Chat",messages:[],error:null});try{if(this.offlineRepository){const messages=await this.offlineRepository.messages(id);if(g===this.generation&&this.state.selected===id)this.publish({messages});}else await this.sync?.openConversation(id);}catch{if(g===this.generation)this.publish({error:"Sync unavailable; showing local history"});}}
  async send(text:string){if(!this.state.selected||!this.sync)return;const g=this.generation,owner=this.sync;try{const id=this.state.selected;await owner.send.send(id,text);if(g===this.generation){this.activity.set(id,Date.now());if(this.repository)await this.updateList(this.repository,g);}}catch{if(g===this.generation)this.publish({error:"Message could not be saved"});}}
  async retry(id:string){const g=this.generation,owner=this.sync;if(!owner)return;try{await owner.send.retry(this.state.selected,id);}catch{if(g===this.generation)this.publish({error:"Retry unavailable"});}}
  async reconnect(){const g=this.generation,owner=this.sync;if(!owner)return;try{owner.send.connect(this.state.endpoint.replace(/^https:/,"wss:")+"/v1/ws");await owner.synchronize();}catch{if(g===this.generation)this.publish({error:"Connection unavailable"});}}
  disconnect(){this.sync?.send.disconnect();}
  async search(query:string){if(!this.auth)return;const auth=this.auth,g=this.generation;this.publish({busy:true,results:[],error:null});try{const results=await auth.search(query);if(g===this.generation)this.publish({results});}catch(error){if(g===this.generation)this.failure(error);}finally{if(g===this.generation)this.publish({busy:false});}}
  async add(id:string){if(!this.auth)return;const auth=this.auth,g=this.generation;this.publish({busy:true,error:null});try{const conversation=await auth.add(id);if(g!==this.generation)return;const friends=await auth.friends();if(g!==this.generation)return;this.publish({friends,conversations:[...new Set([...this.state.conversations,conversation])]});await this.open(conversation);}catch(error){if(g===this.generation)this.failure(error);}finally{if(g===this.generation)this.publish({busy:false});}}
}

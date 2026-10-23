import {GroupHttp,GroupFailure} from '../../../../shared/protocol-sdk/src/group/http.js';
import {start,targets,type MemberRow} from '../../../../shared/protocol-sdk/src/group/wire.js';
import {errorKey,translate,type Locale,validLocale} from "../../ui/i18n/resources.js";
import {Repository} from "../../../../shared/protocol-sdk/src/storage/repository.js";
import {SyncFailure} from "../../../../shared/protocol-sdk/src/sync/wire.js";
import {SyncHttp} from "../../../../shared/protocol-sdk/src/sync/http.js";
import {WireFailure,decode} from "../../../../shared/protocol-sdk/src/send/wire.js";
import {accountRepository} from "../accountSend.js";
import {SendStorageFailure,SendApplication,type Session,type Socket} from "../send.js";
import {SyncApplication} from "../sync/application.js";
import {Auth,ApiFailure,type Friend,type User,origin} from "./auth.js";
import {NativeCapabilityFailure,NativeTransportFailure,appearance,language,trayText,defaults,nativeFetch,notify,type Appearance} from "./native.js";
export interface WorkspaceState {groups:MemberRow[];groupBusy:boolean;groupError:string;groupStatus:string;language:Locale;languageStored:boolean;appearance:Appearance;busy:boolean;error:string|null;session:Session|null;offlineAccount:string|null;profile:User|null;friends:Friend[];results:User[];conversations:string[];selected:string;messages:ReadonlyArray<ReadonlyArray<string|null>>;connection:string;sync:string;unavailable:readonly string[];page:"Chat"|"Friends"|"AI"|"Plugin"|"Settings";endpoint:string;previews:Record<string,{text:string;time:number}>}
export class Workspace {
  state:WorkspaceState={groups:[],groupBusy:false,groupError:"",groupStatus:"",language:"en",languageStored:true,appearance:defaults,busy:false,error:null,session:null,offlineAccount:null,profile:null,friends:[],results:[],conversations:[],selected:"",messages:[],connection:"offline",sync:"idle",unavailable:[],page:"Chat",endpoint:"https://localhost:8443",previews:{}};
  private listeners=new Set<()=>void>();private auth:Auth|null=null;private sync:SyncApplication|null=null;private offlineRepository:Repository|null=null;private generation=0;private operation=0;private detach: (()=>void)[]=[];private repository:Repository|null=null;private listRevision=0;private activity=new Map<string,number>();private friendRevision=0;private friendCursor="";private refreshTimer:ReturnType<typeof setInterval>|null=null;
  observe=(fn:()=>void)=>{this.listeners.add(fn);return()=>{this.listeners.delete(fn);};};
  snapshot=()=>this.state;
  private publish(value:Partial<WorkspaceState>){this.state={...this.state,...value};for(const listener of this.listeners)listener();}
  private languageRevision=0;
  async start(){const revision=this.languageRevision;const value=await language.load();if(revision===this.languageRevision)this.publish({language:value});await this.updateTray();try{this.publish({appearance:await appearance.load()});}catch(error){this.failure(error);this.publish({error:"Appearance could not be loaded"});}}
  private trayWrites:Promise<void>=Promise.resolve();
  private updateTray(){const revision=this.languageRevision;
    this.trayWrites=this.trayWrites.then(async()=>{if(revision!==this.languageRevision)return;const t=(key:string)=>translate(this.state.language,key);try{await trayText(t("tray.open"),t("tray.hide"),t("tray.quit"),t("tray.tooltip"));}catch(error){this.failure(error);if(revision===this.languageRevision)this.publish({error:"Operation unavailable"});}});return this.trayWrites;
  }
  private languageWrites:Promise<void>=Promise.resolve();
  selectLanguage(value:Locale){if(!validLocale(value))return Promise.resolve();const revision=++this.languageRevision;this.publish({language:value,languageStored:true});const tray=this.updateTray();
    this.languageWrites=this.languageWrites.then(async()=>{try{await language.save(value);if(revision===this.languageRevision)this.publish({languageStored:true});}catch(error){this.failure(error);if(revision===this.languageRevision)this.publish({languageStored:false});}});return Promise.all([this.languageWrites,tray]).then(()=>{});
  }
  page(page:WorkspaceState["page"]){this.publish({page,error:null});}
  async testNotification(){try{await notify("IM+",translate(this.state.language,"notify.ready"));}catch(error){this.failure(error);this.publish({error:"System notification unavailable"});}}
  private appearanceWrites:Promise<void>=Promise.resolve();
  preferences(value:Appearance){this.publish({appearance:value,error:null});this.appearanceWrites=this.appearanceWrites.then(async()=>{try{await appearance.save(value);}catch(error){this.failure(error);this.publish({error:"Appearance could not be saved"});}});return this.appearanceWrites;}
  private async stop(preserveGroup=false){if(!preserveGroup){this.groupOperation=undefined;}this.groupScanning=false;this.groupDirty=false;this.generation++;if(this.refreshTimer)clearInterval(this.refreshTimer);this.refreshTimer=null;this.detach.forEach(fn=>fn());this.detach=[];const old=this.sync;this.sync=null;this.offlineRepository=null;this.repository=null;this.friendCursor="";this.friendRevision++;this.listRevision++;this.activity.clear();const failures:unknown[]=[];
    try{this.publish({groups:preserveGroup?this.state.groups:[],groupBusy:false,groupError:"",groupStatus:preserveGroup?(this.groupOperation?"unconfirmed":this.state.groupStatus):"",session:null,offlineAccount:null,profile:null,friends:[],results:[],conversations:[],selected:"",messages:[],connection:"offline",sync:"idle",unavailable:[],previews:{}});}catch(error){failures.push(error);}
    try{await old?.close();}catch(error){if(!failures.includes(error))failures.push(error);}
    if(failures.length===1)throw failures[0];if(failures.length>1)throw new AggregateError(failures,"Workspace retirement failed");}
  private socket(url:string,expired:()=>void):Socket {
    const ws=new WebSocket(url);let onmessage:Socket["onmessage"]=null;
    ws.onmessage=event=>{try{const frame=decode(event.data);if(frame.type==="session.revoked"||frame.type==="auth.ack"&&frame.payload.status==="rejected"){expired();return;}}catch(error){if(!(error instanceof WireFailure))throw error;/* Send owns invalid wire rejection. */}onmessage?.(event);};
    return {get onopen(){return ws.onopen;},set onopen(fn){ws.onopen=fn;},get onmessage(){return onmessage;},set onmessage(fn){onmessage=fn;},get onclose(){return ws.onclose;},set onclose(fn){ws.onclose=fn;},get onerror(){return ws.onerror;},set onerror(fn){ws.onerror=fn;},send:text=>ws.send(text),close:()=>ws.close()};
  }
  private async bind(session:Session,op:number){
    if(op!==this.operation)return;
    await this.stop(this.state.session?.userId===session.userId);if(op!==this.operation)return;const owner=this.auth,g=this.generation,active=()=>g===this.generation&&op===this.operation,repo=accountRepository(session.userId);await repo.initialize();if(!active())return;
    const send=new SendApplication(repo,session,url=>this.socket(url,()=>{void this.expire();}));
    this.repository=repo;const sync=new SyncApplication(send,new SyncHttp(this.state.endpoint,session,nativeFetch,undefined,error=>error instanceof NativeTransportFailure || error instanceof DOMException));this.sync=sync;
    const conversations=await repo.conversationIds();if(!active())return;this.publish({session,conversations,error:null});
    this.detach.push(send.observe(s=>{if(active()){this.publish({connection:s.connection,...(s.error?{error:s.error==="storage"?"Local history unavailable":"Protocol error"}:{})});void this.updateList(repo,g);}}));
    this.detach.push(sync.observe(s=>{if(!active())return;this.publish({sync:s.status,unavailable:s.unavailable,...(s.error?{error:"Sync "+s.error}:{})});if(s.error==="authentication")void this.expire();if(s.status==="idle"){void this.updateList(repo,g);void this.refreshFriends(repo,g);void this.refreshGroups();}}));
    this.detach.push(send.observeDelivery(()=>{if(active()&&document.visibilityState!=="visible")void notify("IM+",translate(this.state.language,"notify.activity")).catch(error=>{if(!(error instanceof NativeCapabilityFailure))throw error;if(active())this.publish({error:"System notification unavailable"});});}));
    await this.updateList(repo,g);if(!active())return;
    this.publish({selected:"",messages:[]});send.connect(this.state.endpoint.replace(/^https:/,"wss:")+"/v1/ws");
    this.refreshTimer=setInterval(()=>{if(active()&&this.auth?.needsRefresh())void this.refresh();},30000);
    try{const profile=await owner!.profile();if(!active())return;this.publish({profile});await this.refreshFriends(repo,g);await this.refreshGroups();}catch(error){this.failure(error,active());}
  }
  private async refreshFriends(repo:Repository,g:number){
    const owner=this.auth;if(!owner)return;const revision=++this.friendRevision;
    try{const cursor=await repo.cursor();if(g!==this.generation||cursor===this.friendCursor)return;
      const friends=await owner.friends();if(g!==this.generation||owner!==this.auth||revision!==this.friendRevision)return;
      this.friendCursor=cursor;this.publish({friends});await this.updateList(repo,g);
    }catch(error){this.failure(error,g===this.generation&&revision===this.friendRevision);}
  }
  private failure(error:unknown,active=true){
    const failures=error instanceof AggregateError?error.errors:[error];
    if(!failures.length || !failures.every(root=>root instanceof ApiFailure || root instanceof WireFailure || root instanceof SyncFailure || root instanceof SendStorageFailure || root instanceof NativeCapabilityFailure || root instanceof GroupFailure))throw error;
    if(!active)return;
    const authentication=error instanceof ApiFailure?error:undefined;
    try{this.publish({error:authentication?authentication.message:"Operation unavailable"});}catch(observer){if(observer===error)throw error;throw new AggregateError([error,observer],"Operation and observer failed");}if(authentication?.kind==="session_expired")void this.expire();}
  private async updateList(repo:Repository,g:number){
    const revision=++this.listRevision;
    try{const ids=[...new Set([...await repo.conversationIds(),...this.state.friends.map(f=>f.directConversationId),...this.state.groups.map(r=>r.conversationId)])];
      const settled=await Promise.allSettled(ids.map(async id=>{const rows=await repo.messages(id);const last=rows.at(-1);const time=Math.max(0,...rows.map(m=>m[6]?Date.parse(m[6]):0),this.activity.get(id)??0);return [id,{text:last?.[2]??"",time},rows] as const;}));
      const failures=[...new Set(settled.filter(result=>result.status==="rejected").map(result=>result.reason))];
      if(failures.length===1)throw failures[0];
      if(failures.length>1)throw new AggregateError(failures,"Conversation history failed");
      const entries=settled.filter(result=>result.status==="fulfilled").map(result=>result.value);
      if(g!==this.generation||revision!==this.listRevision)return;
      const previews=Object.fromEntries(entries.map(([id,preview])=>[id,preview]));ids.sort((a,b)=>previews[b].time-previews[a].time||a.localeCompare(b));this.publish({conversations:ids,previews,messages:entries.find(e=>e[0]===this.state.selected)?.[2]??[]});
    }catch(error){this.failure(error,g===this.generation&&revision===this.listRevision);if(g===this.generation&&revision===this.listRevision)this.publish({error:"Conversation history unavailable"});}
  }
  async register(username:string,password:string,confirmation:string){
    if(this.state.busy)return false;
    if(password!==confirmation){this.publish({error:"Passwords do not match"});return false;}
    if(!/^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$/.test(username)||[...password].length<12||[...password].length>256){this.publish({error:"Use a 3–64 character username and a 12–256 character password"});return false;}
    const op=++this.operation;let completed=false,failed=false,rejected=false,failure:unknown;
    try{this.publish({busy:true,error:null});await new Auth(this.state.endpoint).register(username,password);completed=op===this.operation;}
    catch(error){failed=true;failure=error;try{this.failure(error,op===this.operation);}catch(propagated){failure=propagated;rejected=true;}}
    finally{if(op===this.operation)try{this.publish({busy:false});}catch(error){failure=failed&&error!==failure?new AggregateError([failure,error],"Registration and observer failed"):error;rejected=true;}}
    if(rejected)throw failure;return completed;
  }
  async login(endpoint:string,username:string,password:string){if(this.state.busy)return;const op=++this.operation;let failed=false,failure:unknown;
    try{this.publish({busy:true,error:null});await this.stop();await this.auth?.clear();if(op!==this.operation)return;const base=origin(endpoint);this.publish({endpoint:base});const owner=new Auth(base);this.auth=owner;const session=await owner.login(username,password);if(op===this.operation)await this.bind(session,op);}catch(error){failed=true;failure=error;}
    finally{if(op===this.operation)try{this.publish({busy:false});}catch(error){failure=failed&&error!==failure?new AggregateError([failure,error],"Login and observer failed"):error;failed=true;}}
    if(failed)this.failure(failure,op===this.operation);
  }
  async restore(endpoint:string){if(this.state.busy)return;const op=++this.operation;let failed=false,failure:unknown;
    try{this.publish({busy:true,error:null});await this.stop();const base=origin(endpoint);this.publish({endpoint:base});const auth=new Auth(base);this.auth=auth;const account=await auth.savedAccount();if(op!==this.operation)return;
      if(!account)this.publish({error:"No saved session for this server"});
      else{const repo=accountRepository(account);await repo.initialize();const ids=await repo.conversationIds(),selected="",messages:ReadonlyArray<ReadonlyArray<string|null>>=[];if(op!==this.operation)return;this.offlineRepository=repo;this.publish({offlineAccount:account,conversations:ids,selected,messages,error:"Showing saved history while the secure session resumes"});await this.updateList(repo,this.generation);const session=await auth.refresh();if(op===this.operation)await this.bind(session,op);}
    }catch(error){failed=true;failure=error;}
    finally{if(op===this.operation)try{this.publish({busy:false});}catch(error){failure=failed&&error!==failure?new AggregateError([failure,error],"Restore and observer failed"):error;failed=true;}}
    if(failed)this.failure(failure,op===this.operation);
  }
  async refresh(){if(this.state.busy||!this.auth)return;const op=++this.operation;const owner=this.auth,g=this.generation;let failed=false,failure:unknown;try{this.publish({busy:true,error:null});const session=await owner.refresh();if(op===this.operation)await this.bind(session,op);}catch(error){
    failed=true;failure=error;
    if(op===this.operation&&owner===this.auth&&g===this.generation&&!owner.session){this.auth=null;try{await this.stop();}catch(cleanup){if(cleanup!==error)failure=new AggregateError([error,cleanup],"Refresh and retirement failed");}}
  }finally{if(op===this.operation)try{this.publish({busy:false});}catch(cleanup){failure=failed&&cleanup!==failure?new AggregateError([failure,cleanup],"Refresh and observer failed"):cleanup;failed=true;}}
    if(failed)this.failure(failure,op===this.operation);
  }
  async expire(){const op=++this.operation,owner=this.auth;this.auth=null;const failures:unknown[]=[];let cleanupFailed=false;
    try{await this.stop();}catch(error){failures.push(error);}
    try{await owner?.clear();}catch(error){cleanupFailed=true;if(!failures.includes(error))failures.push(error);}
    if(op===this.operation)try{this.publish({busy:false,error:cleanupFailed?"Session expired; secure credential cleanup failed":"Session expired. Sign in again."});}catch(error){if(!failures.includes(error))failures.push(error);}
    if(failures.length)this.failure(failures.length===1?failures[0]:new AggregateError(failures,"Expiry cleanup failed"),false);
  }
  async logout(){const op=++this.operation,auth=this.auth;this.auth=null;const failures:unknown[]=[];
    try{this.publish({busy:true});}catch(error){failures.push(error);}
    const settled=await Promise.allSettled([auth?.logout(),this.stop()]);
    for(const result of settled)if(result.status==="rejected"&&!failures.includes(result.reason))failures.push(result.reason);
    if(op===this.operation)try{this.publish({busy:false,...(!failures.length?{error:null}:{})});}catch(error){if(!failures.includes(error))failures.push(error);}
    if(failures.length){const failure=failures.length===1?failures[0]:new AggregateError(failures,"Logout retirement failed");
      this.failure(failure,op===this.operation);}

  }
  closeConversation(){this.publish({selected:"",messages:[]});}
  async open(id:string){if(this.state.page==="Chat"&&this.state.selected===id){this.closeConversation();return;}const g=this.generation;this.publish({selected:id,page:"Chat",messages:[],error:null});try{if(this.offlineRepository){const messages=await this.offlineRepository.messages(id);if(g===this.generation&&this.state.selected===id)this.publish({messages});}else await this.sync?.openConversation(id);}catch(error){this.failure(error,g===this.generation);if(g===this.generation)this.publish({error:"Sync unavailable; showing local history"});}}
  async send(text:string){if(!this.state.selected||!this.sync)return;const g=this.generation,owner=this.sync;try{const id=this.state.selected;await owner.send.send(id,text);if(g===this.generation){this.activity.set(id,Date.now());if(this.repository)await this.updateList(this.repository,g);}}catch(error){this.failure(error,g===this.generation);if(g===this.generation)this.publish({error:"Message could not be saved"});}}
  async retry(id:string){const g=this.generation,owner=this.sync;if(!owner)return;try{await owner.send.retry(this.state.selected,id);}catch(error){this.failure(error,g===this.generation);if(g===this.generation)this.publish({error:"Retry unavailable"});}}
  async reconnect(){const g=this.generation,owner=this.sync;if(!owner)return;try{owner.send.connect(this.state.endpoint.replace(/^https:/,"wss:")+"/v1/ws");await owner.synchronize();}catch(error){this.failure(error,g===this.generation);if(g===this.generation)this.publish({error:"Connection unavailable"});}}
  disconnect(){this.sync?.send.disconnect();}
  async search(query:string){if(!this.auth)return;const auth=this.auth,g=this.generation;let failed=false,rejected=false,failure:unknown;
    try{this.publish({busy:true,results:[],error:null});const results=await auth.search(query);if(g===this.generation)this.publish({results});}
    catch(error){failed=true;failure=error;try{this.failure(error,g===this.generation);}catch(propagated){failure=propagated;rejected=true;}}
    finally{if(g===this.generation)try{this.publish({busy:false});}catch(error){failure=failed&&error!==failure?new AggregateError([failure,error],"Search and observer failed"):error;rejected=true;}}
    if(rejected)throw failure;
  }
  async add(id:string){if(!this.auth)return;const auth=this.auth,g=this.generation;let failed=false,rejected=false,failure:unknown;
    try{this.publish({busy:true,error:null});const conversation=await auth.add(id);if(g!==this.generation)return;const revision=++this.friendRevision;const friends=await auth.friends();if(g!==this.generation||auth!==this.auth)return;if(revision===this.friendRevision)this.publish({friends,conversations:[...new Set([...this.state.conversations,conversation])]});await this.open(conversation);}
    catch(error){failed=true;failure=error;try{this.failure(error,g===this.generation);}catch(propagated){failure=propagated;rejected=true;}}
    finally{if(g===this.generation)try{this.publish({busy:false});}catch(error){failure=failed&&error!==failure?new AggregateError([failure,error],"Friend add and observer failed"):error;rejected=true;}}
    if(rejected)throw failure;
  }

  private groupOperation?:Readonly<{account:string;requestId:string;targets:readonly string[];conversation?:string}>;
  private groupScanning=false;private groupDirty=false;
  async createGroup(ids:string[],conversation?:string){const s=this.state.session;if(!s||this.state.groupBusy||this.groupOperation)return;
    this.groupOperation=Object.freeze({account:s.userId,requestId:crypto.randomUUID(),targets:Object.freeze(targets(ids,s.userId)),conversation});await this.retryGroup();}
  private groupHttp(){const s=this.state.session;if(!s)throw new GroupFailure('authentication');return new GroupHttp(this.state.endpoint,s.userId,s.accessToken,nativeFetch,e=>e instanceof NativeTransportFailure||e instanceof DOMException);}
  async retryGroup(){const s=this.state.session,g=this.generation,op=this.groupOperation;if(!s||!op||op.account!==s.userId||this.state.groupBusy)return;
    this.publish({groupBusy:true,groupError:'',groupStatus:'loading'});
    try{const answer=await this.groupHttp().mutate(op.requestId,op.targets,new AbortController().signal,op.conversation);if(g!==this.generation)return;
      this.groupOperation=undefined;this.publish({groupBusy:false,groupStatus:'success'});await this.refreshGroups();if(g===this.generation)await this.open(answer.conversationId);
    }catch(error){this.failure(error,g===this.generation);if(g!==this.generation)return;if(error instanceof GroupFailure&&error.kind==='authentication'){await this.expire();return;}
      const rejected=error instanceof GroupFailure&&error.kind==='rejected';if(rejected)this.groupOperation=undefined;
      this.publish({groupBusy:false,groupStatus:rejected?'rejected':'unconfirmed',groupError:error instanceof GroupFailure?error.code||error.kind:'protocol'});}
  }
  async refreshGroups(){const s=this.state.session,g=this.generation;if(!s)return;this.groupDirty=true;if(this.groupScanning)return;this.groupScanning=true;
    try{const http=this.groupHttp();while(this.groupDirty&&g===this.generation){this.groupDirty=false;let after={...start};const rows=new Map<string,MemberRow>();let last:MemberRow|undefined;
      for(;;){const p=await http.members(crypto.randomUUID(),new AbortController().signal,after);if(g!==this.generation)return;for(const r of p.items){if(last?.conversationId===r.conversationId&&(last.kind!==r.kind||last.createdBy!==r.createdBy||last.createdAt!==r.createdAt))throw new WireFailure();rows.set(r.conversationId+'/'+r.member.user.userId,r);last=r;}if(!p.hasMore)break;after=p.next;}
      this.publish({groups:[...rows.values()].filter(r=>r.kind==='GROUP'),groupError:''});if(this.repository)await this.updateList(this.repository,g);
    }}catch(error){this.failure(error,g===this.generation);if(g===this.generation){if(error instanceof GroupFailure&&error.kind==='authentication'){await this.expire();return;}this.publish({groupError:error instanceof GroupFailure?error.code||error.kind:'protocol'});}}
    finally{if(g===this.generation)this.groupScanning=false;}
  }
}

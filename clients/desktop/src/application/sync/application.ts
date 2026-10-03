import {uuid} from "../../../../shared/protocol-sdk/src/send/wire.js";
import {SendApplication} from "../send.js";
import {SyncHttp} from "../../../../shared/protocol-sdk/src/sync/http.js";
import {SyncFailure} from "../../../../shared/protocol-sdk/src/sync/wire.js";
export interface SyncState {status:"idle"|"syncing"|"failed"|"retired";error:string|null;unavailable:readonly string[]}
export class SyncApplication {
  private opened="";
  private generation=0;private retired=false;private stopped=false;private controller=new AbortController();
  private queue:Promise<void>=Promise.resolve();private requested=false;private listeners=new Set<(s:SyncState)=>void>();
  private detach:()=>void;private detachDelivery:()=>void;private wasReady=false;
  private current:SyncState={status:"idle",error:null,unavailable:[]};
  constructor(readonly send:SendApplication,private http:SyncHttp) {
    if(!http.matchesSession(s=>send.matchesSession(s))) throw new SyncFailure("authentication");
    this.detachDelivery=send.observeDelivery(()=>{if(send.state.connection==="ready") void this.synchronize().catch(()=>{});});
    this.detach=send.observe(s=>{
      const ready=s.connection==="ready";
      if(!ready && this.wasReady){this.generation++;this.controller.abort();this.controller=new AbortController();}
      if(ready && !this.wasReady && !this.stopped) void this.synchronize().catch(()=>{});
      this.wasReady=ready;
    });
  }
  get state():SyncState{return this.current;}
  observe(listener:(s:SyncState)=>void):()=>void{this.listeners.add(listener);listener(this.current);return()=>this.listeners.delete(listener);}
  private publish(s:SyncState){if(this.retired)return;this.current=Object.freeze({...s,unavailable:Object.freeze([...s.unavailable])});for(const l of this.listeners){try{l(this.current);}catch{/* Observer owns no commit. */}}}
  async openConversation(c:string):Promise<void>{const selected=uuid(c);await this.send.openConversation(selected);this.opened=selected;await this.synchronize();}
  synchronize():Promise<void>{
    if(this.retired || this.stopped)return Promise.resolve();
    this.requested=true;
    const job=this.queue.then(async()=>{
      if(!this.requested || this.retired || this.stopped)return;
      this.requested=false;const g=this.generation,signal=this.controller.signal;
      const active=()=>!this.retired && !this.stopped && this.generation===g && !signal.aborted;
      this.publish({status:"syncing",error:null,unavailable:[]});
      const unavailable:string[]=[];
      try{
        do{
          if(!active())return;const cursor=await this.send.repository.cursor(),page=await this.http.user(cursor,signal);
          if(!active())return;await this.send.mergeUserPage(page,cursor,active);if(!active())return;
          if(!page.hasMore)break;
          if(await this.send.repository.cursor()===cursor)throw new SyncFailure("protocol");
        }while(active());
        for(const c of new Set([...(await this.send.repository.conversationIds()),...(this.opened?[this.opened]:[])])){
          try{
            do{
              if(!active())return;const after=await this.send.repository.contiguous(c),page=await this.http.conversation(c,after,signal);
              if(!active())return;await this.send.mergeMessages(page.messages,active);if(!active())return;
              if(!page.hasMore)break;
              if(await this.send.repository.contiguous(c)<=after)throw new SyncFailure("protocol");
            }while(active());
          }catch(error){if(error instanceof SyncFailure && error.kind==="unavailable"){unavailable.push(c);continue;}throw error;}
        }
        if(active())this.publish({status:"idle",error:null,unavailable});
      }catch(error){
        if(!active())return;
        const kind=error instanceof SyncFailure?error.kind:"storage";
        if(kind==="authentication"){this.stopped=true;this.generation++;this.controller.abort();this.send.disconnect();}
        this.publish({status:"failed",error:kind,unavailable});throw new SyncFailure(kind);
      }
    });
    this.queue=job.catch(()=>{});return job;
  }
  async idle(){await this.queue;await this.send.idle();}
  async close(){if(this.retired)return;this.retired=true;this.generation++;this.controller.abort();this.detach();this.detachDelivery();this.listeners.clear();this.current={status:"retired",error:null,unavailable:[]};this.send.close();await this.queue;await this.send.idle();}
}

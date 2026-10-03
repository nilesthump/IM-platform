import { Repository } from "../../../shared/protocol-sdk/src/storage/repository.js";
import type { LocalMessage, ServerMessage, Committed, UserPage } from "../../../shared/protocol-sdk/src/storage/models.js";
import { content, decode, envelope, uuid } from "../../../shared/protocol-sdk/src/send/wire.js";
export interface Session { userId: string; sessionId: string; sessionEpoch: bigint; accessToken: string }
export interface Socket {
  onopen: ((event:Event)=>void)|null; onmessage: ((event:MessageEvent<unknown>)=>void)|null;
  onclose: ((event:CloseEvent)=>void)|null; onerror: ((event:Event)=>void)|null;
  send(text: string): void; close(): void;}
export interface SendState { connection: "offline"|"binding"|"ready"; messages: ReadonlyArray<ReadonlyArray<string|null>>; error: "storage"|"protocol"|null }
// Each instance owns exactly one account/session. Retiring it cannot publish into
// a replacement account. All Repository operations and confirmations are ordered.
export class SendApplication {
  private socket: Socket|null=null;
  private generation=0;
  private binding="";
  private bound=false;
  private retired=false;
  private queue: Promise<void>=Promise.resolve();
  private attempts=new Map<string,{message:LocalMessage; generation:number; timer:ReturnType<typeof setTimeout>|null; sent:boolean}>();
  private known=new Map<string,LocalMessage>();
  // RID -> sole Conversation, or null once ambiguous on this connection. Keep
  // settled identities until disconnect so delayed rejects remain unattributable.
  private requestConversations=new Map<string,string|null>();
  private listeners=new Set<(state:SendState)=>void>();
  private deliveries=new Set<(conversationId:string,seq:bigint)=>void>();
  private conversation="";
  private current: SendState={connection:"offline",messages:[],error:null};
  private readonly session: Readonly<Session>;
  constructor(readonly repository: Repository, session: Session, private factory:(url:string)=>Socket = url=>new WebSocket(url), private timeoutMs=15000, private id:()=>string=()=>crypto.randomUUID()) {
    this.session=Object.freeze({...session,userId:uuid(session.userId),sessionId:uuid(session.sessionId)});
    if(session.sessionEpoch<1n || !session.accessToken || timeoutMs<1) throw new Error("Invalid send session");
  }
  matchesSession(s:Session):boolean {return s.userId===this.session.userId && s.sessionId===this.session.sessionId && s.sessionEpoch===this.session.sessionEpoch && s.accessToken===this.session.accessToken;}
  get state(): SendState { return this.current; }
  observe(listener:(state:SendState)=>void): ()=>void { this.listeners.add(listener); listener(this.current); return ()=>this.listeners.delete(listener); }
  observeDelivery(listener:(conversationId:string,seq:bigint)=>void):()=>void { this.deliveries.add(listener); return ()=>this.deliveries.delete(listener); }
  private delivered(c:string,n:bigint):void { if(!this.retired) for(const listener of this.deliveries) {try {listener(c,n);} catch {/* Commit already completed. */}} }
  private publish(state: SendState): void {
    if(this.retired) return;
    this.current=Object.freeze({...state,messages:Object.freeze(state.messages.map(r=>Object.freeze([...r])))});
    for(const listener of this.listeners) { try { listener(this.current); } catch { /* Observers do not own the transaction. */ } }
  }
  private serial(action:()=>Promise<void>): Promise<void> {
    const result=this.queue.then(action);
    this.queue=result.catch(()=>{this.publish({...this.current,error:"storage"});});
    return result;
  }
  async idle(): Promise<void> { await this.queue; }
  private async refresh(): Promise<void> {
    const messages=this.conversation?await this.repository.messages(this.conversation):[];
    this.publish({...this.current,messages});
  }
  async openConversation(conversationId:string): Promise<void> {
    return this.serial(async()=>{if(this.retired) return; this.conversation=uuid(conversationId); await this.refresh();});
  }
  connect(endpoint:string): void {
    if(this.retired) throw new Error("Send application retired");
    let url: URL; try { url=new URL(endpoint); } catch { throw new Error("Invalid WSS endpoint"); }
    if(url.protocol!=="wss:" || url.username || url.password || url.search || url.hash) throw new Error("Invalid WSS endpoint");
    this.disconnect(); const generation=++this.generation; this.binding=uuid(this.id()); this.bound=false;
    const socket=this.factory(url.href); this.socket=socket;
    this.publish({...this.current,connection:"binding"});
    const active=()=>!this.retired && this.socket===socket && this.generation===generation;
    socket.onopen=()=>{if(active()) { try { socket.send(envelope("auth.bind",this.binding,{accessToken:this.session.accessToken})); } catch { this.disconnect(); } }};
    socket.onmessage=event=>{if(active()) void this.serial(async()=>{if(!active()) return; if(typeof event.data!=="string") { this.protocolFailure(); return; } try { await this.receive(event.data,generation); } catch(error) { if(error instanceof Error && error.message==="Invalid WSS frame") this.protocolFailure(); else throw new Error("Send storage operation failed"); }}).catch(()=>{});};
    socket.onerror=socket.onclose=()=>{if(active()) this.disconnect();};
  }
  private protocolFailure(): void { this.disconnect(); this.publish({...this.current,error:"protocol"}); }
  disconnect(): void {
    const old=this.socket; this.socket=null; this.bound=false; this.generation++; this.requestConversations.clear();
    if(old) { old.onopen=old.onmessage=old.onclose=old.onerror=null; try { old.close(); } catch { /* Already closed. */ } }
    this.publish({...this.current,connection:"offline"});
    for(const [key,attempt] of this.attempts) {
      if(attempt.timer) clearTimeout(attempt.timer); this.attempts.delete(key);
      void this.serial(async()=>{await this.repository.markFailed(attempt.message.conversationId,attempt.message.requestId); await this.refresh();}).catch(()=>{});
    }
  }
  close(): void { this.disconnect(); this.retired=true; this.listeners.clear(); this.deliveries.clear(); this.current={connection:"offline",messages:[],error:null}; }
  async send(conversationId:string,text:string): Promise<string> {
    const requestId=uuid(this.id());
    const message: LocalMessage={conversationId:uuid(conversationId),requestId,senderId:this.session.userId,content:content({kind:"TEXT",text})};
    await this.start(message); return requestId;
  }
  async retry(conversationId:string,requestId:string): Promise<void> {
    await this.serial(async()=>{
      if(this.retired) throw new Error("Send application retired");
      const c=uuid(conversationId), r=uuid(requestId), row=(await this.repository.messages(c)).find(row=>row[0]===r);
      if(!row || row[1]!==this.session.userId) throw new Error("Unknown own send");
      if(row[3]==="SENT") return;
      await this.begin({conversationId:c,requestId:r,senderId:row[1]!,content:content({kind:"TEXT",text:row[2]})});
    });
  }
  private start(message:LocalMessage): Promise<void> { return this.serial(()=>this.begin(message)); }
  private key(message:Pick<LocalMessage,"conversationId"|"requestId">): string { return message.conversationId+"/"+message.requestId; }
  private async begin(message:LocalMessage): Promise<void> {
    if(this.retired) throw new Error("Send application retired");
    await this.repository.localSend(message);
    this.known.set(this.key(message),message); await this.refresh();
    if(this.retired) return;
    const key=this.key(message), prior=this.attempts.get(key); if(prior?.timer) clearTimeout(prior.timer);
    const attempt={message,generation:this.generation,timer:null as ReturnType<typeof setTimeout>|null,sent:false};
    this.attempts.set(key,attempt);
    if(!this.bound || !this.socket) { await this.fail(key,attempt); return; }
    try { this.socket.send(envelope("message.send",message.requestId,{conversationId:message.conversationId,content:message.content})); attempt.sent=true; }
    catch { await this.fail(key,attempt); return; }
    const priorConversation=this.requestConversations.get(message.requestId);
    this.requestConversations.set(message.requestId,priorConversation===undefined || priorConversation===message.conversationId ? message.conversationId : null);
    attempt.timer=setTimeout(()=>{void this.serial(()=>this.fail(key,attempt)).catch(()=>{});},this.timeoutMs);
  }
  private async fail(key:string,attempt:{message:LocalMessage}): Promise<void> {
    if(this.attempts.get(key)!==attempt) return;
    this.attempts.delete(key); await this.repository.markFailed(attempt.message.conversationId,attempt.message.requestId); await this.refresh();
  }
  private clear(c:string,r:string): void { const key=c+"/"+r, a=this.attempts.get(key); if(a?.timer) clearTimeout(a.timer); this.attempts.delete(key); }
  private async receive(raw:string,generation:number): Promise<void> {
    const frame=decode(raw), p=frame.payload;
    if(frame.type==="ping") { this.socket?.send(envelope("pong",frame.requestId,{})); return; }
    if(frame.type==="pong") return;
    if(frame.type==="auth.ack") {
      if(frame.requestId!==this.binding || p.status!=="bound" || p.userId!==this.session.userId || p.sessionId!==this.session.sessionId || p.clientType!=="DESKTOP" || p.sessionEpoch!==this.session.sessionEpoch || this.bound) { this.protocolFailure(); return; }
      this.bound=true; this.publish({...this.current,connection:"ready"}); return;
    }
    if(!this.bound) { this.protocolFailure(); return; }
    if(frame.type==="session.revoked") { if(p.sessionId!==this.session.sessionId) this.protocolFailure(); else this.disconnect(); return; }
    if(frame.type==="message.created") {
      const message={...p,requestId:frame.requestId} as unknown as ServerMessage;
      await this.repository.syncMessages([message]); this.clear(message.conversationId,message.requestId); await this.refresh(); this.delivered(message.conversationId,BigInt(message.seq)); return;
    }
    if(frame.type==="message.ack") {
      if(p.status==="rejected") {
        // Rejection has no Conversation. Ambiguous identities must keep their
        // independent confirmation/timeout paths instead of failing all sends.
        const matches=[...this.attempts].filter(([,a])=>a.message.requestId===frame.requestId && a.sent && a.generation===generation);
        if(matches.length===1 && this.requestConversations.get(frame.requestId)===matches[0][1].message.conversationId) await this.fail(matches[0][0],matches[0][1]);
      } else {
        const c=p.conversationId as string, key=c+"/"+frame.requestId;
        // An ACK only confirms a send issued by this application; retry reloads
        // the durable intent after restart. Realtime/Sync own other deliveries.
        if(!this.known.has(key)) return;
        await this.repository.committedAck(frame.requestId,p as unknown as Committed); this.clear(c,frame.requestId); await this.refresh(); this.delivered(c,p.seq as bigint);
      }
    }
  }
  async mergeMessages(messages:ServerMessage[], active:()=>boolean=()=>true, failBeforeAdvance=false): Promise<void> {
    return this.serial(async()=>{if(this.retired || !active()) return; await this.repository.syncMessages(messages,failBeforeAdvance); for(const m of messages) this.clear(m.conversationId,m.requestId); await this.refresh();});
  }
  async mergeUserPage(page:UserPage,expectedCursor:string,active:()=>boolean,failBeforeAdvance=false):Promise<void> {
    return this.serial(async()=>{if(this.retired || !active()) return; await this.repository.userPage(page,expectedCursor,failBeforeAdvance);});
  }

}

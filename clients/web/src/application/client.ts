import {GroupHttp,GroupFailure} from '../../../shared/protocol-sdk/src/group/http.js';
import {start,targets,type MemberRow} from '../../../shared/protocol-sdk/src/group/wire.js';
import {WireFailure,decode,envelope,object,uuid,content} from '../../../shared/protocol-sdk/src/send/wire.js';
import {SyncHttp} from '../../../shared/protocol-sdk/src/sync/http.js';
import {SyncFailure} from '../../../shared/protocol-sdk/src/sync/wire.js';
import type {Committed,RealtimeMessage} from '../../../shared/protocol-sdk/src/storage/models.js';
import {Http,auth,user,friends,ApiFailure} from './http.js';
import type {User,Friend,Session} from './http.js';
import {MemoryRepository} from './repository.js';
export type Connection = 'idle'|'ready'|'connecting'|'failed'|'protocol_error'|'offline';
export interface View {groups:MemberRow[];confirmedGroups:string[];groupReadBusy:boolean;groupReadError:string;groupSuccessRevision:number;groupBusy:boolean;groupError:string;groupStatus:string;session:boolean;authBusy:boolean;notice:string;connection:Connection;sync:string;user?:User;friends:Friend[];friendsBusy:boolean;friendsError:string;profileBusy:boolean;profileError:string;searchBusy:boolean;searchError:string;searchResults:User[];selected:string;revision:number}
export class WebClient {
  readonly repository=new MemoryRepository();
  private state:View={groups:[],confirmedGroups:[],groupReadBusy:false,groupReadError:'',groupSuccessRevision:0,groupBusy:false,groupError:'',groupStatus:'',session:false,authBusy:false,notice:'',connection:'idle',sync:'',friends:[],friendsBusy:false,friendsError:'',profileBusy:false,profileError:'',searchBusy:false,searchError:'',searchResults:[],selected:'',revision:0};
  private listeners=new Set<()=>void>();private session?:Session;private generation=0;private abort=new AbortController();private socket?:WebSocket;private friendRevision=0;private userCursor="0";private userSyncing=false;private userPoll?:ReturnType<typeof setInterval>;private reconnectTimer?:ReturnType<typeof setTimeout>;private refreshTimer?:ReturnType<typeof setTimeout>;private pending=new Map<string,{conversation:string;timer:ReturnType<typeof setTimeout>}>();private opened=new Set<string>();private syncing=new Map<string,{again:boolean}>();private bind='';private device=crypto.randomUUID();private refreshing?:Promise<void>;
  readonly http:Http;
  constructor(origin:string,private fetcher:typeof fetch=(input,init)=>fetch(input,init),private socketFactory:(url:string)=>WebSocket=url=>new WebSocket(url),private timeout=10000){this.http=new Http(origin,fetcher);}
  view=()=>this.state;
  subscribe=(f:()=>void)=>{this.listeners.add(f);return()=>{this.listeners.delete(f);};};
  private publish(p:Partial<View>={}){this.state={...this.state,...p,revision:this.state.revision+1};for(const f of this.listeners)f();}
  private metadata(){return {clientType:'WEB',deviceId:this.device,clientVersion:'0.1.0',protocolVersion:'1'};}
  private alive(g:number){return g===this.generation;}
  private clear(notice:string){this.generation++;this.groupScanning=undefined;this.groupDirty=false;this.groupOperation=undefined;this.waitingGroupFrames=[];this.abort.abort();this.abort=new AbortController();clearTimeout(this.reconnectTimer);clearTimeout(this.refreshTimer);clearInterval(this.userPoll);this.userPoll=undefined;this.userCursor="0";this.userSyncing=false;this.friendRevision++;for(const p of this.pending.values())clearTimeout(p.timer);this.pending.clear();this.opened.clear();this.syncing.clear();this.socket?.close();this.socket=undefined;this.session=undefined;this.repository.reset();this.state={groups:[],confirmedGroups:[],groupReadBusy:false,groupReadError:'',groupSuccessRevision:0,groupBusy:false,groupError:'',groupStatus:'',session:false,authBusy:false,notice,connection:'idle',sync:'',friends:[],friendsBusy:false,friendsError:'',profileBusy:false,profileError:'',searchBusy:false,searchError:'',searchResults:[],selected:'',revision:this.state.revision};this.publish();}
  private error(e:unknown,g:number){if(!(e instanceof ApiFailure || e instanceof SyncFailure || e instanceof WireFailure || e instanceof GroupFailure))throw e;if(!this.alive(g))return;if(e instanceof ApiFailure&&e.status===401||e instanceof SyncFailure&&e.kind==='authentication'||e instanceof GroupFailure&&e.kind==='authentication')this.clear('会话已过期，请重新登录。');}
  async login(username:string,password:string){this.clear('');const g=this.generation;this.publish({authBusy:true});try {const s=auth(await this.http.request('/v1/auth/login','POST',{...this.metadata(),username,password},undefined,this.abort.signal));if(!this.alive(g))return;this.session=s;this.publish({session:true,authBusy:false,notice:'已登录 · 消息仅保留在当前页面内存'});this.connected();void this.loadFriends();void this.loadProfile();}catch(e){this.error(e,g);if(this.alive(g))this.publish({authBusy:false,notice:e instanceof ApiFailure&&e.status===401?'账号或密码不正确。':'登录失败，请检查网络后重试。'});}}
  async refresh(){if(this.refreshing)return this.refreshing;const g=this.generation;this.publish({authBusy:true,notice:'正在刷新会话…'});this.refreshing=(async()=>{try {const s=auth(await this.http.request('/v1/auth/refresh/web','POST',this.metadata(),undefined,this.abort.signal));if(!this.alive(g))return;if(this.session&&(s.userId!==this.session.userId||s.sessionId!==this.session.sessionId||s.sessionEpoch!==this.session.sessionEpoch)){this.clear('会话已被替换，请重新登录。');return;}this.session=s;this.publish({session:true,authBusy:false,notice:'会话已刷新'});this.socket?.close();this.connected();void this.loadFriends();void this.loadProfile();}catch(e){this.error(e,g);if(this.alive(g))this.publish({authBusy:false,notice:'会话刷新失败，请重试或重新登录。'});}finally{this.refreshing=undefined;}})();return this.refreshing;}
  async logout(){const s=this.session,g=this.generation;const signal=this.abort.signal;this.publish({authBusy:true});try {if(s)await this.http.request('/v1/auth/logout','POST',undefined,s.accessToken,signal);if(this.alive(g))this.clear('已退出登录。');}catch(e){if(!(e instanceof ApiFailure || e instanceof SyncFailure || e instanceof WireFailure || e instanceof GroupFailure))throw e;if(this.alive(g)){this.clear('本页已退出，但服务端撤销未确认；请使用恢复会话再重试退出。');}}}
  async loadProfile(){const s=this.session,g=this.generation;if(!s)return;this.publish({profileBusy:true,profileError:''});try{const p=object(await this.http.request('/v1/users/me','GET',undefined,s.accessToken,this.abort.signal),['user']),u=user(p.user);if(u.userId!==s.userId)throw new WireFailure();if(this.alive(g))this.publish({user:u,profileBusy:false});}catch(e){this.error(e,g);if(this.alive(g))this.publish({profileBusy:false,profileError:'个人资料加载失败，可重试。'});}}
  async loadFriends(){const revision=++this.friendRevision;const s=this.session,g=this.generation;if(!s)return;this.publish({friendsBusy:true,friendsError:''});try{const list=friends(await this.http.request('/v1/friends','GET',undefined,s.accessToken,this.abort.signal));if(list.some(f=>f.user.userId===s.userId))throw new WireFailure();if(this.alive(g)&&revision===this.friendRevision)this.publish({friends:list,friendsBusy:false});}catch(e){this.error(e,g);if(this.alive(g)&&revision===this.friendRevision)this.publish({friendsBusy:false,friendsError:'好友加载失败，可重试。'});}}
  async search(username:string){const s=this.session,g=this.generation;if(!s)return;this.publish({searchBusy:true,searchError:'',searchResults:[]});try{const p=object(await this.http.request('/v1/users/search?username='+encodeURIComponent(username),'GET',undefined,s.accessToken,this.abort.signal),['users']);if(!Array.isArray(p.users)||p.users.length>1)throw new WireFailure();const users=p.users.map(user);if(this.alive(g))this.publish({searchBusy:false,searchResults:users});}catch(e){this.error(e,g);if(this.alive(g))this.publish({searchBusy:false,searchError:'搜索失败，请检查用户名后重试。'});}}
  async addFriend(id:string){const s=this.session,g=this.generation;if(!s)return;this.publish({searchBusy:true,searchError:''});try{const p=object(await this.http.request('/v1/friends/'+uuid(id),'PUT',undefined,s.accessToken,this.abort.signal),['friendshipId','normalizedPair','directConversationId','memberUserIds','created']);uuid(p.friendshipId);const pair=object(p.normalizedPair,['lowUserId','highUserId']);if(!Array.isArray(p.memberUserIds)||p.memberUserIds.length!==2||new Set(p.memberUserIds).size!==2||!p.memberUserIds.includes(s.userId)||!p.memberUserIds.includes(id)||uuid(pair.lowUserId)!==[s.userId,id].sort()[0]||uuid(pair.highUserId)!==[s.userId,id].sort()[1]||typeof p.created!=='boolean')throw new WireFailure();const c=uuid(p.directConversationId);if(!this.alive(g))return;await this.loadFriends();if(this.alive(g))this.publish({searchBusy:false,notice:'好友已添加，唯一私聊已建立',selected:c});}catch(e){this.error(e,g);if(this.alive(g))this.publish({searchBusy:false,searchError:'添加好友失败，请重试。'});}}
  open(c:string){if(!this.authorized(c))return;this.opened.add(c);this.publish({selected:c,sync:this.repository.hasBaseline(c)?'':'仅接收本页实时消息 · 不补历史'});void this.sync(c);}
  send(text:string){const s=this.session,c=this.state.selected;if(!s||!c||!this.authorized(c))return;const m={conversationId:c,requestId:crypto.randomUUID(),senderId:s.userId,content:content({kind:'TEXT',text})};this.repository.begin(m);this.transmit(m.conversationId,m.requestId);return m.requestId;}
  retry(c:string,r:string){const s=this.session,row=this.repository.snapshot(c).find(v=>v.requestId===r);if(!s||!row||row.state!=='FAILED'||row.senderId!==s.userId)return;this.repository.begin(row);this.transmit(c,r);}
  private transmit(c:string,r:string){const m=this.repository.snapshot(c).find(v=>v.requestId===r);if(!m)return;this.opened.add(c);this.publish();if(this.state.connection!=='ready'||!this.socket){this.repository.fail(c,r);this.publish();return;}try {this.socket.send(envelope('message.send',r,{conversationId:c,content:m.content}));const g=this.generation;const timer=setTimeout(()=>{if(this.alive(g)){this.pending.delete(r);this.repository.fail(c,r);this.publish();void this.sync(c);}},this.timeout);this.pending.set(r,{conversation:c,timer});}catch(error){if(!(error instanceof DOMException))throw error;this.repository.fail(c,r);this.publish();}}
  reconnect(){if(!this.session)return;clearTimeout(this.reconnectTimer);this.socket?.close();this.connected();}
  private connected(){const s=this.session,g=this.generation;if(!s)return;clearTimeout(this.refreshTimer);const wait=Math.max(1,s.expires-Date.now()-30000);this.refreshTimer=setTimeout(()=>void this.refresh(),wait);const url=this.http.origin.replace('https:','wss:')+'/v1/ws';let socket:WebSocket;try{socket=this.socketFactory(url);}catch(error){if(!(error instanceof DOMException))throw error;this.publish({connection:'failed'});return;}this.socket=socket;this.bind=crypto.randomUUID();const bind=this.bind;this.publish({connection:'connecting'});const current=()=>this.alive(g)&&this.socket===socket;
    const authTimer=setTimeout(()=>{if(current())socket.close();},10000);
    socket.onopen=()=>{if(current())socket.send(envelope('auth.bind',bind,{accessToken:s.accessToken}));};
    socket.onmessage=e=>{if(!current()||typeof e.data!=='string')return;try{const f=decode(e.data),p=f.payload;if(f.type==='auth.ack'){clearTimeout(authTimer);if(f.requestId!==bind)throw new WireFailure();if(p.status==='rejected'){const code=(p.error as {code:string}).code;if(code==='AUTH_TOKEN_EXPIRED'){void this.refresh();return;}this.clear('会话已失效，请重新登录。');return;}if(p.userId!==s.userId||p.sessionId!==s.sessionId||p.clientType!=='WEB'||p.sessionEpoch!==s.sessionEpoch)throw new WireFailure();this.publish({connection:'ready'});void this.syncFriends();void this.refreshGroups();if(!this.userPoll)this.userPoll=setInterval(()=>{if(this.state.connection==='ready'){void this.syncFriends();void this.refreshGroups();}},10000);for(const c of this.opened)void this.sync(c);}
      else if(f.type==='ping')socket.send(envelope('pong',f.requestId,{}));
      else if(f.type==='session.revoked'){if(p.sessionId===s.sessionId)this.clear('会话已过期或在其他网页被替换，请重新登录。');}
      else if(this.state.connection==='ready'&&f.type==='message.ack'){
        const pending=this.pending.get(f.requestId);
        if(p.status==='committed'){
          if(pending&&p.conversationId!==pending.conversation)throw new WireFailure();
          // Attempt timeout does not erase the logical send stored in page memory.
          const c=p.conversationId as string,row=this.repository.snapshot(c).find(v=>v.requestId===f.requestId&&v.senderId===s.userId);
          if(!row||!this.authorized(c))return;
          this.repository.ack(f.requestId,p as unknown as Committed);
        }else {if(!pending)return;this.repository.fail(pending.conversation,f.requestId);}
        if(pending)clearTimeout(pending.timer);this.pending.delete(f.requestId);this.publish();
        if(p.status==='committed'&&this.opened.has(p.conversationId as string))void this.sync(p.conversationId as string);
      }
      else if(this.state.connection==='ready'&&f.type==='message.created'){const c=p.conversationId as string;if(!this.authorized(c)){this.waitingGroupFrames.push({requestId:f.requestId,message:p as unknown as RealtimeMessage});void this.refreshGroups();return;}this.repository.realtime(f.requestId,p as unknown as RealtimeMessage);const pending=this.pending.get(f.requestId);if(pending&&pending.conversation===c){clearTimeout(pending.timer);this.pending.delete(f.requestId);}this.publish();if(this.opened.has(c))void this.sync(c);}
    }catch(error){if(!(error instanceof WireFailure))throw error;socket.close();this.publish({connection:'protocol_error',sync:'无效响应未改变已确认消息'});}};
    socket.onclose=()=>{clearTimeout(authTimer);if(!current())return;for(const [r,v] of this.pending){clearTimeout(v.timer);this.repository.fail(v.conversation,r);}this.pending.clear();this.publish({connection:'offline'});this.reconnectTimer=setTimeout(()=>{if(current())this.connected();},2000);};socket.onerror=()=>{if(current())this.publish({connection:'failed'});};
  }
  private async syncFriends(){
    const s=this.session,g=this.generation;if(!s||this.userSyncing)return;
    this.userSyncing=true;
    try{const http=new SyncHttp(this.http.origin,s,this.fetcher);
      for(;;){const cursor=this.userCursor,page=await http.user(cursor,this.abort.signal);if(!this.alive(g))return;
        // Consume metadata by re-reading the canonical friend projection; no history pull.
        if(page.events.length){void this.refreshGroups();const revision=++this.friendRevision;const list=friends(await this.http.request('/v1/friends','GET',undefined,s.accessToken,this.abort.signal));if(!this.alive(g)||revision!==this.friendRevision)return;
          if(list.some(f=>f.user.userId===s.userId))throw new WireFailure();
          this.publish({friends:list,friendsBusy:false,friendsError:''});
        }
        this.userCursor=page.nextCursor;if(!page.hasMore)break;
      }
    }catch(e){this.error(e,g);if(this.alive(g))this.publish({friendsError:'好友同步失败，可重试或重连。'});}
    finally{if(this.alive(g))this.userSyncing=false;}
  }
  async sync(c:string){
    const s=this.session,g=this.generation;if(!s||!this.repository.hasBaseline(c)||!this.authorized(c))return;
    const active=this.syncing.get(c);if(active){active.again=true;return;}
    const job={again:false};this.syncing.set(c,job);this.publish({sync:'正在补齐本页在线消息…'});
    try{
      const http=new SyncHttp(this.http.origin,s,this.fetcher);let more=true;
      while(more&&this.alive(g)){
        job.again=false;const after=this.repository.after(c);
        const page=await http.conversation(c,after,this.abort.signal);if(!this.alive(g))return;
        this.repository.page(c,after,page.messages);
        const prefix=this.repository.after(c),gap=this.repository.snapshot(c).some(m=>m.seq!==undefined&&m.seq>prefix);
        // A realtime frame may supersede the window while this page is in flight.
        // Re-read from the committed live prefix, never from initial history.
        more=page.hasMore||job.again||prefix<after;
        if(!more&&gap)throw new SyncFailure("protocol");
        this.publish();
      }
      if(this.alive(g))this.publish({sync:'本页在线消息已同步 · 不补历史'});
    }catch(e){this.error(e,g);if(this.alive(g))this.publish({sync:'同步失败，重连或重新打开会话重试'});}
    finally{if(this.alive(g))this.syncing.delete(c);}
  }
  private groupOperation?:Readonly<{account:string;requestId:string;targets:readonly string[];conversation?:string}>;
  private waitingGroupFrames:{requestId:string;message:RealtimeMessage}[]=[];
  private groupScanning?:Promise<boolean>;private groupDirty=false;
  private authorized(c:string){return this.state.friends.some(f=>f.directConversationId===c)||this.state.groups.some(r=>r.conversationId===c)||this.state.confirmedGroups.includes(c);}
  async createGroup(ids:string[],conversation?:string){
    const s=this.session;if(!s||this.state.groupBusy||this.groupOperation)return;
    this.groupOperation=Object.freeze({account:s.userId,requestId:crypto.randomUUID(),targets:Object.freeze(targets(ids,s.userId)),conversation});
    await this.retryGroup();
  }
  async retryGroup(){
    const s=this.session,g=this.generation,op=this.groupOperation;if(!s||!op||op.account!==s.userId||this.state.groupBusy)return;
    this.publish({groupBusy:true,groupError:'',groupStatus:'loading'});
    let answer;
    try{answer=await new GroupHttp(this.http.origin,s.userId,s.accessToken,this.fetcher).mutate(op.requestId,op.targets,this.abort.signal,op.conversation);
    }catch(error){this.error(error,g);if(!this.alive(g))return;
      const rejected=error instanceof GroupFailure&&error.kind==='rejected';if(rejected)this.groupOperation=undefined;
      this.publish({groupBusy:false,groupStatus:rejected?'rejected':'unconfirmed',groupError:error instanceof GroupFailure?error.code||error.kind:'protocol'});
      return;
    }
    if(!this.alive(g))return;
    // Only a validated committed response grants this temporary identity. It is
    // not a member snapshot or history baseline, and is cleared with the account.
    if(!this.state.groups.some(r=>r.conversationId===answer.conversationId))this.publish({confirmedGroups:[...new Set([...this.state.confirmedGroups,answer.conversationId])]});
    this.groupOperation=undefined;this.open(answer.conversationId);
    this.publish({groupBusy:false,groupStatus:'success',groupSuccessRevision:this.state.groupSuccessRevision+1});
    // A failed/held read must not undo confirmation or retain a mutation retry.
    // Awaiting still propagates unknown read failures to the operation's caller.
    await this.refreshGroups();
  }
  async refreshGroups():Promise<boolean>{
    const s=this.session,g=this.generation;if(!s)return false;
    this.groupDirty=true;if(this.groupScanning)return this.groupScanning;
    this.publish({groupReadBusy:true,groupReadError:''});
    this.groupScanning=(async()=>{
    try{const http=new GroupHttp(this.http.origin,s.userId,s.accessToken,this.fetcher);
      while(this.groupDirty&&this.alive(g)){this.groupDirty=false;let after={...start};const rows=new Map<string,MemberRow>();let last:MemberRow|undefined;
        for(;;){const p=await http.members(crypto.randomUUID(),this.abort.signal,after);if(!this.alive(g))return false;
          for(const r of p.items){if(last?.conversationId===r.conversationId&&(last.kind!==r.kind||last.createdBy!==r.createdBy||last.createdAt!==r.createdAt))throw new WireFailure();rows.set(r.conversationId+'/'+r.member.user.userId,r);last=r;}
          if(!p.hasMore)break;after=p.next;
        }
        const groups=[...rows.values()].filter(r=>r.kind==='GROUP');
        this.publish({groups,confirmedGroups:this.state.confirmedGroups.filter(c=>!groups.some(r=>r.conversationId===c)),groupReadError:''});
        const waiting=this.waitingGroupFrames;this.waitingGroupFrames=[];for(const frame of waiting){if(this.authorized(frame.message.conversationId))this.repository.realtime(frame.requestId,frame.message);}if(waiting.length)this.publish();
      }
      return this.alive(g);
    }catch(error){this.error(error,g);if(this.alive(g))this.publish({groupReadError:error instanceof GroupFailure?error.code||error.kind:'protocol'});return false;}
    finally{if(this.alive(g)){this.groupScanning=undefined;this.publish({groupReadBusy:false});}}
    })();return this.groupScanning;
  }
  dispose(){this.clear('');this.listeners.clear();}
}

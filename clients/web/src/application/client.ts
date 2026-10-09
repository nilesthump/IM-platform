import {decode,envelope,object,uuid,content} from '../../../shared/protocol-sdk/src/send/wire.js';
import {SyncHttp} from '../../../shared/protocol-sdk/src/sync/http.js';
import {SyncFailure} from '../../../shared/protocol-sdk/src/sync/wire.js';
import type {Committed,RealtimeMessage} from '../../../shared/protocol-sdk/src/storage/models.js';
import {Http,auth,user,friends,ApiFailure} from './http.js';
import type {User,Friend,Session} from './http.js';
import {MemoryRepository} from './repository.js';
export interface View {session:boolean;authBusy:boolean;notice:string;connection:string;sync:string;user?:User;friends:Friend[];friendsBusy:boolean;friendsError:string;profileBusy:boolean;profileError:string;searchBusy:boolean;searchError:string;searchResults:User[];selected:string;revision:number}
export class WebClient {
  readonly repository=new MemoryRepository();
  private state:View={session:false,authBusy:false,notice:'',connection:'未连接',sync:'',friends:[],friendsBusy:false,friendsError:'',profileBusy:false,profileError:'',searchBusy:false,searchError:'',searchResults:[],selected:'',revision:0};
  private listeners=new Set<()=>void>();private session?:Session;private generation=0;private abort=new AbortController();private socket?:WebSocket;private reconnectTimer?:ReturnType<typeof setTimeout>;private refreshTimer?:ReturnType<typeof setTimeout>;private pending=new Map<string,{conversation:string;timer:ReturnType<typeof setTimeout>}>();private opened=new Set<string>();private syncing=new Map<string,{again:boolean}>();private bind='';private device=crypto.randomUUID();private refreshing?:Promise<void>;
  readonly http:Http;
  constructor(origin:string,private fetcher:typeof fetch=(input,init)=>fetch(input,init),private socketFactory:(url:string)=>WebSocket=url=>new WebSocket(url),private timeout=10000){this.http=new Http(origin,fetcher);}
  view=()=>this.state;
  subscribe=(f:()=>void)=>{this.listeners.add(f);return()=>{this.listeners.delete(f);};};
  private publish(p:Partial<View>={}){this.state={...this.state,...p,revision:this.state.revision+1};for(const f of this.listeners)f();}
  private metadata(){return {clientType:'WEB',deviceId:this.device,clientVersion:'0.1.0',protocolVersion:'1'};}
  private alive(g:number){return g===this.generation;}
  private clear(notice:string){this.generation++;this.abort.abort();this.abort=new AbortController();clearTimeout(this.reconnectTimer);clearTimeout(this.refreshTimer);for(const p of this.pending.values())clearTimeout(p.timer);this.pending.clear();this.opened.clear();this.syncing.clear();this.socket?.close();this.socket=undefined;this.session=undefined;this.repository.reset();this.state={session:false,authBusy:false,notice,connection:'未连接',sync:'',friends:[],friendsBusy:false,friendsError:'',profileBusy:false,profileError:'',searchBusy:false,searchError:'',searchResults:[],selected:'',revision:this.state.revision};this.publish();}
  private error(e:unknown,g:number){if(!this.alive(g))return;if(e instanceof ApiFailure&&e.status===401||e instanceof SyncFailure&&e.kind==='authentication')this.clear('会话已过期，请重新登录。');}
  async login(username:string,password:string){this.clear('');const g=this.generation;this.publish({authBusy:true});try {const s=auth(await this.http.request('/v1/auth/login','POST',{...this.metadata(),username,password},undefined,this.abort.signal));if(!this.alive(g))return;this.session=s;this.publish({session:true,authBusy:false,notice:'已登录 · 消息仅保留在当前页面内存'});this.connected();void this.loadFriends();void this.loadProfile();}catch(e){if(this.alive(g))this.publish({authBusy:false,notice:e instanceof ApiFailure&&e.status===401?'账号或密码不正确。':'登录失败，请检查网络后重试。'});}}
  async refresh(){if(this.refreshing)return this.refreshing;const g=this.generation;this.publish({authBusy:true,notice:'正在刷新会话…'});this.refreshing=(async()=>{try {const s=auth(await this.http.request('/v1/auth/refresh/web','POST',this.metadata(),undefined,this.abort.signal));if(!this.alive(g))return;if(this.session&&(s.userId!==this.session.userId||s.sessionId!==this.session.sessionId||s.sessionEpoch!==this.session.sessionEpoch)){this.clear('会话已被替换，请重新登录。');return;}this.session=s;this.publish({session:true,authBusy:false,notice:'会话已刷新'});this.socket?.close();this.connected();void this.loadFriends();void this.loadProfile();}catch(e){if(this.alive(g)){this.error(e,g);if(this.alive(g))this.publish({authBusy:false,notice:'会话刷新失败，请重试或重新登录。'});}}finally{this.refreshing=undefined;}})();return this.refreshing;}
  async logout(){const s=this.session,g=this.generation;const signal=this.abort.signal;this.publish({authBusy:true});try {if(s)await this.http.request('/v1/auth/logout','POST',undefined,s.accessToken,signal);if(this.alive(g))this.clear('已退出登录。');}catch{if(this.alive(g)){this.clear('本页已退出，但服务端撤销未确认；请使用恢复会话再重试退出。');}}}
  async loadProfile(){const s=this.session,g=this.generation;if(!s)return;this.publish({profileBusy:true,profileError:''});try{const p=object(await this.http.request('/v1/users/me','GET',undefined,s.accessToken,this.abort.signal),['user']),u=user(p.user);if(u.userId!==s.userId)throw new Error('Account mismatch');if(this.alive(g))this.publish({user:u,profileBusy:false});}catch(e){this.error(e,g);if(this.alive(g))this.publish({profileBusy:false,profileError:'个人资料加载失败，可重试。'});}}
  async loadFriends(){const s=this.session,g=this.generation;if(!s)return;this.publish({friendsBusy:true,friendsError:''});try{const list=friends(await this.http.request('/v1/friends','GET',undefined,s.accessToken,this.abort.signal));if(list.some(f=>f.user.userId===s.userId))throw new Error('Invalid friend');if(this.alive(g))this.publish({friends:list,friendsBusy:false});}catch(e){this.error(e,g);if(this.alive(g))this.publish({friendsBusy:false,friendsError:'好友加载失败，可重试。'});}}
  async search(username:string){const s=this.session,g=this.generation;if(!s)return;this.publish({searchBusy:true,searchError:'',searchResults:[]});try{const p=object(await this.http.request('/v1/users/search?username='+encodeURIComponent(username),'GET',undefined,s.accessToken,this.abort.signal),['users']);if(!Array.isArray(p.users)||p.users.length>1)throw new Error('Invalid search');const users=p.users.map(user);if(this.alive(g))this.publish({searchBusy:false,searchResults:users});}catch(e){this.error(e,g);if(this.alive(g))this.publish({searchBusy:false,searchError:'搜索失败，请检查用户名后重试。'});}}
  async addFriend(id:string){const s=this.session,g=this.generation;if(!s)return;this.publish({searchBusy:true,searchError:''});try{const p=object(await this.http.request('/v1/friends/'+uuid(id),'PUT',undefined,s.accessToken,this.abort.signal),['friendshipId','normalizedPair','directConversationId','memberUserIds','created']);uuid(p.friendshipId);const pair=object(p.normalizedPair,['lowUserId','highUserId']);if(!Array.isArray(p.memberUserIds)||p.memberUserIds.length!==2||new Set(p.memberUserIds).size!==2||!p.memberUserIds.includes(s.userId)||!p.memberUserIds.includes(id)||uuid(pair.lowUserId)!==[s.userId,id].sort()[0]||uuid(pair.highUserId)!==[s.userId,id].sort()[1]||typeof p.created!=='boolean')throw new Error('Invalid relationship');const c=uuid(p.directConversationId);if(!this.alive(g))return;await this.loadFriends();if(this.alive(g))this.publish({searchBusy:false,notice:'好友已添加，唯一私聊已建立',selected:c});}catch(e){this.error(e,g);if(this.alive(g))this.publish({searchBusy:false,searchError:'添加好友失败，请重试。'});}}
  open(c:string){if(!this.state.friends.some(f=>f.directConversationId===c))return;this.opened.add(c);this.publish({selected:c,sync:this.repository.hasBaseline(c)?'':'仅接收本页实时消息 · 不补历史'});void this.sync(c);}
  send(text:string){const s=this.session,c=this.state.selected;if(!s||!c||!this.state.friends.some(f=>f.directConversationId===c))return;const m={conversationId:c,requestId:crypto.randomUUID(),senderId:s.userId,content:content({kind:'TEXT',text})};this.repository.begin(m);this.transmit(m.conversationId,m.requestId);return m.requestId;}
  retry(c:string,r:string){const s=this.session,row=this.repository.snapshot(c).find(v=>v.requestId===r);if(!s||!row||row.state!=='FAILED'||row.senderId!==s.userId)return;this.repository.begin(row);this.transmit(c,r);}
  private transmit(c:string,r:string){const m=this.repository.snapshot(c).find(v=>v.requestId===r);if(!m)return;this.opened.add(c);this.publish();if(this.state.connection!=='在线'||!this.socket){this.repository.fail(c,r);this.publish();return;}try {this.socket.send(envelope('message.send',r,{conversationId:c,content:m.content}));const g=this.generation;const timer=setTimeout(()=>{if(this.alive(g)){this.pending.delete(r);this.repository.fail(c,r);this.publish();void this.sync(c);}},this.timeout);this.pending.set(r,{conversation:c,timer});}catch{this.repository.fail(c,r);this.publish();}}
  reconnect(){if(!this.session)return;clearTimeout(this.reconnectTimer);this.socket?.close();this.connected();}
  private connected(){const s=this.session,g=this.generation;if(!s)return;clearTimeout(this.refreshTimer);const wait=Math.max(1,s.expires-Date.now()-30000);this.refreshTimer=setTimeout(()=>void this.refresh(),wait);const url=this.http.origin.replace('https:','wss:')+'/v1/ws';let socket:WebSocket;try{socket=this.socketFactory(url);}catch{this.publish({connection:'连接失败'});return;}this.socket=socket;this.bind=crypto.randomUUID();const bind=this.bind;this.publish({connection:'正在连接'});const current=()=>this.alive(g)&&this.socket===socket;
    const authTimer=setTimeout(()=>{if(current())socket.close();},10000);
    socket.onopen=()=>{if(current())socket.send(envelope('auth.bind',bind,{accessToken:s.accessToken}));};
    socket.onmessage=e=>{if(!current()||typeof e.data!=='string')return;try{const f=decode(e.data),p=f.payload;if(f.type==='auth.ack'){clearTimeout(authTimer);if(f.requestId!==bind)throw new Error('Bind correlation');if(p.status==='rejected'){const code=(p.error as {code:string}).code;if(code==='AUTH_TOKEN_EXPIRED'){void this.refresh();return;}this.clear('会话已失效，请重新登录。');return;}if(p.userId!==s.userId||p.sessionId!==s.sessionId||p.clientType!=='WEB'||p.sessionEpoch!==s.sessionEpoch)throw new Error('Session mismatch');this.publish({connection:'在线'});for(const c of this.opened)void this.sync(c);}
      else if(f.type==='ping')socket.send(envelope('pong',f.requestId,{}));
      else if(f.type==='session.revoked'){if(p.sessionId===s.sessionId)this.clear('会话已过期或在其他网页被替换，请重新登录。');}
      else if(this.state.connection==='在线'&&f.type==='message.ack'){
        const pending=this.pending.get(f.requestId);
        if(p.status==='committed'){
          if(pending&&p.conversationId!==pending.conversation)throw new Error('Wrong conversation');
          // Attempt timeout does not erase the logical send stored in page memory.
          const c=p.conversationId as string,row=this.repository.snapshot(c).find(v=>v.requestId===f.requestId&&v.senderId===s.userId);
          if(!row||!this.state.friends.some(v=>v.directConversationId===c))return;
          this.repository.ack(f.requestId,p as unknown as Committed);
        }else {if(!pending)return;this.repository.fail(pending.conversation,f.requestId);}
        if(pending)clearTimeout(pending.timer);this.pending.delete(f.requestId);this.publish();
      }
      else if(this.state.connection==='在线'&&f.type==='message.created'){const c=p.conversationId as string;if(!this.state.friends.some(v=>v.directConversationId===c))return;this.repository.realtime(f.requestId,p as unknown as RealtimeMessage);const pending=this.pending.get(f.requestId);if(pending&&pending.conversation===c){clearTimeout(pending.timer);this.pending.delete(f.requestId);}this.publish();if(this.opened.has(c))void this.sync(c);}
    }catch{socket.close();this.publish({connection:'协议错误',sync:'无效响应未改变已确认消息'});}};
    socket.onclose=()=>{clearTimeout(authTimer);if(!current())return;for(const [r,v] of this.pending){clearTimeout(v.timer);this.repository.fail(v.conversation,r);}this.pending.clear();this.publish({connection:'连接已断开'});this.reconnectTimer=setTimeout(()=>{if(current())this.connected();},2000);};socket.onerror=()=>{if(current())this.publish({connection:'连接失败'});};
  }
  async sync(c:string){
    const s=this.session,g=this.generation;if(!s||!this.repository.hasBaseline(c)||!this.state.friends.some(f=>f.directConversationId===c))return;
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
        if(!more&&gap)throw new Error('Terminal Sync did not fill the known live gap');
        this.publish();
      }
      if(this.alive(g))this.publish({sync:'本页在线消息已同步 · 不补历史'});
    }catch(e){this.error(e,g);if(this.alive(g))this.publish({sync:'同步失败，重连或重新打开会话重试'});}
    finally{if(this.alive(g))this.syncing.delete(c);}
  }
  dispose(){this.clear('');this.listeners.clear();}
}

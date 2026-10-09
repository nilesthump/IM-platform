import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const {WebClient}=await import(pathToFileURL(process.env.WEB_BUILD_DIR+'/web/src/application/client.js'));
const {Http}=await import(pathToFileURL(process.env.WEB_BUILD_DIR+'/web/src/application/http.js'));
const id=n=>'10000000-0000-4000-8000-'+String(n).padStart(12,'0'),c=id(3),u=id(1),peer=id(2),sid=id(4);
const auth={session:{userId:u,sessionId:sid,clientType:'WEB',sessionEpoch:1,status:'ACTIVE'},tokens:{accessToken:'controlled-regression-access',accessTokenExpiresInSeconds:3600,refreshTokenDelivery:'HTTP_ONLY_SECURE_COOKIE'},replacedExistingSession:false};
const json=(p,status=200)=>new Response(JSON.stringify(p),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
const frame=(type,r,p)=>JSON.stringify({protocolVersion:'1.0',type,requestId:r,payload:p});
const message=seq=>({conversationId:c,requestId:id(100+seq),messageId:id(300+seq),senderId:peer,seq,createdAt:'2026-10-09T09:00:00Z',content:{kind:'TEXT',text:'sequence '+seq}});
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
function observe(client,predicate){if(predicate())return Promise.resolve();return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{off();reject(Error('Expected client observation did not occur'));},2000);const off=client.subscribe(()=>{if(predicate()){clearTimeout(timer);off();resolve();}});});}
async function setup(handler,timeout=10000){
 const sockets=[];const api=async(url,options)=>{
  if(url.endsWith('/auth/login'))return json(auth);
  if(url.endsWith('/users/me'))return json({user:{userId:u,username:'alice',displayName:'Alice'}});
  if(url.endsWith('/friends'))return json({friends:[{user:{userId:peer,username:'bob',displayName:'Bob'},friendshipId:id(6),directConversationId:c}]});
  return handler(url,options);
 };
 const factory=()=>{const socket={sent:[],send(raw){this.sent.push(JSON.parse(raw));},close(){this.onclose?.();}};sockets.push(socket);return socket;};
 const client=new WebClient('https://regression.invalid',api,factory,timeout);
 await client.login('alice','controlled-password');await observe(client,()=>client.view().friends.length===1);
 const socket=sockets.at(-1);socket.onopen();const bind=socket.sent.at(-1);
 socket.onmessage({data:frame('auth.ack',bind.requestId,{status:'bound',userId:u,sessionId:sid,clientType:'WEB',sessionEpoch:1})});client.open(c);
 return {client,socket};
}
const created=(socket,seq)=>{const {requestId,...payload}=message(seq);socket.onmessage({data:frame('message.created',requestId,payload)});};
const page=(request,messages,hasMore=false)=>json({syncVersion:'1.0',type:'sync.conversation.page',requestId:request.requestId,conversationId:c,messages,hasMore});
// Timeout must not lose logical correlation. Unknown/wrong conversation/old
// socket cannot confirm it; one late durable ACK does, and SENT stays terminal.
{
 const {client,socket}=await setup(async()=>{throw Error('No initial history pull');},20);
 try{
  const rid=client.send('late confirmation');const failed=()=>client.repository.snapshot(c)[0].state==='FAILED';await observe(client,failed);
  const ack={status:'committed',conversationId:c,messageId:id(800),seq:101,createdAt:'2026-10-09T09:00:00Z'};
  socket.onmessage({data:frame('message.ack',id(999),ack)});assert(failed());
  socket.onmessage({data:frame('message.ack',rid,{...ack,conversationId:id(999)})});assert(failed());
  socket.onmessage({data:frame('message.ack',rid,ack)});assert.equal(client.repository.snapshot(c)[0].state,'SENT');assert.equal(client.repository.snapshot(c)[0].messageId,ack.messageId);
  socket.onmessage({data:frame('message.ack',rid,{status:'rejected',error:{code:'AUTHORIZATION_DENIED',message:'Controlled denial'}})});assert.equal(client.repository.snapshot(c)[0].state,'SENT');
  client.reconnect();socket.onmessage({data:frame('message.created',id(999),{...message(102),content:{kind:'TEXT',text:'stale socket'}})});assert.equal(client.repository.snapshot(c).length,1);
  await client.logout();socket.onmessage({data:frame('message.ack',rid,ack)});assert.equal(client.repository.snapshot(c).length,0);
 }finally{client.dispose();}
}
// Hold terminal page101. Realtime either expands downward99/gap100 or upward
// 103/gap102 while in flight. Superseded request must not be dropped.
for(const late of [99,103]){
 const hold=deferred(),began=deferred(),pulls=[];
 const {client,socket}=await setup(async(url,options)=>{assert(url.endsWith('/sync/conversation'));const request=JSON.parse(options.body);pulls.push(request);
  if(pulls.length===1){began.resolve();return hold.promise.then(()=>page(request,[]));}
  const seqs=late===99?[100,101]:[102,103];return page(request,seqs.filter(v=>v>request.afterSeq).map(message));
 });
 try{
  created(socket,101);await began.promise;assert.equal(pulls[0].afterSeq,101);created(socket,late);assert.equal(client.repository.after(c),late===99?99n:101n);
  const done=observe(client,()=>client.view().sync==='本页在线消息已同步 · 不补历史');hold.resolve();await done;
  assert.deepEqual(pulls.map(v=>v.afterSeq),late===99?[101,99]:[101,101]);assert.equal(client.repository.after(c),late===99?101n:103n);assert.deepEqual(client.repository.snapshot(c).map(v=>Number(v.seq)),late===99?[99,100,101]:[101,102,103]);
 }finally{hold.resolve();client.dispose();}
}
// Legal multi-page response commits each page; malformed later page is atomic
// and must leave both rows/prefix from the prior committed page unchanged.
{
 let mode='bad',calls=[];const {client,socket}=await setup(async(url,options)=>{assert(url.endsWith('/sync/conversation'));const request=JSON.parse(options.body);calls.push(request.afterSeq);
  if(request.afterSeq===101)return page(request,[message(102)],true);
  if(mode==='bad')return page(request,[message(103),{...message(104),messageId:message(102).messageId}]);
  return page(request,[message(103),message(104)]);
 });
 try{created(socket,101);await observe(client,()=>client.view().sync.includes('同步失败'));assert.deepEqual(calls,[101,102]);assert.equal(client.repository.after(c),102n);assert.deepEqual(client.repository.snapshot(c).map(v=>Number(v.seq)),[101,102]);mode='ok';await client.sync(c);assert.equal(client.repository.after(c),104n);assert.deepEqual(calls,[101,102,102]);assert.equal(client.repository.snapshot(c).length,4);}finally{client.dispose();}
}
// A stable terminal response missing a known gap is failure, not a busy loop
// or false success; an explicit retry can recover it without moving over gap.
{
 const hold=deferred(),began=deferred();let calls=0,repair=false;
 const {client,socket}=await setup(async(url,options)=>{assert(url.endsWith('/sync/conversation'));const request=JSON.parse(options.body);calls++;if(calls===1){began.resolve();await hold.promise;}return page(request,repair?[message(102),message(103)]:[]);});
 try{created(socket,101);await began.promise;created(socket,103);const failed=observe(client,()=>client.view().sync.includes('同步失败'));hold.resolve();await failed;assert.equal(calls,2);assert.equal(client.repository.after(c),101n);repair=true;await client.sync(c);assert.equal(client.repository.after(c),103n);}finally{hold.resolve();client.dispose();}
}
// Only logout POST204/null body bypasses JSON; every other JSON endpoint and
// invented successful200 logout are rejected. Genuine failure stays honest.
{
 const signal=new AbortController().signal;
 const http=new Http('https://regression.invalid',async()=>new Response(null,{status:204}));
 assert.equal(await http.request('/v1/auth/logout','POST',undefined,'controlled-access',signal),undefined);
 const streamResponse=bytes=>({status:204,ok:true,redirected:false,body:new ReadableStream({start(controller){if(bytes)controller.enqueue(new Uint8Array([1]));controller.close();}})});
 const empty=new Http('https://regression.invalid',async()=>streamResponse(false));assert.equal(await empty.request('/v1/auth/logout','POST',undefined,'controlled-access',signal),undefined);
 const illegal=new Http('https://regression.invalid',async()=>streamResponse(true));await assert.rejects(()=>illegal.request('/v1/auth/logout','POST',undefined,'controlled-access',signal));
 const broken=new Http('https://regression.invalid',async()=>({status:204,ok:true,redirected:false,body:new ReadableStream({start(controller){controller.error(Error('Controlled read failure'));}})}));await assert.rejects(()=>broken.request('/v1/auth/logout','POST',undefined,'controlled-access',signal));
 await assert.rejects(()=>http.request('/v1/users/me','GET',undefined,'controlled-access',signal));
 const fake=new Http('https://regression.invalid',async()=>json({revoked:true}));await assert.rejects(()=>fake.request('/v1/auth/logout','POST',undefined,'controlled-access',signal));
 for(const success of [true,false]){const {client}=await setup(async url=>{assert(url.endsWith('/auth/logout'));return success?new Response(null,{status:204}):json({requestId:id(999),error:{code:'AUTH_SESSION_REVOKED',message:'Controlled rejection'}},401);});try{await client.logout();assert.equal(client.view().session,false);assert.equal(client.view().notice,success?'已退出登录。':'本页已退出，但服务端撤销未确认；请使用恢复会话再重试退出。');}finally{client.dispose();}}
}
console.log('PASS Web regression: late ACK identity, both terminal-page crossing directions, continued pagination/atomic failed-page rollback, stable missing-gap failure/retry, strict legal logout204 and genuine failure');

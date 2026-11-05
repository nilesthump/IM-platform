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
if(new URL(url).pathname==='/v1/conversations'){assert.equal(options.method,'GET');return json({requestId:new URL(url).searchParams.get('requestId'),items:[],hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});}
  if(url.endsWith('/sync/user')){const b=JSON.parse(options.body);return json({syncVersion:'1.0',type:'sync.user.page',requestId:b.requestId,events:[],nextCursor:b.cursor,hasMore:false});}
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
 const {client,socket}=await setup(async()=>{throw new TypeError('Controlled after-baseline network failure');},20);
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
// Durable ACKs alone can expose a live gap. Both an idle Sync and a held
// terminal response must compensate it without realtime/reconnect/timeout.
for(const held of [false,true]){
 const hold=deferred(),began=deferred(),pulls=[];let second;
 const {client,socket}=await setup(async(url,options)=>{assert(url.endsWith('/sync/conversation'));const request=JSON.parse(options.body);pulls.push(request);
  if(pulls.length===1){began.resolve();if(held)await hold.promise;return page(request,[]);}
  return page(request,[message(102),second]);
 });
 try{
  const ack=(rid,seq,n)=>socket.onmessage({data:frame('message.ack',rid,{status:'committed',conversationId:c,messageId:id(n),seq,createdAt:'2026-10-09T09:00:00Z'})});
  const first=client.send('first ACK');ack(first,101,901);await began.promise;
  if(!held)await observe(client,()=>client.view().sync==='本页在线消息已同步 · 不补历史');
  const rid=client.send('second ACK');second={...message(103),requestId:rid,messageId:id(903),senderId:u,content:{kind:'TEXT',text:'second ACK'}};
  socket.onmessage({data:frame('message.ack',id(999),{status:'committed',conversationId:c,messageId:id(999),seq:103,createdAt:'2026-10-09T09:00:00Z'})});assert.equal(pulls.length,1);
  const done=observe(client,()=>client.repository.after(c)===103n&&client.view().sync==='本页在线消息已同步 · 不补历史');ack(rid,103,903);if(held)hold.resolve();await done;
  assert.deepEqual(pulls.map(v=>v.afterSeq),[101,101]);assert.deepEqual(client.repository.snapshot(c).map(v=>Number(v.seq)),[101,102,103]);
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
// STATE friend projection: late old responses/errors cannot overwrite new
// snapshots; failed canonical projection does not consume the UserSync cursor.
{
 const {SyncHttp}=await import(pathToFileURL(process.env.WEB_BUILD_DIR+'/shared/protocol-sdk/src/sync/http.js'));
 const validWithoutCache=new Http('https://regression.invalid',async()=>new Response(JSON.stringify({user:{userId:u,username:'alice',displayName:'Alice'}}),{headers:{'content-type':'application/json'}}));
 assert.equal((await validWithoutCache.request('/v1/users/me','GET',undefined,'controlled',new AbortController().signal)).user.userId,u);
 for(const fetcher of [async()=>new Response('{}',{headers:{'content-type':'text/plain'}}),async()=>new Response('{broken',{headers:{'content-type':'application/json'}})])await assert.rejects(()=>new Http('https://regression.invalid',fetcher).request('/v1/users/me','GET',undefined,'controlled',new AbortController().signal));
 const sync=new SyncHttp('https://regression.invalid',{userId:u,sessionId:sid,sessionEpoch:1n,accessToken:'controlled'},async(_url,options)=>{const b=JSON.parse(options.body);return new Response(JSON.stringify({syncVersion:'1.0',type:'sync.user.page',requestId:b.requestId,events:[],nextCursor:b.cursor,hasMore:false}),{headers:{'content-type':'application/json'}});});
 await assert.rejects(()=>sync.user('0',new AbortController().signal));
 const list=n=>({friends:[{user:{userId:id(n),username:'peer'+n,displayName:'Peer '+n},friendshipId:id(60+n),directConversationId:id(80+n)}]});
 for(const staleError of [false,true]){
  const old=deferred();let count=0;
  const api=async url=>{if(url.endsWith('/auth/login'))return json(auth);if(url.endsWith('/users/me'))return json({user:{userId:u,username:'alice',displayName:'Alice'}});if(url.endsWith('/friends'))return ++count===1?old.promise:json(list(7));throw Error('Unexpected path');};
  const client=new WebClient('https://regression.invalid',api,()=>({close(){},send(){}}));
  try{await client.login('alice','controlled');await client.loadFriends();assert.equal(client.view().friends[0].user.userId,id(7));old.resolve(staleError?json({requestId:id(999),error:{code:'VALIDATION_FAILED'}},400):json(list(2)));await new Promise(r=>setTimeout(r,0));assert.equal(client.view().friends[0].user.userId,id(7));assert.equal(client.view().friendsError,'');}finally{old.resolve(json(list(2)));client.dispose();}
 }
 {
  let projectionFail=true;const cursors=[];
  const api=async(url,options)=>{if(new URL(url).pathname==='/v1/conversations'){assert.equal(options.method,'GET');return json({requestId:new URL(url).searchParams.get('requestId'),items:[],hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});}if(url.endsWith('/auth/login'))return json(auth);if(url.endsWith('/users/me'))return json({user:{userId:u,username:'alice',displayName:'Alice'}});if(url.endsWith('/friends'))return cursors.length&&projectionFail?json({requestId:id(999),error:{code:'VALIDATION_FAILED'}},400):json(list(cursors.length?7:2));if(url.endsWith('/sync/user')){const b=JSON.parse(options.body);cursors.push(b.cursor);return json({syncVersion:'1.0',type:'sync.user.page',requestId:b.requestId,events:[{eventId:id(30),cursor:'opaque-friend-1',kind:'friend.changed',subjectId:id(7),revision:1}],nextCursor:'opaque-friend-1',hasMore:false});}throw Error('Unexpected path');};
  const client=new WebClient('https://regression.invalid',api,()=>({close(){},send(){}}));
  try{await client.login('alice','controlled');await new Promise(r=>setTimeout(r,0));await client.syncFriends();assert.equal(client.userCursor,'0');assert.equal(client.view().friends[0].user.userId,peer);projectionFail=false;await client.syncFriends();assert.deepEqual(cursors,['0','0']);assert.equal(client.userCursor,'opaque-friend-1');assert.equal(client.view().friends[0].user.userId,id(7));}finally{client.dispose();}
 }
 {
  const old=deferred();let friendsCount=0;
  const client=new WebClient('https://regression.invalid',async url=>{if(url.endsWith('/auth/login'))return json(auth);if(url.endsWith('/users/me'))return json({user:{userId:u,username:'alice',displayName:'Alice'}});if(url.endsWith('/friends'))return ++friendsCount===1?old.promise:json(list(7));if(url.endsWith('/auth/logout'))return new Response(null,{status:204});throw Error('Unexpected path');},()=>({close(){},send(){}}));
  try{await client.login('alice','controlled');await client.logout();await client.login('alice','controlled');await new Promise(r=>setTimeout(r,0));old.resolve(json(list(2)));await new Promise(r=>setTimeout(r,0));assert.equal(client.view().friends[0].user.userId,id(7));}finally{old.resolve(json(list(2)));client.dispose();}
 }
 console.log('PASS STATE real-contract cache alignment, strict Sync cache rejection, late old friend success/error isolation, cursor projection failure retry, prior login generation isolation');
}

// Internal bugs propagate with original identity instead of false network/UI data.
{
 const original=Error('controlled internal Web adapter bug');
 const http=new Http('https://regression.invalid',async()=>{throw original;});
 await assert.rejects(http.request('/v1/users/me','GET',undefined,'controlled',new AbortController().signal),e=>e===original);
 const client=new WebClient('https://regression.invalid',async()=>{throw original;});
 await assert.rejects(client.login('fixture','controlled-only-input'),e=>e===original);
 assert.equal(client.view().session,false);client.dispose();
 const primitive='controlled unexpected primitive';
 const value=new Http('https://regression.invalid',async()=>{throw primitive;});
 await assert.rejects(value.request('/v1/users/me','GET',undefined,'controlled',new AbortController().signal),e=>e===primitive);
}
console.log('PASS unknown Web adapter Error and primitive preserve original failure');

{
 const signal=new AbortController().signal;
 const invalid=new Http('https://regression.invalid',async()=>new Response(new Uint8Array([0xff]),{headers:{'content-type':'application/json'}}));
 await assert.rejects(invalid.request('/v1/users/me','GET',undefined,'controlled',signal),e=>e.code==='INVALID_RESPONSE');
 const streamed=new Http('https://regression.invalid',async()=>new Response(new ReadableStream({start(c){c.error(new TypeError('controlled stream network failure'));}}),{headers:{'content-type':'application/json'}}));
 await assert.rejects(streamed.request('/v1/users/me','GET',undefined,'controlled',signal),e=>e.code==='CONNECTION_UNAVAILABLE');
 const original=Error('controlled retired refresh bug');let reject,started;
 const began=new Promise(r=>{started=r;});const held=new Promise((_,r)=>{reject=r;});
 const {client}=await setup(async url=>{if(url.endsWith('/auth/refresh/web')){started();return held;}if(url.endsWith('/auth/logout'))return new Response(null,{status:204});throw Error('Unexpected controlled route');});
 const refreshing=client.refresh();await began;await client.logout();reject(original);
 await assert.rejects(refreshing,e=>e===original);assert.equal(client.view().session,false);client.dispose();
}
console.log('PASS Web UTF8/read classification and retired refresh unknown-error identity without account publication');

// Execute the real compiled JSX with the existing language lookup; context alone is controlled.
{
 const {readFileSync,writeFileSync}=await import("node:fs"),{createRequire}=await import("node:module"),{resolve}=await import("node:path");
 const root=process.env.WEB_BUILD_DIR,require=createRequire(resolve(root,"../clients/web/package.json")),React=require("react"),{renderToStaticMarkup}=require("react-dom/server");
 const {translate,displayText}=await import(pathToFileURL(root+"/web/src/ui/i18n/resources.js"));
 globalThis.__webRenderer={React,useText:()=>key=>translate("en",key),useDisplayText:()=>value=>displayText("en",value)};
 try{
  const modules={};for(const name of ["Messages","FriendsPanel"]){const code=readFileSync(root+"/web/src/ui/components/"+name+".js","utf8").replace(/^import .*;\r?\n/gm,"");const output=root+"/"+name+"-probe.mjs";writeFileSync(output,"const {React,useText,useDisplayText}=globalThis.__webRenderer;\n"+code);modules[name]=await import(pathToFileURL(output));}
  const row={requestId:"controlled-request",senderId:u,conversationId:c,content:{kind:"TEXT",text:"controlled body"},state:"SENDING"};
  const render=m=>renderToStaticMarkup(React.createElement(modules.Messages.Messages,{v:{user:{userId:u},groups:[]},messages:[m],retry:()=>{}}));
  for(const state of ["SENDING","SENT","FAILED"])assert.match(render({...row,state}),/controlled body/);
  for(const invalid of [{...row,state:"UNKNOWN"},{...row,requestId:""},{...row,content:{kind:"TEXT",text:null}}])assert.throws(()=>render(invalid),/Invalid message/);
  const noMatch=translate("en","friends.noMatch"),base={friends:[],friendsBusy:false,friendsError:"",searchBusy:false,searchError:"",searchResults:[],user:{userId:u}};let searched=true;
  const props={v:base,search:"alice",setSearch:()=>{},searched:true,setSearched:value=>{searched=value},open:()=>{},loadFriends:async()=>{},searchUsers:async()=>{},addFriend:async()=>{}};
  const friends=extra=>renderToStaticMarkup(React.createElement(modules.FriendsPanel.FriendsPanel,{...props,...extra}));
  assert(friends({}).includes(noMatch));assert(!friends({searched:false}).includes(noMatch));assert(!friends({v:{...base,searchError:"CONNECTION_UNAVAILABLE"}}).includes(noMatch));
  const tree=modules.FriendsPanel.FriendsPanel(props);const find=node=>{if(!node||typeof node!=="object")return null;if(node.type==="input")return node;for(const child of [node.props?.children].flat(Infinity)){const hit=find(child);if(hit)return hit;}return null};find(tree).props.onChange({target:{value:"bob"}});assert.equal(searched,false);
 }finally{delete globalThis.__webRenderer}
}
console.log("PASS compiled Web renderer three-state/content/identity and truthful successful-empty search; editing query clears old completion");

{
 const {verifyStreamCleanup}=await import('../errors/stream_cleanup.mjs');
 const {Http,ApiFailure}=await import(pathToFileURL(process.env.WEB_BUILD_DIR+'/web/src/application/http.js'));
 const invoke=(path,method)=>(response,signal)=>new Http('https://localhost/',async()=>response).request(path,method,undefined,undefined,signal);
 await verifyStreamCleanup(invoke('/v1/users/me','GET'),(error,mode)=>error instanceof ApiFailure&&error.code===((mode==='protocol-distinct'||mode==='direct-validation')?'INVALID_RESPONSE':'CONNECTION_UNAVAILABLE'),'{}');
 await verifyStreamCleanup(invoke('/v1/auth/logout','POST'),(error,mode)=>error instanceof ApiFailure&&error.code===((mode==='protocol-distinct'||mode==='direct-validation')?'INVALID_RESPONSE':'CONNECTION_UNAVAILABLE'),'',{logout:true});
}

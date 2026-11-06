const assert=require('node:assert/strict'),path=require('node:path');
const {Workspace}=require(path.join(process.argv[2],'desktop/src/application/ui/workspace.js'));
const {ApiFailure}=require(path.join(process.argv[2],'desktop/src/application/ui/auth.js'));
const A='10000000-0000-4000-8000-000000000001',B='10000000-0000-4000-8000-000000000002',C='30000000-0000-4000-8000-000000000001',R='40000000-0000-4000-8000-000000000001',time='2026-10-18T06:30:00Z';
const rows=[A,B].map(id=>({conversationId:C,kind:'GROUP',createdBy:A,createdAt:time,member:{user:{userId:id,username:'user',displayName:'Same'},role:id===A?'OWNER':'MEMBER',joinedAt:time}}));
(async()=>{
 // Exercise the real Workspace while a bind-time read is superseded by add's read.
 const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no});return {promise,resolve,reject}};
 for(const unknown of [false,true]){
  const app=new Workspace(),initial=deferred(),entered=deferred();let puts=0,gets=0;
  const failure=unknown?new Error('owned unexpected friend read'):new ApiFailure('connection_unavailable');
  app.auth={add:async()=>{puts++;return C},friends:()=>{gets++;if(gets===1){entered.resolve();return initial.promise}if(gets===2)return Promise.reject(failure);return Promise.resolve([])}};
  const repo={cursor:async()=> '1',conversationIds:async()=>[],messages:async()=>[]};
  const pending=app.refreshFriends(repo,0);await entered.promise;
  if(unknown)await assert.rejects(app.add(B),e=>e===failure);else await app.add(B);
  initial.resolve([]);await pending;
  assert.equal(app.state.friendsStatus,'error','failed replacement read must end loading');assert.equal(app.state.busy,false);
  assert.equal(puts,1);assert.equal(gets,2);
  await app.refreshFriends(repo,0);
  assert.equal(app.state.friendsStatus,'ready');assert.deepEqual(app.state.friends,[]);
  assert.equal(puts,1,'read recovery must never replay the committed PUT');assert.equal(gets,3);
 }
 for(const retire of ['generation','owner','revision']){
  const app=new Workspace(),read=deferred(),entered=deferred();
  app.auth={add:async()=>C,friends:()=>{entered.resolve();return read.promise}};
  const pending=app.add(B);await entered.promise;
  if(retire==='generation')app.generation++;else if(retire==='owner')app.auth={};else app.friendRevision++;
  app.state={...app.state,friendsStatus:'ready',error:null,busy:false};
  read.reject(new ApiFailure('connection_unavailable'));await pending;
  assert.equal(app.state.friendsStatus,'ready',retire+' must retire failed GET');assert.equal(app.state.error,null);
 }
 {
  const app=new Workspace(),primary=new Error('owned read failure'),observer=new Error('owned observer failure');
  app.auth={add:async()=>C,friends:async()=>{throw primary}};
  app.observe(()=>{if(!app.state.busy)throw observer});
  await assert.rejects(app.add(B),e=>e instanceof AggregateError&&e.errors[0]===primary&&e.errors[1]===observer);
  assert.equal(app.state.friendsStatus,'error');
 }
 console.log('Desktop actual friend PUT/GET failure, GET-only recovery, unknown/observer and stale ownership PASS');
 let mutations=0;const bodies=[];let failScan=false;
 global.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  assert.equal(command,'native_https');let value,status=200;
  if(args.method==='POST'){bodies.push(args.body);if(++mutations===1)throw 'HTTPS transport unavailable';const body=JSON.parse(Buffer.from(args.body).toString());value={requestId:body.requestId,conversationId:C,addedMemberUserIds:args.url.endsWith('/members')?[B]:[A,B],createdAt:time};status=args.url.endsWith('/members')?200:201;}
  else {const q=new URL(args.url).searchParams;value={requestId:q.get('requestId'),items:failScan?[rows[1],rows[0]]:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}}}
  return [status,{'content-type':'application/json','cache-control':'no-store'},Array.from(Buffer.from(JSON.stringify(value)))];
 }}};
 const app=new Workspace();app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
 await app.createGroup([B]);assert.equal(app.state.groupStatus,'unconfirmed');await app.retryGroup();assert.equal(app.state.groupStatus,'success');assert.deepEqual(bodies[0],bodies[1]);assert.equal(app.state.groups.length,2);assert.equal(app.state.selected,C);assert.equal(app.state.page,'Chat');
 await app.createGroup([B],C);assert.equal(app.state.groupStatus,'success');assert.equal(app.state.selected,C,'adding to the active group must not toggle it closed');assert.equal(app.state.page,'Chat');
 failScan=true;await app.refreshGroups();assert.equal(app.state.groups.length,2);assert.equal(app.state.groupError,'protocol');
 const unknown=new Error('controlled native bug');window.__TAURI_INTERNALS__.invoke=async()=>{throw unknown};await assert.rejects(()=>app.refreshGroups(),e=>e===unknown);
 await app.stop();assert.equal(app.state.groups.length,0);assert.equal(app.groupOperation,undefined);
 console.log('Group Desktop actual native adapter retry/snapshot/unknown/isolation behavior PASS');
 // Only the literal native invoke is controlled: compiled nativeFetch, GroupHttp
 // and Workspace must propagate unexpected failures, even after retirement.
 for(const name of ['Error','InvalidStateError','DataCloneError','AbortError'])for(const method of ['POST','GET'])for(const retired of [false,true]){
  const app=new Workspace(),entered=deferred(),pendingNative=deferred();
  const cause=name==='Error'?new Error('owned native bug'):new DOMException('owned native bug',name);
  let calls=0;
  window.__TAURI_INTERNALS__.invoke=async(command,args)=>{assert.equal(command,'native_https');assert.equal(args.method,method);calls++;entered.resolve();return pendingNative.promise;};
  app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
  const pending=method==='POST'?app.createGroup([B]):app.refreshGroups();await entered.promise;
  if(retired){await app.stop();app.state={...app.state,session:{userId:B,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};}
  const before=app.state,rejection=assert.rejects(pending,e=>e===cause,name+' must retain the same cause');
  pendingNative.reject(cause);await rejection;
  assert.equal(app.state,before,'unknown failure must not publish a fabricated transport state');assert.equal(calls,1);
  if(retired)assert.equal(app.groupOperation,undefined,'retirement clears the old operation');
  else if(method==='POST')assert.equal(app.groupOperation.account,A,'unknown commit must not discard original identity');
 }
 // Workspace creates fresh, unexposed signals and does not cancel group calls.
 // Exercise real adapter cancellation via its actual GroupHttp, with an owned
 // signal: cancellation must reject as AbortError, never as GroupFailure.
 for(const phase of ['before-invoke','after-invoke']){
  const app=new Workspace(),controller=new AbortController();let calls=0;
  app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
  window.__TAURI_INTERNALS__.invoke=async(command,args)=>{
   assert.equal(command,'native_https');calls++;controller.abort();
   return [201,{'content-type':'application/json','cache-control':'no-store'},Array.from(Buffer.from(JSON.stringify({requestId:R,conversationId:C,addedMemberUserIds:[A,B],createdAt:time})))];
  };
  if(phase==='before-invoke')controller.abort();
  const before=app.state;
  await assert.rejects(app.groupHttp().mutate(R,[B],controller.signal),e=>e instanceof DOMException&&e.name==='AbortError');
  assert.equal(calls,phase==='before-invoke'?0:1);assert.equal(app.state,before);
 }
 console.log('Desktop actual native/group/workspace DOM cause, account retirement and real signal cancellation PASS');
 // A confirmed mutation must not defer its navigation until an older member read finishes.
 for(const next of ['create','manual','retired','unknown']){
  const app=new Workspace(),held=deferred(),entered=deferred(),later='30000000-0000-4000-8000-000000000002';
  const sentinel=new Error('owned stale member read');let posts=0,gets=0;
  window.__TAURI_INTERNALS__.invoke=async(command,args)=>{
   assert.equal(command,'native_https');let value,status=200;
   if(args.method==='POST'){const q=JSON.parse(Buffer.from(args.body).toString());value={requestId:q.requestId,conversationId:++posts===1?C:later,addedMemberUserIds:[A,B],createdAt:time};status=201;}
   else{if(++gets===1){entered.resolve();await held.promise;}const q=new URL(args.url).searchParams;value={requestId:q.get('requestId'),items:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}};}
   return [status,{'content-type':'application/json','cache-control':'no-store'},Array.from(Buffer.from(JSON.stringify(value)))];
  };
  app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
  const first=app.createGroup([B]);await entered.promise;
  if(next==='create')await app.createGroup([B]);else{if(next==='retired')await app.stop();await app.open(later);}
  assert.equal(app.state.selected,later);
  if(next==='unknown'){const rejection=assert.rejects(first,e=>e===sentinel);held.reject(sentinel);await rejection;}else{held.resolve();await first;}
  assert.equal(app.state.selected,later,next+': old read must preserve latest navigation');
  assert.equal(posts,next==='create'?2:1);assert.equal(gets,next==='create'?2:1);
 }
 console.log('Desktop delayed member read preserves later CREATE/manual selection, retired generation and unknown cause PASS');
 {
  const app=new Workspace(),opening=deferred(),entered=deferred();let calls=0;
  window.__TAURI_INTERNALS__.invoke=async(command,args)=>{
   assert.equal(command,'native_https');assert.equal(args.method,'POST','retired open must not start a member read for the new account');calls++;
   const q=JSON.parse(Buffer.from(args.body).toString());return [201,{'content-type':'application/json','cache-control':'no-store'},Array.from(Buffer.from(JSON.stringify({requestId:q.requestId,conversationId:C,addedMemberUserIds:[A,B],createdAt:time})))];
  };
  app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
  app.sync={openConversation:()=>{entered.resolve();return opening.promise},close:async()=>{}};
  const pending=app.createGroup([B]);await entered.promise;await app.stop();
  app.state={...app.state,session:{userId:B,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
  opening.resolve();await pending;assert.equal(calls,1);assert.equal(app.state.selected,'');assert.deepEqual(app.state.groups,[]);
 }
 console.log('Desktop retired post-confirmation Sync cannot refresh a replacement account PASS');
})().catch(e=>{console.error(e);process.exitCode=1});

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
})().catch(e=>{console.error(e);process.exitCode=1});

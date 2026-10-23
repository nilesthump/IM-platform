const assert=require('node:assert/strict'),path=require('node:path');
const {Workspace}=require(path.join(process.argv[2],'desktop/src/application/ui/workspace.js'));
const A='10000000-0000-4000-8000-000000000001',B='10000000-0000-4000-8000-000000000002',C='30000000-0000-4000-8000-000000000001',R='40000000-0000-4000-8000-000000000001',time='2026-10-18T06:30:00Z';
const rows=[A,B].map(id=>({conversationId:C,kind:'GROUP',createdBy:A,createdAt:time,member:{user:{userId:id,username:'user',displayName:'Same'},role:id===A?'OWNER':'MEMBER',joinedAt:time}}));
(async()=>{
 let mutations=0;const bodies=[];let failScan=false;
 global.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  assert.equal(command,'native_https');let value,status=200;
  if(args.method==='POST'){bodies.push(args.body);if(++mutations===1)throw 'HTTPS transport unavailable';const body=JSON.parse(Buffer.from(args.body).toString());value={requestId:body.requestId,conversationId:C,addedMemberUserIds:[A,B],createdAt:time};status=201;}
  else {const q=new URL(args.url).searchParams;value={requestId:q.get('requestId'),items:failScan?[rows[1],rows[0]]:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}}}
  return [status,{'content-type':'application/json','cache-control':'no-store'},Array.from(Buffer.from(JSON.stringify(value)))];
 }}};
 const app=new Workspace();app.state={...app.state,session:{userId:A,sessionId:R,sessionEpoch:1n,accessToken:'controlled-only'}};
 await app.createGroup([B]);assert.equal(app.state.groupStatus,'unconfirmed');await app.retryGroup();assert.equal(app.state.groupStatus,'success');assert.deepEqual(bodies[0],bodies[1]);assert.equal(app.state.groups.length,2);assert.equal(app.state.selected,C);assert.equal(app.state.page,'Chat');
 failScan=true;await app.refreshGroups();assert.equal(app.state.groups.length,2);assert.equal(app.state.groupError,'protocol');
 const unknown=new Error('controlled native bug');window.__TAURI_INTERNALS__.invoke=async()=>{throw unknown};await assert.rejects(()=>app.refreshGroups(),e=>e===unknown);
 await app.stop();assert.equal(app.state.groups.length,0);assert.equal(app.groupOperation,undefined);
 console.log('Group Desktop actual native adapter retry/snapshot/unknown/isolation behavior PASS');
})().catch(e=>{console.error(e);process.exitCode=1});

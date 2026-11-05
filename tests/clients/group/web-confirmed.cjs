// Actual WebClient/GroupHttp; only the HTTP boundary is controlled.
const assert=require('node:assert/strict'),path=require('node:path');
module.exports=async function confirmedMutation(out){
 const within=async promise=>{let timer;try{return await Promise.race([promise,new Promise((_,reject)=>timer=setTimeout(()=>reject(Error('Web confirmation test did not settle')),2500))]);}finally{clearTimeout(timer);}};
 const {WebClient}=require(path.join(out,'web/src/application/client.js'));
 const A='10000000-0000-4000-8000-000000000001',B='10000000-0000-4000-8000-000000000002',C='30000000-0000-4000-8000-000000000001',D='30000000-0000-4000-8000-000000000002',S='40000000-0000-4000-8000-000000000001',time='2026-11-05T00:00:00Z';
 const session={userId:A,sessionId:S,sessionEpoch:1n,accessToken:'controlled-token',expires:Date.now()+60000};
 const rows=[A,B].map(id=>({conversationId:C,kind:'GROUP',createdBy:A,createdAt:time,member:{user:{userId:id,username:id===A?'alice':'bob',displayName:'Same'},role:id===A?'OWNER':'MEMBER',joinedAt:time}}));
 const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 for(const adding of [false,true]){
  let release,entered,mode='held',calls=0;const held=new Promise(r=>release=r),reading=new Promise(r=>entered=r),root=new Error('unknown member-read bug');
  const client=new WebClient('https://owned.invalid',async(url,init)=>{
   if(init.method==='POST'){calls++;return response({requestId:JSON.parse(init.body).requestId,conversationId:C,addedMemberUserIds:adding?[B]:[A,B],createdAt:time},adding?200:201);}
   entered();if(mode==='held')await held;if(mode==='failure')throw new TypeError('known read failure');if(mode==='unknown')throw root;
   return response({requestId:new URL(url).searchParams.get('requestId'),items:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});
  });
  client.session={...session};client.publish({session:true,friends:[{user:rows[1].member.user,directConversationId:D}],groups:adding?rows:[]});
  try{
   const operation=client.createGroup([B],adding?C:undefined);await within(reading);
   assert.equal(client.view().groupStatus,'success','validated mutation succeeds before held member read');
   assert.equal(client.view().groupBusy,false);assert.equal(client.groupOperation,undefined);assert.equal(client.view().selected,C);
   assert.equal(client.view().groupReadBusy,true);assert.deepEqual(client.view().groups,adding?rows:[],'no fabricated member snapshot');
   assert.equal(client.repository.hasBaseline(C),false,'confirmation does not establish a history baseline');
   client.open(S);assert.equal(client.view().selected,C,'arbitrary ID does not gain authorization');
   client.open(D);mode='failure';release();await within(operation);
   assert.equal(client.view().selected,D,'later metadata failure cannot override manual selection');
   assert.equal(client.view().groupStatus,'success');assert.equal(client.view().groupError,'');assert.equal(client.view().groupReadError,'transport');assert.equal(client.view().groupReadBusy,false);
   await client.retryGroup();assert.equal(calls,1,'confirmed operation cannot be retransmitted');
   mode='unknown';await assert.rejects(client.refreshGroups(),e=>e===root,'unknown cause propagates');assert.equal(client.view().groupReadBusy,false);
   mode='ok';await client.refreshGroups();assert.deepEqual(client.view().groups,rows);assert.deepEqual(client.view().confirmedGroups,[],'real projection supersedes identity-only confirmation');assert.equal(client.view().groupReadError,'');assert.equal(client.view().selected,D);
   client.dispose();client.open(C);assert.equal(client.view().selected,'');assert.deepEqual(client.view().confirmedGroups,[]);
  }finally{release();client.dispose();}
 }
 // Unknown post-confirmation failures propagate without restoring mutation retry.
 const root=new Error('unknown follow-up failure');
 const unknown=new WebClient('https://owned.invalid',async(url,init)=>{
  if(init.method==='POST')return response({requestId:JSON.parse(init.body).requestId,conversationId:C,addedMemberUserIds:[A,B],createdAt:time},201);
  throw root;
 });
 unknown.session={...session};await assert.rejects(unknown.createGroup([B]),e=>e===root);assert.equal(unknown.view().groupStatus,'success');assert.equal(unknown.view().selected,C);assert.equal(unknown.groupOperation,undefined);unknown.dispose();
 // A read authentication rejection retires the confirmed account along with its IDs.
 const expired=new WebClient('https://owned.invalid',async(url,init)=>{
  if(init.method==='POST')return response({requestId:JSON.parse(init.body).requestId,conversationId:C,addedMemberUserIds:[A,B],createdAt:time},201);
  return response({requestId:new URL(url).searchParams.get('requestId'),error:{code:'AUTH_TOKEN_EXPIRED',message:'Expired'}},401);
 });
 expired.session={...session};expired.publish({session:true});await expired.createGroup([B]);assert.equal(expired.view().session,false);assert.deepEqual(expired.view().confirmedGroups,[]);assert.equal(expired.view().selected,'');expired.open(C);assert.equal(expired.view().selected,'');expired.dispose();
 // Retirement while the post-confirmation read is pending cannot publish old data.
 let release,entered;const held=new Promise(r=>release=r),reading=new Promise(r=>entered=r);
 const retired=new WebClient('https://owned.invalid',async(url,init)=>{
  if(init.method==='POST')return response({requestId:JSON.parse(init.body).requestId,conversationId:C,addedMemberUserIds:[A,B],createdAt:time},201);
  entered();await held;return response({requestId:new URL(url).searchParams.get('requestId'),items:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});
 });
 retired.session={...session};const operation=retired.createGroup([B]);await within(reading);retired.dispose();retired.session={...session,userId:B};release();await within(operation);
 assert.equal(retired.view().selected,'');assert.deepEqual(retired.view().groups,[]);assert.deepEqual(retired.view().confirmedGroups,[]);retired.dispose();
 // Real member reads and subscribed observers can fail independently. Finalizing
 // loading must preserve both causes, without changing single-failure identity.
 for(const read of ['ok','unknown','known'])for(const endingFails of [false,true]){
  const readCause=read==='known'?new TypeError('member transport failed'):new Error('member read failed');
  const observerCause=new Error('ending observer failed');let recover=false;
  const client=new WebClient('https://owned.invalid',async url=>{
   if(!recover&&read!=='ok')throw readCause;
   return response({requestId:new URL(url).searchParams.get('requestId'),items:rows,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});
  });
  client.session={...session};const unsubscribe=client.subscribe(()=>{if(endingFails&&!client.view().groupReadBusy)throw observerCause;});
  try{
   let rejected=false,cause,result;try{result=await client.refreshGroups();}catch(error){rejected=true;cause=error;}
   assert.equal(rejected,read==='unknown'||endingFails,`${read}/${endingFails}: rejection`);
   if(read==='unknown'&&!endingFails)assert.equal(cause,readCause);
   if(read==='ok'&&endingFails)assert.equal(cause,observerCause);
   if(read!=='ok'&&endingFails){
    assert.ok(cause instanceof AggregateError,'read and ending failures must both survive');assert.equal(cause.errors.length,2);assert.equal(cause.errors[1],observerCause);
    if(read==='unknown')assert.equal(cause.errors[0],readCause);
    else {assert.equal(cause.errors[0].kind,'transport');assert.equal(cause.errors[0].cause,readCause);}
   }
   if(!rejected)assert.equal(result,read==='ok');
   if(read==='known')assert.equal(client.view().groupReadError,'transport');
   assert.equal(client.view().groupReadBusy,false);assert.equal(client.groupScanning,undefined);
   unsubscribe();recover=true;assert.equal(await client.refreshGroups(),true);assert.deepEqual(client.view().groups,rows);assert.equal(client.view().groupReadError,'');
  }finally{unsubscribe();client.dispose();}
 }
 // JavaScript permits any thrown value; undefined/null must not mean "no error".
 for(const readCause of [undefined,null,0,'',NaN])for(const endingFails of [false,true]){
  const observerCause=new Error('ending observer failed');
  const client=new WebClient('https://owned.invalid',async()=>{throw readCause;});client.session={...session};
  const unsubscribe=client.subscribe(()=>{if(endingFails&&!client.view().groupReadBusy)throw observerCause;});
  try{
   let rejected=false,cause;try{await client.refreshGroups();}catch(error){rejected=true;cause=error;}
   assert.equal(rejected,true);
   if(endingFails){assert.ok(cause instanceof AggregateError);assert.deepEqual(cause.errors,[readCause,observerCause]);}
   else assert.ok(Object.is(cause,readCause),'single thrown value is unchanged');
   assert.equal(client.view().groupReadBusy,false);assert.equal(client.groupScanning,undefined);
  }finally{unsubscribe();client.dispose();}
 }
 // A notification of the known error can fail before loading ends as well.
 for(const endingFails of [false,true]){
  const readCause=new TypeError('member transport failed'),reportCause=new Error('error observer failed'),endingCause=new Error('ending observer failed');
  const client=new WebClient('https://owned.invalid',async()=>{throw readCause;});client.session={...session};
  const unsubscribe=client.subscribe(()=>{
   if(client.view().groupReadError&&client.view().groupReadBusy)throw reportCause;
   if(endingFails&&!client.view().groupReadBusy)throw endingCause;
  });
  try{
   await assert.rejects(client.refreshGroups(),error=>{
    assert.ok(error instanceof AggregateError);assert.equal(error.errors[0].cause,readCause);
    assert.deepEqual(error.errors.slice(1),endingFails?[reportCause,endingCause]:[reportCause]);return true;
   });
   assert.equal(client.view().groupReadBusy,false);assert.equal(client.groupScanning,undefined);
  }finally{unsubscribe();client.dispose();}
 }
 console.log('PASS Web confirmed CREATE/ADD held/read failure, honest snapshot, unknown cause, selection and account isolation');
 console.log('PASS Web member-read and ending-observer single/dual causes, falsy throws and recovery');
};

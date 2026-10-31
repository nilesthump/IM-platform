const fs=require('fs'),path=require('path'),assert=require('assert/strict');
// Run: node desktop-picker.cjs <repo> <desktop-node-modules> <playwright-module> <browser-executable>
// Headless component regression; native I/O controlled at invoke. Not native acceptance.
const [base,deps,playwright,browser]=process.argv.slice(2);if(!browser)throw Error('Four paths required');
const ts=require(deps+'/typescript'),{chromium}=require(playwright);
const sources={};for(const [id,file] of Object.entries({react:'react/cjs/react.development.js','react-dom':'react-dom/cjs/react-dom.development.js',scheduler:'scheduler/cjs/scheduler.development.js'}))sources[id]=fs.readFileSync(deps+'/'+file,'utf8');
function add(rel){if(sources[rel])return;const code=fs.readFileSync(base+'/'+rel,'utf8');sources[rel]=ts.transpileModule(code,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true,target:ts.ScriptTarget.ES2022}}).outputText;for(const m of sources[rel].matchAll(/require\("([^"]+)"\)/g)){if(!m[1].startsWith('.'))continue;const stem=path.posix.normalize(path.posix.join(path.posix.dirname(rel),m[1])).replace(/\.js$/,'');const next=['.ts','.tsx'].map(e=>stem+e).find(f=>fs.existsSync(base+'/'+f));if(!next)throw Error(stem);add(next)}}
const shell='clients/desktop/src/ui/components/Shell.tsx',work='clients/desktop/src/application/ui/workspace.ts';add(shell);
const boot=`const sources=${JSON.stringify(sources)},cache={};window.process={env:{NODE_ENV:'development'}};window.bodies=[];
window.mutationMode='transport';window.groupId='30000000-0000-4000-8000-000000000002';
const answer=(status,body)=>[status,{'content-type':'application/json','cache-control':'no-store'},Array.from(new TextEncoder().encode(JSON.stringify(body)))];
async function invoke(cmd,args){if(cmd==='language_load')return 'en';if(cmd==='appearance_load')return ['cold',16,1];if(cmd==='window_maximized')return false;if(['language_save','tray_text'].includes(cmd))return;if(cmd==='native_https'){
 if(args.method==='POST'){bodies.push(args.body);const req=JSON.parse(new TextDecoder().decode(new Uint8Array(args.body)));
  if(mutationMode==='transport')throw 'HTTPS transport unavailable';
  if(mutationMode==='unknown')throw Error('mutation sentinel');
  if(mutationMode==='rejected')return answer(403,{requestId:req.requestId,error:{code:'AUTHORIZATION_DENIED',message:'Not authorized'}});
  const adding=args.url.endsWith('/members');return answer(adding?200:201,{requestId:req.requestId,conversationId:groupId,addedMemberUserIds:adding?req.memberUserIds:[session.userId,...req.memberUserIds].sort(),createdAt:'2026-10-29T00:00:00Z'});
 }
 const req=new URL(args.url);if(req.pathname==='/v1/conversations'){if(window.holdMembers)await new Promise(resolve=>{window.finishMembers=()=>{window.holdMembers=false;resolve()}});return answer(200,{requestId:req.searchParams.get('requestId'),items:[session.userId,friends[0].user.userId].sort().map(userId=>({conversationId:groupId,kind:'GROUP',createdBy:session.userId,createdAt:'2026-10-29T00:00:00Z',member:{user:{userId,username:'fixture',displayName:'Fixture'},role:userId===session.userId?'OWNER':'MEMBER',joinedAt:'2026-10-29T00:00:00Z'}})),hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}});}
 throw Error('Unexpected GET');}throw Error('Unexpected native '+cmd)}
function load(id){if(cache[id])return cache[id].exports;const m={exports:{}};cache[id]=m;function req(s){if(s==='@tauri-apps/api/core')return {invoke};if(sources[s])return load(s);const parts=id.split('/');parts.pop();for(const p of s.split('/')){if(p==='..')parts.pop();else if(p!=='.')parts.push(p)}const stem=parts.join('/').replace(/\\.js$/,'');const key=[stem+'.ts',stem+'.tsx'].find(k=>sources[k]);if(!key)throw Error(s+' from '+id);return load(key)}new Function('require','module','exports',sources[id])(req,m,m.exports);return m.exports;}
const W=load('${work}').Workspace,original=W.prototype.start;W.prototype.start=function(){window.app=this;return original.call(this)};const React=load('react');load('react-dom').createRoot(document.getElementById('root')).render(React.createElement(load('${shell}').Shell));
window.session={userId:'10000000-0000-4000-8000-000000000001',sessionId:'40000000-0000-4000-8000-000000000001',sessionEpoch:1n,accessToken:'controlled-only'};window.friends=[{user:{userId:'10000000-0000-4000-8000-000000000002',username:'friend',displayName:'Friend'},directConversationId:'30000000-0000-4000-8000-000000000001'}];`;
(async()=>{
 const b=await chromium.launch({executablePath:browser,headless:true});
 try{
  const p=await b.newPage();p.setDefaultTimeout(3000);const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.route('http://localhost:18743/',r=>r.fulfill({contentType:'text/html',body:'<div id="root"></div>'}));
  await p.goto('http://localhost:18743/');await p.addScriptTag({content:boot});await p.waitForFunction(()=>window.app);
  await p.evaluate(()=>app.publish({session,friends,friendsStatus:'ready'}));
  const open=async()=>{await p.locator('.new-chat > button').click();await p.locator('.new-chat-menu button').nth(1).click();};
  const confirm=()=>p.locator('dialog footer button').first().click(),cancel=()=>p.locator('dialog footer button').last().click();
  const select=async()=>{await p.locator('dialog input[type=checkbox]').check();await p.locator('dialog input:not([type])').fill('Friend');};
  const frame=()=>p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await open();await select();await confirm();await p.waitForFunction(()=>app.state.groupStatus==='unconfirmed');await cancel();
  await p.evaluate(()=>app.selectLanguage('ja-JP'));await open();assert.equal(await p.locator('dialog').evaluate(e=>e.open),true);assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),true);
  console.log('CONTROL language-only reopen PASS');await cancel();
  // The actual transient stop(true) phase of same-account bind; controlled native port, no auth/SQLite claim.
  await p.evaluate(()=>app.stop(true));await p.waitForFunction(()=>!app.state.session);await p.evaluate(()=>app.publish({session,friends,friendsStatus:'ready'}));
  await p.evaluate(()=>app.selectLanguage('en'));await open();assert.equal(await p.locator('dialog').count(),1,'pending picker survives same-account stop(true)');assert.equal(await p.locator('dialog').evaluate(e=>e.open),true);
  assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),true);assert.equal(await p.locator('dialog input:not([type])').inputValue(),'Friend');
  await confirm();await p.waitForFunction(()=>bodies.length===2);assert.deepEqual(await p.evaluate(()=>bodies[0]),await p.evaluate(()=>bodies[1]));
  await p.evaluate(()=>app.stop(true));await p.waitForFunction(()=>!app.state.session);assert.equal(await p.locator('dialog').count(),1);
  await p.evaluate(()=>app.stop());await p.waitForFunction(()=>document.querySelector('dialog')===null);
  await p.evaluate(()=>app.publish({session:{...session,userId:'10000000-0000-4000-8000-000000000003'},friends,friendsStatus:'ready'}));await open();
  assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),false);assert.equal(await p.locator('dialog input:not([type])').inputValue(),'');await cancel();assert.deepEqual(errors,[]);
  console.log('PASS actual Shell/GroupPanel/Workspace lifecycle, original request body and retirement/different-account isolation');

  for(const outcome of ['resolve','unknown']){
   await p.evaluate(()=>app.stop());await p.evaluate(()=>{app.publish({session,friends,friendsStatus:'ready'});window.mutationMode='transport';window.bodies=[];});
   await open();await select();await confirm();await p.waitForFunction(()=>app.state.groupStatus==='unconfirmed');await cancel();
   await p.evaluate(()=>app.stop(true));await p.evaluate(()=>app.publish({session,friends,friendsStatus:'ready'}));
   for(const locale of ['zh-CN','en']){await p.evaluate(value=>app.selectLanguage(value),locale);await open();assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),true);assert.equal(await p.locator('dialog input:not([type])').inputValue(),'Friend');await cancel();}
   await p.evaluate(()=>{window.mutationMode='success';window.tailStarted=false;window.tailFinished=false;app.sync={openConversation:async()=>{window.tailStarted=true;await new Promise((resolve,reject)=>{window.finishTail=()=>resolve();window.failTail=()=>reject(Error('post-commit sentinel'));});window.tailFinished=true;},close:async()=>{}};});
   await open();await confirm();await p.waitForFunction(()=>app.state.groupStatus==='success'&&window.tailStarted);await frame();
   assert.equal(await p.locator('dialog').count(),0,'successful retry closes before post-commit Sync settles');
   assert.deepEqual(await p.evaluate(()=>bodies[0]),await p.evaluate(()=>bodies[1]));
   assert.equal(await p.evaluate(()=>app.state.selected),await p.evaluate(()=>groupId));assert.equal(await p.evaluate(()=>app.groupOperation),undefined);
   await open();assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),false);assert.equal(await p.locator('dialog input:not([type])').inputValue(),'');
   if(outcome==='resolve'){await p.evaluate(()=>finishTail());await p.waitForFunction(()=>tailFinished);}
   else{await p.evaluate(()=>failTail());await p.waitForTimeout(50);assert.deepEqual(errors,['post-commit sentinel']);}
   await frame();assert.equal(await p.locator('dialog').evaluate(e=>e.open),true,'late prior completion must not close a newly opened picker');
   assert.equal(await p.evaluate(()=>app.state.groupStatus),'success');assert.equal(await p.evaluate(()=>app.groupOperation),undefined);await cancel();
   console.log('PASS successful original retry closes with '+outcome+' Sync tail; late completion cannot close next picker');
  }
  // New CREATE and ADD close at the same confirmed boundary even while member refresh waits.
  for(const adding of [false,true]){
   await p.evaluate(()=>{window.mutationMode='success';window.holdMembers=true;});
   if(adding){await p.locator('.chat-heading button').last().click();await p.locator('.group-management > button').click();}else await open();
   await select();await confirm();await p.waitForFunction(()=>app.state.groupStatus==='success'&&typeof window.finishMembers==='function');await frame();
   assert.equal(await p.locator('dialog').count(),0,'confirmed create/add closes before member refresh');
   await p.evaluate(()=>{finishMembers();window.finishMembers=undefined;});await frame();
   assert.equal(await p.evaluate(()=>app.state.selected),await p.evaluate(()=>groupId));
  }
  // A newer explicit choice and its draft survive the first CREATE's delayed member read.
  for(const next of ['create','manual']){
   await p.evaluate(()=>app.stop());await p.evaluate(()=>{app.publish({session,friends,friendsStatus:'ready',conversations:[friends[0].directConversationId]});window.groupId='30000000-0000-4000-8000-000000000002';window.mutationMode='success';window.holdMembers=true;window.finishMembers=undefined;window.bodies=[];});
   await open();await select();await confirm();await p.waitForFunction(()=>typeof window.finishMembers==='function');await frame();
   assert.equal(await p.locator('dialog').count(),0);
   if(next==='create'){
    await p.evaluate(()=>{window.groupId='30000000-0000-4000-8000-000000000003';});await open();await select();await confirm();
    await p.waitForFunction(()=>app.state.selected===groupId&&app.state.groupSuccessRevision>0);await frame();assert.equal(await p.locator('dialog').count(),0);
   }else await p.locator('.conversation-list .conversation').click();
   const selected=await p.evaluate(()=>app.state.selected),draft='Draft for the latest '+next;
   await p.locator('#message').fill(draft);
   await p.evaluate(()=>{finishMembers();window.finishMembers=undefined;});await p.waitForFunction(()=>!app.groupScanning);await frame();
   assert.equal(await p.evaluate(()=>app.state.selected),selected,'old member read must not replace '+next+' selection');
   assert.equal(await p.locator('#message').inputValue(),draft,'latest conversation draft stays attached to selected conversation');
   assert.equal(await p.evaluate(()=>bodies.length),next==='create'?2:1);
  }
  console.log('PASS actual React delayed member read preserves later CREATE/manual navigation and draft');
  for(const mode of ['rejected','unknown']){
   await p.evaluate(()=>app.stop());await p.evaluate(value=>{app.publish({session,friends,friendsStatus:'ready'});window.mutationMode=value;},mode);
   await open();await select();await confirm();await p.waitForTimeout(50);await frame();
   assert.equal(await p.locator('dialog').evaluate(e=>e.open),true,'failed mutation must retain picker');
   assert.equal(await p.locator('dialog input[type=checkbox]').isChecked(),true);
   if(mode==='rejected')assert.equal(await p.evaluate(()=>app.state.groupStatus),'rejected');
   else assert.deepEqual(errors,['post-commit sentinel','mutation sentinel']);
  }
  await p.evaluate(()=>app.stop());assert.deepEqual(errors,['post-commit sentinel','mutation sentinel']);
  console.log('PASS actual React confirmed CREATE/ADD, pending/rejected/unknown retention and error propagation');
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exitCode=1});

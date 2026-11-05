// Exercises both complete runtime runners against actual Web React components and
// WebClient group HTTP/retry/scan logic. Login/server are controlled test boundaries;
// no TLS, permissions, durable database or real runtime acceptance is claimed.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const [root,deps,playwright,browserPath]=process.argv.slice(2);
const ts=require(path.join(deps,'typescript')),{chromium}=require(playwright);
const sources={};
for(const [id,file] of Object.entries({react:'react/cjs/react.development.js','react-dom':'react-dom/cjs/react-dom.development.js',scheduler:'scheduler/cjs/scheduler.development.js'}))sources[id]=fs.readFileSync(path.join(deps,file),'utf8');
function add(rel){if(sources[rel])return;sources[rel]=ts.transpileModule(fs.readFileSync(path.join(root,rel),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.React,esModuleInterop:true,target:ts.ScriptTarget.ES2022}}).outputText;for(const m of sources[rel].matchAll(/require\("([^"]+)"\)/g)){if(!m[1].startsWith('.'))continue;const stem=path.posix.normalize(path.posix.join(path.posix.dirname(rel),m[1])).replace(/\.js$/,'');const next=['.ts','.tsx'].map(e=>stem+e).find(f=>fs.existsSync(path.join(root,f)));if(!next)throw Error(stem);add(next)}}
add('clients/web/src/ui/components/Shell.tsx');
const accounts=Object.fromEntries(['A','B','C'].map((who,i)=>[who,{userId:`10000000-0000-4000-8000-${String(i+1).padStart(12,'0')}`,username:'fixture_'+who.toLowerCase(),displayName:'Group Fixture '+who,password:'controlled-only'}]));
const boot=`const sources=${JSON.stringify(sources)},cache={};window.process={env:{NODE_ENV:'development'}};
function load(id){if(cache[id])return cache[id].exports;const m={exports:{}};cache[id]=m;function req(s){if(sources[s])return load(s);const parts=id.split('/');parts.pop();for(const p of s.split('/')){if(p==='..')parts.pop();else if(p!=='.')parts.push(p)}const stem=parts.join('/').replace(/\\.js$/,'');const key=[stem+'.ts',stem+'.tsx'].find(k=>sources[k]);if(!key)throw Error(s+' from '+id);return load(key)}new Function('require','module','exports',sources[id])(req,m,m.exports);return m.exports;}
const accounts=${JSON.stringify(accounts)},mod=load('clients/web/src/application/client.ts'),Base=mod.WebClient;
mod.WebClient=class extends Base{constructor(...args){super(...args);window.app=this;}
 async login(username){const who=Object.keys(accounts).find(k=>accounts[k].username===username);if(!who)throw Error('Unknown test actor');const u=accounts[who];this.session={userId:u.userId,sessionId:'40000000-0000-4000-8000-000000000001',sessionEpoch:1n,accessToken:who,expires:Date.now()+60000};this.publish({session:true,connection:'ready',user:u});await this.loadFriends();await this.refreshGroups();}
 async loadFriends(){const who=this.session.accessToken;const peers=who==='B'?['A','C']:['B'];this.publish({friends:peers.map(k=>({user:accounts[k],directConversationId:'50000000-0000-4000-8000-'+accounts[k].userId.slice(-12)})),friendsBusy:false});}
};
const React=load('react');load('react-dom').createRoot(document.getElementById('root')).render(React.createElement(load('clients/web/src/ui/components/Shell.tsx').Shell));`;
async function run(file){
 const reports=new Map(),errors=[],pages=[],groups=new Map(),receipts=new Map(),mutations=[];let groupNumber=0,closed=false;
 const cfg={credentials:'controlled-accounts',playwright:'controlled-playwright',browser:browserPath,out:'controlled-output',modes:['before','after']};
 const browser=await chromium.launch({executablePath:browserPath,headless:true}),failures=[];
 function api(request){const url=new URL(request.url()),who=request.headers().authorization?.slice(7),actor=accounts[who];assert.ok(actor,'known fixture actor');
  if(request.method()==='POST'&&url.pathname.startsWith('/v1/groups')){const body=request.postDataJSON(),existing=receipts.get(body.requestId);mutations.push({who,body});if(existing)return existing;
   const adding=url.pathname.endsWith('/members'),gid=adding?url.pathname.split('/')[3]:`${String(++groupNumber).padStart(8,'0')}-0000-4000-8000-000000000001`,members=adding?groups.get(gid):[actor.userId];assert.ok(members);for(const id of body.memberUserIds)if(!members.includes(id))members.push(id);groups.set(gid,members);const result={status:adding?200:201,body:{requestId:body.requestId,conversationId:gid,addedMemberUserIds:adding?body.memberUserIds:[actor.userId,...body.memberUserIds].sort(),createdAt:'2026-10-18T06:30:00Z'}};receipts.set(body.requestId,result);return result;
  }
  assert.equal(url.pathname,'/v1/conversations');const items=[];for(const [gid,members]of groups)if(members.includes(actor.userId))for(const id of [...members].sort()){const user=Object.values(accounts).find(u=>u.userId===id);items.push({conversationId:gid,kind:'GROUP',createdBy:accounts.A.userId,createdAt:'2026-10-18T06:30:00Z',member:{user:{userId:id,username:user.username,displayName:user.displayName},role:id===accounts.A.userId?'OWNER':'MEMBER',joinedAt:'2026-10-18T06:30:00Z'}})}
  return {status:200,body:{requestId:url.searchParams.get('requestId'),items,hasMore:false,next:{afterConversationId:'',afterMemberUserId:''}}};
 }
 async function respond(route,value){await route.fulfill({status:value.status,contentType:'application/json',headers:{'cache-control':'no-store'},body:JSON.stringify(value.body)});}
 const newContext=browser.newContext.bind(browser);
 browser.newContext=async options=>{const context=await newContext(options);const originalPage=context.newPage.bind(context);context.newPage=async()=>{const page=await originalPage();pages.push(page);page.setDefaultTimeout(2500);page.on('pageerror',e=>errors.push(e));
  const pageRoute=page.route.bind(page);await pageRoute('**/*',async route=>{const u=new URL(route.request().url());if(u.pathname==='/')return route.fulfill({contentType:'text/html',body:'<div id="root"></div>'});if(u.pathname==='/logo.png')return route.fulfill({status:404,body:''});try{await respond(route,api(route.request()));}catch(e){errors.push(e);await route.abort();}});
  const goto=page.goto.bind(page);page.goto=async url=>{await goto(url);await page.addScriptTag({content:boot});};
  // The G06 runner's route.fetch is the upstream service boundary, kept in memory.
  page.route=async(pattern,handler)=>pageRoute(pattern,route=>handler(new Proxy(route,{get(target,key){if(key==='fetch')return async()=>{const value=api(target.request());return {status:()=>value.status,json:async()=>value.body}};if(key==='continue')return async()=>respond(target,api(target.request()));const v=target[key];return typeof v==='function'?v.bind(target):v;}})));
  // Model an online metadata poll at another actor's observable conversation lookup.
  const locator=page.locator.bind(page);page.locator=(selector,...args)=>{const loc=locator(selector,...args);if(selector==='button.conversation'){const filter=loc.filter.bind(loc);loc.filter=options=>{const filtered=filter(options),click=filtered.click.bind(filtered);filtered.click=async()=>{await page.evaluate(()=>app.refreshGroups());return click();};return filtered;};}return loc;};
  page.screenshot=async()=>Buffer.alloc(0);return page;};return context;};
 const close=browser.close.bind(browser);browser.close=async()=>{await close();closed=true;};
 const proc={argv:['node',file,'controlled-config'],exitCode:0};const logs=[];
 try{await vm.runInNewContext(fs.readFileSync(path.join(root,'tests/clients/group',file),'utf8'),{require:id=>id==='controlled-playwright'?{chromium:{launch:async()=>browser}}:id==='node:fs'?{readFileSync:p=>JSON.stringify(p==='controlled-config'?cfg:accounts),mkdirSync:()=>{},existsSync:()=>true,writeFileSync:(p,data)=>reports.set(path.basename(p),JSON.parse(data))}:require(id),process:proc,console:{log:s=>logs.push(s),error:e=>logs.push(String(e))},setTimeout,clearTimeout,URL,AggregateError},{filename:file});assert.equal(proc.exitCode,0,logs.join('\n'));assert.equal(closed,true);assert.deepEqual(errors,[]);assert.ok(reports.get('result.json').result.startsWith('PASS'));
  if(file==='web.cjs'){assert.equal(groups.size,2,'both G06 modes create a distinct group');for(const mode of cfg.modes){const r=reports.get(`web-${mode}-success.json`);assert.equal(r.attempts.length,2);assert.deepEqual(r.attempts[0],r.attempts[1]);assert.deepEqual(r.targets,[accounts.B.userId]);}assert.equal(mutations.length,3,'before first call not forwarded; after replay is original result');}
  else{assert.equal(groups.size,1);assert.deepEqual([...groups.values()][0].sort(),Object.values(accounts).map(a=>a.userId).sort());assert.deepEqual(mutations.map(m=>m.who),['A','B']);}
 }catch(e){failures.push(e);}finally{if(!closed)try{await close();}catch(e){failures.push(e);}}
 if(failures.length===1)throw failures[0];if(failures.length)throw new AggregateError(failures,file+' regression');console.log('PASS '+file+' actual React and WebClient group flow; controlled service/login');
}
(async()=>{const failures=[];for(const file of ['web.cjs','web-ui.cjs'])try{await run(file);}catch(e){failures.push(e);}if(failures.length)throw new AggregateError(failures,'Web runner UI regressions');})().catch(e=>{console.error(e);process.exitCode=1});

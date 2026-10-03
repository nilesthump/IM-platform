import assert from "node:assert/strict";
import {spawnSync} from "node:child_process";
import {mkdtempSync,rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join,resolve} from "node:path";
import {Repository} from "../../../clients/shared/protocol-sdk/dist/storage/repository.js";
import {SendApplication} from "../../../clients/desktop/dist/desktop/src/application/send.js";
import {SyncApplication} from "../../../clients/desktop/dist/desktop/src/application/sync/application.js";
import {SyncHttp} from "../../../clients/desktop/dist/shared/protocol-sdk/src/sync/http.js";
const probe=resolve(process.argv[2]),endpoint=process.argv[3],root=mkdtempSync(join(tmpdir(),"im-sync-desktop-"));
const u="10000000-0000-4000-8000-000000000001",sid="20000000-0000-4000-8000-000000000001",c="30000000-0000-4000-8000-000000000001",d="30000000-0000-4000-8000-000000000002",denied="30000000-0000-4000-8000-000000000003";
const session={userId:u,sessionId:sid,sessionEpoch:1n,accessToken:"fixture-desktop"};
const uid=n=>"50000000-0000-4000-8000-"+String(n).padStart(12,"0");
const hex=s=>Buffer.from(s,"utf8").toString("hex"),bind=s=>s===null?"~":hex(s);
function database(account=u){function call(input){const r=spawnSync(probe,[root,account],{input,encoding:"utf8",maxBuffer:10*1024*1024});if(r.status || r.error)throw new Error("Native SQLx operation failed");return r.stdout;}
return {async transaction(steps){call(steps.length?steps.map(([sql,args,changes])=>["T",changes??"-",hex(sql),...args.map(bind)].join("\t")).join("\n")+"\n":"");},async query(sql,args){const raw=call(["Q",hex(sql),...args.map(bind)].join("\t")+"\n").trimEnd();return raw?raw.split(/\r?\n/).map(l=>l.split("\t").map(v=>v==="~"?null:Buffer.from(v,"hex").toString("utf8"))):[];}};}
const delay=n=>new Promise(r=>setTimeout(r,n));
async function until(check){for(let n=0;n<600;n++){if(await check())return;await delay(10);}throw new Error("Condition timed out");}
const response=p=>new Response(JSON.stringify(p),{headers:{"content-type":"application/json","cache-control":"no-store"}});
const repo=new Repository(database());await repo.initialize();
let send=new SendApplication(repo,session,undefined,100,()=>uid(1001));await send.openConversation(c);
assert.equal(await send.send(c,"message-1"),uid(1001));assert.equal((await repo.messages(c))[0][3],"FAILED");
let sync=new SyncApplication(send,new SyncHttp(endpoint,session));
send.connect(endpoint.replace("https:","wss:")+"/ws");await until(()=>send.state.connection==="ready");
try {await until(async()=>await repo.contiguous(c)===205n && sync.state.status==="idle");} catch(error) {console.error({phase:"initial",sync:sync.state,send:send.state.connection,sendError:send.state.error,cursor:await repo.cursor(),contiguous:String(await repo.contiguous(c))});throw error;}await sync.idle();
assert.equal(await repo.cursor(),"u-205");assert.equal((await repo.messages(c)).length,205);assert.equal((await repo.messages(c)).find(r=>r[0]===uid(1001))[3],"SENT");
assert.equal(await repo.contiguous(d),2n);assert.deepEqual(await repo.conversationIds(),[c,d,denied]);assert(sync.state.unavailable.includes(denied));assert.equal(send.state.messages.length,205);
await fetch(endpoint+"/fixture/append");await until(async()=>await repo.contiguous(c)===208n && await repo.cursor()==="u-206" && sync.state.status==="idle");assert.equal((await repo.messages(c)).length,208);
send.disconnect();await send.idle();send.connect(endpoint.replace("https:","wss:")+"/ws");await until(()=>send.state.connection==="ready");await until(()=>sync.state.status==="idle");await sync.idle();assert.equal(await repo.contiguous(c),208n);
await sync.close();assert.deepEqual(send.state.messages,[]);
send=new SendApplication(new Repository(database()),session);await send.repository.initialize();sync=new SyncApplication(send,new SyncHttp(endpoint,session));await sync.openConversation(c);assert.equal(send.state.messages.length,208);assert.equal(await send.repository.cursor(),"u-206");await sync.close();
const other=new Repository(database(uid(90000)));await other.initialize();assert.equal((await other.messages(c)).length,0);
function fakeSend(repository,owner=session){return new SendApplication(repository,owner,()=>({onopen:null,onmessage:null,onclose:null,onerror:null,send(){},close(){}}));}
function fakePage(request,input="0",next="fault",events=true){return {syncVersion:"1.0",type:"sync.user.page",requestId:request.requestId,events:events?[{eventId:uid(90001),cursor:next,kind:"conversation.changed",subjectId:c,revision:1}]:[],nextCursor:events?next:input,hasMore:false};}
let fault=false;const db=database(uid(90002));const faulty=new Repository({...db,transaction:steps=>db.transaction(fault?[...steps,["INSERT INTO __sync_fault_missing VALUES(1)",[],null]]:steps)});await faulty.initialize();
const fakeFetch=async(url,options)=>{const request=JSON.parse(options.body);return response(url.endsWith("user")?fakePage(request,request.cursor):{syncVersion:"1.0",type:"sync.conversation.page",requestId:request.requestId,conversationId:c,messages:[],hasMore:false});};
send=fakeSend(faulty);sync=new SyncApplication(send,new SyncHttp("https://localhost/",session,fakeFetch));fault=true;await assert.rejects(sync.synchronize());assert.equal(await faulty.cursor(),"0");assert.equal((await db.query("SELECT count(*) FROM user_state",[]))[0][0],"0");fault=false;await sync.synchronize();assert.equal(await faulty.cursor(),"fault");await sync.close();
const retired=new Repository(database(uid(90003)));await retired.initialize();send=fakeSend(retired);
let release,requested=false;const delayed=async(url,options)=>{requested=true;await new Promise(r=>release=r);return response(fakePage(JSON.parse(options.body)));};
sync=new SyncApplication(send,new SyncHttp("https://localhost/",session,delayed));const pulling=sync.synchronize();await until(()=>requested);const closing=sync.close();release();await Promise.all([pulling,closing]);assert.equal(await retired.cursor(),"0");assert.equal((await retired.messages(c)).length,0);
let count=0;send=fakeSend(retired);const unauthorized=async(url,options)=>{count++;const request=JSON.parse(options.body);return new Response(JSON.stringify({requestId:request.requestId,error:{code:"AUTH_SESSION_REVOKED",message:"Revoked"}}),{status:401,headers:{"content-type":"application/json","cache-control":"no-store"}});};
sync=new SyncApplication(send,new SyncHttp("https://localhost/",session,unauthorized));await assert.rejects(sync.synchronize());assert.equal(sync.state.error,"authentication");await sync.synchronize();assert.equal(count,1);await sync.close();
send=fakeSend(retired);assert.throws(()=>new SyncApplication(send,new SyncHttp("https://localhost/",{...session,userId:uid(99999)})));send.close();

// Present discovery: FAILED-only local intent and empty explicit selection.
for(const local of [true,false]){
 const fresh=new Repository(database(uid(local?91000:91001)));await fresh.initialize();const chosen=uid(local?91002:91003),request=uid(local?91004:91005);
 if(local){await fresh.localSend({conversationId:chosen,requestId:request,senderId:u,content:{kind:"TEXT",text:"discovery"}});await fresh.markFailed(chosen,request);}
 let pulled=0;
 const fetchDiscovery=async(url,options)=>{const r=JSON.parse(options.body);if(url.endsWith("user"))return response({syncVersion:"1.0",type:"sync.user.page",requestId:r.requestId,events:[],nextCursor:r.cursor,hasMore:false});
 pulled++;assert.equal(r.conversationId,chosen);return response({syncVersion:"1.0",type:"sync.conversation.page",requestId:r.requestId,conversationId:chosen,messages:[{conversationId:chosen,requestId:request,senderId:u,content:{kind:"TEXT",text:"discovery"},messageId:uid(local?91006:91007),seq:1,createdAt:"2026-10-03T00:00:00Z"}],hasMore:false});};
 const owner=fakeSend(fresh),app=new SyncApplication(owner,new SyncHttp("https://localhost/",session,fetchDiscovery));
 if(local)await app.synchronize();else await app.openConversation(chosen);
 assert.equal(pulled,1);assert.equal(await fresh.contiguous(chosen),1n);assert.equal((await fresh.messages(chosen))[0][3],"SENT");assert.equal(await fresh.cursor(),"0");await app.close();
}

// Raw API defaults must reject fixture CA; no product trust override.
const env={...process.env};delete env.NODE_EXTRA_CA_CERTS;
const rejection=spawnSync(process.execPath,["--input-type=module","-e","try { await fetch(process.argv[1]); process.exit(2); } catch { process.exit(0); }",endpoint],{env,encoding:"utf8"});assert.equal(rejection.status,0);
rmSync(root,{recursive:true,force:true});
console.log("PASS: actual Desktop SQLx+HTTPS+WSS 205->208 complete pagination, all Conversation gaps/realtime duplicates, FAILED->SENT/local-first/restart/reconnect/403, atomic rollback, in-flight retirement/401/mismatched session and untrusted CA");

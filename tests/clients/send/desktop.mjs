import assert from "node:assert/strict";
import {spawnSync} from "node:child_process";
import {mkdtempSync} from "node:fs";
import {tmpdir} from "node:os";
import {join,resolve} from "node:path";
import {Repository} from "../../../clients/shared/protocol-sdk/dist/storage/repository.js";
import {SendApplication} from "../../../clients/desktop/dist/desktop/src/application/send.js";
const probe=resolve(process.argv[2]), endpoint=process.argv[3];
const root=mkdtempSync(join(tmpdir(),'im-send-'));
const user='10000000-0000-4000-8000-000000000001', sessionId='20000000-0000-4000-8000-000000000001', c='30000000-0000-4000-8000-000000000001';
const session={userId:user,sessionId,sessionEpoch:1n,accessToken:'fixture-desktop'};
const hex=s=>Buffer.from(s,'utf8').toString('hex'),bind=s=>s===null?'~':hex(s);
function database(account=user) {
  function call(input) {const r=spawnSync(probe,[root,account],{input,encoding:'utf8',maxBuffer:8*1024*1024});if(r.error)throw r.error;if(r.status)throw new Error('Native storage failed');return r.stdout;}
  return {async transaction(steps){call(steps.map(([sql,args,changes])=>['T',changes??'-',hex(sql),...args.map(bind)].join('\t')).join('\n')+'\n');},async query(sql,args){const raw=call(['Q',hex(sql),...args.map(bind)].join('\t')+'\n').trimEnd();return raw?raw.split(/\r?\n/).map(line=>line.split('\t').map(v=>v==='~'?null:Buffer.from(v,'hex').toString('utf8'))):[];}};
}
const repo=new Repository(database());await repo.initialize();
const delay=n=>new Promise(r=>setTimeout(r,n));
async function until(check){for(let n=0;n<200;n++){if(await check())return;await delay(10);}throw new Error('Condition timed out');}
function application(timeout=120){return new SendApplication(repo,session,undefined,timeout);}
async function connect(app,mode='normal'){app.connect(endpoint+'/'+mode);await until(()=>app.state.connection==='ready');await app.openConversation(c);}
let app=application();await app.openConversation(c);
const offline=await app.send(c,'offline');assert.equal((await repo.messages(c)).find(row=>row[0]===offline)[3],'FAILED');
await connect(app);const seen=[];app.observe(s=>seen.push(s.messages.find(row=>row[0]===offline)?.[3]));await app.retry(c,offline);await until(()=>app.state.messages.find(row=>row[0]===offline)?.[3]==='SENT');assert(seen.includes('SENDING'));assert.equal((await repo.messages(c)).find(row=>row[0]===offline)[5],'9007199254740993');
app.close();app=application();await connect(app,'timeout');const timeout=await app.send(c,'retry after restart');await until(()=>app.state.messages.find(row=>row[0]===timeout)?.[3]==='FAILED');app.close();
app=application();await connect(app);await app.retry(c,timeout);await until(()=>app.state.messages.find(row=>row[0]===timeout)?.[3]==='SENT');assert.equal((await repo.messages(c)).filter(row=>row[0]===timeout).length,1);app.close();
app=application();await connect(app,'late');const late=await app.send(c,'late');await until(()=>app.state.messages.find(row=>row[0]===late)?.[3]==='FAILED');await until(()=>app.state.messages.find(row=>row[0]===late)?.[3]==='SENT');await delay(150);assert.equal(app.state.messages.find(row=>row[0]===late)[3],'SENT');app.close();
app=application();await connect(app,'realtime');const realtime=await app.send(c,'event-first');await until(()=>app.state.messages.find(row=>row[0]===realtime)?.[3]==='SENT');assert.equal(app.state.messages.filter(row=>row[0]===realtime).length,1);app.close();
app=application();await connect(app,'reject');const rejected=await app.send(c,'denied');await until(()=>app.state.messages.find(row=>row[0]===rejected)?.[3]==='FAILED');app.close();
app=application();await connect(app,'invalid');const invalid=await app.send(c,'invalid-ACK');await until(()=>app.state.connection==='offline');await app.idle();assert.equal((await repo.messages(c)).find(row=>row[0]===invalid)[3],'FAILED');assert.equal(app.state.error,'protocol');app.close();
app=application();await connect(app,'revoked');const revoked=await app.send(c,'revoked-session');await until(()=>app.state.connection==='offline');await app.idle();assert.equal((await repo.messages(c)).find(row=>row[0]===revoked)[3],'FAILED');const afterRevocation=await app.send(c,'offline after revoke');assert.equal((await repo.messages(c)).find(row=>row[0]===afterRevocation)[3],'FAILED');app.close();
app=application();app.connect(endpoint+'/wrong-session');await until(()=>app.state.error==='protocol');assert.equal(app.state.connection,'offline');app.close();
// Actual SQLx rollback before transmission and before SENT publication.
let fault=false;const db=database();const faulty=new Repository({...db,transaction:steps=>db.transaction(fault?[...steps,['INSERT INTO __send_fault_missing_table VALUES(1)',[],null]]:steps)});await faulty.initialize();
let socket, transmitted=0;const frames=[];
const factory=()=>socket={onopen:null,onmessage:null,onclose:null,onerror:null,send(raw){frames.push(JSON.parse(raw));if(JSON.parse(raw).type==='message.send')transmitted++;},close(){}};
app=new SendApplication(faulty,session,factory,60);await app.openConversation(c);app.connect('wss://localhost/');socket.onopen(new Event('open'));let auth;
// Bind uses the application's own auth request identity.
app.disconnect();await app.idle();app.connect('wss://localhost/');socket.onopen(new Event('open'));auth=frames.at(-1);
const deliver=(s,type,r,p)=>s.onmessage?.(new MessageEvent('message',{data:JSON.stringify({protocolVersion:'1.0',type,requestId:r,payload:p})}));
deliver(socket,'auth.ack',auth.requestId,{status:'bound',userId:user,sessionId,clientType:'DESKTOP',sessionEpoch:1});await app.idle();
fault=true;await assert.rejects(app.send(c,'rollback'));assert.equal(transmitted,0);fault=false;
const timer=await app.send(c,'new attempt timer');await delay(25);await app.retry(c,timer);await delay(40);await app.idle();assert.equal(app.state.messages.find(row=>row[0]===timer)[3],'SENDING');deliver(socket,'message.ack',timer,{status:'committed',conversationId:c,messageId:crypto.randomUUID(),seq:7,createdAt:'2026-10-03T00:00:00Z'});await app.idle();await delay(80);assert.equal(app.state.messages.find(row=>row[0]===timer)[3],'SENT');
const failure=await app.send(c,'ack rollback');fault=true;deliver(socket,'message.ack',failure,{status:'committed',conversationId:c,messageId:crypto.randomUUID(),seq:3,createdAt:'2026-10-03T00:00:00Z'});await app.idle();assert.equal((await repo.messages(c)).find(row=>row[0]===failure)[3],'SENDING');assert.equal(app.state.messages.find(row=>row[0]===failure)[3],'SENDING');fault=false;
const old=socket,oldCallback=socket.onmessage;app.disconnect();await app.idle();app.connect('wss://localhost/');oldCallback(new MessageEvent('message',{data:JSON.stringify({protocolVersion:'1.0',type:'message.ack',requestId:failure,payload:{status:'committed',conversationId:c,messageId:crypto.randomUUID(),seq:4,createdAt:'2026-10-03T00:00:00Z'}})}));await app.idle();assert.equal((await repo.messages(c)).find(row=>row[0]===failure)[3],'FAILED');app.close();
// Sync convergence calls the same existing Repository; no fetch runner.
app=application();await app.openConversation(c);await app.mergeMessages([{conversationId:c,requestId:rejected,senderId:user,content:{kind:'TEXT',text:'denied'},messageId:crypto.randomUUID(),seq:99n,createdAt:'2026-10-03T00:00:00Z'}]);assert.equal(app.state.messages.find(row=>row[0]===rejected)[3],'SENT');await app.retry(c,rejected);assert.equal(app.state.messages.find(row=>row[0]===rejected)[3],'SENT');app.close();assert.deepEqual(app.state.messages,[]);
const otherRepo=new Repository(database('10000000-0000-4000-8000-000000000002'));await otherRepo.initialize();assert.equal((await otherRepo.messages(c)).length,0);
console.log('PASS: actual SQLx + builtin WSS TLS send, persisted SENDING, timeout/offline/reject, same-ID restart retry, late ACK/realtime/Sync terminal merge, strict invalid/session checks, transactional rollback, stale socket and account isolation');

// Real accepted Go entry; credentials arrive on private stdin, never argv/logs.
import assert from "node:assert/strict";
import {readFileSync,mkdtempSync} from "node:fs";
import {spawnSync} from "node:child_process";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {Repository} from "../../../clients/shared/protocol-sdk/dist/storage/repository.js";
import {SendApplication} from "../../../clients/desktop/dist/desktop/src/application/send.js";
const config=JSON.parse(readFileSync(0,'utf8')),root=mkdtempSync(join(tmpdir(),'im-send-go-'));
const hex=s=>Buffer.from(s,'utf8').toString('hex'),bind=s=>s===null?'~':hex(s);
function call(input){const r=spawnSync(config.probe,[root,config.session.userId],{input,encoding:'utf8'});if(r.error||r.status)throw new Error('SQLx failed');return r.stdout;}
const db={async transaction(steps){call(steps.map(([sql,args,count])=>['T',count??'-',hex(sql),...args.map(bind)].join('\t')).join('\n')+'\n');},async query(sql,args){const s=call(['Q',hex(sql),...args.map(bind)].join('\t')+'\n').trimEnd();return s?s.split(/\r?\n/).map(line=>line.split('\t').map(v=>v==='~'?null:Buffer.from(v,'hex').toString('utf8'))):[];}};
const repo=new Repository(db);await repo.initialize();const session={...config.session,sessionEpoch:BigInt(config.session.sessionEpoch)};
const delay=n=>new Promise(r=>setTimeout(r,n));async function until(check){for(let n=0;n<1000;n++){if(check())return;await delay(10);}throw new Error('Go client confirmation timeout');}
let app=new SendApplication(repo,session);await app.openConversation(config.conversationId);
// Save the intent while offline, then recover it through a new application.
const requestId=await app.send(config.conversationId,'actual-client-send');assert.equal(app.state.messages[0][3],'FAILED');app.close();
app=new SendApplication(repo,session);await app.openConversation(config.conversationId);app.connect(config.endpoint);await until(()=>app.state.connection==='ready');await app.retry(config.conversationId,requestId);await until(()=>app.state.messages[0]?.[3]==='SENT');
const row=(await repo.messages(config.conversationId))[0];await app.retry(config.conversationId,requestId);await delay(300);assert.equal((await repo.messages(config.conversationId)).length,1);assert.equal(app.state.messages[0][3],'SENT');app.close();
console.log(JSON.stringify({result:'PASS',requestId,messageId:row[4],seq:row[5]}));

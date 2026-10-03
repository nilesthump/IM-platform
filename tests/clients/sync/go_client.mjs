// Credentials arrive only on private stdin; output contains public counts/positions.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {spawnSync} from "node:child_process";
const config=JSON.parse(readFileSync(0,"utf8")),session={...config.session,sessionEpoch:BigInt(config.session.sessionEpoch)};
if(config.probe){
 const {Repository}=await import("../../../clients/desktop/dist/shared/protocol-sdk/src/storage/repository.js");
 const {SendApplication}=await import("../../../clients/desktop/dist/desktop/src/application/send.js");
 const {SyncApplication}=await import("../../../clients/desktop/dist/desktop/src/application/sync/application.js");
 const {SyncHttp}=await import("../../../clients/desktop/dist/shared/protocol-sdk/src/sync/http.js");
 const hex=s=>Buffer.from(s).toString("hex"),bind=s=>s===null?"~":hex(s);
 function call(input){const r=spawnSync(config.probe,[config.localRoot,session.userId],{input,encoding:"utf8",maxBuffer:10*1024*1024});if(r.status || r.error)throw new Error("Actual SQLx failed");return r.stdout;}
 const db={async transaction(steps){call(steps.length?steps.map(([sql,args,count])=>["T",count??"-",hex(sql),...args.map(bind)].join("\t")).join("\n")+"\n":"");},async query(sql,args){const s=call(["Q",hex(sql),...args.map(bind)].join("\t")+"\n").trimEnd();return s?s.split(/\r?\n/).map(l=>l.split("\t").map(v=>v==="~"?null:Buffer.from(v,"hex").toString())):[];}};
 const repo=new Repository(db);await repo.initialize();const send=new SendApplication(repo,session,undefined,100,()=>config.firstRequestId);await send.openConversation(config.conversationId);
 if(config.phase===1){await send.send(config.conversationId,"actual-sync-0");assert.equal(send.state.messages[0][3],"FAILED");}
 const sync=new SyncApplication(send,new SyncHttp(config.endpoint,session));send.connect(config.endpoint.replace("https:","wss:")+"/v1/ws");
 for(let n=0;n<500 && send.state.connection!=="ready";n++)await new Promise(r=>setTimeout(r,10));assert.equal(send.state.connection,"ready");
 await sync.synchronize();await sync.idle();assert.equal(await repo.contiguous(config.conversationId),BigInt(config.expected));assert.equal((await repo.messages(config.conversationId)).length,config.expected);assert.equal(send.state.messages.find(r=>r[0]===config.firstRequestId)[3],"SENT");
 const cursor=await repo.cursor();assert.notEqual(cursor,"0");await sync.close();
 console.log(JSON.stringify({result:"PASS",mode:"Desktop-SQLx",messages:config.expected,cursor}));
}else{
 const {SyncHttp}=await import("../../../clients/shared/protocol-sdk/dist/sync/http.js");const http=new SyncHttp(config.endpoint,session),signal=new AbortController().signal;
 let cursor=config.cursor??"0",events=0,pages=0;do {const p=await http.user(cursor,signal);events+=p.events.length;pages++;cursor=p.nextCursor;if(!p.hasMore)break;}while(true);
 let seq=BigInt(config.afterSeq??0),messages=0,messagePages=0;do {const p=await http.conversation(config.conversationId,seq,signal);messages+=p.messages.length;messagePages++;if(p.messages.length)seq=BigInt(p.messages.at(-1).seq);if(!p.hasMore)break;}while(true);
 assert.equal(seq,BigInt(config.expected));assert.equal(messages,config.phase===1?205:1);assert.equal(events,config.phase===1?208:1);if(config.phase===1){assert.equal(pages,3);assert.equal(messagePages,3);}
 console.log(JSON.stringify({result:"PASS",mode:"shared-HTTPS",messages:messages,cursor,afterSeq:String(seq)}));
}

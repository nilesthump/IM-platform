import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { Repository } from "../../../clients/shared/protocol-sdk/dist/storage/repository.js";
import { v1, v2 } from "../../../clients/shared/protocol-sdk/dist/storage/schema.js";
const probe=resolve(process.argv[2]);
const root=mkdtempSync(join(tmpdir(),"im-desktop-storage-"));
const account="10000000-0000-4000-8000-000000000001";
const other="10000000-0000-4000-8000-000000000002";
const c="30000000-0000-4000-8000-000000000001";
const c2="30000000-0000-4000-8000-000000000002";
const r="40000000-0000-4000-8000-000000000001";
const id="50000000-0000-4000-8000-000000000001";
const hex=s=>Buffer.from(s,"utf8").toString("hex");
const bind=s=>s===null?"~":hex(s);
let assertions=0;
function equal(actual,expected) { assert.deepEqual(actual,expected); assertions++; }
function database(accountId) {
  function call(input) {
    const result=spawnSync(probe,[root,accountId],{input,encoding:"utf8",maxBuffer:8*1024*1024});
    if(result.error) throw result.error;
    if(result.status!==0) throw new Error(result.stderr.trim()||"Native adapter failed");
    return result.stdout;
  }
  return {
    async transaction(steps) { call(steps.map(([sql,args,changes])=>["T",changes??"-",hex(sql),...args.map(bind)].join("\t")).join("\n")+"\n"); },
    async query(sql,args) {
      const output=call(["Q",hex(sql),...args.map(bind)].join("\t")+"\n").trimEnd();
      return output?output.split(/\r?\n/).map(line=>line.split("\t").map(v=>v==="~"?null:Buffer.from(v,"hex").toString("utf8"))):[];
    },
  };
}
const golden=JSON.parse(readFileSync(new URL("../../../contracts/fixtures/sync-plugin/golden.json",import.meta.url)));
const cases=golden.cases.filter(test=>test.steps.every(s=>["sync.message","sync.user","local.failed"].includes(s.op)));
let index=10;
for(const test of cases) {
  const accountId="10000000-0000-4000-8000-"+String(index++).padStart(12,"0");
  const repo=new Repository(database(accountId)); await repo.initialize();
  let error=false; let cursor="0";
  for(let i=0;i<test.steps.length;i++) {
    const s=test.steps[i]; let last;
    try {
      if(s.op==="local.failed") {
        if(!(await repo.messages(s.conversationId)).some(row=>row[0]===s.requestId)) {
          const future=test.steps.find(x=>x.message?.requestId===s.requestId).message;
          await repo.localSend(future);
        }
        await repo.markFailed(s.conversationId,s.requestId);
        last=(await repo.messages(s.conversationId)).find(row=>row[0]===s.requestId)[3];
      } else if(s.op==="sync.message") {
        await repo.syncMessages([s.message],s.fault==="before_commit"); last="APPLIED";
      } else {
        await repo.userPage(s.page,cursor,s.fault==="before_commit"); cursor=s.page.nextCursor; last="APPLIED";
      }
    } catch(e) {
      if(s.fault==="before_commit") last="ROLLED_BACK";
      else { error=true; break; }
    }
    const expected=test.expect?.timeline?.[i];
    const conversation=s.message?.conversationId??c;
    if(expected) {
      equal(await repo.cursor(),expected.cursor);
      equal(await repo.contiguous(conversation),expected.contiguous);
      equal(Object.fromEntries((await repo.messages(conversation)).filter(row=>row[5]!==null).map(row=>[row[5],row[4]])),expected.messages);
      equal(Object.fromEntries((await repo.db.query("SELECT kind,subject_id,CAST(revision AS TEXT) FROM user_state",[])).map(row=>[row[0]+"/"+row[1],Number(row[2])])),expected.userState);
      equal(last,expected.last);
    }
    const localExpected=test.expect?.localTimeline?.[i];
    if(localExpected) {
      const rows=await repo.messages(s.conversationId??s.message.conversationId);
      equal(rows.length,localExpected.itemCount);
      equal(Object.fromEntries(rows.filter(row=>row[0]!==null).map(row=>[(s.conversationId??s.message.conversationId)+"/"+row[0],row[3]])),localExpected.local);
      equal(last,localExpected.last);
    }
  }
  equal(error,Boolean(test.expectError));
  if(!error) {
    if(test.expect?.contiguous!==undefined) equal(await repo.contiguous(test.steps.find(s=>s.message)?.message.conversationId??c),test.expect.contiguous);
    if(test.expect?.cursor!==undefined) equal(await repo.cursor(),test.expect.cursor);
    for(const [conversation,expected] of Object.entries(test.expect?.conversations??{})) {
      equal(await repo.contiguous(conversation),expected.contiguous);
      equal(Object.fromEntries((await repo.messages(conversation)).map(row=>[row[5],row[4]])),expected.messages);
    }
  }
}
const db=database(account);
await db.transaction(readFileSync(new URL("./v1.sql",import.meta.url),"utf8").split(";").filter(s=>s.trim()).map(s=>[s,[],null]));
const repo=new Repository(db);
const local={conversationId:c,requestId:r,senderId:account,content:{kind:"TEXT",text:"durable"}};
await repo.localSend(local);
await assert.rejects(db.transaction([...v2.slice(0,1),["INSERT INTO missing_table VALUES(1)",[],null],...v2.slice(1)])); assertions++;
equal(Number((await db.query("PRAGMA user_version",[]))[0][0]),1);
equal((await db.query("SELECT name FROM sqlite_master WHERE name='user_state'",[])).length,0);
await repo.initialize();
equal((await repo.messages(c))[0][2],"durable");
const server={...local,messageId:id,seq:1,createdAt:"2026-09-28T00:00:01Z"};
const {requestId,...realtime}=server;
await repo.realtime(realtime);
equal((await repo.messages(c)).length,2); // request is absent from realtime payload
await repo.committedAck(r,{status:"committed",...server});
equal((await repo.messages(c)).length,1);
await repo.markFailed(c,r);
await repo.localSend(local);
equal((await repo.messages(c))[0][3],"SENT");
await repo.syncMessages([server,server]); equal((await repo.messages(c)).length,1);
await assert.rejects(repo.syncMessages([{...server,content:{kind:"TEXT",text:"changed"}}])); assertions++;
await assert.rejects(repo.localSend({...local,content:{kind:"TEXT",text:"changed"}})); assertions++;
await assert.rejects(repo.syncMessages([{...server,conversationId:c2}])); assertions++; // global message identity
await assert.rejects(repo.syncMessages([{...server,messageId:"50000000-0000-4000-8000-000000000009"}])); assertions++;
equal((await repo.messages(c))[0][2],"durable"); equal(await repo.contiguous(c),1);
const next={...server,requestId:"40000000-0000-4000-8000-000000000002",messageId:"50000000-0000-4000-8000-000000000002",seq:2};
await assert.rejects(repo.syncMessages([next],true)); assertions++;
equal((await repo.messages(c)).length,1); equal(await repo.contiguous(c),1);
await repo.syncMessages([next]); equal(await repo.contiguous(c),2);
const restart=new Repository(database(account)); await restart.initialize();
equal(await restart.messages(c),await repo.messages(c));
const isolated=new Repository(database(other)); await isolated.initialize(); equal(await isolated.messages(c),[]);
const crossedId="50000000-0000-4000-8000-000000000003";
const crossed={...server,conversationId:c2,messageId:crossedId};
await repo.realtime({...realtime,conversationId:c2,messageId:crossedId});
await repo.localSend({...local,conversationId:c2});
await repo.syncMessages([crossed]); equal((await repo.messages(c2)).length,1); equal(await repo.contiguous(c2),1);
await repo.committedAck(r,{status:"committed",...crossed}); equal((await repo.messages(c2)).length,1);
await assert.rejects(db.query("DELETE FROM messages RETURNING content",[])); assertions++;
equal((await repo.messages(c)).length,2);
const unicode=new Repository(database("10000000-0000-4000-8000-000000000003"));
await unicode.initialize();
const emoji="\u{1f600}".repeat(4096);
const unicodeLocal={...local,content:{kind:"TEXT",text:emoji}};
await unicode.localSend(unicodeLocal);
const unicodeServer={...server,content:unicodeLocal.content};
await unicode.syncMessages([unicodeServer]);
equal((await unicode.messages(c))[0][2],emoji);
const durableUnicode=await unicode.messages(c);
await assert.rejects(unicode.localSend({...unicodeLocal,requestId:"40000000-0000-4000-8000-000000000009",content:{kind:"TEXT",text:emoji+"\u{1f600}"}})); assertions++;
equal(await unicode.messages(c),durableUnicode);
await assert.rejects(unicode.syncMessages([{...unicodeServer,requestId:"40000000-0000-4000-8000-000000000009",messageId:"50000000-0000-4000-8000-000000000009",seq:2,content:{kind:"TEXT",text:emoji+"\u{1f600}"}}])); assertions++;
equal(await unicode.messages(c),durableUnicode); equal(await unicode.contiguous(c),1); equal(await unicode.cursor(),"0");
const unicodeRestart=new Repository(database("10000000-0000-4000-8000-000000000003")); await unicodeRestart.initialize();
equal(await unicodeRestart.messages(c),durableUnicode);
console.log(JSON.stringify({result:"PASS",engine:"actual SQLx SQLite",canonicalCases:cases.length,assertions,root}));

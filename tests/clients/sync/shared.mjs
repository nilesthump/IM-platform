import assert from "node:assert/strict";
import {userPage,conversationPage,conversationRequest,MAX_RESPONSE,errorResponse,SyncFailure} from "../../../clients/shared/protocol-sdk/dist/sync/wire.js";
import {SyncHttp} from "../../../clients/shared/protocol-sdk/dist/sync/http.js";
import {decode} from "../../../clients/shared/protocol-sdk/dist/send/wire.js";
const id="40000000-0000-4000-8000-000000000001",c="30000000-0000-4000-8000-000000000001",u="10000000-0000-4000-8000-000000000001";
const uid=n=>"50000000-0000-4000-8000-"+String(n).padStart(12,"0");
const event={eventId:id,cursor:"opaque",kind:"conversation.changed",subjectId:c,revision:1};
const page={syncVersion:"1.0",type:"sync.user.page",requestId:id,events:[event],nextCursor:"opaque",hasMore:false};
const message=n=>({conversationId:c,seq:n,messageId:uid(n),senderId:u,requestId:uid(n+1000),createdAt:"2026-10-03T00:00:00Z",content:{kind:"TEXT",text:"😀".repeat(4096)}});
const cp={syncVersion:"1.0",type:"sync.conversation.page",requestId:id,conversationId:c,messages:Array.from({length:100},(_,i)=>message(i+1)),hasMore:true};
const json=p=>JSON.stringify(p),throws=f=>assert.throws(f,/Invalid Sync response/);
assert.equal(userPage(json(page),id,"0").events[0].revision,1n);
for(const n of ["9007199254740993","9007199254740993.0","90071992547409930e-1"])assert.equal(userPage(json(page).replace('"revision":1','"revision":'+n),id,"0").events[0].revision,9007199254740993n);
for(const p of [{...page,hasMore:"false"},{...page,nextCursor:"different"},{...page,events:[],hasMore:true},{...page,extra:1},{...page,syncVersion:"2.0"},{...page,events:[{...event,kind:"message.created"}]},{...page,events:[event,event]}])throws(()=>userPage(json(p),id,"0"));
throws(()=>userPage(json(page).replace('"revision":1','"revision":1,"revision":2'),id,"0"));
throws(()=>userPage(json(page),uid(999),"0"));
assert.equal(conversationPage(json(cp),id,c,0n).messages.length,100);
const escaped=json(cp).replaceAll("😀","\\ud83d\\ude00");assert(Buffer.byteLength(escaped)<MAX_RESPONSE);assert.equal(conversationPage(escaped,id,c,0n).messages[99].content.text,cp.messages[99].content.text);
for(const p of [{...cp,messages:[message(2)]},{...cp,messages:[message(1),message(1)]},{...cp,messages:[],hasMore:true},{...cp,messages:[{...message(1),conversationId:u}]},{...cp,messages:[{...message(1),content:{kind:"TEXT",text:"😀".repeat(4097)}}]},{...cp,messages:Array.from({length:101},(_,i)=>message(i+1))}])throws(()=>conversationPage(json(p),id,c,0n));
assert(conversationRequest(id,c,9007199254740993n).includes('"afterSeq":9007199254740993'));
const huge={...cp,messages:[{...message(1),seq:1,content:{kind:"TEXT",text:"x"}}],hasMore:false};
assert.equal(conversationPage(json(huge).replace('"seq":1','"seq":9007199254740993'),id,c,9007199254740992n).messages[0].seq,9007199254740993n);
assert.equal(errorResponse(json({requestId:id,error:{code:"AUTH_SESSION_REVOKED",message:"Revoked"}}),id,401,false).kind,"authentication");
assert.equal(errorResponse(json({requestId:id,error:{code:"AUTHORIZATION_DENIED",message:"Denied"}}),id,403,true).kind,"unavailable");
assert.equal(errorResponse(json({requestId:id,error:{code:"AUTHORIZATION_DENIED",message:"Denied"}}),id,403,false).kind,"protocol");
// Nonstring enum values must never inherit array/object String coercion.
const malformedEnum=value=>[[value],[[value]],{value},true,false,1];
const syncAuthCodes=["AUTH_REQUIRED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH"];
for(const kind of ["friend.changed","conversation.changed","membership.changed","plugin.changed"]) {
  assert.equal(userPage(json({...page,events:[{...event,kind}]}),id,"0").events[0].kind,kind);
  for(const invalidKind of malformedEnum(kind)) throws(()=>userPage(json({...page,events:[{...event,kind:invalidKind}]}),id,"0"));
}
for(const code of syncAuthCodes) {
  assert.equal(errorResponse(json({requestId:id,error:{code,message:"Error"}}),id,401,false).kind,"authentication");
  for(const invalidCode of malformedEnum(code)) assert.equal(errorResponse(json({requestId:id,error:{code:invalidCode,message:"Error"}}),id,401,false).kind,"protocol");
}
const wss=(type,payload)=>json({protocolVersion:"1.0",type,requestId:id,payload});
const rejectedCodes={
  "auth.ack":["VALIDATION_FAILED","AUTH_TOKEN_INVALID","AUTH_TOKEN_EXPIRED","AUTH_SESSION_REVOKED","AUTH_SESSION_EPOCH_STALE","AUTH_CLIENT_TYPE_MISMATCH","PROTOCOL_VERSION_UNSUPPORTED"],
  "message.ack":["VALIDATION_FAILED","AUTH_REQUIRED","AUTH_SESSION_REVOKED","AUTHORIZATION_DENIED","MESSAGE_REQUEST_CONFLICT","MESSAGE_COMMIT_FAILED"]
};
for(const [type,codes] of Object.entries(rejectedCodes)) for(const code of codes) {
  assert.equal(decode(wss(type,{status:"rejected",error:{code,message:"Error"}})).payload.error.code,code);
  for(const invalidCode of malformedEnum(code)) assert.throws(()=>decode(wss(type,{status:"rejected",error:{code:invalidCode,message:"Error"}})),/Invalid WSS frame/);
}
for(const clientType of ["WEB","DESKTOP","MOBILE"]) {
  const payload={status:"bound",userId:u,sessionId:id,clientType,sessionEpoch:1};
  assert.equal(decode(wss("auth.ack",payload)).payload.clientType,clientType);
  for(const invalidType of malformedEnum(clientType)) assert.throws(()=>decode(wss("auth.ack",{...payload,clientType:invalidType})),/Invalid WSS frame/);
}
for(const reason of ["LOGOUT","REPLACED","REVOKED"]) {
  assert.equal(decode(wss("session.revoked",{sessionId:id,reason})).payload.reason,reason);
  for(const invalidReason of malformedEnum(reason)) assert.throws(()=>decode(wss("session.revoked",{sessionId:id,reason:invalidReason})),/Invalid WSS frame/);
}
const session={userId:u,sessionId:id,sessionEpoch:1n,accessToken:"fixture-desktop"};
for(const url of ["http://localhost/","https://user@localhost/","https://localhost/?token=x","https://localhost/sub"])assert.throws(()=>new SyncHttp(url,session));
let calls=0;
const http=new SyncHttp("https://localhost/",session,async (url,options)=>{
calls++;assert.equal(url,"https://localhost/v1/sync/user");assert.equal(options.redirect,"error");assert.equal(options.credentials,"omit");assert.equal(options.cache,"no-store");assert.equal(options.headers.Authorization,"Bearer fixture-desktop");const request=JSON.parse(options.body);assert.equal(request.limit,100);
return new Response(json({...page,requestId:request.requestId}),{headers:{"content-type":"application/json","cache-control":"no-store"}});
});
assert.equal((await http.user("0",new AbortController().signal)).nextCursor,"opaque");assert.equal(calls,1);
const bad=new SyncHttp("https://localhost/",session,async()=>new Response("x".repeat(MAX_RESPONSE+1),{headers:{"content-type":"application/json","cache-control":"no-store"}}));
await assert.rejects(bad.user("0",new AbortController().signal),SyncFailure);
const frame=json({protocolVersion:"1.0",type:"ping",requestId:id,payload:{}});
assert.throws(()=>decode(" ".repeat(131073)+frame));
console.log("PASS: exact Sync correlation/shapes/gap/progress/kinds/numbers, 100x4096 escaped/literal Unicode bounded transport, strict nonstring Sync/WSS enums and WSS bound regression");

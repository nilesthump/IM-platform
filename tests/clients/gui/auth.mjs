// UI auth boundary controls; no screenshots or durable ACK acceptance claimed.
import assert from "node:assert/strict";
const credentials=new Map(),requests=[],appearanceSaves=[];
const A="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",B="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",S="11111111-1111-4111-8111-111111111111";
let reply,delayed=null,delayedPath="";
globalThis.window={__TAURI_INTERNALS__:{invoke:async(command,args)=>{
  if(command==="credential_read")return credentials.get(args.slot)??null;
  if(command==="credential_write"){credentials.set(args.slot,args.value);return;}
  if(command==="credential_remove"){credentials.delete(args.slot);return;}
  // Stub only empty initialization reads for application lifecycle races.
  // These rows never establish SQLite/Send/ACK behavior acceptance.
  if(command==="database_query")return args.sql==="PRAGMA user_version"?[["2"]]:[];
  if(command==="database_transaction")return;
  if(command==="appearance_save"){appearanceSaves.push(args.value);return;}
  if(command==="native_https"){
    requests.push(args);if(delayed && (!delayedPath||args.url.includes(delayedPath)))return delayed;
    return [reply.status??200,{"content-type":"application/json","cache-control":"no-store"},Array.from(new TextEncoder().encode(reply.raw??JSON.stringify(reply.data)))];
  }
  throw Error("Unexpected command");
}}};
const {Auth,origin}=await import("../../../clients/desktop/dist/desktop/src/application/ui/auth.js");
const authResult=(user,token="fixture-rotation")=>({session:{sessionId:S,userId:user,clientType:"DESKTOP",sessionEpoch:9007199254740993n,status:"ACTIVE"},tokens:{accessToken:"fixture-access",accessTokenExpiresInSeconds:300,refreshToken:token,refreshTokenExpiresInSeconds:86400,refreshTokenDelivery:"RESPONSE_BODY_FOR_OS_SECURE_STORAGE"},replacedExistingSession:false});
const encode=v=>JSON.stringify(v,(_,value)=>typeof value==="bigint"?"INTEGER:"+value:value).replace(/"INTEGER:(\d+)"/g,"$1");
reply={raw:encode(authResult(A))};const auth=new Auth("https://localhost:8443");
const session=await auth.login("fixture-user","fixture-only-input");assert.equal(session.sessionEpoch,9007199254740993n);assert.equal(credentials.size,2);
assert.equal(requests[0].url,"https://localhost:8443/v1/auth/login");const body=JSON.parse(new TextDecoder().decode(new Uint8Array(requests[0].body)));assert.equal(body.clientType,"DESKTOP");assert.equal(body.protocolVersion,"1");assert(!Object.hasOwn(requests[0].headers,"authorization"));
reply={raw:encode(authResult(A,"fixture-next"))};await auth.refresh();assert([...credentials.values()].includes("fixture-next"));assert(![...credentials.values()].includes("fixture-rotation"));
reply={data:{users:[]}};await auth.search("token");assert(requests.at(-1).url.endsWith("?username=token"));assert.equal(requests.at(-1).headers.authorization,"Bearer fixture-access");
assert.equal(await auth.savedAccount(),A);
reply={status:204,raw:""};await auth.logout();assert.equal(auth.session,null);assert.equal(credentials.size,0);
let release;delayed=new Promise(r=>{release=r;});const old=new Auth("https://localhost:8443");const pending=old.login("fixture-user","fixture-only-input");await new Promise(r=>setTimeout(r,0));await old.clear();release([200,{"content-type":"application/json"},Array.from(new TextEncoder().encode(encode(authResult(A))))]);await assert.rejects(pending,/Session expired/);assert.equal(credentials.size,0);delayed=null;
reply={raw:encode(authResult(B))};const next=new Auth("https://localhost:8443");await next.login("fixture-b","fixture-only-input");assert.equal(next.session.userId,B);assert(![...credentials.keys()].some(k=>k.includes(A)));
reply={status:401,data:{error:{code:"AUTH_REFRESH_REVOKED",message:"Expired"},requestId:S}};await assert.rejects(next.refresh(),/Session expired/);assert.equal(credentials.size,0);
for(const value of ["http://localhost","https://u:p@localhost","https://localhost/path","https://localhost/?token=x"])assert.throws(()=>origin(value));
reply={raw:encode(authResult(A)).replace('"sessionEpoch":9007199254740993','"sessionEpoch":1.5')};await assert.rejects(new Auth("https://localhost:8443").login("fixture-user","fixture-only-input"));assert.equal(credentials.size,0);
console.log("PASS GUI auth: exact epoch, canonical native metadata, rotation, OS storage intent, logout, delayed retired login isolation, account switch, expired cleanup, HTTPS origin and malformed response controls");
const {Workspace}=await import("../../../clients/desktop/dist/desktop/src/application/ui/workspace.js");
const workspace=new Workspace();
reply={status:204,raw:""};delayedPath="/v1/auth/login";delayed=new Promise(r=>{release=r;});
const retiredLogin=workspace.login("https://localhost:8443","fixture-a","fixture-only-input");await new Promise(r=>setTimeout(r,0));await workspace.logout();
release([200,{"content-type":"application/json"},Array.from(new TextEncoder().encode(encode(authResult(A))))]);await retiredLogin;
assert.equal(workspace.state.session,null);assert.equal(workspace.state.busy,false);assert.equal(workspace.state.error,null);assert.equal(credentials.size,0);delayed=null;
for(const operation of ["search","add"]){
  reply={raw:encode(authResult(A))};const owner=new Auth("https://localhost:8443");await owner.login("fixture-a","fixture-only-input");workspace.auth=owner;workspace.state={...workspace.state,session:owner.session};
  delayedPath=operation==="search"?"/v1/users/search":"/v1/friends/";delayed=new Promise(r=>{release=r;});
  const pending=operation==="search"?workspace.search("fixture-b"):workspace.add(B);await new Promise(r=>setTimeout(r,0));reply={status:204,raw:""};await workspace.logout();
  const data=operation==="search"?{users:[{userId:B,username:"fixture-b",displayName:"Fixture B"}]}:{friendshipId:S,normalizedPair:[A,B],directConversationId:S,memberUserIds:[A,B],created:true};
  release([200,{"content-type":"application/json"},Array.from(new TextEncoder().encode(JSON.stringify(data)))]);await pending;delayed=null;
  assert.equal(workspace.state.session,null);assert.equal(workspace.state.busy,false);assert.equal(workspace.state.results.length,0);assert.equal(workspace.state.conversations.length,0);assert.equal(credentials.size,0);
}
console.log("PASS GUI workspace: delayed login, search and add cannot repopulate a logged-out account or overwrite the current busy/error state");
reply={raw:encode(authResult(A))};const raceOwner=new Auth("https://localhost:8443");await raceOwner.login("fixture-a","fixture-only-input");workspace.auth=raceOwner;
let closeRelease;workspace.sync={close:()=>new Promise(r=>{closeRelease=r;})};workspace.operation=20;
const binding=workspace.bind(raceOwner.session,20);await new Promise(r=>setTimeout(r,0));reply={status:204,raw:""};await workspace.logout();closeRelease();await binding;
assert.equal(workspace.state.session,null);assert.equal(credentials.size,0);
reply={raw:encode(authResult(A))};const refreshOwner=new Auth("https://localhost:8443");await refreshOwner.login("fixture-a","fixture-only-input");workspace.auth=refreshOwner;workspace.state={...workspace.state,session:refreshOwner.session};
delayedPath="/v1/auth/refresh/native";delayed=new Promise(r=>{release=r;});const refresh=workspace.refresh();await new Promise(r=>setTimeout(r,0));reply={status:204,raw:""};await workspace.logout();release([200,{"content-type":"application/json"},Array.from(new TextEncoder().encode(encode(authResult(A))))]);await refresh;delayed=null;
assert.equal(workspace.state.session,null);assert.equal(workspace.state.error,null);assert.equal(credentials.size,0);
globalThis.WebSocket=class {onopen=null;onmessage=null;onclose=null;onerror=null;close(){};send(){}};
reply={raw:encode(authResult(A))};const profileOwner=new Auth("https://localhost:8443");await profileOwner.login("fixture-a","fixture-only-input");workspace.auth=profileOwner;workspace.operation=30;
delayedPath="/v1/users/me";delayed=new Promise(r=>{release=r;});const profile=workspace.bind(profileOwner.session,30);await new Promise(r=>setTimeout(r,10));reply={status:204,raw:""};await workspace.logout();
reply={raw:encode(authResult(B))};const profileNext=new Auth("https://localhost:8443");await profileNext.login("fixture-b","fixture-only-input");workspace.auth=profileNext;const nextUser={userId:B,username:"fixture-b",displayName:"Fixture B"};workspace.state={...workspace.state,session:profileNext.session,profile:nextUser};
const beforeFriends=requests.filter(r=>r.url.endsWith("/v1/friends")).length;
release([200,{"content-type":"application/json"},Array.from(new TextEncoder().encode(JSON.stringify({user:{userId:A,username:"fixture-a",displayName:"Fixture A"}})))]);await profile;delayed=null;
assert.equal(workspace.state.profile.userId,B);assert.equal(workspace.state.session.userId,B);assert.equal(requests.filter(r=>r.url.endsWith("/v1/friends")).length,beforeFriends);
reply={status:204,raw:""};await workspace.logout();assert.equal(credentials.size,0);
console.log("PASS GUI workspace: delayed close/bind, refresh and profile cannot restore or overwrite a retired account");
const font=workspace.preferences({...workspace.state.appearance,fontSize:22});const theme=workspace.preferences({...workspace.state.appearance,theme:"warm"});const density=workspace.preferences({...workspace.state.appearance,density:1.2});await Promise.all([font,theme,density]);
assert.deepEqual(appearanceSaves,[["cold",22,1],["warm",22,1],["warm",22,1.2]]);assert.deepEqual(workspace.state.appearance,{theme:"warm",fontSize:22,density:1.2});
console.log("PASS GUI appearance: rapid font/theme/density changes preserve independent intent and serialized native writes");

// Registration reuses the canonical endpoint, never sends confirmation.
reply={status:201,data:{user:{userId:A,username:"fixture-register",displayName:"fixture-register"}}};
const registeredUser=await new Auth("https://localhost:8443").register("fixture-register","fixture-register-only-input");
assert.equal(registeredUser.userId,A);
const registration=requests.at(-1);assert(registration.url.endsWith("/v1/auth/register"));
assert.deepEqual(JSON.parse(new TextDecoder().decode(new Uint8Array(registration.body))),{username:"fixture-register",password:"fixture-register-only-input",displayName:"fixture-register"});
assert(!Object.hasOwn(registration.headers,"authorization"));assert.equal(credentials.size,0);
const beforeRegistration=requests.length;
assert.equal(await workspace.register("fixture-register","fixture-register-only-input","different"),false);
assert.equal(requests.length,beforeRegistration);assert.equal(workspace.state.error,"Passwords do not match");
assert.equal(await workspace.register("fixture-register","short","short"),false);assert.equal(requests.length,beforeRegistration);
assert.equal(await workspace.register("fixture-register","fixture-register-only-input","fixture-register-only-input"),true);
assert.equal(workspace.state.session,null);
reply={status:409,data:{error:{code:"USERNAME_ALREADY_EXISTS"}}};
assert.equal(await workspace.register("fixture-register","fixture-register-only-input","fixture-register-only-input"),false);
assert.equal(workspace.state.error,"USERNAME_ALREADY_EXISTS");
// List includes all existing Repository identities (private + group), deterministic recency.
const direct=S,group="22222222-2222-4222-8222-222222222222";
const rows=new Map([[direct,[[null,A,"older","SENT",S,"1","2026-10-01T12:00:00Z"]]],[group,[[null,B,"newer","SENT",group,"1","2026-10-02T12:00:00Z"]]]]);
const projection={conversationIds:async()=>[direct,group],messages:async id=>rows.get(id)};
await workspace.updateList(projection,workspace.generation);assert.deepEqual(workspace.state.conversations,[group,direct]);
workspace.activity.set(direct,Date.parse("2026-10-03T12:00:00Z"));await workspace.updateList(projection,workspace.generation);assert.deepEqual(workspace.state.conversations,[direct,group]);
workspace.state={...workspace.state,selected:direct,page:"Chat",messages:rows.get(direct)};await workspace.open(direct);assert.equal(workspace.state.selected,"");assert.equal(workspace.state.messages.length,0);
let listRelease;const retiredList=workspace.updateList({conversationIds:()=>new Promise(r=>{listRelease=r;}),messages:async()=>rows.get(direct)},workspace.generation);
await workspace.logout();listRelease([direct]);await retiredList;assert.equal(workspace.state.conversations.length,0);assert.deepEqual(workspace.state.previews,{});
console.log("PASS registration canonical body/confirmation/malformed/conflict; private+group latest-first and retired-account list guard; desktop selected row closes detail");

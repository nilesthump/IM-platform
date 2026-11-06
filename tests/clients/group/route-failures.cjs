// Run the complete G06 runner with controlled browser/filesystem ports.
// This verifies callback failure propagation, not product or TLS acceptance.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const source=fs.readFileSync(process.argv[2]??path.join(__dirname,'web.cjs'),'utf8');
async function check(test){
 const original=test.falsy?test.value:new Error('route original\nCall log: PRIVATE_CALL_DETAIL');
 const abort=new Error('abort cleanup'),wait=new Error('UI wait'),close=new Error('browser cleanup');
 const logs=[],reports=[],aggregates=[],callbackErrors=[];let handler,entered=0,closed=false,releaseAbort;
 const body={requestId:'40000000-0000-4000-8000-000000000001',memberUserIds:['10000000-0000-4000-8000-000000000002']};
 const response={status:()=>201,json:async()=>({requestId:body.requestId,conversationId:'30000000-0000-4000-8000-000000000001'})};
 const route={request:()=>({method:()=>test.nonPost?'GET':'POST',postDataJSON:()=>body}),
  fetch:async()=>{if(!test.success)throw original;return response;},
  continue:async()=>{if(test.retry||test.nonPost)throw original;},
  abort:async reason=>{if(reason==='failed'&&test.deferred){await new Promise(resolve=>{releaseAbort=resolve});throw abort;}if(reason==='failed'&&test.abort)throw abort;}};
 function locator(action){return new Proxy({}, {get:(_,key)=>{
  if(key==='then')return undefined;
  if(key==='getByRole')return (role,options)=>locator(options?.name);
  if(key==='click')return async()=>{if(action==='Confirm'||action==='Retry original request'){entered++;const pending=handler(route);if(test.deferred)pending.catch(e=>callbackErrors.push(e));else await pending;}};
  if(key==='waitFor')return async()=>{await tick();if(action==='Submission unconfirmed. Retry the original request.'&&test.wait)throw wait;};
  return ()=>locator();
 }});}
 const page={on:()=>{},goto:async()=>{},getByLabel:()=>locator(),getByRole:(_,o)=>locator(o.name),getByText:t=>locator(t),
  locator:()=>locator(),screenshot:async()=>{},route:async(_,fn)=>{handler=fn;},unroute:async()=>{},waitForResponse:async()=>response};
 const browser={newContext:async()=>({newPage:async()=>page}),close:async()=>{closed=true;if(releaseAbort)releaseAbort();if(test.close)throw close;}};
 const config={playwright:'controlled-playwright',credentials:'controlled-input',out:'controlled-output',browser:'controlled-browser',modes:[test.retry?'before':'after']};
 const proc={argv:['node','web.cjs','controlled-config'],exitCode:0};
 const context={process:proc,Buffer,setTimeout,clearTimeout,console:{error:e=>logs.push(String(e)),log:e=>logs.push(String(e))},
  AggregateError:class extends AggregateError{constructor(errors,message){super(errors,message);aggregates.push(this);}}};
 context.require=id=>id==='node:fs'?{readFileSync:p=>JSON.stringify(p==='controlled-config'?config:{A:{username:'dummy',password:'dummy',userId:'10000000-0000-4000-8000-000000000001'},B:{username:'dummy'}}),mkdirSync:()=>{},writeFileSync:(p,data)=>reports.push({path:p,data:JSON.parse(data)}),existsSync:()=>true}:id==='controlled-playwright'?{chromium:{launch:async()=>browser}}:require(id);
 vm.runInNewContext(source,context,{filename:'actual-web.cjs'});
 for(let i=0;i<50;i++)await tick();
 assert.ok(entered>0,test.name+' callback executed: '+logs.join('; '));assert.ok(closed,test.name+' browser closed');
 assert.deepEqual(callbackErrors,[],test.name+' callback failures are owned by the runner');
 const report=reports.find(r=>r.path.endsWith('result.json'))?.data;assert.ok(report,test.name+' final report');
 if(test.success){assert.equal(proc.exitCode,0);assert.equal(report.result,'PASS_WEB_G06_UI_AND_REAL_RESPONSES');return;}
 assert.equal(proc.exitCode,1,test.name+' fails process');assert.equal(report.result,'FAIL',test.name+' fails report');
 assert.ok(!logs.some(s=>s.includes('PASS_WEB')),test.name+' no false PASS');
 const text=logs.join('\n');assert.ok(text.includes(test.falsy?String(original):'route original'),test.name+' public primary');
 assert.ok(!text.includes('PRIVATE_CALL_DETAIL'),test.name+' private call details excluded');
 const leaves=e=>Array.isArray(e?.errors)?e.errors.flatMap(leaves):[e];const originals=aggregates.flatMap(leaves);
 if(test.abort||test.deferred||test.wait||test.close){assert.ok(originals.includes(original),test.name+' exact primary');}
 for(const [enabled,value] of [[test.abort||test.deferred,abort],[test.wait,wait],[test.close,close]])if(enabled){assert.ok(originals.includes(value),test.name+' exact secondary');assert.ok(text.includes(value.message),test.name+' public secondary');}
 if(test.retry)assert.equal(entered,2,'later retry callback was exercised');
}
(async()=>{
 const cases=[{name:'success',success:true},{name:'primary'},{name:'primary-abort',abort:true},{name:'primary-wait',wait:true},
  {name:'primary-abort-wait-close',abort:true,wait:true,close:true},{name:'late-abort',deferred:true},
  {name:'retry-route',retry:true},{name:'non-post-route',nonPost:true}];
 for(const value of [null,undefined,0,false,''])cases.push({name:'falsy-'+String(value),falsy:true,value,abort:true,wait:true});
 const failures=[];for(const test of cases){try{await check(test);}catch(e){failures.push(e);}}
 if(failures.length)throw new AggregateError(failures,'Actual G06 route failure regressions');
 console.log('PASS '+cases.length+' actual G06 callback boundary cases; no product/TLS acceptance');
})().catch(error=>{console.error(error);process.exitCode=1});

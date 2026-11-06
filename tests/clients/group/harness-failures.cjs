// Full runner control flow; only external browser/fs/assertion ports are controlled.
// UI assertions are inert in this boundary fixture, so this is never product/UI acceptance.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../..');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 let count=0;const failures=[];
 for(const file of ['desktop-friends.cjs','desktop-picker.cjs','web.cjs','web-ui.cjs']){
  const web=file.startsWith('web');
  for(const faults of web?[[],['body'],['report'],['close'],['body','report'],['body','close'],['report','close'],['body','report','close']]:[[],['body'],['close'],['body','close'],['falsy','close']]){
   try{
   const primary=faults.includes('falsy')?0:new Error('operation sentinel\nCall log: PRIVATE_CALL_DETAIL'),report=new Error('report sentinel'),close=new Error('close sentinel');
   const logged=[],output=[],order=[],reports=[],aggregates=[];let closeReached=false,reportReached=false,bodyReached=false;
   const result={conversationId:'30000000-0000-4000-8000-000000000001',requestId:'40000000-0000-4000-8000-000000000001'};
   const response={status:()=>201,json:async()=>result};
   const page=new Proxy({}, {get:(_,key)=>key==='then'?undefined:key==='waitForResponse'?async()=>response:key==='evaluate'?async()=>undefined:()=>page});
   const browser={newPage:async()=>{bodyReached=true;if(faults.includes('body')||faults.includes('falsy'))throw primary;return page;},newContext:async()=>{bodyReached=true;if(faults.includes('body'))throw primary;return {newPage:async()=>page};},close:async()=>{closeReached=true;order.push('close');if(faults.includes('close'))throw close;}};
   const config={credentials:'dummy-credentials',playwright:'dummy-playwright',out:'dummy-output',browser:'dummy-browser',modes:[]};
   const accounts={A:{username:'dummy',password:'dummy'},B:{username:'dummy'},C:{username:'dummy'}};
   const proc={argv:web?['node',file,'dummy-config']:['node',file,'dummy-source','dummy-deps','dummy-playwright','dummy-browser'],exitCode:0};
   const noopAssert=new Proxy(()=>{}, {get:()=>()=>{}});
   const context={process:proc,console:{error:e=>logged.push(e),log:e=>{output.push(e);order.push('log');}},Buffer,setTimeout,clearTimeout,AggregateError:class extends AggregateError{constructor(errors,message){super(errors,message);aggregates.push(this);}}};
   context.require=id=>{
    if(id==='fs'||id==='node:fs')return {readFileSync:p=>web?JSON.stringify(p==='dummy-config'?config:accounts):'',existsSync:()=>web,mkdirSync:()=>{},writeFileSync:(p,data)=>{reportReached=true;order.push('report');if(faults.includes('report'))throw report;reports.push(JSON.parse(data));}};
    if(id==='dummy-deps/typescript')return {transpileModule:()=>({outputText:''}),ModuleKind:{CommonJS:1},JsxEmit:{React:1},ScriptTarget:{ES2022:1}};
    if(id==='dummy-playwright')return {chromium:{launch:async()=>browser}};
    if(id==='assert/strict'||id==='node:assert/strict')return noopAssert;
    return require(id);
   };
   vm.runInNewContext(fs.readFileSync(path.join(root,'tests/clients/group',file),'utf8'),context,{filename:file});
   for(let n=0;n<50;n++)await tick();
   const label=file+'/'+faults.join('+');assert.ok(bodyReached,label);assert.ok(closeReached,label+' always closes');if(web)assert.ok(reportReached,label+' always reports');
   assert.equal(proc.exitCode,faults.length?1:0,label+' exit');
   const leaves=e=>Array.isArray(e?.errors)?e.errors.flatMap(leaves):[e];
   if(!web){
    const errors=logged.flatMap(leaves);if(faults.includes('body')||faults.includes('falsy'))assert.ok(errors.includes(primary),label+' original primary');if(faults.includes('close'))assert.ok(errors.includes(close),label+' original close');
    if(faults.length)assert.equal(output.filter(x=>String(x).includes('PASS')).length,0,label+' no premature PASS');
   }else{
    const text=logged.map(String).join('\n');for(const name of faults)assert.ok(text.includes(({body:'operation',report:'report',close:'close'})[name]+' sentinel'),label+' all public causes');assert.ok(!text.includes('PRIVATE_CALL_DETAIL'),label+' no private call log');
    if(!faults.includes('report')){assert.equal(reports.length,1,label+' durable report');assert.equal(reports[0].result.startsWith('PASS'),!faults.length,label+' report is FAIL on operation/cleanup failure');if(faults.includes('body'))assert.equal(reports[0].failure,'operation sentinel');if(faults.includes('close'))assert.equal(reports[0].cleanupFailure,'close sentinel');}
    if(faults.length>1){assert.equal(aggregates.length,1,label+' combined original causes');for(const name of faults)assert.ok(aggregates[0].errors.includes(({body:primary,report,close})[name]),label+' original '+name);}
    if(faults.length)assert.ok(!output.some(x=>String(x).includes('PASS')),label+' no false PASS');
   }
   if(!faults.length)assert.ok(output.some(x=>String(x).includes('PASS')),label+' success after cleanup');
   if(order.includes('log'))assert.ok(order.indexOf('log')>order.indexOf('close'),label+' success only after close');count++;
   }catch(error){failures.push(error);}
  }
 }
 if(failures.length)throw new AggregateError(failures,'Runner cleanup regressions');
 console.log('PASS '+count+' actual runner cleanup boundary cases; no browser/network/device/product acceptance');
})().catch(error=>{console.error(error);process.exitCode=1});

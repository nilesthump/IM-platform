const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8').replace(/^\uFEFF/,''));
const {chromium}=require(config.playwright);const accounts=JSON.parse(fs.readFileSync(config.credentials,'utf8').replace(/^\uFEFF/,''));const out=config.out;fs.mkdirSync(out,{recursive:false});
const publicFailure=e=>String(e?.message??e).split('Call log:')[0].trim();
const result={scope:'Actual Web group TLS/UI; independent DB checkpoints are separate',events:[],result:'PENDING'};
const save=(name,data)=>fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2));
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function checkpoint(name,data){save(name+'.json',data);for(let n=0;n<12000;n++){if(fs.existsSync(path.join(out,name+'.continue')))return;await delay(100)}throw new Error('Independent DB observer checkpoint timed out: '+name)}
(async()=>{const browser=await chromium.launch({executablePath:config.browser,headless:true});const failures=[];let page;
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});page=await context.newPage();page.on('pageerror',e=>{result.events.push({type:'pageerror',message:e.message})});await page.goto('https://localhost:18444');
  await page.getByLabel('Username',{exact:true}).fill(accounts.A.username);await page.getByLabel('Password',{exact:true}).fill(accounts.A.password);await page.getByRole('button',{name:'Enter workspace →',exact:true}).click();await page.getByText('Online',{exact:true}).waitFor();
  for(const mode of (config.modes||['before','after'])){
   await page.getByRole('button',{name:'New chat',exact:true}).click();await page.getByRole('button',{name:'Create group',exact:true}).click();
   const picker=page.getByRole('dialog',{name:'Create group',exact:true});await picker.locator('label.group-person').filter({hasText:'@'+accounts.B.username}).getByRole('checkbox').check();await page.screenshot({path:path.join(out,'web-'+mode+'-friend-selection.png'),fullPage:true});
   let first=true,original,reply,routeFailure;const attempts=[];
   await page.route('**/v1/groups',async route=>{try{const request=route.request();if(request.method()!=='POST')return route.continue();const body=request.postDataJSON();attempts.push(body);if(first){first=false;original=body;
    if(mode==='after'){const response=await route.fetch();assert.equal(response.status(),201);reply=await response.json();await checkpoint('web-'+mode+'-committed',{actor:accounts.A.userId,targets:body.memberUserIds,requestId:body.requestId,response:reply,phase:'durably returned201 before browser delivery'});}
    await route.abort('connectionfailed');return;
   }await route.continue()}catch(e){routeFailure=new Error(String(e.message).split('Call log:')[0].trim());await route.abort('failed')}});
   await picker.getByRole('button',{name:'Confirm',exact:true}).click();await page.getByText('Submission unconfirmed. Retry the original request.',{exact:true}).waitFor({timeout:1200000});if(routeFailure)throw routeFailure;await page.screenshot({path:path.join(out,'web-'+mode+'-unconfirmed.png'),fullPage:true});
   await checkpoint('web-'+mode+'-unconfirmed',{actor:accounts.A.userId,targets:original.memberUserIds,requestId:original.requestId,phase:mode==='before'?'not forwarded':'response dropped after real201'});
   const responsePromise=page.waitForResponse(r=>new URL(r.url()).pathname==='/v1/groups'&&r.request().method()==='POST');await page.getByRole('button',{name:'Retry original request',exact:true}).click();const response=await responsePromise;assert.equal(response.status(),201);const success=await response.json();assert.deepEqual(attempts[0],attempts[1]);if(reply)assert.deepEqual(success,reply);await picker.waitFor({state:'detached'});await page.locator('button.conversation.active').filter({hasText:success.conversationId.slice(0,8)}).waitFor();await page.getByRole('button',{name:'Members',exact:true}).click();await page.locator('.group-management > p').filter({hasText:success.conversationId}).waitFor();await page.getByRole('button',{name:'Members',exact:true}).click();
   await page.screenshot({path:path.join(out,'web-'+mode+'-retried.png'),fullPage:true});await checkpoint('web-'+mode+'-success',{actor:accounts.A.userId,requestId:original.requestId,targets:original.memberUserIds,response:success,attempts});result.events.push({mode,original,response:success,attempts});await page.unroute('**/v1/groups');
  }
  assert.equal(result.events.filter(e=>e.type==='pageerror').length,0);result.result='PASS_WEB_G06_UI_AND_REAL_RESPONSES';
 }catch(e){failures.push(e);result.result='FAIL';result.failure=publicFailure(e);if(page){try{await page.screenshot({path:path.join(out,'failure.png'),fullPage:true})}catch(captureError){failures.push(captureError);result.captureFailure=publicFailure(captureError)}}}
 finally{
  try{await browser.close();}catch(error){failures.push(error);result.result='FAIL';result.cleanupFailure=publicFailure(error);}
  try{save('result.json',result);}catch(error){failures.push(error);}
 }
 if(failures.length===1)throw failures[0];
 if(failures.length)throw new AggregateError(failures,failures.map(publicFailure).join('\n'));
 console.log(result.result);
})().catch(e=>{console.error(publicFailure(e));process.exitCode=1});

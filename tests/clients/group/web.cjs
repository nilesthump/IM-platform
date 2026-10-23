const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8').replace(/^\uFEFF/,''));
const {chromium}=require(config.playwright);const accounts=JSON.parse(fs.readFileSync(config.credentials,'utf8').replace(/^\uFEFF/,''));const out=config.out;fs.mkdirSync(out,{recursive:false});
const result={scope:'Actual Web group TLS/UI; independent DB checkpoints are separate',events:[],result:'PENDING'};
const save=(name,data)=>fs.writeFileSync(path.join(out,name),JSON.stringify(data,null,2));
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function checkpoint(name,data){save(name+'.json',data);for(let n=0;n<12000;n++){if(fs.existsSync(path.join(out,name+'.continue')))return;await delay(100)}throw new Error('Independent DB observer checkpoint timed out: '+name)}
(async()=>{const browser=await chromium.launch({executablePath:config.browser,headless:true});let page;
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});page=await context.newPage();page.on('pageerror',e=>{result.events.push({type:'pageerror',message:e.message})});await page.goto('https://localhost:18444');
  await page.getByLabel('Username',{exact:true}).fill(accounts.A.username);await page.getByLabel('Password',{exact:true}).fill(accounts.A.password);await page.getByRole('button',{name:'Enter workspace →',exact:true}).click();await page.getByText('Online',{exact:true}).waitFor();
  await page.locator('nav button').filter({hasText:'Friends'}).click();await page.getByRole('checkbox',{name:'Group Fixture B @'+accounts.B.username,exact:true}).check();await page.screenshot({path:path.join(out,'web-friend-selection.png'),fullPage:true});
  for(const mode of (config.modes||['before','after'])){
   let first=true,original,reply,routeFailure;const attempts=[];
   await page.route('**/v1/groups',async route=>{try{const request=route.request();if(request.method()!=='POST')return route.continue();const body=request.postDataJSON();attempts.push(body);if(first){first=false;original=body;
    if(mode==='after'){const response=await route.fetch();assert.equal(response.status(),201);reply=await response.json();await checkpoint('web-'+mode+'-committed',{actor:accounts.A.userId,targets:body.memberUserIds,requestId:body.requestId,response:reply,phase:'durably returned201 before browser delivery'});}
    await route.abort('connectionfailed');return;
   }await route.continue()}catch(e){routeFailure=new Error(String(e.message).split('Call log:')[0].trim());await route.abort('failed')}});
   await page.getByRole('button',{name:'Create group',exact:true}).click();await page.getByText('Submission unconfirmed. Retry the original request.',{exact:true}).waitFor({timeout:1200000});if(routeFailure)throw routeFailure;await page.screenshot({path:path.join(out,'web-'+mode+'-unconfirmed.png'),fullPage:true});
   await checkpoint('web-'+mode+'-unconfirmed',{actor:accounts.A.userId,targets:original.memberUserIds,requestId:original.requestId,phase:mode==='before'?'not forwarded':'response dropped after real201'});
   const responsePromise=page.waitForResponse(r=>new URL(r.url()).pathname==='/v1/groups'&&r.request().method()==='POST');await page.getByRole('button',{name:'Retry original request',exact:true}).click();const response=await responsePromise;assert.equal(response.status(),201);const success=await response.json();assert.deepEqual(attempts[0],attempts[1]);if(reply)assert.deepEqual(success,reply);await page.getByText('Group updated.',{exact:true}).waitFor();
   await page.screenshot({path:path.join(out,'web-'+mode+'-retried.png'),fullPage:true});await checkpoint('web-'+mode+'-success',{actor:accounts.A.userId,requestId:original.requestId,targets:original.memberUserIds,response:success,attempts});result.events.push({mode,original,response:success,attempts});await page.unroute('**/v1/groups');
  }
  assert.equal(result.events.filter(e=>e.type==='pageerror').length,0);result.result='PASS_WEB_G06_UI_AND_REAL_RESPONSES';
 }catch(e){result.result='FAIL';result.failure=String(e.message).split('Call log:')[0].trim();if(page){try{await page.screenshot({path:path.join(out,'failure.png'),fullPage:true})}catch(captureError){result.captureFailure=String(captureError.message).split('Call log:')[0].trim()}}throw new Error(result.failure)}
 finally{save('result.json',result);await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});

// Render real compiled UI with presentation-only Workspace data; no native/TLS/login acceptance.
import {pathToFileURL} from 'node:url';
if(!process.env.IM_GUI_PLAYWRIGHT_MODULE||!process.env.IM_GUI_RENDER_OUTPUT)throw Error('Set IM_GUI_PLAYWRIGHT_MODULE and IM_GUI_RENDER_OUTPUT');
const {chromium}=await import(pathToFileURL(process.env.IM_GUI_PLAYWRIGHT_MODULE).href);
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import assert from 'node:assert/strict';
const root=resolve('clients/desktop/dist'),out=resolve(process.env.IM_GUI_RENDER_OUTPUT);
const fixture=`export class Workspace {
 constructor(){this.listeners=new Set();this.s={appearance:{theme:'cold',fontSize:20,density:1.2},session:{userId:'avery'},offlineAccount:null,profile:{displayName:'Renderer Fixture Avery',username:'renderer_fixture',userId:'avery'},friends:[{friendshipId:'f1',directConversationId:'c1',user:{userId:'morgan',username:'renderer_morgan',displayName:'Renderer Fixture Morgan'}},{friendshipId:'f2',directConversationId:'c2',user:{userId:'riley',username:'renderer_riley',displayName:'Renderer Fixture Riley'}}],conversations:['c1','c2'],selected:'c1',previews:{},unavailable:[],results:[],connection:'offline',sync:'idle',error:null,busy:false,page:'Chat',endpoint:'https://localhost:8443',messages:Array.from({length:30},(_,i)=>['m'+i,i%2?'avery':'morgan','Render-only message '+i,'SENT',null,null,'2026-10-07T06:40:00Z'])};this.observe=fn=>{this.listeners.add(fn);return()=>this.listeners.delete(fn)};this.snapshot=()=>this.s}
 update(v){this.s={...this.s,...v};this.listeners.forEach(fn=>fn())}
 async start(){} page(page){this.update({page})} async preferences(appearance){this.update({appearance})} async open(id){this.update({selected:this.s.selected===id?null:id,page:'Chat'})} disconnect(){this.update({connection:'offline'})} async logout(){this.update({session:null,offlineAccount:'avery'})} async reconnect(){this.update({connection:'ready'})}
}`;
const server=createServer(async(req,res)=>{try{const path=resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!path.startsWith(root))throw Error('path');const data=await readFile(path===root?resolve(root,'index.html'):path);res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.png':'image/png'})[extname(path)]??'application/octet-stream');res.end(data)}catch{res.writeHead(404);res.end()}});
await mkdir(out,{recursive:true});
await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser,page;const results=[];
try{
 browser=await chromium.launch({headless:true,...(process.env.IM_GUI_BROWSER_EXECUTABLE?{executablePath:process.env.IM_GUI_BROWSER_EXECUTABLE}:{})});page=await browser.newPage({viewport:{width:1280,height:840}});const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.log('PAGEERROR',e.message)});page.on('console',m=>console.log('BROWSER',m.type(),m.text()));page.on('requestfailed',r=>console.log('REQUESTFAIL',r.url(),r.failure()));
 await page.route('**/desktop/src/application/ui/workspace.js',route=>route.fulfill({contentType:'text/javascript',body:fixture}));
 await page.addInitScript(()=>{window.__TAURI_INTERNALS__={invoke:async()=>false}});
 await page.goto('http://127.0.0.1:'+server.address().port+'/index.html');await page.locator('.composer-resize').waitFor();
 assert.equal(await page.locator('.connection').innerText(),'Online');assert.match(await page.locator('.chat-heading').innerText(),/Offline/);results.push('Session Online remains distinct from realtime Offline');
 const min=page.getByRole('button',{name:'Minimize',exact:true}),max=page.getByRole('button',{name:'Maximize',exact:true});
 for(const button of [min,max]){await page.mouse.move(700,150);const before=await button.evaluate(e=>getComputedStyle(e).backgroundColor);await button.hover();const after=await button.evaluate(e=>getComputedStyle(e).backgroundColor);assert.notEqual(before,after);assert.equal(after,'rgba(0, 0, 0, 0.08)');assert.ok(await button.getAttribute('title'));}
 await page.screenshot({path:out+'/renderer-hover.png'});results.push('Minimize and Maximize actual hover grey background and title');
 const height=()=>page.locator('#message').evaluate(e=>e.getBoundingClientRect().height),bottom=()=>page.locator('.composer').evaluate(e=>e.getBoundingClientRect().bottom);
 async function drag(dy){const b=await page.locator('.composer-resize').boundingBox();await page.mouse.move(b.x+b.width/2,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width/2,b.y+b.height/2+dy,{steps:6});await page.mouse.up();}
 const initial=await height(),anchor=await bottom();await drag(-30);assert.equal(await height(),initial+30);assert.ok(Math.abs(await bottom()-anchor)<1);await drag(30);assert.equal(await height(),initial);await drag(-250);assert.equal(await height(),150);await drag(250);assert.equal(await height(),42);await page.mouse.move(800,350);assert.equal(await height(),42);
 await page.locator('.composer-resize').focus();await page.keyboard.press('ArrowUp');assert.equal(await height(),52);await page.keyboard.press('ArrowDown');assert.equal(await height(),42);
 results.push('Actual pointer drag up grows/down shrinks; bottom anchored; 42..150 clamp; release and keyboard');await page.screenshot({path:out+'/renderer-composer.png'});
 const messages=page.locator('.messages');await messages.hover();await page.mouse.wheel(0,600);await page.waitForFunction(()=>document.querySelector('.messages').scrollTop>0);results.push('Message pane actual mouse wheel scroll');
 await page.getByRole('button',{name:'⚙ Settings'}).click();const settings=page.locator('.settings');assert.ok(await settings.evaluate(e=>e.scrollHeight>e.clientHeight));await settings.hover();await page.mouse.wheel(0,600);await page.waitForFunction(()=>document.querySelector('.settings').scrollTop>0);
 assert.deepEqual(await settings.evaluate(e=>[getComputedStyle(e).scrollbarWidth,getComputedStyle(e,'::-webkit-scrollbar').display]),['none','none']);await page.screenshot({path:out+'/renderer-settings20.png'});results.push('Settings20px actual mouse wheel scroll with both scrollbar styles hidden');
 for(const theme of ['cold','warm']){await page.locator('.theme-choice').nth(theme==='cold'?0:1).click();for(const font of [14,20,22]){const range=page.locator('.settings input[type=range]').first();await range.focus();await page.keyboard.press('Home');for(let i=14;i<font;i++)await page.keyboard.press('ArrowRight');assert.equal(await range.inputValue(),String(font));assert.ok(await page.evaluate(()=>document.documentElement.scrollHeight===innerHeight));assert.equal(await settings.evaluate(e=>getComputedStyle(e).scrollbarWidth),'none');results.push(theme+' '+font+'px fixed viewport without root overflow')}}
 await page.getByRole('button',{name:'Sign out',exact:true}).click();assert.equal(await page.locator('.connection').innerText(),'Offline');results.push('No Session local history shows Offline');assert.deepEqual(errors,[]);await writeFile(out+'/results.json',JSON.stringify({result:'PASS',scope:'Real compiled frontend with presentation Workspace fixture; not native OS, TLS or real login acceptance',checks:results},null,2));console.log(JSON.stringify({result:'PASS',checks:results},null,2));
}catch(e){await page?.screenshot({path:out+'/renderer-failure.png'});console.log(await page?.content());await writeFile(out+'/failure.txt',e.stack);throw e}finally{await browser?.close();await new Promise(r=>server.close(r))}



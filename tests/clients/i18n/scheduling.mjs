import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
export async function verifyScheduling(root,out,ts,loaded){
 const source=readFileSync(join(root,'clients/desktop/src/application/ui/workspace.ts'),'utf8');
 // Execute the actual complete Workspace class; only native/dependency import boundaries are controlled.
 const stripped=source.replace(/^import .*;\r?\n/gm,'');
 const js=ts.transpileModule(stripped,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
 class NativeCapabilityFailure extends Error {}
 const fixture={NativeCapabilityFailure,GroupFailure:class extends Error {},ApiFailure:class extends Error {},WireFailure:class extends Error {},SyncFailure:class extends Error {},SendStorageFailure:class extends Error {}};globalThis.__i18nScheduling=fixture;
 const filename=join(out,'scheduling-workspace.mjs');
 writeFileSync(filename,'const {language,appearance,trayText,defaults,translate,validLocale,NativeCapabilityFailure,GroupFailure,ApiFailure,WireFailure,SyncFailure,SendStorageFailure}=globalThis.__i18nScheduling;\n'+js);
 const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return{promise,resolve,reject}};
 const tick=()=>new Promise(r=>setImmediate(r));
 const initial=deferred(),save=deferred(),calls=[],disk=[];
 Object.assign(fixture,{language:{load:()=>initial.promise,save:async value=>{disk.push(value);if(disk.length===1)await save.promise}},appearance:{load:async()=>({theme:'warm',fontSize:22,density:1.2})},defaults:{theme:'cold',fontSize:16,density:1},translate:loaded.desktop.translate,validLocale:loaded.desktop.validLocale,trayText:async(...labels)=>{calls.push(labels);if(fixture.holdTray)await fixture.holdTray.promise}});
 try{
  const {Workspace}=await import(pathToFileURL(filename));const app=new Workspace();const startup=app.start();const selected=app.selectLanguage('ja-JP');await tick();
  assert.equal(app.state.language,'ja-JP');assert.equal(calls.length,1,'Tray must update while save remains unresolved');assert.equal(calls[0][0],loaded.desktop.resources['ja-JP']['tray.open']);
  initial.resolve('en');await startup;assert.equal(app.state.language,'ja-JP','Initial read cannot overwrite newer selection');save.resolve();await selected;
  const held=deferred();fixture.language.save=async()=>{};fixture.holdTray=held;
  // An old native presentation call is genuinely in flight; later selections must settle last.
  const app2=new Workspace();const a=app2.selectLanguage('en');await tick();const b=app2.selectLanguage('zh-CN'),c=app2.selectLanguage('ja-JP');fixture.holdTray=null;held.resolve();await Promise.all([a,b,c]);assert.equal(app2.state.language,'ja-JP');assert.equal(calls.at(-1)[0],loaded.desktop.resources['ja-JP']['tray.open']);
  const failing=deferred(),lastSave=deferred();let count=0;fixture.language.save=async()=>{const n=++count;if(n===1)await failing.promise;if(n===3)await lastSave.promise};const app3=new Workspace();const old=app3.selectLanguage('en');await tick();const middle=app3.selectLanguage('zh-CN'),latest=app3.selectLanguage('en');failing.reject(new NativeCapabilityFailure('Language unavailable'));await old;await tick();assert.equal(app3.state.languageStored,true,'Stale same-value write failure cannot poison latest revision while its own save is pending');lastSave.resolve();await Promise.all([middle,latest]);
  for(const original of [new Error("controlled internal locale bug"),"Language unavailable"]){fixture.language.save=async()=>{throw original};const app4=new Workspace();await assert.rejects(app4.selectLanguage("en"),e=>e===original);}
  for(const module of Object.values(loaded))for(const locale of module.locales)for(const [code,key] of Object.entries({USER_NOT_FOUND:'error.userNotFound',FRIEND_SELF_NOT_ALLOWED:'error.friendSelf',FRIENDSHIP_STATE_CONFLICT:'error.friendState'})){assert.equal(module.errorKey(code),key);assert.equal(module.displayText(locale,code),module.resources[locale][key]);assert.notEqual(module.displayText(locale,code),module.resources[locale]['error.operation']);assert.equal(module.displayText(locale,'untrusted server detail'),module.resources[locale]['error.operation']);}
  const mobile=readFileSync(join(root,'clients/mobile/app/src/main/kotlin/im/platform/client/ui/WorkspaceViewModel.kt'),'utf8');assert.match(mobile,/if\(revision==languageRevision\)publish\{it.copy\(language=language\)\}/);assert.match(mobile,/val revision=\+\+languageRevision/);
  console.log('PASS source-derived Workspace delayed locale/save/tray/revision tests and bounded friendship display; Mobile guard source only, not native acceptance');
 }finally{delete globalThis.__i18nScheduling;}
}

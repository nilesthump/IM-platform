import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const module=await import(pathToFileURL(process.env.WEB_BUILD_DIR+'/web/src/ui/appearance.js'));
const data=new Map([['unrelated','untouched']]);globalThis.window={localStorage:{getItem:k=>data.get(k)??null,setItem:(k,v)=>data.set(k,v)}};
const {defaults,validate,loadAppearance,saveAppearance}=module;
assert.deepEqual(loadAppearance(),defaults);
for(const theme of ['cold','warm'])for(const fontSize of [14,16,18,20])for(const density of ['compact','comfortable','spacious']){const value={theme,fontSize,density};assert.equal(saveAppearance(value),true);assert.deepEqual(loadAppearance(),value);assert.deepEqual(Object.keys(JSON.parse(data.get('plugworldim.appearance.v1'))),['theme','fontSize','density']);}
for(const bad of [null,[],{}, {...defaults,accessToken:'forbidden'}, {...defaults,fontSize:15}, {...defaults,density:'huge'},{...defaults,theme:'dark'}])assert.throws(()=>validate(bad));
for(const bad of [{...defaults,theme:{toString:()=>"cold"}},{...defaults,density:{toString:()=>"comfortable"}}])assert.throws(()=>validate(bad));
for(const raw of ['{','x'.repeat(129),JSON.stringify({...defaults,user:'forbidden'})]){data.set('plugworldim.appearance.v1',raw);assert.deepEqual(loadAppearance(),defaults);}
saveAppearance({theme:'cold',fontSize:20,density:'spacious'});saveAppearance({...loadAppearance(),theme:'warm'});assert.deepEqual(loadAppearance(),{theme:'warm',fontSize:20,density:'spacious'});assert.equal(data.get('unrelated'),'untouched');
globalThis.window={localStorage:{getItem(){throw Error('Unavailable');},setItem(){throw Error('Unavailable');}}};assert.deepEqual(loadAppearance(),defaults);assert.equal(saveAppearance(defaults),false);
console.log('PASS appearance: bounded values, rejection, restart, theme independence, unavailable storage, unrelated key preservation');

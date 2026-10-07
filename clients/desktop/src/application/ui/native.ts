import {invoke} from "@tauri-apps/api/core";
export interface Appearance {theme:"cold"|"warm";fontSize:number;density:number}
export const defaults:Appearance={theme:"cold",fontSize:16,density:1};
export const nativeFetch:typeof fetch=async(input,init)=>{
  const request=new Request(input,init);
  if(request.signal.aborted)throw new DOMException("Aborted","AbortError");
  const [status,headers,body]=await invoke<[number,Record<string,string>,number[]]>("native_https",{
    url:request.url,method:request.method,headers:Object.fromEntries(request.headers),body:Array.from(new Uint8Array(await request.arrayBuffer()))});
  if(request.signal.aborted)throw new DOMException("Aborted","AbortError");
  return new Response(status===204?null:new Uint8Array(body),{status,headers});
};
export const appearance={load:async()=>{const [theme,fontSize,density]=await invoke<[Appearance["theme"],number,number]>("appearance_load");return {theme,fontSize,density};},save:(value:Appearance)=>invoke<void>("appearance_save",{value:[value.theme,value.fontSize,value.density]})};
// No token is stored in appearance, localStorage or the account database.
export const secure={read:(slot:string)=>invoke<string|null>("credential_read",{slot}),write:(slot:string,value:string)=>invoke<void>("credential_write",{slot,value}),remove:(slot:string)=>invoke<void>("credential_remove",{slot})};
export const windowControl=(action:"minimize"|"maximize"|"close"|"drag")=>invoke<void>("window_control",{action});
export const notify=(title:string,body:string)=>invoke<void>("native_notify",{title,body});

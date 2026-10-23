import {LanguageContext,useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
function stateKey(state:string|null):string {switch(state){case "SENT":return "chat.sent";case "SENDING":return "chat.sending";case "FAILED":return "chat.failed";default:throw new Error("Unknown message state");}}
export function Messages({s,retry,run}:{s:Pick<WorkspaceState,"groups"|"messages"|"offlineAccount"|"selected"|"session">;retry:(id:string)=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
  const t=useText();const locale=React.useContext(LanguageContext);
return <div className="messages" role="log" aria-live="polite">{!s.selected?<div className="empty"><span>✧</span><h3>{t("chat.place")}</h3><p>{t("chat.choose")}</p></div>:s.messages.length===0?<div className="empty"><h3>{t("chat.fresh")}</h3><p>{t("chat.hello")}</p></div>:s.messages.map(m=>{const identity=m[0]??m[4];if(identity==null)throw new Error("Message identity missing");if(m[2]==null)throw new Error("Message content missing");const key=stateKey(m[3]);return <div key={identity} className={m[1]===(s.session?.userId??s.offlineAccount)?"message own":"message"}><small>{(()=>{const u=s.groups.find(r=>r.conversationId===s.selected&&r.member.user.userId===m[1])?.member.user;return u?u.displayName+' @'+u.username:m[1];})()}</small><div className="bubble">{m[2]}</div><small>{m[6]?new Date(m[6]).toLocaleTimeString(locale,{hour:"2-digit",minute:"2-digit"}):t("chat.now")} · {t(key)}{m[3]==="FAILED"&&m[1]===(s.session?.userId??s.offlineAccount)&&m[0]&&<button disabled={!s.session} onClick={()=>run(retry(m[0]!))}>{t("chat.retry")}</button>}</small></div>;})}</div>;
}

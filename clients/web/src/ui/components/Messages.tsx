import {useText} from "../i18n/context.js";
import React from "react";
import type {View} from "../../application/client.js";
import type {MemoryRepository} from "../../application/repository.js";
export function Messages({v,messages,retry}:{v:Pick<View,"user"|"groups">;messages:ReturnType<MemoryRepository["snapshot"]>;retry:(conversation:string,request:string)=>void}){
  const t=useText();
  const status=(value:unknown)=>{switch(value){case "SENDING":return t("chat.webSending");case "SENT":return t("chat.webSent");case "FAILED":return t("chat.webFailed");default:throw new Error("Invalid message state");}};
  const body=(m:(typeof messages)[number])=>{if(typeof m.content?.text!=="string" || !m.requestId)throw new Error("Invalid message content or identity");return m.content.text;};
  return <div className="messages" aria-live="polite">{!messages.length&&<div className="empty"><span>◌</span><h3>{t("chat.webStart")}</h3><p>{t("web.emptyChat1")}<br/>{t("web.emptyChat2")}</p></div>}{messages.map(m=><article key={m.requestId} className={'message '+(m.senderId===v.user?.userId?'own':'')}><small>{(()=>{const u=v.groups.find(r=>r.conversationId===m.conversationId&&r.member.user.userId===m.senderId)?.member.user;return u?u.displayName+' @'+u.username:m.senderId;})()}</small><p>{body(m)}</p><div className="message-meta"><span>{status(m.state)}</span>{m.state==='FAILED'&&<button onClick={()=>retry(m.conversationId,m.requestId)}>{t("chat.retry")}</button>}{m.seq!==undefined&&<span>#{m.seq.toString()}</span>}</div></article>)}</div>;
}

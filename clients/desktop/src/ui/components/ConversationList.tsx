import {useText} from "../i18n/context.js";
import React from "react";
import type {WorkspaceState} from "../../application/ui/workspace.js";
import type {Appearance} from "../../application/ui/native.js";
import type {Friend} from "../../application/ui/auth.js";
export function ConversationList({s,page,open,run,newChat}:{newChat:()=>void;s:Pick<WorkspaceState,"conversations"|"friends"|"previews"|"selected"|"unavailable">;page:(page:WorkspaceState["page"])=>void;open:(id:string)=>Promise<void>;run:(promise:Promise<unknown>)=>void}){
  const t=useText();
return <aside className="conversation-list glass"><div className="section-heading"><h2>{t("chat.messages")}</h2><button className="quiet" onClick={newChat}>{t("chat.new")}</button></div><p className="muted list-caption">{t("chat.caption")}</p>{s.conversations.length===0?<div className="empty"><span>◫</span><h3>{t("chat.next")}</h3><p>{t("chat.addHint")}</p><button onClick={()=>page("Friends")}>{t("chat.find")}</button></div>:s.conversations.map(id=>{const f=s.friends.find(f=>f.directConversationId===id);return <button key={id} className={s.selected===id?"conversation active":"conversation"} onClick={()=>run(open(id))}><span className="avatar">{f?.user.displayName[0]??"#"}</span><div><strong>{f?.user.displayName??t("chat.conversationId",{id:id.slice(0,8)})}</strong><small>{s.unavailable.includes(id)?t("chat.access"):s.previews[id]?.text||t("chat.noMessages")}</small></div></button>;})}</aside>;
}

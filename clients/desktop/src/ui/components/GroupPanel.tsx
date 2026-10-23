import React,{useState} from 'react';
import {useText} from '../i18n/context.js';
import type {WorkspaceState} from '../../application/ui/workspace.js';
export function GroupPanel({s,conversation,submit,retry}:{s:WorkspaceState;conversation?:string;submit:(ids:string[],conversation?:string)=>Promise<void>;retry:()=>Promise<void>}){
 const t=useText(),[selection,setSelection]=useState<string[]>([]);
 return <section className="glass group-panel"><header className="section-heading"><h2>{t(conversation?'group.add':'group.create')}</h2></header>
 <fieldset disabled={!s.session||s.groupBusy||s.groupStatus==='unconfirmed'}><legend>{t('group.members')}</legend>
 {!s.friends.length&&<p>{t('group.empty')}</p>}
 {s.friends.map(f=><label key={f.user.userId}><input type="checkbox" checked={selection.includes(f.user.userId)} onChange={e=>setSelection(e.target.checked?[...selection,f.user.userId]:selection.filter(id=>id!==f.user.userId))}/><span>{f.user.displayName} <small>@{f.user.username}</small></span></label>)}
 <button disabled={!selection.length||selection.length>100} onClick={()=>void submit(selection,conversation)}>{t(conversation?'group.add':'group.create')}</button></fieldset>
 {s.groupStatus&&<p role="status">{t('group.'+s.groupStatus)}</p>}{s.groupError&&<p role="alert">{t(s.groupError==='GROUP_REQUEST_CONFLICT'?'group.conflict':'group.failure')}</p>}
 {s.groupStatus==='unconfirmed'&&<button disabled={s.groupBusy||!s.session} onClick={()=>void retry()}>{t('group.retry')}</button>}
 {conversation&&<ul>{s.groups.filter(r=>r.conversationId===conversation).map(r=><li key={r.member.user.userId}>{r.member.user.displayName} @{r.member.user.username}</li>)}</ul>}
 </section>;
}
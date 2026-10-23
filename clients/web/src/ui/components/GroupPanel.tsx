import React,{useState} from 'react';
import {useText} from '../i18n/context.js';
import type {View} from '../../application/client.js';
export function GroupPanel({v,conversation,submit,retry}:{v:View;conversation?:string;submit:(ids:string[],conversation?:string)=>Promise<void>;retry:()=>Promise<void>}){
 const t=useText(),[selected,setSelected]=useState<string[]>([]);
 const pending=v.groupBusy||v.groupStatus==='unconfirmed';
 return <section className="card group-panel"><h2>{t(conversation?'group.add':'group.create')}</h2>
 {v.friendsBusy&&<p role="status">{t('group.loading')}</p>}
 {!v.friendsBusy&&!v.friendsError&&!v.friends.length&&<p>{t('group.empty')}</p>}
 {v.friends.map(f=><label key={f.user.userId}><input type="checkbox" checked={selected.includes(f.user.userId)} disabled={pending} onChange={e=>setSelected(e.target.checked?[...selected,f.user.userId]:selected.filter(id=>id!==f.user.userId))}/>{f.user.displayName} @{f.user.username}</label>)}
 <button disabled={pending||!selected.length||selected.length>100} onClick={()=>void submit(selected,conversation)}>{t(conversation?'group.add':'group.create')}</button>
 {v.groupStatus&&<p role="status">{t('group.'+v.groupStatus)}</p>}
 {v.groupError&&<p role="alert">{t(v.groupError==='GROUP_REQUEST_CONFLICT'?'group.conflict':'group.failure')}</p>}
 {v.groupStatus==='unconfirmed'&&<button disabled={v.groupBusy} onClick={()=>void retry()}>{t('group.retry')}</button>}
 {conversation&&<><h3>{t('group.members')}</h3>{v.groups.filter(r=>r.conversationId===conversation).map(r=><p key={r.member.user.userId}>{r.member.user.displayName} @{r.member.user.username}</p>)}</>}
 </section>;
}
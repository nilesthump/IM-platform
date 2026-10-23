import React,{useState,useEffect,useRef} from 'react';
import {useText} from '../i18n/context.js';
import type {View} from '../../application/client.js';
export function GroupPanel({v,conversation,submit,retry,close,visible}:{v:View;conversation?:string;submit:(ids:string[],conversation?:string)=>Promise<void>;retry:()=>Promise<void>;close:()=>void;visible:boolean}){
 const t=useText(),[selected,setSelected]=useState<string[]>([]),[search,setSearch]=useState('');
 const dialog=useRef<HTMLDialogElement>(null),pending=v.groupBusy||v.groupStatus==='unconfirmed';
 useEffect(()=>{const previous=document.activeElement;if(visible)dialog.current!.showModal();else dialog.current!.close();return()=>{if(previous instanceof HTMLElement)previous.focus();};},[visible]);
 const friends=v.friends.filter(f=>[f.user.displayName,f.user.username,f.user.userId].some(s=>s.toLowerCase().includes(search.toLowerCase())));
 const remove=(id:string)=>setSelected(selected.filter(x=>x!==id));
 return <dialog ref={dialog} className="group-picker" aria-labelledby="group-picker-title" onCancel={e=>{e.preventDefault();if(!v.groupBusy)close();}}>
 <header><h2 id="group-picker-title">{t(conversation?'group.add':'group.create')}</h2></header>
 <div className="group-columns"><section><input autoFocus aria-label={t('group.search')} placeholder={t('group.search')} value={search} onChange={e=>setSearch(e.target.value)}/>
 <div className="group-friend-list">{v.friendsBusy&&<p role="status">{t('group.loading')}</p>}{!v.friendsBusy&&!v.friends.length&&<p>{t('group.empty')}</p>}
 {friends.map(f=><label className="group-person" key={f.user.userId}><input type="checkbox" checked={selected.includes(f.user.userId)} disabled={pending} onChange={e=>e.target.checked?setSelected([...selected,f.user.userId]):remove(f.user.userId)}/><span className="avatar">{f.user.userId.slice(0,1)}</span><span>{f.user.displayName}<small>@{f.user.username}</small></span></label>)}</div></section>
 <section><h3>{t('group.selected')} · {selected.length}</h3><div className="group-friend-list">{selected.map(id=>{const user=v.friends.find(f=>f.user.userId===id)?.user;return <div className="group-person" key={id}><span className="avatar">{id.slice(0,1)}</span><span>{user?.displayName??id}</span><button disabled={pending} aria-label={t('group.remove')+' '+(user?.displayName??id)} onClick={()=>remove(id)}>×</button></div>;})}</div></section></div>
 {v.groupStatus&&v.groupStatus!=='success'&&<p role="status">{t('group.'+v.groupStatus)}</p>}{v.groupError&&<p role="alert">{t(v.groupError==='GROUP_REQUEST_CONFLICT'?'group.conflict':'group.failure')}</p>}
 <footer>{v.groupStatus==='unconfirmed'?<button disabled={v.groupBusy} onClick={()=>void retry()}>{t('group.retry')}</button>:<button className="primary" disabled={pending||!selected.length||selected.length>100} onClick={()=>void submit(selected,conversation)}>{t('group.confirm')}</button>}<button disabled={v.groupBusy} onClick={close}>{t('group.cancel')}</button></footer>
 </dialog>;
}

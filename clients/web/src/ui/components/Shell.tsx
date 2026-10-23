import {GroupPanel} from './GroupPanel.js';
import {LanguageContext,useText,useDisplayText} from "../i18n/context.js";
import {Navigation} from "./Navigation.js";
import {Header} from "./Header.js";
import {AuthPanel} from "./AuthPanel.js";
import {ConversationList} from "./ConversationList.js";
import {Messages} from "./Messages.js";
import {Composer} from "./Composer.js";
import {FriendsPanel} from "./FriendsPanel.js";
import {Placeholder} from "./Placeholder.js";
import {SettingsPanel} from "./SettingsPanel.js";
import {ProfilePanel} from "./ProfilePanel.js";
import React,{useState,useEffect,useSyncExternalStore} from 'react';
import {WebClient} from '../../application/client.js';
import {loadAppearance,saveAppearance} from '../appearance.js';
import type {Appearance} from '../appearance.js';
const client=new WebClient(window.location.origin);
import {loadLanguage,saveLanguage} from "../language.js";
import {validLocale,type Locale} from "../i18n/resources.js";
export function Shell(){const [locale,setLocale]=useState(loadLanguage),[languageStored,setLanguageStored]=useState(true);
 function selectLanguage(value:Locale){if(!validLocale(value))return;setLocale(value);setLanguageStored(saveLanguage(value));}
 useEffect(()=>{document.documentElement.lang=locale;},[locale]);
 return <LanguageContext.Provider value={locale}><WorkspaceShell locale={locale} selectLanguage={selectLanguage} languageStored={languageStored}/></LanguageContext.Provider>;
}
function WorkspaceShell({locale,selectLanguage,languageStored}:{locale:Locale;selectLanguage:(value:Locale)=>void;languageStored:boolean}){
 const t=useText();const display=useDisplayText();
 const [pickerVisible,setPickerVisible]=useState(false),[menu,setMenu]=useState(false),[picker,setPicker]=useState<{conversation?:string}|null>(null),[management,setManagement]=useState(false);
 async function submitGroup(ids:string[],conversation?:string){await client.createGroup(ids,conversation);if(client.view().groupStatus==='success'){setPicker(null);setPage('Chat');}}
 async function retryGroup(){await client.retryGroup();if(client.view().groupStatus==='success'){setPicker(null);setPage('Chat');}}
  const v=useSyncExternalStore(client.subscribe,client.view);const [page,setPage]=useState<"Chat"|"Friends"|"AI"|"Plugin"|"Settings"|"Profile">('Chat'),[prefs,setPrefs]=useState(loadAppearance),[stored,setStored]=useState(true),[username,setUsername]=useState(''),[password,setPassword]=useState(''),[search,setSearch]=useState(''),[searched,setSearched]=useState(false),[text,setText]=useState('');
  useEffect(()=>{document.documentElement.dataset.theme=prefs.theme;document.documentElement.dataset.density=prefs.density;document.documentElement.style.setProperty('--font-size',prefs.fontSize+'px');},[prefs]);
  useEffect(()=>{if(!v.session){setPage('Chat');setMenu(false);setPicker(null);setManagement(false);setText('');setSearch('');setSearched(false);setUsername('');setPassword('');}},[v.session]);
  const loadProfile=client.loadProfile.bind(client),logout=client.logout.bind(client),refresh=client.refresh.bind(client),loadFriends=client.loadFriends.bind(client),reconnect=client.reconnect.bind(client),retry=client.retry.bind(client),send=client.send.bind(client),searchUsers=client.search.bind(client),addFriend=client.addFriend.bind(client),login=client.login.bind(client);
  function appearance(p:Partial<Appearance>){const next={...prefs,...p};setPrefs(next);setStored(saveAppearance(next));}
  function open(c:string){client.open(c);setPage('Chat');setManagement(false);}
  const selected=v.friends.find(f=>f.directConversationId===v.selected),messages=client.repository.snapshot(v.selected),group=v.groups.find(r=>r.conversationId===v.selected);
  return <div className="workspace">
    <Navigation page={page} setPage={setPage} v={v} loadProfile={loadProfile}/>
    <div className="main">{v.session&&<div className="new-chat" onKeyDown={e=>{if(e.key==='Escape')setMenu(false);}}><button aria-expanded={menu} onClick={()=>setMenu(!menu)}>{t('chat.new')}</button>{menu&&<div className="new-chat-menu"><button onClick={()=>{setMenu(false);setPage('Friends');}}>{t('group.friend')}</button><button onClick={()=>{setMenu(false);if(v.groupStatus!=='unconfirmed')setPicker({});setPickerVisible(true);void loadFriends();}}>{t('group.create')}</button></div>}</div>}<Header page={page} setPage={setPage} v={v} logout={logout}/>
    {!v.session&&page!=='Settings'?<AuthPanel v={v} username={username} setUsername={setUsername} password={password} setPassword={setPassword} login={login} refresh={refresh}/>:
    page==='Chat'?<section className="chat-layout"><ConversationList v={v} open={open} setPage={setPage} loadFriends={loadFriends}/><div className="chat-view">{selected||group?<><div className="chat-heading"><span className="avatar">{selected?.user.displayName.slice(0,1)??'◈'}</span><div><h2>{selected?.user.displayName??t('group.title')}</h2><p>{t("chat.webLive")}</p></div>{group&&<button aria-label={t('group.members')} aria-expanded={management} onClick={()=>setManagement(!management)}>…</button>}<button onClick={()=>reconnect()}>{t("auth.reconnect")}</button></div>{v.sync&&<p className="sync" role="status">{display(v.sync)}</p>}<Messages v={v} messages={messages} retry={retry}/><Composer text={text} setText={setText} send={send}/></>:<div className="empty chat-empty"><span>◌</span><h2>{t("chat.place")}</h2><p>{t("chat.choose")}</p></div>}</div>{group&&management&&<aside className="group-management"><h2>{t('group.title')}</h2><p>{v.selected}</p><h3>{t('group.members')}</h3>{v.groups.filter(r=>r.conversationId===v.selected).map(r=><div className="group-person" key={r.member.user.userId}><span className="avatar">{r.member.user.userId.slice(0,1)}</span><span>{r.member.user.displayName}<small>{r.member.user.userId}</small></span></div>)}<button onClick={()=>{if(v.groupStatus!=='unconfirmed')setPicker({conversation:v.selected});setPickerVisible(true);void loadFriends();}}>{t('group.add')}</button></aside>}</section>:
    page==='Friends'?<><FriendsPanel v={v} search={search} setSearch={setSearch} searched={searched} setSearched={setSearched} open={open} loadFriends={loadFriends} searchUsers={searchUsers} addFriend={addFriend}/></>:
    page==='AI'||page==='Plugin'?<Placeholder page={page} setPage={setPage}/>:
    page==='Settings'?<SettingsPanel locale={locale} selectLanguage={selectLanguage} languageStored={languageStored} prefs={prefs} appearance={appearance} stored={stored}/>:
    <ProfilePanel v={v} loadProfile={loadProfile} refresh={refresh} logout={logout}/>}
    {picker&&<GroupPanel v={v} conversation={picker.conversation} submit={submitGroup} retry={retryGroup} visible={pickerVisible} close={()=>{setPickerVisible(false);if(v.groupStatus!=='unconfirmed')setPicker(null);}}/>}</div></div>;
}


import {GroupPanel} from './GroupPanel.js';
import {LanguageContext,useText,useDisplayText} from "../i18n/context.js";
import {WindowBar} from "./WindowBar.js";
import {Navigation} from "./Navigation.js";
import {Header} from "./Header.js";
import {AuthPanel} from "./AuthPanel.js";
import {ConversationList} from "./ConversationList.js";
import {Messages} from "./Messages.js";
import {Composer} from "./Composer.js";
import {FriendsPanel} from "./FriendsPanel.js";
import {AIPlaceholder} from "./AIPlaceholder.js";
import {PluginPlaceholder} from "./PluginPlaceholder.js";
import {SettingsPanel} from "./SettingsPanel.js";
import React,{useEffect,useRef,useState,useSyncExternalStore} from "react";
import {Workspace} from "../../application/ui/workspace.js";
import {windowControl,windowMaximized} from "../../application/ui/native.js";
import {resizedComposerHeight} from "../composer.js";
const app=new Workspace();
export function Shell(){const s=useSyncExternalStore(app.observe,app.snapshot);
 useEffect(()=>{document.documentElement.lang=s.language;},[s.language]);
 return <LanguageContext.Provider value={s.language}><WorkspaceShell/></LanguageContext.Provider>;
}
function WorkspaceShell(){const t=useText();const display=useDisplayText();
  const s=useSyncExternalStore(app.observe,app.snapshot),[registering,setRegistering]=useState(false),[confirmation,setConfirmation]=useState(""),[registered,setRegistered]=useState(false),[username,setUsername]=useState(""),[password,setPassword]=useState(""),[query,setQuery]=useState(""),[draft,setDraft]=useState(""),[maximized,setMaximized]=useState(false);
  const [menu,setMenu]=useState(false),[picker,setPicker]=useState<{conversation?:string}|null>(null),[pickerVisible,setPickerVisible]=useState(false),[management,setManagement]=useState(false);
  async function submitGroup(ids:string[],conversation?:string){await app.createGroup(ids,conversation);if(app.snapshot().groupStatus==='success')setPicker(null);}
  async function retryGroup(){await app.retryGroup();if(app.snapshot().groupStatus==='success')setPicker(null);}
  function showPicker(conversation?:string){if(s.groupStatus!=='unconfirmed')setPicker({conversation});setPickerVisible(true);setMenu(false);}
  useEffect(()=>{setManagement(false);},[s.selected]);
  useEffect(()=>{if(!s.session){setPicker(null);setMenu(false);setManagement(false);}},[s.session]);
  const [composerHeight,setComposerHeight]=useState(72),textarea=useRef<HTMLTextAreaElement>(null),resize=useRef<{y:number;height:number}|null>(null);
  useEffect(()=>{void app.start();},[]);
  useEffect(()=>{let active=true;const refresh=()=>{void windowMaximized().then(value=>{if(active)setMaximized(value);});};refresh();window.addEventListener("resize",refresh);return()=>{active=false;window.removeEventListener("resize",refresh);};},[]);
  const add=app.add.bind(app),disconnect=app.disconnect.bind(app),login=app.login.bind(app),logout=app.logout.bind(app),open=app.open.bind(app),page=app.page.bind(app),preferences=app.preferences.bind(app),reconnect=app.reconnect.bind(app),refresh=app.refresh.bind(app),register=app.register.bind(app),restore=app.restore.bind(app),retry=app.retry.bind(app),search=app.search.bind(app),send=app.send.bind(app),testNotification=app.testNotification.bind(app);
  const prefs=s.appearance,friend=s.friends.find(f=>f.directConversationId===s.selected),title=friend?.user.displayName??(s.selected?t("chat.conversationId",{id:s.selected.slice(0,8)}):t("chat.your"));
  const run=(p:Promise<unknown>)=>{void p;};
  const authenticated=!!(s.session||s.offlineAccount);
  return <div className={"app-window "+prefs.theme} style={{"--font":prefs.fontSize+"px","--density":prefs.density} as React.CSSProperties}>
    <WindowBar maximized={maximized} windowControl={windowControl} run={run}/>
    <div className={"workspace "+(authenticated?"authenticated":"anonymous")}>
    {authenticated&&<Navigation s={s} page={page}/>}<main>
      {authenticated&&<Header s={s} prefs={prefs} preferences={preferences} run={run}/>}
      {s.error&&<div className="notice" role="alert"><span>{display(s.error)}</span>{s.session&&<button disabled={!s.session} onClick={()=>run(reconnect())}>{t("auth.reconnect")}</button>}</div>}
      {!authenticated?<AuthPanel s={s} registering={registering} setRegistering={setRegistering} confirmation={confirmation} setConfirmation={setConfirmation} registered={registered} setRegistered={setRegistered} username={username} setUsername={setUsername} password={password} setPassword={setPassword} register={register} login={login} restore={restore} run={run}/>:
      s.page==="Chat"?<section className="chat-layout"><ConversationList newChat={<div className="new-chat"><button className="quiet" aria-expanded={menu} onClick={()=>setMenu(!menu)}>{t("chat.new")}</button>{menu&&<div className="new-chat-menu" onKeyDown={e=>{if(e.key==='Escape')setMenu(false);}}><button onClick={()=>{setMenu(false);page('Friends');}}>{t('group.friend')}</button><button onClick={()=>showPicker()}>{t('group.create')}</button></div>}</div>} s={s} page={page} open={open} run={run}/>
      <div className="chat-pane glass">{s.selected&&<><div className="chat-heading"><span className="avatar">{friend?.user.displayName[0]??"#"}</span><div><h2>{title}</h2><small>{s.connection==="ready"?t("sync.connected"):t("sync.offline")}</small></div><button className="quiet" disabled={!s.session} onClick={()=>run(reconnect())}>{t("auth.reconnect")}</button>{s.groups.some(r=>r.conversationId===s.selected)&&<button aria-label={t('group.members')} aria-expanded={management} onClick={()=>setManagement(!management)}>…</button>}</div><Messages s={s} retry={retry} run={run}/><Composer s={s} draft={draft} setDraft={setDraft} send={send} run={run} textarea={textarea} composerHeight={composerHeight} setComposerHeight={setComposerHeight} resize={resize}/></>}</div>{management&&s.groups.some(r=>r.conversationId===s.selected)&&<aside className="group-management"><h2>{t('group.title')}</h2><p>{s.selected}</p><h3>{t('group.members')}</h3>{s.groups.filter(r=>r.conversationId===s.selected).map(r=><div className="group-person" key={r.member.user.userId}><span className="avatar">{r.member.user.userId.slice(0,1)}</span><span>{r.member.user.displayName}</span></div>)}<button onClick={()=>showPicker(s.selected)}>{t('group.add')}</button></aside>}</section>:
      s.page==="Friends"?<><FriendsPanel s={s} query={query} setQuery={setQuery} search={search} add={add} open={open} run={run}/></>:
      s.page==="AI"?<AIPlaceholder />:
      s.page==="Plugin"?<PluginPlaceholder />:
      <SettingsPanel selectLanguage={app.selectLanguage.bind(app)} language={s.language} languageStored={s.languageStored} s={s} prefs={prefs} preferences={preferences} refresh={refresh} disconnect={disconnect} reconnect={reconnect} testNotification={testNotification} logout={logout} run={run}/>}
    {picker&&<GroupPanel v={s} conversation={picker.conversation} submit={submitGroup} retry={retryGroup} visible={pickerVisible} close={()=>{setPickerVisible(false);if(s.groupStatus!=='unconfirmed')setPicker(null);}}/>}</main></div></div>;
}


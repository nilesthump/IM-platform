//! Generic Windows adapters. Auth/protocol/Repository decisions stay TypeScript.
use std::collections::BTreeMap;
use tauri::Manager;
use tauri_plugin_notification::NotificationExt;
use tauri_plugin_global_shortcut::{GlobalShortcutExt,ShortcutState};
const MAX_BODY:usize=4*1024*1024;
#[tauri::command]
pub async fn native_https(url:String,method:String,headers:BTreeMap<String,String>,body:Vec<u8>)->Result<(u16,BTreeMap<String,String>,Vec<u8>),String>{
    let url=reqwest::Url::parse(&url).map_err(|_|"HTTPS request invalid")?;
    if url.scheme()!="https" || url.host_str().is_none() || !url.username().is_empty() || url.password().is_some() || url.fragment().is_some() || body.len()>MAX_BODY {return Err("HTTPS request invalid".into());}
    if url.query_pairs().any(|(name,_)|matches!(name.to_ascii_lowercase().as_str(),"token"|"access_token"|"accesstoken"|"refresh_token"|"refreshtoken"|"password"|"credential")){return Err("Credential query forbidden".into());}
    let method=reqwest::Method::from_bytes(method.as_bytes()).map_err(|_|"HTTPS method invalid")?;
    if ![reqwest::Method::GET,reqwest::Method::POST,reqwest::Method::PUT].contains(&method) || headers.len()>16{return Err("HTTPS request invalid".into());}
    let client=reqwest::Client::builder().https_only(true).redirect(reqwest::redirect::Policy::none()).timeout(std::time::Duration::from_secs(15)).build().map_err(|_|"HTTPS transport unavailable")?;
    let mut request=client.request(method,url).body(body);
    for (name,value) in headers {
        if !["authorization","content-type","accept"].contains(&name.to_ascii_lowercase().as_str()) || value.len()>8192 || value.contains(['\r','\n']){return Err("HTTPS headers invalid".into());}
        request=request.header(name,value);
    }
    let mut response=request.send().await.map_err(|_|"HTTPS transport unavailable")?;
    let status=response.status().as_u16();
    if (300..400).contains(&status){return Err("HTTPS redirects forbidden".into());}
    let response_headers:BTreeMap<String,String>=response.headers().iter().filter_map(|(k,v)|v.to_str().ok().map(|v|(k.as_str().to_owned(),v.to_owned()))).collect();
    if response.content_length().map(|n|n>MAX_BODY as u64).unwrap_or(false){return Err("HTTPS response too large".into());}
    let mut bytes=Vec::new();while let Some(chunk)=response.chunk().await.map_err(|_|"HTTPS transport unavailable")? {if bytes.len()+chunk.len()>MAX_BODY{return Err("HTTPS response too large".into());}bytes.extend_from_slice(&chunk);}
    Ok((status,response_headers,bytes))
}
fn entry(slot:&str)->Result<keyring::Entry,String>{
    if slot.is_empty() || slot.len()>240 || slot.contains(['\r','\n']) {return Err("Credential slot invalid".into());}
    keyring::Entry::new("im.platform.desktop",slot).map_err(|_|"Secure credential storage unavailable".into())
}
#[tauri::command]
pub fn credential_read(slot:String)->Result<Option<String>,String>{match entry(&slot)?.get_password(){Ok(value)=>Ok(Some(value)),Err(keyring::Error::NoEntry)=>Ok(None),Err(_)=>Err("Secure credential storage unavailable".into())}}
#[tauri::command]
pub fn credential_write(slot:String,value:String)->Result<(),String>{if value.is_empty()||value.len()>8192{return Err("Credential value invalid".into());}entry(&slot)?.set_password(&value).map_err(|_|"Secure credential storage unavailable".into())}
#[tauri::command]
pub fn credential_remove(slot:String)->Result<(),String>{match entry(&slot)?.delete_credential(){Ok(())|Err(keyring::Error::NoEntry)=>Ok(()),Err(_)=>Err("Secure credential storage unavailable".into())}}
fn appearance_path(app:&tauri::AppHandle)->Result<std::path::PathBuf,String>{Ok(app.path().app_data_dir().map_err(|_|"Appearance unavailable")?.join("appearance.json"))}
type Appearance=(String,u8,f64);
fn valid_appearance(value:&Appearance)->bool{matches!(value.0.as_str(),"cold"|"warm")&&(14..=22).contains(&value.1)&&[0.8,1.0,1.2].iter().any(|v|(value.2-v).abs()<0.001)}
fn appearance_bytes(value:&Appearance)->Vec<u8>{format!("[\"{}\",{},{}]",value.0,value.1,value.2).into_bytes()}
#[tauri::command]
pub fn appearance_load(app:tauri::AppHandle)->Result<Appearance,String>{let p=appearance_path(&app)?;if !p.exists(){return Ok(("cold".into(),16,1.0));}let bytes=std::fs::read(p).map_err(|_|"Appearance unavailable")?;if bytes.len()>64{return Err("Appearance invalid".into());}for theme in ["cold","warm"]{for font in 14..=22{for density in [0.8,1.0,1.2]{let value=(theme.to_owned(),font,density);if appearance_bytes(&value)==bytes{return Ok(value);}}}}Err("Appearance invalid".into())}
#[tauri::command]
pub fn appearance_save(app:tauri::AppHandle,mut value:Appearance)->Result<(),String>{if !valid_appearance(&value){return Err("Appearance invalid".into());}value.2=[0.8,1.0,1.2].into_iter().find(|v|(value.2-v).abs()<0.001).ok_or("Appearance invalid")?;let p=appearance_path(&app)?;std::fs::create_dir_all(p.parent().ok_or("Appearance unavailable")?).map_err(|_|"Appearance unavailable")?;std::fs::write(p,appearance_bytes(&value)).map_err(|_|"Appearance unavailable".into())}
#[tauri::command]
pub fn native_notify(app:tauri::AppHandle,title:String,body:String)->Result<(),String>{if title.chars().count()>80||body.chars().count()>300{return Err("Notification invalid".into());}app.notification().builder().title(title).body(body).show().map_err(|_|"Notification unavailable".into())}
#[tauri::command]
pub fn window_maximized(window:tauri::WebviewWindow)->Result<bool,String>{window.is_maximized().map_err(|_|"Window unavailable".into())}
#[tauri::command]
pub fn window_control(window:tauri::WebviewWindow,action:String)->Result<(),String>{
    let result=match action.as_str(){
        "minimize"=>window.minimize(),
        "maximize"=>if window.is_maximized().map_err(|_|"Window unavailable")?{window.unmaximize()}else{window.maximize()},
        "close"=>window.close(),
        "drag"=>window.start_dragging(),
        _=>return Err("Window action invalid".into()),
    };
    result.map_err(|_|"Window unavailable".into())
}
fn show(app:&tauri::AppHandle){if let Some(w)=app.get_webview_window("main"){let _=w.show();let _=w.unminimize();let _=w.set_focus();}}
pub fn setup(app:&mut tauri::App)->Result<(),Box<dyn std::error::Error>>{
    app.global_shortcut().on_shortcut("Ctrl+Shift+Space",|app,_,event|{if event.state==ShortcutState::Pressed{show(app);}})?;
    let open=tauri::menu::MenuItem::with_id(app,"open","Open IM+",true,None::<&str>)?;
    let hide=tauri::menu::MenuItem::with_id(app,"hide","Hide window",true,None::<&str>)?;
    let quit=tauri::menu::MenuItem::with_id(app,"quit","Quit IM+",true,None::<&str>)?;
    let menu=tauri::menu::Menu::with_items(app,&[&open,&hide,&quit])?;
    let icon=app.default_window_icon().ok_or("Application icon unavailable")?.clone();
    tauri::tray::TrayIconBuilder::with_id("im-plus").icon(icon).tooltip("IM+ · Your workspace").menu(&menu).on_menu_event(|app,event|match event.id.as_ref(){"open"=>show(app),"hide"=>{if let Some(w)=app.get_webview_window("main"){let _=w.hide();}},"quit"=>app.exit(0),_=>{}}).build(app)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn actual_windows_credential_manager_roundtrip() {
        let nonce=std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        let slot=format!("https://gui-owned-fixture.invalid/{}/{nonce}",std::process::id());
        assert_eq!(credential_read(slot.clone()).unwrap(),None);
        struct Owned(String);
        impl Drop for Owned {fn drop(&mut self){let _=credential_remove(self.0.clone());}}
        let cleanup=Owned(slot.clone());
        credential_write(slot.clone(),"gui-owned-fixture-refresh-value".into()).unwrap();
        assert_eq!(credential_read(slot.clone()).unwrap().as_deref(),Some("gui-owned-fixture-refresh-value"));
        credential_write(slot.clone(),"gui-owned-fixture-rotated-value".into()).unwrap();
        assert_eq!(credential_read(slot.clone()).unwrap().as_deref(),Some("gui-owned-fixture-rotated-value"));
        credential_remove(slot.clone()).unwrap();
        assert_eq!(credential_read(slot).unwrap(),None);
        drop(cleanup);
    }
}

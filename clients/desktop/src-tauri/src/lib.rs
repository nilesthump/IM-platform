pub mod database;
#[cfg(windows)]
mod desktop_capabilities;
use std::path::PathBuf;
use tauri::Manager;

// Commands carry only generic SQL/bindings/row-count assertions. No models,
// migration, identity decisions or Repository orchestration lives in Rust.
fn root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    app.path().app_data_dir().map_err(|_| "Storage directory unavailable".into())
}
#[tauri::command]
async fn database_transaction(app: tauri::AppHandle, account_id: String,
    statements: Vec<database::Statement>) -> Result<(), String> {
    let mut connection = database::open(root(&app)?, &account_id).await?;
    database::transaction(&mut connection, statements).await
}
#[tauri::command]
async fn database_query(app: tauri::AppHandle, account_id: String,
    sql: String, binds: Vec<Option<String>>) -> Result<Vec<Vec<Option<String>>>, String> {
    let mut connection = database::open_read_only(root(&app)?, &account_id).await?;
    database::query(&mut connection, &sql, binds).await
}
pub fn run() {
    #[cfg(not(windows))]
    let builder=tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![database_transaction, database_query])
        ;
    #[cfg(windows)]
    let builder=tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .setup(desktop_capabilities::setup)
        .on_window_event(|window,event|if let tauri::WindowEvent::CloseRequested{api,..}=event {api.prevent_close();let _=window.hide();})
        .invoke_handler(tauri::generate_handler![database_transaction,database_query,desktop_capabilities::native_https,desktop_capabilities::credential_read,desktop_capabilities::credential_write,desktop_capabilities::credential_remove,desktop_capabilities::appearance_load,desktop_capabilities::appearance_save,desktop_capabilities::native_notify]);
    builder.run(tauri::generate_context!())
        .expect("Tauri startup failed");
}

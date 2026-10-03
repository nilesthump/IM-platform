pub mod database;
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
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![database_transaction, database_query])
        .run(tauri::generate_context!())
        .expect("Tauri startup failed");
}

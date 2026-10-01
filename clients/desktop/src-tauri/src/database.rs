use sqlx::{Connection, Row, SqliteConnection, TypeInfo, ValueRef};
use sqlx::sqlite::SqliteConnectOptions;
use std::{path::PathBuf, time::Duration};

pub type Statement = (String, Vec<Option<String>>, Option<u64>);
pub async fn open(root: PathBuf, account: &str) -> Result<SqliteConnection, String> {
    // UUID filenames prevent directory traversal/aliases and keep accounts apart.
    if account.len() != 36 || !account.chars().enumerate().all(|(i,c)|
        if [8,13,18,23].contains(&i) { c=='-' } else { c.is_ascii_hexdigit() }) {
        return Err("Invalid account identity".into());
    }
    std::fs::create_dir_all(&root).map_err(|_| "Storage directory unavailable")?;
    let options = SqliteConnectOptions::new()
        .filename(root.join(format!("im-{}.sqlite",account.to_ascii_lowercase())))
        .create_if_missing(true).busy_timeout(Duration::from_secs(5));
    SqliteConnection::connect_with(&options).await.map_err(|_| "Storage open failed".into())
}
pub async fn open_read_only(root: PathBuf, account: &str) -> Result<SqliteConnection, String> {
    // Ensure the account's empty file can exist before its first migration,
    // then reopen physically read-only: even caller PRAGMAs cannot enable writes.
    open(root.clone(), account).await?.close().await.map_err(|_| "Storage close failed")?;
    let options = SqliteConnectOptions::new()
        .filename(root.join(format!("im-{}.sqlite", account.to_ascii_lowercase())))
        .read_only(true).busy_timeout(Duration::from_secs(5));
    SqliteConnection::connect_with(&options).await.map_err(|_| "Storage read open failed".into())
}
pub async fn transaction(connection: &mut SqliteConnection, statements: Vec<Statement>) -> Result<(), String> {
    let mut tx = connection.begin().await.map_err(|_| "Transaction start failed")?;
    for (sql, binds, expected) in statements {
        let mut query = sqlx::query(&sql);
        for value in binds { query = query.bind(value); }
        match query.execute(&mut *tx).await {
            Ok(result) if expected.is_none() || expected == Some(result.rows_affected()) => (),
            _ => {
                tx.rollback().await.map_err(|_| "Transaction rollback failed")?;
                return Err("Storage statement rejected".into());
            }
        }
    }
    tx.commit().await.map_err(|_| "Transaction commit failed".into())
}
pub async fn query(connection: &mut SqliteConnection, sql: &str, binds: Vec<Option<String>>) -> Result<Vec<Vec<Option<String>>>, String> {
    // The product query command is read-only. SQLite query_only applies to this
    // connection; transaction commands open their own connection.
    sqlx::query("PRAGMA query_only=ON").execute(&mut *connection).await.map_err(|_| "Read-only setup failed")?;
    let mut query = sqlx::query(sql);
    for value in binds { query=query.bind(value); }
    let result = query.fetch_all(&mut *connection).await;
    sqlx::query("PRAGMA query_only=OFF").execute(&mut *connection).await.map_err(|_| "Read-only reset failed")?;
    let rows = result.map_err(|_| "Storage query rejected")?;
    rows.iter().map(|row| (0..row.len()).map(|i| {
        let value = row.try_get_raw(i).map_err(|_| "Storage result unavailable".to_string())?;
        match value.type_info().name() {
            "INTEGER" => row.try_get::<Option<i64>,_>(i).map(|v|v.map(|n|n.to_string())),
            _ => row.try_get::<Option<String>,_>(i),
        }.map_err(|_| "Storage result type rejected".to_string())
    }).collect()).collect()
}

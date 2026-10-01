use im_client_storage::database;
#[test]
fn real_atomic_adapter_rolls_back_and_queries_are_read_only() {
    tauri::async_runtime::block_on(async {
        let root=std::env::temp_dir().join(format!("im-storage-native-{}",std::process::id()));
        let mut db=database::open(root.clone(),"10000000-0000-4000-8000-000000000001").await.unwrap();
        database::transaction(&mut db,vec![("CREATE TABLE probe(v TEXT)".into(),vec![],None)]).await.unwrap();
        assert!(database::transaction(&mut db,vec![
            ("INSERT INTO probe VALUES(?)".into(),vec![Some("rollback".into())],Some(1)),
            ("INSERT INTO missing_table VALUES(1)".into(),vec![],None)]).await.is_err());
        assert!(database::query(&mut db,"SELECT v FROM probe",vec![]).await.unwrap().is_empty());
        assert!(database::query(&mut db,"INSERT INTO probe VALUES('bad') RETURNING v",vec![]).await.is_err());
        assert!(database::open(root.clone(),"../bad").await.is_err());
        sqlx::Connection::close(db).await.unwrap();
        // Only the test's uniquely named owned file is removed.
        std::fs::remove_file(root.join("im-10000000-0000-4000-8000-000000000001.sqlite")).unwrap();
        std::fs::remove_dir(root).unwrap();
    });
}

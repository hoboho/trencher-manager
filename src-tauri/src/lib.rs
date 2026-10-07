mod commands;

use commands::DbState;
use std::sync::Mutex;
use tauri::Manager;
use terencher_core::db;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // Resolve a writable per-app data directory (Android/iOS/desktop safe).
            let data_dir = app
                .path()
                .app_data_dir()
                .expect("could not resolve app data dir");
            std::fs::create_dir_all(&data_dir).ok();
            let db_path = data_dir.join("terencher.db");

            let conn = db::init_db(&db_path).expect("failed to open database");
            app.manage(DbState {
                conn: Mutex::new(conn),
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_projects,
            commands::create_project,
            commands::update_project,
            commands::delete_project,
            commands::get_machines,
            commands::create_machine,
            commands::update_machine,
            commands::delete_machine,
            commands::get_operators,
            commands::create_operator,
            commands::update_operator,
            commands::delete_operator,
            commands::get_transactions,
            commands::create_transaction,
            commands::update_transaction,
            commands::delete_transaction,
            commands::get_dashboard_stats,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

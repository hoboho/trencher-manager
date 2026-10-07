use rusqlite::Connection;
use std::sync::Mutex;
use tauri::State;
use terencher_core::db;
use terencher_core::models::*;

pub struct DbState {
    pub conn: Mutex<Connection>,
}

macro_rules! list_cmd {
    ($fn_name:ident, $db_fn:ident, $ty:ty) => {
        #[tauri::command]
        pub fn $fn_name(state: State<DbState>) -> Vec<$ty> {
            let conn = state.conn.lock().unwrap();
            db::$db_fn(&conn).unwrap_or_default()
        }
    };
}

macro_rules! create_cmd {
    ($fn_name:ident, $db_fn:ident, $ty:ty, $arg:ident) => {
        #[tauri::command]
        pub fn $fn_name(state: State<DbState>, $arg: $ty) -> Result<i64, String> {
            let conn = state.conn.lock().unwrap();
            db::$db_fn(&conn, &$arg).map_err(|e| e.to_string())
        }
    };
}

macro_rules! update_cmd {
    ($fn_name:ident, $db_fn:ident, $ty:ty, $arg:ident) => {
        #[tauri::command]
        pub fn $fn_name(state: State<DbState>, $arg: $ty) -> Result<(), String> {
            let conn = state.conn.lock().unwrap();
            db::$db_fn(&conn, &$arg).map_err(|e| e.to_string())
        }
    };
}

macro_rules! delete_cmd {
    ($fn_name:ident, $db_fn:ident) => {
        #[tauri::command]
        pub fn $fn_name(state: State<DbState>, id: i64) -> Result<(), String> {
            let conn = state.conn.lock().unwrap();
            db::$db_fn(&conn, id).map_err(|e| e.to_string())
        }
    };
}

list_cmd!(get_projects, get_projects, Project);
create_cmd!(create_project, create_project, Project, project);
update_cmd!(update_project, update_project, Project, project);
delete_cmd!(delete_project, delete_project);

list_cmd!(get_machines, get_machines, Machine);
create_cmd!(create_machine, create_machine, Machine, machine);
update_cmd!(update_machine, update_machine, Machine, machine);
delete_cmd!(delete_machine, delete_machine);

list_cmd!(get_operators, get_operators, Operator);
create_cmd!(create_operator, create_operator, Operator, operator);
update_cmd!(update_operator, update_operator, Operator, operator);
delete_cmd!(delete_operator, delete_operator);

list_cmd!(get_transactions, get_transactions, Transaction);
create_cmd!(create_transaction, create_transaction, Transaction, transaction);
update_cmd!(update_transaction, update_transaction, Transaction, transaction);
delete_cmd!(delete_transaction, delete_transaction);

#[tauri::command]
pub fn get_dashboard_stats(state: State<DbState>) -> DashboardStats {
    let conn = state.conn.lock().unwrap();
    db::get_dashboard_stats(&conn).unwrap_or(DashboardStats {
        total_projects: 0,
        active_projects: 0,
        total_machines: 0,
        active_machines: 0,
        total_operators: 0,
        total_income: 0.0,
        total_expense: 0.0,
        net_profit: 0.0,
        recent_projects: vec![],
    })
}

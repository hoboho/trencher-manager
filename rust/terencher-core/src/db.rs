use rusqlite::{Connection, Result, params};
use crate::models::*;

pub fn init_db(path: &std::path::Path) -> Result<Connection> {
    let conn = Connection::open(path)?;
    conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;")?;
    schema(&conn)?;
    Ok(conn)
}

fn schema(conn: &Connection) -> Result<()> {
    conn.execute_batch("
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_name TEXT,
            client_contact TEXT,
            location TEXT,
            contract_amount REAL NOT NULL DEFAULT 0,
            received_amount REAL NOT NULL DEFAULT 0,
            start_date TEXT NOT NULL,
            end_date TEXT,
            total_length REAL,
            average_depth REAL,
            average_width REAL,
            status TEXT NOT NULL DEFAULT 'active',
            description TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT,
            purchase_date TEXT,
            purchase_price REAL,
            fuel_consumption_rate REAL,
            fuel_cost_per_liter REAL,
            maintenance_cost_per_hour REAL,
            trenching_depth REAL,
            trenching_width REAL,
            maximum_speed REAL,
            weight REAL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hourly_rate REAL NOT NULL DEFAULT 0,
            overtime_rate REAL NOT NULL DEFAULT 0,
            overtime_threshold REAL NOT NULL DEFAULT 8,
            contact TEXT,
            skills TEXT,
            specialization TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL DEFAULT 'other',
            description TEXT,
            date TEXT NOT NULL,
            project_id INTEGER REFERENCES projects(id),
            operator_id INTEGER REFERENCES operators(id),
            machine_id INTEGER REFERENCES machines(id),
            created_at TEXT DEFAULT (datetime('now'))
        );
    ")
}

// ─── Projects ───────────────────────────────────────────────────────────────

pub fn get_projects(conn: &Connection) -> Result<Vec<Project>> {
    let mut stmt = conn.prepare(
        "SELECT id,name,client_name,client_contact,location,contract_amount,
                received_amount,start_date,end_date,total_length,average_depth,
                average_width,status,description,notes,created_at
         FROM projects ORDER BY created_at DESC")?;
    let rows = stmt.query_map([], |r| Ok(Project {
        id: r.get(0)?, name: r.get(1)?, client_name: r.get(2)?, client_contact: r.get(3)?,
        location: r.get(4)?, contract_amount: r.get(5)?, received_amount: r.get(6)?,
        start_date: r.get(7)?, end_date: r.get(8)?, total_length: r.get(9)?,
        average_depth: r.get(10)?, average_width: r.get(11)?, status: r.get(12)?,
        description: r.get(13)?, notes: r.get(14)?, created_at: r.get(15)?,
    }))?;
    rows.collect()
}

pub fn create_project(conn: &Connection, p: &Project) -> Result<i64> {
    conn.execute(
        "INSERT INTO projects (name,client_name,client_contact,location,contract_amount,
            received_amount,start_date,end_date,total_length,average_depth,average_width,
            status,description,notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14)",
        params![p.name, p.client_name, p.client_contact, p.location, p.contract_amount,
                p.received_amount, p.start_date, p.end_date, p.total_length, p.average_depth,
                p.average_width, p.status, p.description, p.notes])?;
    Ok(conn.last_insert_rowid())
}

pub fn update_project(conn: &Connection, p: &Project) -> Result<()> {
    conn.execute(
        "UPDATE projects SET name=?1,client_name=?2,client_contact=?3,location=?4,
            contract_amount=?5,received_amount=?6,start_date=?7,end_date=?8,total_length=?9,
            average_depth=?10,average_width=?11,status=?12,description=?13,notes=?14
         WHERE id=?15",
        params![p.name, p.client_name, p.client_contact, p.location, p.contract_amount,
                p.received_amount, p.start_date, p.end_date, p.total_length, p.average_depth,
                p.average_width, p.status, p.description, p.notes, p.id])?;
    Ok(())
}

pub fn delete_project(conn: &Connection, id: i64) -> Result<()> {
    conn.execute("DELETE FROM projects WHERE id=?1", params![id])?;
    Ok(())
}

// ─── Machines ───────────────────────────────────────────────────────────────

pub fn get_machines(conn: &Connection) -> Result<Vec<Machine>> {
    let mut stmt = conn.prepare(
        "SELECT id,name,model,purchase_date,purchase_price,fuel_consumption_rate,
                fuel_cost_per_liter,maintenance_cost_per_hour,trenching_depth,
                trenching_width,maximum_speed,weight,status,created_at
         FROM machines ORDER BY created_at DESC")?;
    let rows = stmt.query_map([], |r| Ok(Machine {
        id: r.get(0)?, name: r.get(1)?, model: r.get(2)?, purchase_date: r.get(3)?,
        purchase_price: r.get(4)?, fuel_consumption_rate: r.get(5)?,
        fuel_cost_per_liter: r.get(6)?, maintenance_cost_per_hour: r.get(7)?,
        trenching_depth: r.get(8)?, trenching_width: r.get(9)?, maximum_speed: r.get(10)?,
        weight: r.get(11)?, status: r.get(12)?, created_at: r.get(13)?,
    }))?;
    rows.collect()
}

pub fn create_machine(conn: &Connection, m: &Machine) -> Result<i64> {
    conn.execute(
        "INSERT INTO machines (name,model,purchase_date,purchase_price,fuel_consumption_rate,
            fuel_cost_per_liter,maintenance_cost_per_hour,trenching_depth,trenching_width,
            maximum_speed,weight,status) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12)",
        params![m.name, m.model, m.purchase_date, m.purchase_price, m.fuel_consumption_rate,
                m.fuel_cost_per_liter, m.maintenance_cost_per_hour, m.trenching_depth,
                m.trenching_width, m.maximum_speed, m.weight, m.status])?;
    Ok(conn.last_insert_rowid())
}

pub fn update_machine(conn: &Connection, m: &Machine) -> Result<()> {
    conn.execute(
        "UPDATE machines SET name=?1,model=?2,purchase_date=?3,purchase_price=?4,
            fuel_consumption_rate=?5,fuel_cost_per_liter=?6,maintenance_cost_per_hour=?7,
            trenching_depth=?8,trenching_width=?9,maximum_speed=?10,weight=?11,status=?12
         WHERE id=?13",
        params![m.name, m.model, m.purchase_date, m.purchase_price, m.fuel_consumption_rate,
                m.fuel_cost_per_liter, m.maintenance_cost_per_hour, m.trenching_depth,
                m.trenching_width, m.maximum_speed, m.weight, m.status, m.id])?;
    Ok(())
}

pub fn delete_machine(conn: &Connection, id: i64) -> Result<()> {
    conn.execute("DELETE FROM machines WHERE id=?1", params![id])?;
    Ok(())
}

// ─── Operators ──────────────────────────────────────────────────────────────

pub fn get_operators(conn: &Connection) -> Result<Vec<Operator>> {
    let mut stmt = conn.prepare(
        "SELECT id,name,hourly_rate,overtime_rate,overtime_threshold,contact,skills,
                specialization,notes,created_at FROM operators ORDER BY created_at DESC")?;
    let rows = stmt.query_map([], |r| Ok(Operator {
        id: r.get(0)?, name: r.get(1)?, hourly_rate: r.get(2)?, overtime_rate: r.get(3)?,
        overtime_threshold: r.get(4)?, contact: r.get(5)?, skills: r.get(6)?,
        specialization: r.get(7)?, notes: r.get(8)?, created_at: r.get(9)?,
    }))?;
    rows.collect()
}

pub fn create_operator(conn: &Connection, o: &Operator) -> Result<i64> {
    conn.execute(
        "INSERT INTO operators (name,hourly_rate,overtime_rate,overtime_threshold,contact,
            skills,specialization,notes) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
        params![o.name, o.hourly_rate, o.overtime_rate, o.overtime_threshold, o.contact,
                o.skills, o.specialization, o.notes])?;
    Ok(conn.last_insert_rowid())
}

pub fn update_operator(conn: &Connection, o: &Operator) -> Result<()> {
    conn.execute(
        "UPDATE operators SET name=?1,hourly_rate=?2,overtime_rate=?3,overtime_threshold=?4,
            contact=?5,skills=?6,specialization=?7,notes=?8 WHERE id=?9",
        params![o.name, o.hourly_rate, o.overtime_rate, o.overtime_threshold, o.contact,
                o.skills, o.specialization, o.notes, o.id])?;
    Ok(())
}

pub fn delete_operator(conn: &Connection, id: i64) -> Result<()> {
    conn.execute("DELETE FROM operators WHERE id=?1", params![id])?;
    Ok(())
}

// ─── Transactions ───────────────────────────────────────────────────────────

pub fn get_transactions(conn: &Connection) -> Result<Vec<Transaction>> {
    let mut stmt = conn.prepare(
        "SELECT t.id,t.transaction_type,t.amount,t.category,t.description,t.date,
                t.project_id,t.operator_id,t.machine_id,p.name,o.name,m.name,t.created_at
         FROM transactions t
         LEFT JOIN projects p ON t.project_id=p.id
         LEFT JOIN operators o ON t.operator_id=o.id
         LEFT JOIN machines m ON t.machine_id=m.id
         ORDER BY t.date DESC")?;
    let rows = stmt.query_map([], |r| Ok(Transaction {
        id: r.get(0)?, transaction_type: r.get(1)?, amount: r.get(2)?, category: r.get(3)?,
        description: r.get(4)?, date: r.get(5)?, project_id: r.get(6)?, operator_id: r.get(7)?,
        machine_id: r.get(8)?, project_name: r.get(9)?, operator_name: r.get(10)?,
        machine_name: r.get(11)?, created_at: r.get(12)?,
    }))?;
    rows.collect()
}

pub fn create_transaction(conn: &Connection, t: &Transaction) -> Result<i64> {
    conn.execute(
        "INSERT INTO transactions (transaction_type,amount,category,description,date,
            project_id,operator_id,machine_id) VALUES (?1,?2,?3,?4,?5,?6,?7,?8)",
        params![t.transaction_type, t.amount, t.category, t.description, t.date,
                t.project_id, t.operator_id, t.machine_id])?;
    Ok(conn.last_insert_rowid())
}

pub fn update_transaction(conn: &Connection, t: &Transaction) -> Result<()> {
    conn.execute(
        "UPDATE transactions SET transaction_type=?1,amount=?2,category=?3,description=?4,
            date=?5,project_id=?6,operator_id=?7,machine_id=?8 WHERE id=?9",
        params![t.transaction_type, t.amount, t.category, t.description, t.date,
                t.project_id, t.operator_id, t.machine_id, t.id])?;
    Ok(())
}

pub fn delete_transaction(conn: &Connection, id: i64) -> Result<()> {
    conn.execute("DELETE FROM transactions WHERE id=?1", params![id])?;
    Ok(())
}

// ─── Dashboard ──────────────────────────────────────────────────────────────

pub fn get_dashboard_stats(conn: &Connection) -> Result<DashboardStats> {
    let q1 = |sql: &str| -> i64 { conn.query_row(sql, [], |r| r.get(0)).unwrap_or(0) };
    let total_projects = q1("SELECT COUNT(*) FROM projects");
    let active_projects = q1("SELECT COUNT(*) FROM projects WHERE status='active'");
    let total_machines = q1("SELECT COUNT(*) FROM machines");
    let active_machines = q1("SELECT COUNT(*) FROM machines WHERE status='active'");
    let total_operators = q1("SELECT COUNT(*) FROM operators");
    let total_income: f64 = conn
        .query_row("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE transaction_type='income'", [], |r| r.get(0))
        .unwrap_or(0.0);
    let total_expense: f64 = conn
        .query_row("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE transaction_type='expense'", [], |r| r.get(0))
        .unwrap_or(0.0);
    let recent_projects = get_projects(conn).unwrap_or_default().into_iter().take(5).collect();

    Ok(DashboardStats {
        total_projects, active_projects, total_machines, active_machines,
        total_operators, total_income, total_expense,
        net_profit: total_income - total_expense, recent_projects,
    })
}

/// Open an in-memory database with the schema applied. Useful for tests.
pub fn init_memory() -> Result<Connection> {
    let conn = Connection::open_in_memory()?;
    conn.execute_batch("PRAGMA foreign_keys=ON;")?;
    schema(&conn)?;
    Ok(conn)
}

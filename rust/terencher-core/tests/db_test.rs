use terencher_core::db;
use terencher_core::models::*;

fn sample_project() -> Project {
    Project {
        id: None,
        name: "Trench A1".into(),
        client_name: Some("ACME".into()),
        client_contact: Some("0912".into()),
        location: Some("Tehran".into()),
        contract_amount: 1_000_000.0,
        received_amount: 250_000.0,
        start_date: "2024-01-01".into(),
        end_date: None,
        total_length: Some(120.0),
        average_depth: Some(1.5),
        average_width: Some(0.6),
        status: "active".into(),
        description: None,
        notes: None,
        created_at: None,
    }
}

#[test]
fn project_crud_roundtrip() {
    let conn = db::init_memory().unwrap();
    let id = db::create_project(&conn, &sample_project()).unwrap();
    assert!(id > 0);

    let all = db::get_projects(&conn).unwrap();
    assert_eq!(all.len(), 1);
    assert_eq!(all[0].name, "Trench A1");
    assert_eq!(all[0].contract_amount, 1_000_000.0);

    let mut p = all[0].clone();
    p.status = "completed".into();
    p.received_amount = 1_000_000.0;
    db::update_project(&conn, &p).unwrap();

    let updated = db::get_projects(&conn).unwrap();
    assert_eq!(updated[0].status, "completed");
    assert_eq!(updated[0].received_amount, 1_000_000.0);

    db::delete_project(&conn, id).unwrap();
    assert!(db::get_projects(&conn).unwrap().is_empty());
}

#[test]
fn machine_and_operator_crud() {
    let conn = db::init_memory().unwrap();

    let m = Machine {
        id: None,
        name: "CAT 6015".into(),
        model: Some("6015B".into()),
        purchase_date: Some("2023-05-01".into()),
        purchase_price: Some(9_000_000.0),
        fuel_consumption_rate: Some(18.0),
        fuel_cost_per_liter: Some(6000.0),
        maintenance_cost_per_hour: Some(500_000.0),
        trenching_depth: Some(2.0),
        trenching_width: Some(0.8),
        maximum_speed: Some(150.0),
        weight: Some(15000.0),
        status: "active".into(),
        created_at: None,
    };
    db::create_machine(&conn, &m).unwrap();
    let machines = db::get_machines(&conn).unwrap();
    assert_eq!(machines.len(), 1);
    assert_eq!(machines[0].fuel_consumption_rate, Some(18.0));

    let o = Operator {
        id: None,
        name: "Ali".into(),
        hourly_rate: 400_000.0,
        overtime_rate: 600_000.0,
        overtime_threshold: 8.0,
        contact: Some("0935".into()),
        skills: Some("excavation".into()),
        specialization: Some("heavy".into()),
        notes: None,
        created_at: None,
    };
    db::create_operator(&conn, &o).unwrap();
    let ops = db::get_operators(&conn).unwrap();
    assert_eq!(ops.len(), 1);
    assert_eq!(ops[0].name, "Ali");
    assert_eq!(ops[0].overtime_threshold, 8.0);
}

#[test]
fn transaction_join_and_dashboard() {
    let conn = db::init_memory().unwrap();
    let pid = db::create_project(&conn, &sample_project()).unwrap();

    let income = Transaction {
        id: None,
        transaction_type: "income".into(),
        amount: 500_000.0,
        category: "project_payment".into(),
        description: Some("installment 1".into()),
        date: "2024-02-01".into(),
        project_id: Some(pid),
        operator_id: None,
        machine_id: None,
        project_name: None,
        operator_name: None,
        machine_name: None,
        created_at: None,
    };
    db::create_transaction(&conn, &income).unwrap();

    let expense = Transaction {
        id: None,
        transaction_type: "expense".into(),
        amount: 120_000.0,
        category: "fuel".into(),
        description: Some("diesel".into()),
        date: "2024-02-02".into(),
        project_id: Some(pid),
        operator_id: None,
        machine_id: None,
        project_name: None,
        operator_name: None,
        machine_name: None,
        created_at: None,
    };
    db::create_transaction(&conn, &expense).unwrap();

    let txs = db::get_transactions(&conn).unwrap();
    assert_eq!(txs.len(), 2);
    // project name should be joined in
    assert_eq!(txs[0].project_name.as_deref(), Some("Trench A1"));

    let stats = db::get_dashboard_stats(&conn).unwrap();
    assert_eq!(stats.total_projects, 1);
    assert_eq!(stats.active_projects, 1);
    assert_eq!(stats.total_income, 500_000.0);
    assert_eq!(stats.total_expense, 120_000.0);
    assert_eq!(stats.net_profit, 380_000.0);
    assert_eq!(stats.recent_projects.len(), 1);
}

#[test]
fn empty_dashboard_is_zeroed() {
    let conn = db::init_memory().unwrap();
    let stats = db::get_dashboard_stats(&conn).unwrap();
    assert_eq!(stats.total_projects, 0);
    assert_eq!(stats.total_income, 0.0);
    assert_eq!(stats.net_profit, 0.0);
}

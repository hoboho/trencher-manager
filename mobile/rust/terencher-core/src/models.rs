use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Project {
    pub id: Option<i64>,
    pub name: String,
    pub client_name: Option<String>,
    pub client_contact: Option<String>,
    pub location: Option<String>,
    pub contract_amount: f64,
    pub received_amount: f64,
    pub start_date: String,
    pub end_date: Option<String>,
    pub total_length: Option<f64>,
    pub average_depth: Option<f64>,
    pub average_width: Option<f64>,
    pub status: String,
    pub description: Option<String>,
    pub notes: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Machine {
    pub id: Option<i64>,
    pub name: String,
    pub model: Option<String>,
    pub purchase_date: Option<String>,
    pub purchase_price: Option<f64>,
    pub fuel_consumption_rate: Option<f64>,
    pub fuel_cost_per_liter: Option<f64>,
    pub maintenance_cost_per_hour: Option<f64>,
    pub trenching_depth: Option<f64>,
    pub trenching_width: Option<f64>,
    pub maximum_speed: Option<f64>,
    pub weight: Option<f64>,
    pub status: String,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Operator {
    pub id: Option<i64>,
    pub name: String,
    pub hourly_rate: f64,
    pub overtime_rate: f64,
    pub overtime_threshold: f64,
    pub contact: Option<String>,
    pub skills: Option<String>,
    pub specialization: Option<String>,
    pub notes: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Transaction {
    pub id: Option<i64>,
    pub transaction_type: String,
    pub amount: f64,
    pub category: String,
    pub description: Option<String>,
    pub date: String,
    pub project_id: Option<i64>,
    pub operator_id: Option<i64>,
    pub machine_id: Option<i64>,
    pub project_name: Option<String>,
    pub operator_name: Option<String>,
    pub machine_name: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DashboardStats {
    pub total_projects: i64,
    pub active_projects: i64,
    pub total_machines: i64,
    pub active_machines: i64,
    pub total_operators: i64,
    pub total_income: f64,
    pub total_expense: f64,
    pub net_profit: f64,
    pub recent_projects: Vec<Project>,
}

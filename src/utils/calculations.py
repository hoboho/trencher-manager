from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import Project, Machine, Operator, MachineProject, OperatorProject, ProjectExpense, Payment

def format_currency(amount: float) -> str:
    """Format amount in Rial with thousands separator."""
    return f"{amount:,.0f} ریال"

def format_length(length: float) -> str:
    """Format length in meters with 2 decimal places."""
    return f"{length:.2f} متر"

def format_speed(speed: float) -> str:
    """Format speed in meters per hour with 2 decimal places."""
    return f"{speed:.2f} متر/ساعت"

def calculate_project_summary(project: Project) -> Dict[str, Any]:
    """Calculate a complete financial summary for a project."""
    return {
        'contract_amount': project.contract_amount,
        'received_amount': project.received_amount,
        'remaining_balance': project.calculate_remaining_balance(),
        'total_costs': project.calculate_total_costs(),
        'profit': project.calculate_profit(),
        'profit_margin': (project.calculate_profit() / project.contract_amount * 100) if project.contract_amount > 0 else 0,
        'status': project.status,
        'total_length': project.total_length,
        'completed_length': sum(mp.completed_length for mp in project.machines),
        'progress_percentage': project.calculate_progress(),
        'average_depth': project.average_depth,
        'average_width': project.average_width
    }

def calculate_machine_costs(machine: Machine, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate costs for a specific machine over a date range."""
    total_hours = 0.0
    total_fuel_cost = 0.0
    total_maintenance_cost = 0.0
    total_length = 0.0
    
    for project in machine.projects:
        if project.start_date <= end_date and (not project.end_date or project.end_date >= start_date):
            total_hours += project.hours_used
            total_fuel_cost += (project.hours_used * machine.fuel_consumption_rate * 
                              machine.fuel_cost_per_liter)
            total_maintenance_cost += (project.hours_used * machine.maintenance_cost_per_hour)
            total_length += project.completed_length
    
    # Calculate efficiency metrics
    average_speed = total_length / total_hours if total_hours > 0 else 0
    fuel_efficiency = total_length / (total_hours * machine.fuel_consumption_rate) if total_hours > 0 else 0
    
    return {
        'total_hours': total_hours,
        'total_length': total_length,
        'average_speed': average_speed,
        'fuel_efficiency': fuel_efficiency,
        'total_fuel_cost': total_fuel_cost,
        'total_maintenance_cost': total_maintenance_cost,
        'total_cost': total_fuel_cost + total_maintenance_cost
    }

def calculate_operator_costs(operator: Operator, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Calculate costs for a specific operator over a date range."""
    total_hours = 0.0
    regular_hours = 0.0
    overtime_hours = 0.0
    total_cost = 0.0
    total_length = 0.0
    
    for project in operator.projects:
        if project.start_date <= end_date and (not project.end_date or project.end_date >= start_date):
            total_hours += project.hours_worked
            regular_hours += min(project.hours_worked, operator.overtime_threshold)
            overtime_hours += max(0, project.hours_worked - operator.overtime_threshold)
            total_cost += project.calculate_total_cost()
            total_length += project.completed_length
    
    # Calculate efficiency metrics
    average_speed = total_length / total_hours if total_hours > 0 else 0
    
    return {
        'total_hours': total_hours,
        'total_length': total_length,
        'average_speed': average_speed,
        'regular_hours': regular_hours,
        'overtime_hours': overtime_hours,
        'regular_cost': regular_hours * operator.hourly_rate,
        'overtime_cost': overtime_hours * operator.overtime_rate,
        'total_cost': total_cost
    }

def generate_financial_report(session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate a complete financial report for the specified date range."""
    # Get all projects in the date range
    projects = session.query(Project).filter(
        Project.start_date <= end_date,
        (Project.end_date.is_(None) | (Project.end_date >= start_date))
    ).all()
    
    # Calculate project summaries
    project_summaries = [calculate_project_summary(project) for project in projects]
    
    # Calculate total revenue and costs
    total_revenue = sum(p['received_amount'] for p in project_summaries)
    total_costs = sum(p['total_costs'] for p in project_summaries)
    total_profit = total_revenue - total_costs
    
    # Calculate total length completed
    total_length = sum(p['completed_length'] for p in project_summaries)
    
    # Calculate machine costs
    machines = session.query(Machine).all()
    machine_costs = {
        machine.name: calculate_machine_costs(machine, start_date, end_date)
        for machine in machines
    }
    
    # Calculate operator costs
    operators = session.query(Operator).all()
    operator_costs = {
        operator.name: calculate_operator_costs(operator, start_date, end_date)
        for operator in operators
    }
    
    return {
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'projects': project_summaries,
        'total_revenue': total_revenue,
        'total_costs': total_costs,
        'total_profit': total_profit,
        'profit_margin': (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
        'total_length': total_length,
        'machine_costs': machine_costs,
        'operator_costs': operator_costs
    }

def calculate_daily_progress(project: Project) -> List[Dict[str, Any]]:
    """Calculate daily progress for a project."""
    if not project.start_date:
        return []
    
    end_date = project.end_date or datetime.now().date()
    current_date = project.start_date
    daily_progress = []
    
    while current_date <= end_date:
        # Calculate costs for this day
        daily_machine_costs = sum(
            mp.calculate_total_cost() / (end_date - project.start_date).days
            for mp in project.machines
        )
        
        daily_operator_costs = sum(
            op.calculate_total_cost() / (end_date - project.start_date).days
            for op in project.operators
        )
        
        daily_expenses = sum(
            exp.amount
            for exp in project.expenses
            if exp.date == current_date
        )
        
        # Calculate daily progress
        daily_length = sum(
            mp.completed_length / (end_date - project.start_date).days
            for mp in project.machines
        )
        
        daily_progress.append({
            'date': current_date,
            'machine_costs': daily_machine_costs,
            'operator_costs': daily_operator_costs,
            'expenses': daily_expenses,
            'total_costs': daily_machine_costs + daily_operator_costs + daily_expenses,
            'completed_length': daily_length
        })
        
        current_date += timedelta(days=1)
    
    return daily_progress

def generate_cash_flow_report(session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate a cash flow report for the specified date range."""
    # Get all payments in the date range
    payments = session.query(Payment).filter(
        Payment.payment_date.between(start_date, end_date),
        Payment.status == 'paid'
    ).all()
    
    # Get all expenses in the date range
    expenses = session.query(ProjectExpense).filter(
        ProjectExpense.date.between(start_date, end_date)
    ).all()
    
    # Calculate total inflow (payments received)
    total_inflow = sum(payment.amount for payment in payments)
    
    # Calculate total outflow (expenses)
    total_outflow = sum(expense.amount for expense in expenses)
    
    return {
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'total_inflow': total_inflow,
        'total_outflow': total_outflow,
        'net_cash_flow': total_inflow - total_outflow,
        'payments': [{
            'date': payment.payment_date,
            'amount': payment.amount,
            'recipient': payment.recipient_type,
            'description': payment.description
        } for payment in payments],
        'expenses': [{
            'date': expense.date,
            'amount': expense.amount,
            'category': expense.category,
            'description': expense.description
        } for expense in expenses]
    }

def generate_machine_utilization_report(session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate a machine utilization report for the specified date range."""
    machines = session.query(Machine).all()
    total_days = (end_date - start_date).days
    
    machine_data = {}
    for machine in machines:
        costs = calculate_machine_costs(machine, start_date, end_date)
        
        # Calculate utilization rate (hours used / total possible hours)
        total_possible_hours = total_days * 24  # Assuming 24-hour operation
        utilization_rate = (costs['total_hours'] / total_possible_hours * 100) if total_possible_hours > 0 else 0
        
        machine_data[machine.name] = {
            'utilization_rate': utilization_rate,
            'total_hours': costs['total_hours'],
            'total_length': costs['total_length'],
            'average_speed': costs['average_speed'],
            'fuel_efficiency': costs['fuel_efficiency'],
            'total_cost': costs['total_cost'],
            'fuel_cost': costs['total_fuel_cost'],
            'maintenance_cost': costs['total_maintenance_cost']
        }
    
    return {
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'machines': machine_data
    }

def generate_operator_performance_report(session: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate an operator performance report for the specified date range."""
    operators = session.query(Operator).all()
    
    operator_data = {}
    for operator in operators:
        costs = calculate_operator_costs(operator, start_date, end_date)
        
        # Calculate overtime rate
        overtime_rate = (costs['overtime_hours'] / costs['total_hours'] * 100) if costs['total_hours'] > 0 else 0
        
        operator_data[operator.name] = {
            'total_hours': costs['total_hours'],
            'regular_hours': costs['regular_hours'],
            'overtime_hours': costs['overtime_hours'],
            'overtime_rate': overtime_rate,
            'total_length': costs['total_length'],
            'average_speed': costs['average_speed'],
            'total_cost': costs['total_cost'],
            'regular_cost': costs['regular_cost'],
            'overtime_cost': costs['overtime_cost']
        }
    
    return {
        'date_range': {
            'start': start_date,
            'end': end_date
        },
        'operators': operator_data
    }

def generate_project_health_report(session: Session, project_id: int) -> Dict[str, Any]:
    """Generate a health report for a specific project."""
    project = session.query(Project).get(project_id)
    if not project:
        return {}
    
    summary = calculate_project_summary(project)
    daily_progress = calculate_daily_progress(project)
    
    # Calculate average daily costs
    if daily_progress:
        avg_daily_costs = sum(day['total_costs'] for day in daily_progress) / len(daily_progress)
    else:
        avg_daily_costs = 0
    
    return {
        'project_info': {
            'name': project.name,
            'status': project.status,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'total_length': project.total_length,
            'completed_length': summary['completed_length'],
            'average_depth': project.average_depth,
            'average_width': project.average_width
        },
        'progress_metrics': {
            'progress_percentage': summary['progress_percentage'],
            'daily_progress': daily_progress
        },
        'financial_metrics': {
            'contract_amount': project.contract_amount,
            'received_amount': project.received_amount,
            'remaining_balance': summary['remaining_balance'],
            'total_costs': summary['total_costs'],
            'profit': summary['profit'],
            'profit_margin': summary['profit_margin'],
            'avg_daily_costs': avg_daily_costs
        }
    }

def generate_forecast_report(session: Session, project_id: int) -> Dict[str, Any]:
    """Generate a forecast report for a specific project."""
    project = session.query(Project).get(project_id)
    if not project:
        return {}
    
    health_report = generate_project_health_report(session, project_id)
    if not health_report:
        return {}
    
    # Calculate remaining work
    remaining_length = project.total_length - health_report['project_info']['completed_length']
    
    # Calculate average daily progress
    daily_progress = health_report['progress_metrics']['daily_progress']
    if daily_progress:
        avg_daily_progress = sum(day['completed_length'] for day in daily_progress) / len(daily_progress)
    else:
        avg_daily_progress = 0
    
    # Calculate remaining days
    remaining_days = remaining_length / avg_daily_progress if avg_daily_progress > 0 else 0
    
    # Calculate forecasted costs
    avg_daily_costs = health_report['financial_metrics']['avg_daily_costs']
    forecasted_costs = avg_daily_costs * remaining_days if remaining_days > 0 else 0
    
    # Calculate forecasted completion date
    forecasted_completion = datetime.now() + timedelta(days=remaining_days) if remaining_days > 0 else None
    
    # Calculate cost variance
    total_forecasted_costs = health_report['financial_metrics']['total_costs'] + forecasted_costs
    cost_variance = ((total_forecasted_costs - project.contract_amount) / project.contract_amount * 100) if project.contract_amount > 0 else 0
    
    return {
        'forecast_metrics': {
            'remaining_length': remaining_length,
            'avg_daily_progress': avg_daily_progress,
            'remaining_days': remaining_days,
            'avg_daily_costs': avg_daily_costs,
            'forecasted_costs': forecasted_costs,
            'forecasted_completion': forecasted_completion
        },
        'risk_analysis': {
            'cost_variance': cost_variance,
            'schedule_variance': (remaining_days / 30 * 100) if remaining_days > 0 else 0  # Assuming 30-day projects
        }
    } 
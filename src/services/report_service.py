from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..database.models import (
    Project, Machine, Operator, Transaction,
    MachineProject, OperatorProject, TransactionType,
    MachineCost, Payment, ProjectExpense, ReportCache
)
import logging
import json

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logger
        self.cache_duration = timedelta(hours=1)  # Cache reports for 1 hour

    def _get_cached_report(self, report_type: str, parameters: Dict) -> Optional[Dict]:
        """Try to get a cached report."""
        try:
            cache_entry = (
                self.session.query(ReportCache)
                .filter(
                    ReportCache.report_type == report_type,
                    ReportCache.parameters == json.dumps(parameters),
                    ReportCache.expires_at > datetime.utcnow()
                )
                .first()
            )
            
            if cache_entry:
                return json.loads(cache_entry.data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached report: {str(e)}")
            return None

    def _cache_report(self, report_type: str, parameters: Dict, data: Dict):
        """Cache a report result."""
        try:
            # Delete any existing cache for this report type and parameters
            self.session.query(ReportCache).filter(
                ReportCache.report_type == report_type,
                ReportCache.parameters == json.dumps(parameters)
            ).delete()
            
            # Create new cache entry
            cache_entry = ReportCache(
                report_type=report_type,
                parameters=json.dumps(parameters),
                data=json.dumps(data),
                expires_at=datetime.utcnow() + self.cache_duration
            )
            
            self.session.add(cache_entry)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Error caching report: {str(e)}")
            self.session.rollback()

    def generate_project_summary(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate project summary report with caching."""
        # Check cache first
        cache_params = {'start_date': start_date.isoformat() if start_date else None,
                       'end_date': end_date.isoformat() if end_date else None}
        
        cached_result = self._get_cached_report('project_summary', cache_params)
        if cached_result:
            return cached_result

        try:
            # Query projects
            query = self.session.query(Project)
            if start_date:
                query = query.filter(Project.start_date >= start_date)
            if end_date:
                query = query.filter(Project.end_date <= end_date)
            
            projects = query.all()
            
            # Generate summary for each project
            results = []
            for project in projects:
                summary = project.get_financial_summary()
                summary.update({
                    'name': project.name,
                    'status': project.status,
                    'machines': project.get_machine_summary(),
                    'operators': project.get_operator_summary()
                })
                results.append(summary)
            
            # Cache the results
            self._cache_report('project_summary', cache_params, results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error generating project summary: {str(e)}")
            return []

    def generate_machine_utilization(self, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate machine utilization report with caching."""
        # Check cache first
        cache_params = {'start_date': start_date.isoformat() if start_date else None,
                       'end_date': end_date.isoformat() if end_date else None}
        
        cached_result = self._get_cached_report('machine_utilization', cache_params)
        if cached_result:
            return cached_result

        try:
            # Query for machine utilization
            machines = self.session.query(Machine).all()
            
            results = []
            for machine in machines:
                # Get machine projects within date range
                projects_query = self.session.query(MachineProject).filter(
                    MachineProject.machine_id == machine.id
                )
                
                if start_date:
                    projects_query = projects_query.filter(MachineProject.start_date >= start_date)
                if end_date:
                    projects_query = projects_query.filter(MachineProject.end_date <= end_date)
                
                machine_projects = projects_query.all()
                
                # Calculate utilization metrics
                total_hours = sum(mp.hours_used for mp in machine_projects)
                total_length = sum(mp.completed_length for mp in machine_projects)
                efficiency = total_length / total_hours if total_hours > 0 else 0
                
                # Get maintenance costs
                maintenance_costs = sum(
                    cost.amount for cost in machine.costs
                    if cost.cost_type == 'maintenance'
                    and (not start_date or cost.date >= start_date)
                    and (not end_date or cost.date <= end_date)
                )
                
                results.append({
                    'machine_name': machine.name,
                    'total_hours': total_hours,
                    'total_length': total_length,
                    'efficiency': efficiency,
                    'maintenance_costs': maintenance_costs,
                    'status': machine.status,
                    'projects': [
                        {
                            'project_name': mp.project.name,
                            'hours_used': mp.hours_used,
                            'completed_length': mp.completed_length,
                            'efficiency': mp.completed_length / mp.hours_used if mp.hours_used > 0 else 0
                        }
                        for mp in machine_projects
                    ]
                })
            
            # Cache the results
            self._cache_report('machine_utilization', cache_params, results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error generating machine utilization: {str(e)}")
            return []

    def generate_operator_performance(self, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate operator performance report with caching."""
        # Check cache first
        cache_params = {'start_date': start_date.isoformat() if start_date else None,
                       'end_date': end_date.isoformat() if end_date else None}
        
        cached_result = self._get_cached_report('operator_performance', cache_params)
        if cached_result:
            return cached_result

        try:
            # Query for operators
            operators = self.session.query(Operator).all()
            
            results = []
            for operator in operators:
                # Get operator projects within date range
                projects_query = self.session.query(OperatorProject).filter(
                    OperatorProject.operator_id == operator.id
                )
                
                if start_date:
                    projects_query = projects_query.filter(OperatorProject.start_date >= start_date)
                if end_date:
                    projects_query = projects_query.filter(OperatorProject.end_date <= end_date)
                
                operator_projects = projects_query.all()
                
                # Calculate performance metrics
                total_hours = sum(op.hours_worked for op in operator_projects)
                total_length = sum(op.completed_length for op in operator_projects)
                efficiency = total_length / total_hours if total_hours > 0 else 0
                
                # Get payments
                payments = sum(
                    payment.amount for payment in Payment.query.filter_by(
                        recipient_type='operator',
                        recipient_id=operator.id
                    ).filter(
                        Payment.payment_date >= start_date if start_date else True,
                        Payment.payment_date <= end_date if end_date else True
                    )
                )
                
                results.append({
                    'operator_name': operator.name,
                    'specialization': operator.specialization,
                    'total_hours': total_hours,
                    'total_length': total_length,
                    'efficiency': efficiency,
                    'total_payments': payments,
                    'projects': [
                        {
                            'project_name': op.project.name,
                            'hours_worked': op.hours_worked,
                            'completed_length': op.completed_length,
                            'efficiency': op.completed_length / op.hours_worked if op.hours_worked > 0 else 0
                        }
                        for op in operator_projects
                    ]
                })
            
            # Cache the results
            self._cache_report('operator_performance', cache_params, results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error generating operator performance: {str(e)}")
            return []

    def generate_financial_summary(self, start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate financial summary report with caching."""
        # Check cache first
        cache_params = {'start_date': start_date.isoformat() if start_date else None,
                       'end_date': end_date.isoformat() if end_date else None}
        
        cached_result = self._get_cached_report('financial_summary', cache_params)
        if cached_result:
            return cached_result

        try:
            # Query for all financial data within date range
            transactions = self.session.query(Transaction).filter(
                Transaction.date >= start_date if start_date else True,
                Transaction.date <= end_date if end_date else True
            ).all()
            
            # Calculate totals
            total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
            total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
            
            # Group by category
            category_summary = {}
            for t in transactions:
                if t.category not in category_summary:
                    category_summary[t.category] = {
                        'income': 0,
                        'expenses': 0,
                        'count': 0
                    }
                
                if t.type == TransactionType.INCOME:
                    category_summary[t.category]['income'] += t.amount
                else:
                    category_summary[t.category]['expenses'] += t.amount
                category_summary[t.category]['count'] += 1
            
            results = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_profit': total_income - total_expenses,
                'transaction_count': len(transactions),
                'categories': category_summary,
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            }
            
            # Cache the results
            self._cache_report('financial_summary', cache_params, results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error generating financial summary: {str(e)}")
            return {}

    def generate_project_summary(self, start_date: Optional[datetime] = None, 
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate a summary report for a specific project."""
        try:
            # Query for projects within the date range
            query = self.session.query(Project)
            
            # Apply date filters if provided
            if start_date:
                query = query.filter(Project.created_at >= start_date)
            if end_date:
                query = query.filter(Project.created_at <= end_date)
                
            # Get all projects
            projects = query.all()
            
            # Group projects by status
            status_groups = {}
            for project in projects:
                if project.status not in status_groups:
                    status_groups[project.status] = {
                        'count': 0,
                        'total_amount': 0,
                        'total_received': 0
                    }
                status_groups[project.status]['count'] += 1
                status_groups[project.status]['total_amount'] += project.contract_amount or 0
                status_groups[project.status]['total_received'] += project.total_received or 0

            # Format results
            results = []
            for status, data in status_groups.items():
                results.append({
                    'status': status,
                    'count': data['count'],
                    'total_amount': data['total_amount'],
                    'total_received': data['total_received'],
                    'percentage': (data['total_received'] / data['total_amount'] * 100) if data['total_amount'] > 0 else 0
                })
            
            return results
        except Exception as e:
            raise Exception(f"Error generating project summary: {str(e)}")

    def generate_machine_summary(self, machine_id: int) -> Dict[str, Any]:
        """Generate a summary report for a specific machine."""
        try:
            machine = self.session.query(Machine).get(machine_id)
            if not machine:
                raise ValueError(f"Machine with ID {machine_id} not found")

            # Get machine costs
            costs = self.session.query(
                func.sum(MachineCost.amount)
            ).filter(MachineCost.machine_id == machine_id).first()

            return {
                'machine_name': machine.name,
                'total_costs': float(costs[0] or 0),
                'total_hours': machine.total_hours or 0
            }
        except Exception as e:
            raise Exception(f"Error generating machine summary: {str(e)}")

    def generate_operator_summary(self, operator_id: int) -> Dict[str, Any]:
        """Generate a summary report for a specific operator."""
        try:
            operator = self.session.query(Operator).get(operator_id)
            if not operator:
                raise ValueError(f"Operator with ID {operator_id} not found")

            # Get payments
            payments = self.session.query(
                func.sum(Payment.amount)
            ).filter(Payment.operator_id == operator_id).first()

            return {
                'operator_name': operator.name,
                'total_payments': float(payments[0] or 0),
                'total_hours': operator.total_hours or 0
            }
        except Exception as e:
            raise Exception(f"Error generating operator summary: {str(e)}")

    def generate_category_summary(self, start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate a summary report grouped by transaction category."""
        try:
            # Base query for transactions
            query = self.session.query(
                Transaction.category,
                func.sum(
                    case(
                        (Transaction.type == TransactionType.INCOME, Transaction.amount),
                        (Transaction.type == TransactionType.EXPENSE, -Transaction.amount),
                        else_=0
                    )
                ).label('total_amount'),
                func.count().label('transaction_count')
            ).select_from(Transaction)

            # Apply date filters if provided
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)

            # Group by category
            query = query.group_by(Transaction.category)

            # Execute query
            results = query.all()

            # Format results
            return [{
                'category': result.category,
                'total_amount': float(result.total_amount or 0),
                'transaction_count': result.transaction_count
            } for result in results]
        except Exception as e:
            raise Exception(f"Error generating category summary: {str(e)}") 
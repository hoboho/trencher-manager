from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional, Tuple
from ..database.models import Transaction, TransactionType, TransactionCategory
import logging

class TransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def add_transaction(self, 
                       type: TransactionType,
                       amount: float,
                       category: TransactionCategory,
                       description: str,
                       date: datetime,
                       project_id: Optional[int] = None,
                       operator_id: Optional[int] = None,
                       machine_id: Optional[int] = None) -> Transaction:
        """Add a new transaction."""
        transaction = Transaction(
            type=type,
            amount=amount,
            category=category,
            description=description,
            date=date,
            project_id=project_id,
            operator_id=operator_id,
            machine_id=machine_id
        )
        self.session.add(transaction)
        self.session.commit()
        return transaction

    def get_transactions(self, start_date=None, end_date=None, category=None, page=1, per_page=20):
        """Get transactions with pagination and filters"""
        try:
            query = self.session.query(Transaction)
            
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)
            if category:
                query = query.filter(Transaction._category == category.value)
                
            total = query.count()
            
            if page and per_page:
                offset = (page - 1) * per_page
                transactions = query.order_by(Transaction.date.desc()).offset(offset).limit(per_page).all()
            else:
                transactions = query.order_by(Transaction.date.desc()).all()
            
            return transactions, total
        except Exception as e:
            self.logger.error(f"Error getting transactions: {str(e)}")
            return [], 0

    def get_summary(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> dict:
        """Get financial summary (total income, total expenses, net balance)."""
        try:
            query = self.session.query(
                func.sum(Transaction.amount).filter(Transaction._type == TransactionType.INCOME.value).label('income'),
                func.sum(Transaction.amount).filter(Transaction._type == TransactionType.EXPENSE.value).label('expenses')
            )
            
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)
                
            result = query.first()
            total_income = float(result.income or 0.0)
            total_expenses = float(result.expenses or 0.0)
            net_balance = total_income - total_expenses
            
            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': net_balance
            }
        except Exception as e:
            self.logger.error(f"Error getting transactions summary: {str(e)}")
            return {'total_income': 0.0, 'total_expenses': 0.0, 'net_balance': 0.0}

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction by ID."""
        transaction = self.session.query(Transaction).get(transaction_id)
        if transaction:
            self.session.delete(transaction)
            self.session.commit()
            return True
        return False 
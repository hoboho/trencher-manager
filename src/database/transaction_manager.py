from datetime import datetime
from sqlalchemy import text
from src.database.models import Transaction, TransactionType, TransactionCategory
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TransactionManager:
    def __init__(self, session):
        self.session = session
    
    def save_transaction(self, transaction_data):
        """Save a new transaction with proper enum handling."""
        try:
            # Convert enum values to strings
            transaction_data['type'] = transaction_data['type'].value
            transaction_data['category'] = transaction_data['category'].value
            
            transaction = Transaction(**transaction_data)
            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Transaction saved successfully: {transaction}")
            return transaction
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving transaction: {str(e)}")
            raise
    
    def get_transactions_summary(self, start_date, end_date):
        """Get transaction summary with proper enum handling."""
        try:
            query = text("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type = :income_type THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = :expense_type THEN amount ELSE 0 END), 0) as expenses
                FROM transactions 
                WHERE date >= :start_date AND date <= :end_date
            """)
            
            result = self.session.execute(
                query,
                {
                    'income_type': TransactionType.INCOME.value,
                    'expense_type': TransactionType.EXPENSE.value,
                    'start_date': start_date,
                    'end_date': end_date
                }
            ).first()
            
            if result:
                return {
                    'income': float(result[0] or 0),
                    'expenses': float(result[1] or 0)
                }
            return {'income': 0.0, 'expenses': 0.0}
        except Exception as e:
            logger.error(f"Error getting transactions summary: {str(e)}")
            raise 
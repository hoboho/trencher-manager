from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QGridLayout, QLineEdit, QSpinBox,
    QDoubleSpinBox, QMessageBox, QDialog, QTabWidget, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import logging
from datetime import datetime, timedelta
from ..utils.language_manager import LanguageManager
from ..database.models import TransactionType, TransactionCategory
from ..services.transaction_service import TransactionService
from sqlalchemy.orm import Session
import pandas as pd

logger = logging.getLogger(__name__)

class TransactionDialog(QDialog):
    def __init__(self, parent=None, language_manager=None):
        super().__init__(parent)
        self.language_manager = language_manager
        self.setWindowTitle(self.language_manager.translate("finance.add_transaction"))
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QGridLayout(self)
        
        # Transaction type
        layout.addWidget(QLabel(self.language_manager.translate("finance.transaction_type")), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            self.language_manager.translate("finance.income"),
            self.language_manager.translate("finance.expense")
        ])
        layout.addWidget(self.type_combo, 0, 1)
        
        # Amount
        layout.addWidget(QLabel(self.language_manager.translate("finance.amount")), 1, 0)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 1000000000)
        self.amount_spin.setDecimals(2)
        layout.addWidget(self.amount_spin, 1, 1)
        
        # Category
        layout.addWidget(QLabel(self.language_manager.translate("finance.category")), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            self.language_manager.translate("finance.project_payment"),
            self.language_manager.translate("finance.salary"),
            self.language_manager.translate("finance.maintenance"),
            self.language_manager.translate("finance.fuel"),
            self.language_manager.translate("finance.other")
        ])
        layout.addWidget(self.category_combo, 2, 1)
        
        # Description
        layout.addWidget(QLabel(self.language_manager.translate("finance.description")), 3, 0)
        self.description_edit = QLineEdit()
        layout.addWidget(self.description_edit, 3, 1)
        
        # Date
        layout.addWidget(QLabel(self.language_manager.translate("finance.date")), 4, 0)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit, 4, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.language_manager.translate("common.save"))
        self.cancel_btn = QPushButton(self.language_manager.translate("common.cancel"))
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout, 5, 0, 1, 2)
        
        # Connect signals
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.accept)
        
    def get_transaction_data(self):
        """Get the transaction data from the form."""
        return {
            'type': TransactionType.INCOME if self.type_combo.currentIndex() == 0 else TransactionType.EXPENSE,
            'amount': self.amount_spin.value(),
            'category': list(TransactionCategory)[self.category_combo.currentIndex()],
            'description': self.description_edit.text(),
            'date': self.date_edit.date().toPyDate()
        }

class FinanceWidget(QWidget):
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.language_manager = LanguageManager()
        self.transaction_service = TransactionService(session)
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI with pagination and optimized chart updates"""
        layout = QVBoxLayout(self)
        
        # Header with filters
        header = QHBoxLayout()
        
        # Date range filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel(self.language_manager.translate("finance.date_range")))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        header.addLayout(date_layout)
        
        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItem(self.language_manager.translate("finance.all_categories"))
        for category in TransactionCategory:
            self.category_combo.addItem(category.value)
        header.addWidget(self.category_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.language_manager.translate("finance.add_transaction"))
        self.add_button.clicked.connect(self._add_transaction)
        self.import_button = QPushButton(self.language_manager.translate("finance.import"))
        self.import_button.clicked.connect(self._import_transactions)
        self.export_button = QPushButton(self.language_manager.translate("finance.export"))
        self.export_button.clicked.connect(self._export_transactions)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        header.addLayout(button_layout)
        
        layout.addLayout(header)
        
        # Tabs for different views
        tabs = QTabWidget()
        
        # Transactions table with pagination
        transactions_widget = QWidget()
        transactions_layout = QVBoxLayout(transactions_widget)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            self.language_manager.translate("finance.date"),
            self.language_manager.translate("finance.type"),
            self.language_manager.translate("finance.amount"),
            self.language_manager.translate("finance.category"),
            self.language_manager.translate("finance.description"),
            self.language_manager.translate("finance.actions")
        ])
        transactions_layout.addWidget(self.transactions_table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("Previous")
        self.next_page_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.prev_page_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_page_btn)
        transactions_layout.addLayout(pagination_layout)
        
        tabs.addTab(transactions_widget, self.language_manager.translate("finance.transactions"))
        
        # Charts tab
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        
        # Category distribution chart
        self.category_chart = self._create_category_chart()
        charts_layout.addWidget(self.category_chart)
        
        # Income vs Expenses trend chart
        self.trend_chart = self._create_trend_chart()
        charts_layout.addWidget(self.trend_chart)
        
        tabs.addTab(charts_widget, self.language_manager.translate("finance.charts"))
        
        layout.addWidget(tabs)
        
        # Summary section
        summary_layout = QHBoxLayout()
        self.total_income_label = QLabel()
        self.total_expenses_label = QLabel()
        self.net_balance_label = QLabel()
        summary_layout.addWidget(self.total_income_label)
        summary_layout.addWidget(self.total_expenses_label)
        summary_layout.addWidget(self.net_balance_label)
        layout.addLayout(summary_layout)
        
        # Connect signals
        self.start_date.dateChanged.connect(self._load_transactions)
        self.end_date.dateChanged.connect(self._load_transactions)
        self.category_combo.currentTextChanged.connect(self._load_transactions)
        self.prev_page_btn.clicked.connect(self._previous_page)
        self.next_page_btn.clicked.connect(self._next_page)
        
        # Initialize data
        self.current_page = 1
        self._load_transactions()
        
    def _add_transaction(self):
        """Show dialog to add a new transaction."""
        dialog = TransactionDialog(self, self.language_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_transaction(dialog.get_transaction_data())
        
    def _save_transaction(self, data):
        """Save the new transaction."""
        try:
            self.transaction_service.add_transaction(
                type=data['type'],
                amount=data['amount'],
                category=data['category'],
                description=data['description'],
                date=data['date']
            )
            self._load_transactions()
        except Exception as e:
            logger.error(f"Error saving transaction: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("finance.save_error").format(error=str(e))
            )
            
    def _load_transactions(self):
        """Load transactions with pagination"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            category = None
            if self.category_combo.currentIndex() > 0:
                category = list(TransactionCategory)[self.category_combo.currentIndex() - 1]
            
            # Get transactions with pagination
            transactions, total = self.transaction_service.get_transactions(
                start_date=start_date,
                end_date=end_date,
                category=category,
                page=self.current_page,
                per_page=20
            )
            
            # Calculate total pages
            self.total_pages = (total + 19) // 20
            
            # Update pagination controls
            self.prev_page_btn.setEnabled(self.current_page > 1)
            self.next_page_btn.setEnabled(self.current_page < self.total_pages)
            self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")
            
            # Get summary
            summary = self.transaction_service.get_summary(start_date, end_date)
            
            # Update summary labels
            self.total_income_label.setText(
                self.language_manager.translate("finance.total_income") + 
                f": {summary['total_income']:,.2f}"
            )
            self.total_expenses_label.setText(
                self.language_manager.translate("finance.total_expenses") + 
                f": {summary['total_expenses']:,.2f}"
            )
            self.net_balance_label.setText(
                self.language_manager.translate("finance.net_balance") + 
                f": {summary['net_balance']:,.2f}"
            )
            
            # Update table
            self.transactions_table.setRowCount(len(transactions))
            for row, transaction in enumerate(transactions):
                # Add row data
                self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction.date.strftime("%Y-%m-%d")))
                self.transactions_table.setItem(row, 1, QTableWidgetItem(
                    self.language_manager.translate(f"finance.{transaction.type.value}")
                ))
                self.transactions_table.setItem(row, 2, QTableWidgetItem(f"{transaction.amount:,.2f}"))
                self.transactions_table.setItem(row, 3, QTableWidgetItem(
                    self.language_manager.translate(f"finance.{transaction.category.value}")
                ))
                self.transactions_table.setItem(row, 4, QTableWidgetItem(transaction.description))
                
                # Add delete button
                delete_btn = QPushButton(self.language_manager.translate("common.delete"))
                delete_btn.clicked.connect(lambda checked, t=transaction: self._delete_transaction(t))
                self.transactions_table.setCellWidget(row, 5, delete_btn)
            
            # Update charts
            self._update_charts(transactions)
            
        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("finance.load_error").format(error=str(e))
            )
            
    def _apply_filters(self):
        """Apply the current filters and reload transactions."""
        self._load_transactions()
        
    def _on_language_changed(self, language):
        """Update UI elements when language changes."""
        # Update labels and buttons
        self.add_button.setText(self.language_manager.translate("finance.add_transaction"))
        self.import_button.setText(self.language_manager.translate("finance.import"))
        self.export_button.setText(self.language_manager.translate("finance.export"))
        
        # Update table headers
        self.transactions_table.setHorizontalHeaderLabels([
            self.language_manager.translate("finance.date"),
            self.language_manager.translate("finance.type"),
            self.language_manager.translate("finance.amount"),
            self.language_manager.translate("finance.category"),
            self.language_manager.translate("finance.description"),
            self.language_manager.translate("finance.actions")
        ])
        
        # Reload transactions to update translations
        self._load_transactions()
        
    def _create_category_chart(self):
        """Create a pie chart for category distribution."""
        figure = plt.figure(figsize=(8, 6))
        canvas = FigureCanvas(figure)
        return canvas
        
    def _create_trend_chart(self):
        """Create a bar chart for income vs expenses trend."""
        figure = plt.figure(figsize=(8, 6))
        canvas = FigureCanvas(figure)
        return canvas
        
    def _update_charts(self, transactions):
        """Update chart data."""
        try:
            # Update category distribution chart
            category_data = {}
            for transaction in transactions:
                category = transaction.category.value
                if category not in category_data:
                    category_data[category] = 0
                category_data[category] += transaction.amount
            
            # Clear and update category chart
            category_figure = self.category_chart.figure
            category_figure.clear()
            ax = category_figure.add_subplot(111)
            
            if category_data:
                categories = list(category_data.keys())
                amounts = list(category_data.values())
                ax.pie(amounts, labels=categories, autopct='%1.1f%%')
                ax.set_title(self.language_manager.translate("finance.category_distribution"))
            
            self.category_chart.draw()
            
            # Update trend chart
            months = {}
            for transaction in transactions:
                month = transaction.date.strftime("%Y-%m")
                if month not in months:
                    months[month] = {"income": 0, "expense": 0}
                if transaction.type.value == TransactionType.INCOME.value:
                    months[month]["income"] += transaction.amount
                else:
                    months[month]["expense"] += transaction.amount
            
            # Clear and update trend chart
            trend_figure = self.trend_chart.figure
            trend_figure.clear()
            ax = trend_figure.add_subplot(111)
            
            if months:
                sorted_months = sorted(months.keys())
                income_data = [months[m]["income"] for m in sorted_months]
                expense_data = [months[m]["expense"] for m in sorted_months]
                
                x = range(len(sorted_months))
                width = 0.35
                
                ax.bar([i - width/2 for i in x], income_data, width, 
                      label=self.language_manager.translate("finance.income"))
                ax.bar([i + width/2 for i in x], expense_data, width, 
                      label=self.language_manager.translate("finance.expense"))
                
                ax.set_xticks(x)
                ax.set_xticklabels(sorted_months, rotation=45)
                ax.set_title(self.language_manager.translate("finance.income_vs_expenses"))
                ax.legend()
            
            trend_figure.tight_layout()
            self.trend_chart.draw()
            
        except Exception as e:
            logger.error(f"Error updating charts: {str(e)}")
            # Don't show error to user as charts are not critical
            
    def _import_transactions(self):
        """Import transactions from Excel file."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                self.language_manager.translate("finance.import_dialog_title"),
                "",
                self.language_manager.translate("finance.excel_filter")
            )
            
            if file_name:
                # Read Excel file
                df = pd.read_excel(file_name)
                
                # Validate columns
                required_columns = ['Type', 'Amount', 'Category', 'Description', 'Date']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(
                        self.language_manager.translate("finance.missing_columns").format(
                            columns=", ".join(missing_columns)
                        )
                    )
                
                # Import transactions
                for _, row in df.iterrows():
                    self.transaction_service.add_transaction(
                        type=TransactionType.INCOME if row['Type'].lower() == 'income' else TransactionType.EXPENSE,
                        amount=float(row['Amount']),
                        category=TransactionCategory[row['Category'].upper()],
                        description=str(row['Description']),
                        date=pd.to_datetime(row['Date']).to_pydatetime()
                    )
                    
                # Reload transactions
                self._load_transactions()
                
                QMessageBox.information(
                    self,
                    self.language_manager.translate("common.success"),
                    self.language_manager.translate("finance.import_success")
                )
                
        except Exception as e:
            logger.error(f"Error importing transactions: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("finance.import_error").format(error=str(e))
            )
            
    def _export_transactions(self):
        """Export transactions to Excel file."""
        try:
            # Get current filter values
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            category = None
            if self.category_combo.currentIndex() > 0:
                category = list(TransactionCategory)[self.category_combo.currentIndex() - 1]
            
            # Get all transactions without pagination
            transactions, _ = self.transaction_service.get_transactions(
                start_date=start_date,
                end_date=end_date,
                category=category,
                page=None,
                per_page=None
            )
            
            if not transactions:
                raise ValueError(self.language_manager.translate("finance.no_data"))
            
            # Convert to DataFrame
            data = []
            for transaction in transactions:
                data.append({
                    'Date': transaction.date.strftime("%Y-%m-%d"),
                    'Type': transaction.type.value,
                    'Category': transaction.category.value,
                    'Description': transaction.description,
                    'Amount': transaction.amount
                })
            df = pd.DataFrame(data)
            
            # Get save file name
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                self.language_manager.translate("finance.export_dialog_title"),
                "",
                self.language_manager.translate("finance.excel_filter")
            )
            
            if file_name:
                if not file_name.endswith('.xlsx'):
                    file_name += '.xlsx'
                df.to_excel(file_name, index=False)
                QMessageBox.information(
                    self,
                    self.language_manager.translate("common.success"),
                    self.language_manager.translate("finance.export_success")
                )
                
        except Exception as e:
            logger.error(f"Error exporting transactions: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("finance.export_error").format(error=str(e))
            )
            
    def _previous_page(self):
        """Go to the previous page of transactions"""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_transactions()
            
    def _next_page(self):
        """Go to the next page of transactions"""
        if self.total_pages and self.current_page < self.total_pages:
            self.current_page += 1
            self._load_transactions()
            
    def _delete_transaction(self, transaction):
        """Delete a transaction."""
        try:
            self.transaction_service.delete_transaction(transaction)
            self._load_transactions()
        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("finance.delete_error").format(error=str(e))
            ) 
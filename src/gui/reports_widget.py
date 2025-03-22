from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QGridLayout, QFileDialog, QMessageBox,
    QTabWidget, QSplitter, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import logging
from datetime import datetime, timedelta
from ..utils.language_manager import LanguageManager
from ..services.report_service import ReportService
from sqlalchemy.orm import Session
import pandas as pd

logger = logging.getLogger(__name__)

class ReportsWidget(QWidget):
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.report_service = ReportService(session)
        self.language_manager = LanguageManager()
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI with tabs for different report types."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add report tabs
        self.project_tab = self._create_project_tab()
        self.machine_tab = self._create_machine_tab()
        self.operator_tab = self._create_operator_tab()
        self.financial_tab = self._create_financial_tab()
        
        self.tab_widget.addTab(self.project_tab, self.language_manager.translate("reports.projects"))
        self.tab_widget.addTab(self.machine_tab, self.language_manager.translate("reports.machines"))
        self.tab_widget.addTab(self.operator_tab, self.language_manager.translate("reports.operators"))
        self.tab_widget.addTab(self.financial_tab, self.language_manager.translate("reports.financial"))
        
        layout.addWidget(self.tab_widget)
        
    def _create_project_tab(self):
        """Create the projects report tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        self.project_start_date = QDateEdit()
        self.project_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.project_end_date = QDateEdit()
        self.project_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.start_date")))
        filter_layout.addWidget(self.project_start_date)
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.end_date")))
        filter_layout.addWidget(self.project_end_date)
        
        # Generate button
        self.project_generate_btn = QPushButton(self.language_manager.translate("reports.generate"))
        filter_layout.addWidget(self.project_generate_btn)
        
        layout.addWidget(filter_frame)
        
        # Results section
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(6)
        self.project_table.setHorizontalHeaderLabels([
            self.language_manager.translate("reports.name"),
            self.language_manager.translate("reports.status"),
            self.language_manager.translate("reports.total_amount"),
            self.language_manager.translate("reports.received_amount"),
            self.language_manager.translate("reports.profit"),
            self.language_manager.translate("reports.progress")
        ])
        self.project_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Chart
        self.project_chart = FigureCanvas(plt.figure(figsize=(8, 6)))
        
        results_splitter.addWidget(self.project_table)
        results_splitter.addWidget(self.project_chart)
        
        layout.addWidget(results_splitter)
        
        # Connect signals
        self.project_generate_btn.clicked.connect(self._generate_project_report)
        
        return widget
        
    def _create_machine_tab(self):
        """Create the machines report tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        self.machine_start_date = QDateEdit()
        self.machine_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.machine_end_date = QDateEdit()
        self.machine_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.start_date")))
        filter_layout.addWidget(self.machine_start_date)
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.end_date")))
        filter_layout.addWidget(self.machine_end_date)
        
        # Generate button
        self.machine_generate_btn = QPushButton(self.language_manager.translate("reports.generate"))
        filter_layout.addWidget(self.machine_generate_btn)
        
        layout.addWidget(filter_frame)
        
        # Results section
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table
        self.machine_table = QTableWidget()
        self.machine_table.setColumnCount(6)
        self.machine_table.setHorizontalHeaderLabels([
            self.language_manager.translate("reports.name"),
            self.language_manager.translate("reports.total_hours"),
            self.language_manager.translate("reports.total_length"),
            self.language_manager.translate("reports.efficiency"),
            self.language_manager.translate("reports.maintenance_costs"),
            self.language_manager.translate("reports.status")
        ])
        self.machine_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Chart
        self.machine_chart = FigureCanvas(plt.figure(figsize=(8, 6)))
        
        results_splitter.addWidget(self.machine_table)
        results_splitter.addWidget(self.machine_chart)
        
        layout.addWidget(results_splitter)
        
        # Connect signals
        self.machine_generate_btn.clicked.connect(self._generate_machine_report)
        
        return widget
        
    def _create_operator_tab(self):
        """Create the operators report tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        self.operator_start_date = QDateEdit()
        self.operator_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.operator_end_date = QDateEdit()
        self.operator_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.start_date")))
        filter_layout.addWidget(self.operator_start_date)
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.end_date")))
        filter_layout.addWidget(self.operator_end_date)
        
        # Generate button
        self.operator_generate_btn = QPushButton(self.language_manager.translate("reports.generate"))
        filter_layout.addWidget(self.operator_generate_btn)
        
        layout.addWidget(filter_frame)
        
        # Results section
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Table
        self.operator_table = QTableWidget()
        self.operator_table.setColumnCount(7)
        self.operator_table.setHorizontalHeaderLabels([
            self.language_manager.translate("reports.name"),
            self.language_manager.translate("operator.specialization"),
            self.language_manager.translate("reports.total_hours"),
            self.language_manager.translate("reports.total_length"),
            self.language_manager.translate("reports.efficiency"),
            self.language_manager.translate("reports.total_payments"),
            self.language_manager.translate("reports.projects_count")
        ])
        self.operator_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Chart
        self.operator_chart = FigureCanvas(plt.figure(figsize=(8, 6)))
        
        results_splitter.addWidget(self.operator_table)
        results_splitter.addWidget(self.operator_chart)
        
        layout.addWidget(results_splitter)
        
        # Connect signals
        self.operator_generate_btn.clicked.connect(self._generate_operator_report)
        
        return widget
        
    def _create_financial_tab(self):
        """Create the financial report tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        self.financial_start_date = QDateEdit()
        self.financial_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.financial_end_date = QDateEdit()
        self.financial_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.start_date")))
        filter_layout.addWidget(self.financial_start_date)
        filter_layout.addWidget(QLabel(self.language_manager.translate("reports.end_date")))
        filter_layout.addWidget(self.financial_end_date)
        
        # Generate button
        self.financial_generate_btn = QPushButton(self.language_manager.translate("reports.generate"))
        filter_layout.addWidget(self.financial_generate_btn)
        
        layout.addWidget(filter_frame)
        
        # Results section
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_layout = QGridLayout(summary_frame)
        
        self.total_income_label = QLabel()
        self.total_expenses_label = QLabel()
        self.net_profit_label = QLabel()
        self.transaction_count_label = QLabel()
        
        summary_layout.addWidget(QLabel(self.language_manager.translate("reports.total_income")), 0, 0)
        summary_layout.addWidget(self.total_income_label, 0, 1)
        summary_layout.addWidget(QLabel(self.language_manager.translate("reports.total_expenses")), 1, 0)
        summary_layout.addWidget(self.total_expenses_label, 1, 1)
        summary_layout.addWidget(QLabel(self.language_manager.translate("reports.net_profit")), 2, 0)
        summary_layout.addWidget(self.net_profit_label, 2, 1)
        summary_layout.addWidget(QLabel(self.language_manager.translate("reports.transaction_count")), 3, 0)
        summary_layout.addWidget(self.transaction_count_label, 3, 1)
        
        # Category table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels([
            self.language_manager.translate("reports.category"),
            self.language_manager.translate("reports.income"),
            self.language_manager.translate("reports.expenses"),
            self.language_manager.translate("reports.count")
        ])
        self.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Chart
        self.financial_chart = FigureCanvas(plt.figure(figsize=(8, 6)))
        
        results_splitter.addWidget(summary_frame)
        results_splitter.addWidget(self.category_table)
        results_splitter.addWidget(self.financial_chart)
        
        layout.addWidget(results_splitter)
        
        # Connect signals
        self.financial_generate_btn.clicked.connect(self._generate_financial_report)
        
        return widget
        
    def _generate_project_report(self):
        """Generate and display project report."""
        try:
            start_date = self.project_start_date.date().toPyDate()
            end_date = self.project_end_date.date().toPyDate()
            
            data = self.report_service.generate_project_summary(start_date, end_date)
            
            # Update table
            self.project_table.setRowCount(len(data))
            for row, project in enumerate(data):
                self.project_table.setItem(row, 0, QTableWidgetItem(project['name']))
                self.project_table.setItem(row, 1, QTableWidgetItem(project['status']))
                self.project_table.setItem(row, 2, QTableWidgetItem(f"{project['total_contract']:,.2f}"))
                self.project_table.setItem(row, 3, QTableWidgetItem(f"{project['total_received']:,.2f}"))
                self.project_table.setItem(row, 4, QTableWidgetItem(f"{project['total_profit']:,.2f}"))
                self.project_table.setItem(row, 5, QTableWidgetItem(f"{project['progress_percentage']:.1f}%"))
            
            # Update chart
            self.project_chart.figure.clear()
            ax = self.project_chart.figure.add_subplot(111)
            
            # Create bar chart
            projects = [p['name'] for p in data]
            contract = [p['total_contract'] for p in data]
            received = [p['total_received'] for p in data]
            
            x = range(len(projects))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], contract, width, label=self.language_manager.translate("reports.contract_amount"))
            ax.bar([i + width/2 for i in x], received, width, label=self.language_manager.translate("reports.received_amount"))
            
            ax.set_ylabel(self.language_manager.translate("reports.amount"))
            ax.set_title(self.language_manager.translate("reports.project_summary"))
            ax.set_xticks(x)
            ax.set_xticklabels(projects, rotation=45)
            ax.legend()
            
            self.project_chart.draw()
            
        except Exception as e:
            logger.error(f"Error generating project report: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("reports.generation_failed")
            )
    
    def _generate_machine_report(self):
        """Generate and display machine report."""
        try:
            start_date = self.machine_start_date.date().toPyDate()
            end_date = self.machine_end_date.date().toPyDate()
            
            data = self.report_service.generate_machine_utilization(start_date, end_date)
            
            # Update table
            self.machine_table.setRowCount(len(data))
            for row, machine in enumerate(data):
                self.machine_table.setItem(row, 0, QTableWidgetItem(machine['machine_name']))
                self.machine_table.setItem(row, 1, QTableWidgetItem(f"{machine['total_hours']:.1f}"))
                self.machine_table.setItem(row, 2, QTableWidgetItem(f"{machine['total_length']:.1f}"))
                self.machine_table.setItem(row, 3, QTableWidgetItem(f"{machine['efficiency']:.2f}"))
                self.machine_table.setItem(row, 4, QTableWidgetItem(f"{machine['maintenance_costs']:,.2f}"))
                self.machine_table.setItem(row, 5, QTableWidgetItem(machine['status']))
            
            # Update chart
            self.machine_chart.figure.clear()
            fig = self.machine_chart.figure
            
            # Create two subplots
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            
            # Hours and efficiency chart
            machines = [m['machine_name'] for m in data]
            hours = [m['total_hours'] for m in data]
            efficiency = [m['efficiency'] for m in data]
            
            ax1.bar(machines, hours)
            ax1.set_ylabel(self.language_manager.translate("reports.hours"))
            ax1.set_title(self.language_manager.translate("reports.hours_used"))
            ax1.tick_params(axis='x', rotation=45)
            
            # Maintenance costs pie chart
            costs = [m['maintenance_costs'] for m in data]
            ax2.pie(costs, labels=machines, autopct='%1.1f%%')
            ax2.set_title(self.language_manager.translate("reports.maintenance_distribution"))
            
            fig.tight_layout()
            self.machine_chart.draw()
            
        except Exception as e:
            logger.error(f"Error generating machine report: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("reports.generation_failed")
            )
    
    def _generate_operator_report(self):
        """Generate and display operator report."""
        try:
            start_date = self.operator_start_date.date().toPyDate()
            end_date = self.operator_end_date.date().toPyDate()
            
            data = self.report_service.generate_operator_performance(start_date, end_date)
            
            # Update table
            self.operator_table.setRowCount(len(data))
            for row, operator in enumerate(data):
                self.operator_table.setItem(row, 0, QTableWidgetItem(operator['operator_name']))
                self.operator_table.setItem(row, 1, QTableWidgetItem(operator['specialization']))
                self.operator_table.setItem(row, 2, QTableWidgetItem(f"{operator['total_hours']:.1f}"))
                self.operator_table.setItem(row, 3, QTableWidgetItem(f"{operator['total_length']:.1f}"))
                self.operator_table.setItem(row, 4, QTableWidgetItem(f"{operator['efficiency']:.2f}"))
                self.operator_table.setItem(row, 5, QTableWidgetItem(f"{operator['total_payments']:,.2f}"))
                self.operator_table.setItem(row, 6, QTableWidgetItem(str(len(operator['projects']))))
            
            # Update chart
            self.operator_chart.figure.clear()
            fig = self.operator_chart.figure
            
            # Create two subplots
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            
            # Hours and efficiency chart
            operators = [o['operator_name'] for o in data]
            hours = [o['total_hours'] for o in data]
            efficiency = [o['efficiency'] for o in data]
            
            x = range(len(operators))
            width = 0.35
            
            ax1.bar([i - width/2 for i in x], hours, width, label=self.language_manager.translate("reports.hours"))
            ax1.bar([i + width/2 for i in x], efficiency, width, label=self.language_manager.translate("reports.efficiency"))
            ax1.set_ylabel(self.language_manager.translate("reports.metrics"))
            ax1.set_title(self.language_manager.translate("reports.performance_metrics"))
            ax1.set_xticks(x)
            ax1.set_xticklabels(operators, rotation=45)
            ax1.legend()
            
            # Specialization distribution pie chart
            specializations = {}
            for op in data:
                spec = op['specialization'] or 'Unknown'
                if spec not in specializations:
                    specializations[spec] = 0
                specializations[spec] += 1
            
            ax2.pie(specializations.values(), labels=specializations.keys(), autopct='%1.1f%%')
            ax2.set_title(self.language_manager.translate("reports.specialization_distribution"))
            
            fig.tight_layout()
            self.operator_chart.draw()
            
        except Exception as e:
            logger.error(f"Error generating operator report: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("reports.generation_failed")
            )
    
    def _generate_financial_report(self):
        """Generate and display financial report."""
        try:
            start_date = self.financial_start_date.date().toPyDate()
            end_date = self.financial_end_date.date().toPyDate()
            
            data = self.report_service.generate_financial_summary(start_date, end_date)
            
            # Update summary labels
            self.total_income_label.setText(f"{data['total_income']:,.2f}")
            self.total_expenses_label.setText(f"{data['total_expenses']:,.2f}")
            self.net_profit_label.setText(f"{data['net_profit']:,.2f}")
            self.transaction_count_label.setText(str(data['transaction_count']))
            
            # Update category table
            categories = data['categories']
            self.category_table.setRowCount(len(categories))
            for row, (category, stats) in enumerate(categories.items()):
                self.category_table.setItem(row, 0, QTableWidgetItem(category))
                self.category_table.setItem(row, 1, QTableWidgetItem(f"{stats['income']:,.2f}"))
                self.category_table.setItem(row, 2, QTableWidgetItem(f"{stats['expenses']:,.2f}"))
                self.category_table.setItem(row, 3, QTableWidgetItem(str(stats['count'])))
            
            # Update chart
            self.financial_chart.figure.clear()
            fig = self.financial_chart.figure
            
            # Create two subplots
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)
            
            # Income vs Expenses bar chart
            ax1.bar(['Income', 'Expenses'], [data['total_income'], data['total_expenses']])
            ax1.set_ylabel(self.language_manager.translate("reports.amount"))
            ax1.set_title(self.language_manager.translate("reports.income_vs_expenses"))
            
            # Category distribution pie chart
            categories = list(data['categories'].keys())
            values = [stats['income'] - stats['expenses'] for stats in data['categories'].values()]
            ax2.pie(values, labels=categories, autopct='%1.1f%%')
            ax2.set_title(self.language_manager.translate("reports.category_distribution"))
            
            fig.tight_layout()
            self.financial_chart.draw()
            
        except Exception as e:
            logger.error(f"Error generating financial report: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate("common.error"),
                self.language_manager.translate("reports.generation_failed")
            )
    
    def _on_language_changed(self, language: str):
        """Update UI when language changes."""
        # Update tab titles
        self.tab_widget.setTabText(0, self.language_manager.translate("reports.projects"))
        self.tab_widget.setTabText(1, self.language_manager.translate("reports.machines"))
        self.tab_widget.setTabText(2, self.language_manager.translate("reports.operators"))
        self.tab_widget.setTabText(3, self.language_manager.translate("reports.financial"))
        
        # Update buttons
        self.project_generate_btn.setText(self.language_manager.translate("reports.generate"))
        self.machine_generate_btn.setText(self.language_manager.translate("reports.generate"))
        self.operator_generate_btn.setText(self.language_manager.translate("reports.generate"))
        self.financial_generate_btn.setText(self.language_manager.translate("reports.generate"))
        
        # Regenerate current report
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            self._generate_project_report()
        elif current_tab == 1:
            self._generate_machine_report()
        elif current_tab == 2:
            self._generate_operator_report()
        else:
            self._generate_financial_report() 
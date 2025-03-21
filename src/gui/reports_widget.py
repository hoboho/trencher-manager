from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QDateEdit, QFrame, QScrollArea,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from src.database.database import DatabaseManager
from src.database.models import Project, Machine, Operator
from src.utils.calculations import format_currency
from src.utils.logger import setup_logger
from src.utils.language_manager import LanguageManager
import pandas as pd
from datetime import datetime, timedelta

logger = setup_logger(__name__)

class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating reports UI for language: {language}")
        
        # Update section titles
        self.report_type_label.setText(self.language_manager.translate('reports.type'))
        self.date_range_label.setText(self.language_manager.translate('reports.date_range'))
        
        # Update report type options
        current_type = self.report_type.currentText()
        self.report_type.clear()
        self.report_type.addItems([
            self.language_manager.translate('reports.types.project_summary'),
            self.language_manager.translate('reports.types.machine_utilization'),
            self.language_manager.translate('reports.types.operator_performance'),
            self.language_manager.translate('reports.types.financial_summary')
        ])
        # Try to restore the previous selection
        index = self.report_type.findText(self.language_manager.translate(f'reports.types.{current_type}'))
        if index >= 0:
            self.report_type.setCurrentIndex(index)
        
        # Update date range presets
        self.date_preset.clear()
        self.date_preset.addItems([
            self.language_manager.translate('reports.date_presets.this_month'),
            self.language_manager.translate('reports.date_presets.last_month'),
            self.language_manager.translate('reports.date_presets.this_quarter'),
            self.language_manager.translate('reports.date_presets.last_quarter'),
            self.language_manager.translate('reports.date_presets.this_year'),
            self.language_manager.translate('reports.date_presets.custom')
        ])
        
        # Update buttons
        self.generate_btn.setText(self.language_manager.translate('reports.generate'))
        self.export_btn.setText(self.language_manager.translate('reports.export'))
        
        # Update table headers if table exists
        if hasattr(self, 'report_table'):
            self._update_table_headers()
        
        logger.info("Reports UI update complete")
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Controls section
        controls_section = QWidget()
        controls_layout = QVBoxLayout(controls_section)
        
        # Report type selection
        type_layout = QHBoxLayout()
        self.report_type_label = QLabel(self.language_manager.translate('reports.type'))
        self.report_type = QComboBox()
        self.report_type.addItems([
            self.language_manager.translate('reports.types.project_summary'),
            self.language_manager.translate('reports.types.machine_utilization'),
            self.language_manager.translate('reports.types.operator_performance'),
            self.language_manager.translate('reports.types.financial_summary')
        ])
        type_layout.addWidget(self.report_type_label)
        type_layout.addWidget(self.report_type)
        type_layout.addStretch()
        controls_layout.addLayout(type_layout)
        
        # Date range selection
        date_layout = QHBoxLayout()
        self.date_range_label = QLabel(self.language_manager.translate('reports.date_range'))
        self.date_preset = QComboBox()
        self.date_preset.addItems([
            self.language_manager.translate('reports.date_presets.this_month'),
            self.language_manager.translate('reports.date_presets.last_month'),
            self.language_manager.translate('reports.date_presets.this_quarter'),
            self.language_manager.translate('reports.date_presets.last_quarter'),
            self.language_manager.translate('reports.date_presets.this_year'),
            self.language_manager.translate('reports.date_presets.custom')
        ])
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        
        date_layout.addWidget(self.date_range_label)
        date_layout.addWidget(self.date_preset)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        controls_layout.addLayout(date_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.generate_btn = QPushButton(self.language_manager.translate('reports.generate'))
        self.export_btn = QPushButton(self.language_manager.translate('reports.export'))
        
        self.generate_btn.clicked.connect(self._generate_report)
        self.export_btn.clicked.connect(self._export_report)
        
        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        layout.addWidget(controls_section)
        
        # Report display area
        self.report_area = QScrollArea()
        self.report_area.setWidgetResizable(True)
        self.report_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.report_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_area.setWidget(self.report_container)
        
        layout.addWidget(self.report_area)
        
        # Connect signals
        self.date_preset.currentIndexChanged.connect(self._update_date_range)
        self._update_date_range()  # Initialize date range
    
    def _update_date_range(self):
        """Update date range based on selected preset."""
        today = datetime.now()
        first_day_month = today.replace(day=1)
        
        if self.date_preset.currentText() == self.language_manager.translate('reports.date_presets.this_month'):
            self.start_date.setDate(QDate(first_day_month.year, first_day_month.month, 1))
            self.end_date.setDate(QDate(today.year, today.month, today.day))
        elif self.date_preset.currentText() == self.language_manager.translate('reports.date_presets.last_month'):
            last_month = first_day_month - timedelta(days=1)
            self.start_date.setDate(QDate(last_month.year, last_month.month, 1))
            self.end_date.setDate(QDate(last_month.year, last_month.month, last_month.day))
        # Add other date range presets as needed
    
    def _generate_report(self):
        """Generate the selected report type."""
        try:
            report_type = self.report_type.currentText()
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            # Clear existing report
            while self.report_layout.count():
                item = self.report_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Create report table
            self.report_table = QTableWidget()
            self._update_table_headers()
            
            # Generate report data based on type
            if report_type == self.language_manager.translate('reports.types.project_summary'):
                self._generate_project_summary(start_date, end_date)
            elif report_type == self.language_manager.translate('reports.types.machine_utilization'):
                self._generate_machine_utilization(start_date, end_date)
            elif report_type == self.language_manager.translate('reports.types.operator_performance'):
                self._generate_operator_performance(start_date, end_date)
            elif report_type == self.language_manager.translate('reports.types.financial_summary'):
                self._generate_financial_summary(start_date, end_date)
            
            self.report_layout.addWidget(self.report_table)
            logger.info(f"Generated {report_type} report")
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))
    
    def _update_table_headers(self):
        """Update table headers based on report type."""
        report_type = self.report_type.currentText()
        
        if report_type == self.language_manager.translate('reports.types.project_summary'):
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels([
                self.language_manager.translate('reports.headers.project_name'),
                self.language_manager.translate('reports.headers.start_date'),
                self.language_manager.translate('reports.headers.end_date'),
                self.language_manager.translate('reports.headers.progress'),
                self.language_manager.translate('reports.headers.total_cost'),
                self.language_manager.translate('reports.headers.status')
            ])
        elif report_type == self.language_manager.translate('reports.types.machine_utilization'):
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels([
                self.language_manager.translate('reports.headers.machine_name'),
                self.language_manager.translate('reports.headers.total_hours'),
                self.language_manager.translate('reports.headers.fuel_consumption'),
                self.language_manager.translate('reports.headers.maintenance_cost'),
                self.language_manager.translate('reports.headers.efficiency')
            ])
        elif report_type == self.language_manager.translate('reports.types.operator_performance'):
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels([
                self.language_manager.translate('reports.headers.operator_name'),
                self.language_manager.translate('reports.headers.total_hours'),
                self.language_manager.translate('reports.headers.overtime_hours'),
                self.language_manager.translate('reports.headers.total_cost'),
                self.language_manager.translate('reports.headers.performance_rating')
            ])
        elif report_type == self.language_manager.translate('reports.types.financial_summary'):
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels([
                self.language_manager.translate('reports.headers.category'),
                self.language_manager.translate('reports.headers.revenue'),
                self.language_manager.translate('reports.headers.expenses'),
                self.language_manager.translate('reports.headers.profit'),
                self.language_manager.translate('reports.headers.tax'),
                self.language_manager.translate('reports.headers.net_profit')
            ])
    
    def _export_report(self):
        """Export the current report to Excel."""
        try:
            if not hasattr(self, 'report_table') or self.report_table.rowCount() == 0:
                raise ValueError(self.language_manager.translate('reports.errors.no_data'))
            
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                self.language_manager.translate('reports.export_dialog_title'),
                "",
                self.language_manager.translate('reports.export_dialog_filter')
            )
            
            if file_name:
                # Convert table data to pandas DataFrame
                headers = []
                for col in range(self.report_table.columnCount()):
                    headers.append(self.report_table.horizontalHeaderItem(col).text())
                
                data = []
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_name, index=False)
                
                QMessageBox.information(
                    self,
                    self.language_manager.translate('reports.success'),
                    self.language_manager.translate('reports.export_success')
                )
                logger.info(f"Report exported to {file_name}")
        except Exception as e:
            logger.error(f"Failed to export report: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate('reports.error'),
                str(e)
            ) 
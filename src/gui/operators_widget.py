from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QDoubleSpinBox,
                             QHeaderView)
from PyQt6.QtCore import Qt
from datetime import datetime
from src.database.models import Operator
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.language_manager import LanguageManager
from src.utils.calculations import format_currency

logger = setup_logger(__name__)

class OperatorDialog(QDialog):
    def __init__(self, parent=None, operator=None):
        super().__init__(parent)
        self.operator = operator
        self.setWindowTitle("Add Operator" if not operator else "Edit Operator")
        self.setModal(True)
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout(self)
        
        # Operator name
        self.name_edit = QLineEdit()
        if self.operator:
            self.name_edit.setText(self.operator.name)
        layout.addRow("Operator Name:", self.name_edit)
        
        # Hourly rate
        self.hourly_rate_spin = QDoubleSpinBox()
        self.hourly_rate_spin.setMaximum(1000000)
        self.hourly_rate_spin.setPrefix("ریال ")
        if self.operator:
            self.hourly_rate_spin.setValue(self.operator.hourly_rate)
        layout.addRow("Hourly Rate:", self.hourly_rate_spin)
        
        # Overtime rate
        self.overtime_rate_spin = QDoubleSpinBox()
        self.overtime_rate_spin.setMaximum(1000000)
        self.overtime_rate_spin.setPrefix("ریال ")
        if self.operator:
            self.overtime_rate_spin.setValue(self.operator.overtime_rate)
        layout.addRow("Overtime Rate:", self.overtime_rate_spin)
        
        # Overtime threshold
        self.overtime_threshold_spin = QDoubleSpinBox()
        self.overtime_threshold_spin.setMaximum(24)
        self.overtime_threshold_spin.setSuffix(" hours")
        if self.operator:
            self.overtime_threshold_spin.setValue(self.operator.overtime_threshold)
        layout.addRow("Overtime Threshold:", self.overtime_threshold_spin)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def get_operator_data(self):
        return {
            'name': self.name_edit.text(),
            'hourly_rate': self.hourly_rate_spin.value(),
            'overtime_rate': self.overtime_rate_spin.value(),
            'overtime_threshold': self.overtime_threshold_spin.value()
        }

class OperatorsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
        self._load_operators()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating operators UI for language: {language}")
        
        # Update search placeholder
        self.search_input.setPlaceholderText(self.language_manager.translate('operator.search_placeholder'))
        
        # Update buttons
        self.add_btn.setText(self.language_manager.translate('operator.add'))
        self.edit_btn.setText(self.language_manager.translate('operator.edit'))
        self.delete_btn.setText(self.language_manager.translate('operator.delete'))
        
        # Update table headers
        self._update_table_headers()
        
        logger.info("Operators UI update complete")
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.language_manager.translate('operator.search_placeholder'))
        self.search_input.textChanged.connect(self._filter_operators)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Operators table
        self.operators_table = QTableWidget()
        self.operators_table.setColumnCount(7)
        self._update_table_headers()
        
        # Set table properties
        self.operators_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.operators_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.operators_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.operators_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.language_manager.translate('operator.add'))
        self.edit_btn = QPushButton(self.language_manager.translate('operator.edit'))
        self.delete_btn = QPushButton(self.language_manager.translate('operator.delete'))
        
        self.add_btn.clicked.connect(self._add_operator)
        self.edit_btn.clicked.connect(self._edit_operator)
        self.delete_btn.clicked.connect(self._delete_operator)
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def _update_table_headers(self):
        """Update table headers with current language."""
        headers = [
            self.language_manager.translate('operator.name'),
            self.language_manager.translate('operator.hourly_rate'),
            self.language_manager.translate('operator.overtime_rate'),
            self.language_manager.translate('operator.overtime_threshold'),
            self.language_manager.translate('operator.contact'),
            self.language_manager.translate('operator.skills'),
            self.language_manager.translate('operator.notes')
        ]
        self.operators_table.setHorizontalHeaderLabels(headers)
    
    def _load_operators(self):
        """Load operators from database and display in table."""
        try:
            with self.db_manager.get_session() as session:
                operators = session.query(Operator).all()
                self.operators_table.setRowCount(len(operators))
                
                for row, operator in enumerate(operators):
                    self.operators_table.setItem(row, 0, QTableWidgetItem(operator.name))
                    self.operators_table.setItem(row, 1, QTableWidgetItem(format_currency(operator.hourly_rate)))
                    self.operators_table.setItem(row, 2, QTableWidgetItem(format_currency(operator.overtime_rate)))
                    self.operators_table.setItem(row, 3, QTableWidgetItem(str(operator.overtime_threshold)))
                    self.operators_table.setItem(row, 4, QTableWidgetItem(operator.contact))
                    self.operators_table.setItem(row, 5, QTableWidgetItem(operator.skills))
                    self.operators_table.setItem(row, 6, QTableWidgetItem(operator.notes))
                
                logger.info(f"Loaded {len(operators)} operators")
        except Exception as e:
            logger.error(f"Failed to load operators: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate('common.error'),
                self.language_manager.translate('operator.load_error').format(error=str(e))
            )
    
    def _filter_operators(self):
        """Filter operators based on search text."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.operators_table.rowCount()):
            show_row = False
            for col in range(self.operators_table.columnCount()):
                item = self.operators_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.operators_table.setRowHidden(row, not show_row)
    
    def _add_operator(self):
        """Open dialog to add a new operator."""
        dialog = OperatorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_operator_data()
                with self.db_manager.get_session() as session:
                    operator = Operator(**data)
                    session.add(operator)
                    session.commit()
                
                self._load_operators()
                QMessageBox.information(self, "Success", "Operator added successfully")
                logger.info(f"Added new operator: {data['name']}")
            except Exception as e:
                logger.error(f"Failed to add operator: {str(e)}")
                QMessageBox.critical(self, "Error", "Failed to add operator")
    
    def _edit_operator(self):
        """Open dialog to edit selected operator."""
        current_row = self.operators_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an operator to edit")
            return
        
        operator_id = int(self.operators_table.item(current_row, 0).text())
        try:
            with self.db_manager.get_session() as session:
                operator = session.query(Operator).get(operator_id)
                if operator:
                    dialog = OperatorDialog(self, operator)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        data = dialog.get_operator_data()
                        for key, value in data.items():
                            setattr(operator, key, value)
                        session.commit()
                        
                        self._load_operators()
                        QMessageBox.information(self, "Success", "Operator updated successfully")
                        logger.info(f"Updated operator: {operator.name}")
        except Exception as e:
            logger.error(f"Failed to edit operator: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to edit operator")
    
    def _delete_operator(self):
        """Delete selected operator."""
        current_row = self.operators_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an operator to delete")
            return
        
        operator_id = int(self.operators_table.item(current_row, 0).text())
        operator_name = self.operators_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete operator '{operator_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_session() as session:
                    operator = session.query(Operator).get(operator_id)
                    if operator:
                        session.delete(operator)
                        session.commit()
                        
                        self._load_operators()
                        QMessageBox.information(self, "Success", "Operator deleted successfully")
                        logger.info(f"Deleted operator: {operator_name}")
            except Exception as e:
                logger.error(f"Failed to delete operator: {str(e)}")
                QMessageBox.critical(self, "Error", "Failed to delete operator") 
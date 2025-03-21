from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QDateEdit,
                             QDoubleSpinBox, QComboBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.database.models import Machine
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.calculations import format_currency
from src.utils.language_manager import LanguageManager

logger = setup_logger(__name__)

class MachineDialog(QDialog):
    def __init__(self, parent=None, machine=None):
        super().__init__(parent)
        self.machine = machine
        self.language_manager = LanguageManager()
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle(self.language_manager.translate('machine.dialog.edit_title' if self.machine else 'machine.dialog.add_title'))
        layout = QFormLayout(self)
        
        # Machine name
        self.name_edit = QLineEdit()
        layout.addRow(self.language_manager.translate('machine.name') + ":", self.name_edit)
        
        # Model
        self.model_edit = QLineEdit()
        layout.addRow(self.language_manager.translate('machine.model') + ":", self.model_edit)
        
        # Purchase date
        self.purchase_date = QDateEdit()
        self.purchase_date.setCalendarPopup(True)
        self.purchase_date.setDate(QDate.currentDate())
        layout.addRow(self.language_manager.translate('machine.purchase_date') + ":", self.purchase_date)
        
        # Purchase price
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setMaximum(1000000000)
        self.purchase_price.setPrefix("ریال ")
        layout.addRow(self.language_manager.translate('machine.purchase_price') + ":", self.purchase_price)
        
        # Fuel consumption rate
        self.fuel_rate = QDoubleSpinBox()
        self.fuel_rate.setMaximum(1000)
        self.fuel_rate.setSuffix(" L/h")
        layout.addRow(self.language_manager.translate('machine.fuel_consumption_rate') + ":", self.fuel_rate)
        
        # Fuel cost per liter
        self.fuel_cost = QDoubleSpinBox()
        self.fuel_cost.setMaximum(100000)
        self.fuel_cost.setPrefix("ریال ")
        layout.addRow(self.language_manager.translate('machine.fuel_cost_per_liter') + ":", self.fuel_cost)
        
        # Maintenance cost per hour
        self.maintenance_cost = QDoubleSpinBox()
        self.maintenance_cost.setMaximum(100000)
        self.maintenance_cost.setPrefix("ریال ")
        layout.addRow(self.language_manager.translate('machine.maintenance_cost_per_hour') + ":", self.maintenance_cost)
        
        # Trenching specifications
        self.trenching_depth = QDoubleSpinBox()
        self.trenching_depth.setMaximum(10)
        self.trenching_depth.setSuffix(" m")
        layout.addRow(self.language_manager.translate('machine.trenching_depth') + ":", self.trenching_depth)
        
        self.trenching_width = QDoubleSpinBox()
        self.trenching_width.setMaximum(2)
        self.trenching_width.setSuffix(" m")
        layout.addRow(self.language_manager.translate('machine.trenching_width') + ":", self.trenching_width)
        
        self.maximum_speed = QDoubleSpinBox()
        self.maximum_speed.setMaximum(1000)
        self.maximum_speed.setSuffix(" m/h")
        layout.addRow(self.language_manager.translate('machine.maximum_speed') + ":", self.maximum_speed)
        
        self.weight = QDoubleSpinBox()
        self.weight.setMaximum(10000)
        self.weight.setSuffix(" kg")
        layout.addRow(self.language_manager.translate('machine.weight') + ":", self.weight)
        
        # Status
        self.status = QComboBox()
        self.status.addItems(['active', 'maintenance', 'inactive'])
        layout.addRow(self.language_manager.translate('machine.status') + ":", self.status)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.language_manager.translate('common.save'))
        self.cancel_btn = QPushButton(self.language_manager.translate('common.cancel'))
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addRow("", buttons_layout)
        
        # If editing, populate fields
        if self.machine:
            self.name_edit.setText(self.machine.name)
            self.model_edit.setText(self.machine.model)
            self.purchase_date.setDate(QDate.fromString(self.machine.purchase_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.purchase_price.setValue(self.machine.purchase_price)
            self.fuel_rate.setValue(self.machine.fuel_consumption_rate)
            self.fuel_cost.setValue(self.machine.fuel_cost_per_liter)
            self.maintenance_cost.setValue(self.machine.maintenance_cost_per_hour)
            self.trenching_depth.setValue(self.machine.trenching_depth)
            self.trenching_width.setValue(self.machine.trenching_width)
            self.maximum_speed.setValue(self.machine.maximum_speed)
            self.weight.setValue(self.machine.weight)
            self.status.setCurrentText(self.machine.status)
    
    def get_machine_data(self):
        """Get the machine data from the form."""
        return {
            'name': self.name_edit.text(),
            'model': self.model_edit.text(),
            'purchase_date': self.purchase_date.date().toPyDate(),
            'purchase_price': self.purchase_price.value(),
            'fuel_consumption_rate': self.fuel_rate.value(),
            'fuel_cost_per_liter': self.fuel_cost.value(),
            'maintenance_cost_per_hour': self.maintenance_cost.value(),
            'trenching_depth': self.trenching_depth.value(),
            'trenching_width': self.trenching_width.value(),
            'maximum_speed': self.maximum_speed.value(),
            'weight': self.weight.value(),
            'status': self.status.currentText()
        }

class MachinesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
        self._load_machines()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating machines widget UI for language: {language}")
        
        # Update search placeholder
        self.search_input.setPlaceholderText(self.language_manager.translate('machine.search_placeholder'))
        
        # Update table headers
        self.machines_table.setHorizontalHeaderLabels([
            self.language_manager.translate('machine.name'),
            self.language_manager.translate('machine.model'),
            self.language_manager.translate('machine.purchase_date'),
            self.language_manager.translate('machine.purchase_price'),
            self.language_manager.translate('machine.fuel_consumption_rate'),
            self.language_manager.translate('machine.fuel_cost_per_liter'),
            self.language_manager.translate('machine.maintenance_cost_per_hour'),
            self.language_manager.translate('machine.trenching_depth'),
            self.language_manager.translate('machine.trenching_width'),
            self.language_manager.translate('machine.maximum_speed'),
            self.language_manager.translate('machine.weight'),
            self.language_manager.translate('machine.status')
        ])
        
        # Update buttons
        self.add_btn.setText(self.language_manager.translate('machine.add'))
        self.edit_btn.setText(self.language_manager.translate('machine.edit'))
        self.delete_btn.setText(self.language_manager.translate('machine.delete'))
        
        logger.info("Machines widget UI update complete")
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.language_manager.translate('machine.search_placeholder'))
        self.search_input.textChanged.connect(self._filter_machines)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Machines table
        self.machines_table = QTableWidget()
        self.machines_table.setColumnCount(12)
        self.machines_table.setHorizontalHeaderLabels([
            self.language_manager.translate('machine.name'),
            self.language_manager.translate('machine.model'),
            self.language_manager.translate('machine.purchase_date'),
            self.language_manager.translate('machine.purchase_price'),
            self.language_manager.translate('machine.fuel_consumption_rate'),
            self.language_manager.translate('machine.fuel_cost_per_liter'),
            self.language_manager.translate('machine.maintenance_cost_per_hour'),
            self.language_manager.translate('machine.trenching_depth'),
            self.language_manager.translate('machine.trenching_width'),
            self.language_manager.translate('machine.maximum_speed'),
            self.language_manager.translate('machine.weight'),
            self.language_manager.translate('machine.status')
        ])
        self.machines_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.machines_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.language_manager.translate('machine.add'))
        self.edit_btn = QPushButton(self.language_manager.translate('machine.edit'))
        self.delete_btn = QPushButton(self.language_manager.translate('machine.delete'))
        
        self.add_btn.clicked.connect(self._add_machine)
        self.edit_btn.clicked.connect(self._edit_machine)
        self.delete_btn.clicked.connect(self._delete_machine)
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def _load_machines(self):
        """Load machines from database."""
        try:
            with self.db_manager.get_session() as session:
                machines = session.query(Machine).all()
                self.machines_table.setRowCount(len(machines))
                
                for row, machine in enumerate(machines):
                    self.machines_table.setItem(row, 0, QTableWidgetItem(machine.name))
                    self.machines_table.setItem(row, 1, QTableWidgetItem(machine.model))
                    self.machines_table.setItem(row, 2, QTableWidgetItem(machine.purchase_date.strftime("%Y-%m-%d")))
                    self.machines_table.setItem(row, 3, QTableWidgetItem(format_currency(machine.purchase_price)))
                    self.machines_table.setItem(row, 4, QTableWidgetItem(f"{machine.fuel_consumption_rate:.2f} L/h"))
                    self.machines_table.setItem(row, 5, QTableWidgetItem(format_currency(machine.fuel_cost_per_liter)))
                    self.machines_table.setItem(row, 6, QTableWidgetItem(format_currency(machine.maintenance_cost_per_hour)))
                    self.machines_table.setItem(row, 7, QTableWidgetItem(f"{machine.trenching_depth:.2f} m"))
                    self.machines_table.setItem(row, 8, QTableWidgetItem(f"{machine.trenching_width:.2f} m"))
                    self.machines_table.setItem(row, 9, QTableWidgetItem(f"{machine.maximum_speed:.2f} m/h"))
                    self.machines_table.setItem(row, 10, QTableWidgetItem(f"{machine.weight:.1f} kg"))
                    self.machines_table.setItem(row, 11, QTableWidgetItem(machine.status))
                
                logger.info(f"Loaded {len(machines)} machines")
        except Exception as e:
            logger.error(f"Failed to load machines: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load machines: {str(e)}")
    
    def _filter_machines(self):
        """Filter machines based on search text."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.machines_table.rowCount()):
            show_row = False
            for col in range(self.machines_table.columnCount()):
                item = self.machines_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.machines_table.setRowHidden(row, not show_row)
    
    def _add_machine(self):
        """Add a new machine."""
        dialog = MachineDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                with self.db_manager.get_session() as session:
                    machine_data = dialog.get_machine_data()
                    machine = Machine(**machine_data)
                    session.add(machine)
                    session.commit()
                    
                    logger.info(f"Added new machine: {machine.name}")
                    self._load_machines()
                    
                    QMessageBox.information(self, "Success", "Machine added successfully!")
            except Exception as e:
                logger.error(f"Failed to add machine: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to add machine: {str(e)}")
    
    def _edit_machine(self):
        """Edit the selected machine."""
        current_row = self.machines_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a machine to edit.")
            return
        
        try:
            with self.db_manager.get_session() as session:
                machine_name = self.machines_table.item(current_row, 0).text()
                machine = session.query(Machine).filter_by(name=machine_name).first()
                
                if machine:
                    dialog = MachineDialog(self, machine)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        machine_data = dialog.get_machine_data()
                        for key, value in machine_data.items():
                            setattr(machine, key, value)
                        session.commit()
                        
                        logger.info(f"Updated machine: {machine.name}")
                        self._load_machines()
                        
                        QMessageBox.information(self, "Success", "Machine updated successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Machine not found.")
        except Exception as e:
            logger.error(f"Failed to edit machine: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit machine: {str(e)}")
    
    def _delete_machine(self):
        """Delete the selected machine."""
        current_row = self.machines_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a machine to delete.")
            return
        
        machine_name = self.machines_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete machine '{machine_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_session() as session:
                    machine = session.query(Machine).filter_by(name=machine_name).first()
                    if machine:
                        session.delete(machine)
                        session.commit()
                        
                        logger.info(f"Deleted machine: {machine_name}")
                        self._load_machines()
                        
                        QMessageBox.information(self, "Success", "Machine deleted successfully!")
                    else:
                        QMessageBox.warning(self, "Warning", "Machine not found.")
            except Exception as e:
                logger.error(f"Failed to delete machine: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to delete machine: {str(e)}") 
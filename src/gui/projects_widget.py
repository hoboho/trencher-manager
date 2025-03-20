from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QDateEdit,
                             QDoubleSpinBox, QComboBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.database.models import Project
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProjectDialog(QDialog):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Add Project" if not project else "Edit Project")
        self.setModal(True)
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout(self)
        
        # Project name
        self.name_edit = QLineEdit()
        if self.project:
            self.name_edit.setText(self.project.name)
        layout.addRow("Project Name:", self.name_edit)
        
        # Contract amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMaximum(10000000)
        self.amount_spin.setPrefix("$")
        if self.project:
            self.amount_spin.setValue(self.project.contract_amount)
        layout.addRow("Contract Amount:", self.amount_spin)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        if self.project:
            self.start_date.setDate(self.project.start_date.date())
        layout.addRow("Start Date:", self.start_date)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "completed", "cancelled"])
        if self.project:
            self.status_combo.setCurrentText(self.project.status)
        layout.addRow("Status:", self.status_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def get_project_data(self):
        return {
            'name': self.name_edit.text(),
            'contract_amount': self.amount_spin.value(),
            'start_date': self.start_date.date().toPyDate(),
            'status': self.status_combo.currentText()
        }

class ProjectsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self._init_ui()
        self._load_projects()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search projects...")
        self.search_edit.textChanged.connect(self._filter_projects)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Contract Amount", "Start Date", "Status"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Project")
        add_btn.clicked.connect(self._add_project)
        edit_btn = QPushButton("Edit Project")
        edit_btn.clicked.connect(self._edit_project)
        delete_btn = QPushButton("Delete Project")
        delete_btn.clicked.connect(self._delete_project)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
    
    def _load_projects(self):
        """Load projects from database and display them in the table."""
        try:
            with self.db_manager.get_session() as session:
                projects = session.query(Project).all()
                
                self.table.setRowCount(len(projects))
                for row, project in enumerate(projects):
                    self.table.setItem(row, 0, QTableWidgetItem(str(project.id)))
                    self.table.setItem(row, 1, QTableWidgetItem(project.name))
                    self.table.setItem(row, 2, QTableWidgetItem(f"${project.contract_amount:,.2f}"))
                    self.table.setItem(row, 3, QTableWidgetItem(project.start_date.strftime('%Y-%m-%d')))
                    self.table.setItem(row, 4, QTableWidgetItem(project.status))
                
                self.table.resizeColumnsToContents()
                logger.info(f"Loaded {len(projects)} projects")
        except Exception as e:
            logger.error(f"Failed to load projects: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to load projects")
    
    def _filter_projects(self):
        """Filter projects based on search text."""
        search_text = self.search_edit.text().lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def _add_project(self):
        """Open dialog to add a new project."""
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_project_data()
                with self.db_manager.get_session() as session:
                    project = Project(**data)
                    session.add(project)
                    session.commit()
                
                self._load_projects()
                QMessageBox.information(self, "Success", "Project added successfully")
                logger.info(f"Added new project: {data['name']}")
            except Exception as e:
                logger.error(f"Failed to add project: {str(e)}")
                QMessageBox.critical(self, "Error", "Failed to add project")
    
    def _edit_project(self):
        """Open dialog to edit selected project."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to edit")
            return
        
        project_id = int(self.table.item(current_row, 0).text())
        try:
            with self.db_manager.get_session() as session:
                project = session.query(Project).get(project_id)
                if project:
                    dialog = ProjectDialog(self, project)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        data = dialog.get_project_data()
                        for key, value in data.items():
                            setattr(project, key, value)
                        session.commit()
                        
                        self._load_projects()
                        QMessageBox.information(self, "Success", "Project updated successfully")
                        logger.info(f"Updated project: {project.name}")
        except Exception as e:
            logger.error(f"Failed to edit project: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to edit project")
    
    def _delete_project(self):
        """Delete selected project."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to delete")
            return
        
        project_id = int(self.table.item(current_row, 0).text())
        project_name = self.table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete project '{project_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_session() as session:
                    project = session.query(Project).get(project_id)
                    if project:
                        session.delete(project)
                        session.commit()
                        
                        self._load_projects()
                        QMessageBox.information(self, "Success", "Project deleted successfully")
                        logger.info(f"Deleted project: {project_name}")
            except Exception as e:
                logger.error(f"Failed to delete project: {str(e)}")
                QMessageBox.critical(self, "Error", "Failed to delete project") 
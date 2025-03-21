from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                             QMessageBox, QDialog, QFormLayout, QDateEdit,
                             QDoubleSpinBox, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.database.models import Project
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.calculations import format_currency
from src.utils.language_manager import LanguageManager

logger = setup_logger(__name__)

class ProjectDialog(QDialog):
    def __init__(self, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Add Project" if not self.project else "Edit Project")
        layout = QFormLayout(self)
        
        # Project name
        self.name_edit = QLineEdit()
        layout.addRow("Project Name:", self.name_edit)
        
        # Contract amount
        self.contract_amount = QDoubleSpinBox()
        self.contract_amount.setMaximum(1000000000)
        self.contract_amount.setPrefix("$")
        layout.addRow("Contract Amount:", self.contract_amount)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        layout.addRow("Start Date:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(30))
        layout.addRow("End Date:", self.end_date)
        
        # Status
        self.status = QComboBox()
        self.status.addItems(['active', 'completed', 'cancelled'])
        layout.addRow("Status:", self.status)
        
        # Project specifications
        self.total_length = QDoubleSpinBox()
        self.total_length.setMaximum(100000)
        self.total_length.setSuffix(" m")
        layout.addRow("Total Length:", self.total_length)
        
        self.average_depth = QDoubleSpinBox()
        self.average_depth.setMaximum(100)
        self.average_depth.setSuffix(" m")
        layout.addRow("Average Depth:", self.average_depth)
        
        self.average_width = QDoubleSpinBox()
        self.average_width.setMaximum(100)
        self.average_width.setSuffix(" m")
        layout.addRow("Average Width:", self.average_width)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow("", buttons_layout)
        
        # If editing, populate fields
        if self.project:
            self.name_edit.setText(self.project.name)
            self.contract_amount.setValue(self.project.contract_amount)
            self.start_date.setDate(QDate.fromString(self.project.start_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            if self.project.end_date:
                self.end_date.setDate(QDate.fromString(self.project.end_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.status.setCurrentText(self.project.status)
            if self.project.total_length:
                self.total_length.setValue(self.project.total_length)
            if self.project.average_depth:
                self.average_depth.setValue(self.project.average_depth)
            if self.project.average_width:
                self.average_width.setValue(self.project.average_width)
    
    def get_project_data(self):
        """Get the project data from the form."""
        return {
            'name': self.name_edit.text(),
            'contract_amount': self.contract_amount.value(),
            'start_date': self.start_date.date().toPyDate(),
            'end_date': self.end_date.date().toPyDate(),
            'status': self.status.currentText(),
            'total_length': self.total_length.value(),
            'average_depth': self.average_depth.value(),
            'average_width': self.average_width.value()
        }

class ProjectsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
        self._load_projects()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating projects UI for language: {language}")
        
        # Update search placeholder
        self.search_input.setPlaceholderText(self.language_manager.translate('project.search_placeholder'))
        
        # Update buttons
        self.add_btn.setText(self.language_manager.translate('project.add'))
        self.edit_btn.setText(self.language_manager.translate('project.edit'))
        self.delete_btn.setText(self.language_manager.translate('project.delete'))
        
        # Update table headers
        self._update_table_headers()
        
        logger.info("Projects UI update complete")
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.language_manager.translate('project.search_placeholder'))
        self.search_input.textChanged.connect(self._filter_projects)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Projects table
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(8)
        self._update_table_headers()
        
        # Set table properties
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.projects_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton(self.language_manager.translate('project.add'))
        self.edit_btn = QPushButton(self.language_manager.translate('project.edit'))
        self.delete_btn = QPushButton(self.language_manager.translate('project.delete'))
        
        self.add_btn.clicked.connect(self._add_project)
        self.edit_btn.clicked.connect(self._edit_project)
        self.delete_btn.clicked.connect(self._delete_project)
        
        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def _update_table_headers(self):
        """Update table headers with current language."""
        headers = [
            self.language_manager.translate('project.name'),
            self.language_manager.translate('project.client_name'),
            self.language_manager.translate('project.start_date'),
            self.language_manager.translate('project.end_date'),
            self.language_manager.translate('project.total_length'),
            self.language_manager.translate('project.contract_amount'),
            self.language_manager.translate('project.status'),
            self.language_manager.translate('project.description')
        ]
        self.projects_table.setHorizontalHeaderLabels(headers)
    
    def _load_projects(self):
        """Load projects from database and display in table."""
        try:
            with self.db_manager.get_session() as session:
                projects = session.query(Project).all()
                self.projects_table.setRowCount(len(projects))
                
                for row, project in enumerate(projects):
                    self.projects_table.setItem(row, 0, QTableWidgetItem(project.name))
                    self.projects_table.setItem(row, 1, QTableWidgetItem(project.client_name))
                    self.projects_table.setItem(row, 2, QTableWidgetItem(project.start_date.strftime("%Y-%m-%d")))
                    self.projects_table.setItem(row, 3, QTableWidgetItem(project.end_date.strftime("%Y-%m-%d")))
                    self.projects_table.setItem(row, 4, QTableWidgetItem(str(project.total_length)))
                    self.projects_table.setItem(row, 5, QTableWidgetItem(format_currency(project.contract_amount)))
                    self.projects_table.setItem(row, 6, QTableWidgetItem(project.status))
                    self.projects_table.setItem(row, 7, QTableWidgetItem(project.description))
                
                logger.info(f"Loaded {len(projects)} projects")
        except Exception as e:
            logger.error(f"Failed to load projects: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate('common.error'),
                self.language_manager.translate('project.load_error').format(error=str(e))
            )
    
    def _filter_projects(self):
        """Filter projects based on search text."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.projects_table.rowCount()):
            show_row = False
            for col in range(self.projects_table.columnCount()):
                item = self.projects_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.projects_table.setRowHidden(row, not show_row)
    
    def _add_project(self):
        """Add a new project."""
        dialog = ProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                with self.db_manager.get_session() as session:
                    project_data = dialog.get_project_data()
                    project = Project(**project_data)
                    session.add(project)
                    session.commit()
                    
                    logger.info(f"Added new project: {project.name}")
                    self._load_projects()
                    
                    QMessageBox.information(self, "Success", "Project added successfully!")
            except Exception as e:
                logger.error(f"Failed to add project: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to add project: {str(e)}")
    
    def _edit_project(self):
        """Edit the selected project."""
        current_row = self.projects_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to edit.")
            return
        
        try:
            with self.db_manager.get_session() as session:
                project_name = self.projects_table.item(current_row, 0).text()
                project = session.query(Project).filter_by(name=project_name).first()
                
                if project:
                    dialog = ProjectDialog(self, project)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        project_data = dialog.get_project_data()
                        for key, value in project_data.items():
                            setattr(project, key, value)
                        session.commit()
                        
                        logger.info(f"Updated project: {project.name}")
                        self._load_projects()
                        
                        QMessageBox.information(self, "Success", "Project updated successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Project not found.")
        except Exception as e:
            logger.error(f"Failed to edit project: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit project: {str(e)}")
    
    def _delete_project(self):
        """Delete the selected project."""
        current_row = self.projects_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a project to delete.")
            return
        
        project_name = self.projects_table.item(current_row, 0).text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete project '{project_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_session() as session:
                    project = session.query(Project).filter_by(name=project_name).first()
                    if project:
                        session.delete(project)
                        session.commit()
                        
                        logger.info(f"Deleted project: {project_name}")
                        self._load_projects()
                        
                        QMessageBox.information(self, "Success", "Project deleted successfully!")
                    else:
                        QMessageBox.warning(self, "Warning", "Project not found.")
            except Exception as e:
                logger.error(f"Failed to delete project: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to delete project: {str(e)}") 
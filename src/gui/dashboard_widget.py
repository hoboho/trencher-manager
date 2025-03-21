from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFrame, QGridLayout, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
from src.database.models import Project, Machine, Operator
from src.database.database import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.calculations import format_currency
from src.gui.projects_widget import ProjectDialog
from src.gui.machines_widget import MachineDialog
from src.gui.operators_widget import OperatorDialog
from src.utils.language_manager import LanguageManager

logger = setup_logger(__name__)

class StatCard(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("stat-card")
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("stat-title")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat-value")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
    
    def update_text(self, title, value):
        self.title_label.setText(title)
        self.value_label.setText(value)

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self._init_ui()
        self._load_stats()
        self._load_recent_activities()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating dashboard UI for language: {language}")
        
        # Update quick action buttons
        self.add_project_btn.setText(self.language_manager.translate('dashboard.add_project'))
        self.add_machine_btn.setText(self.language_manager.translate('dashboard.add_machine'))
        self.add_operator_btn.setText(self.language_manager.translate('dashboard.add_operator'))
        
        # Update section titles
        self.stats_title.setText(self.language_manager.translate('dashboard.overview_title'))
        self.actions_title.setText(self.language_manager.translate('dashboard.actions_title'))
        self.activities_title.setText(self.language_manager.translate('dashboard.activities_title'))
        
        # Update statistics cards
        self._load_stats()
        
        # Update recent activities
        self._load_recent_activities()
        
        logger.info("Dashboard UI update complete")
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Statistics section
        stats_section = QWidget()
        stats_layout = QVBoxLayout(stats_section)
        
        self.stats_title = QLabel(self.language_manager.translate('dashboard.overview_title'))
        self.stats_title.setObjectName("section-title")
        stats_layout.addWidget(self.stats_title)
        
        # Grid for stat cards
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Create stat cards (will be populated later)
        self.total_projects = StatCard("", "")
        self.active_projects = StatCard("", "")
        self.total_machines = StatCard("", "")
        self.active_machines = StatCard("", "")
        self.total_operators = StatCard("", "")
        self.active_operators = StatCard("", "")
        self.monthly_revenue = StatCard("", "")
        self.monthly_costs = StatCard("", "")
        self.monthly_profit = StatCard("", "")
        
        # Add stat cards to grid
        stats_grid.addWidget(self.total_projects, 0, 0)
        stats_grid.addWidget(self.active_projects, 0, 1)
        stats_grid.addWidget(self.total_machines, 0, 2)
        stats_grid.addWidget(self.active_machines, 1, 0)
        stats_grid.addWidget(self.total_operators, 1, 1)
        stats_grid.addWidget(self.active_operators, 1, 2)
        stats_grid.addWidget(self.monthly_revenue, 2, 0)
        stats_grid.addWidget(self.monthly_costs, 2, 1)
        stats_grid.addWidget(self.monthly_profit, 2, 2)
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_section)
        
        # Quick actions section
        actions_section = QWidget()
        actions_layout = QVBoxLayout(actions_section)
        
        self.actions_title = QLabel(self.language_manager.translate('dashboard.actions_title'))
        self.actions_title.setObjectName("section-title")
        actions_layout.addWidget(self.actions_title)
        
        buttons_layout = QHBoxLayout()
        self.add_project_btn = QPushButton(self.language_manager.translate('dashboard.add_project'))
        self.add_machine_btn = QPushButton(self.language_manager.translate('dashboard.add_machine'))
        self.add_operator_btn = QPushButton(self.language_manager.translate('dashboard.add_operator'))
        
        # Connect button signals
        self.add_project_btn.clicked.connect(self._add_project)
        self.add_machine_btn.clicked.connect(self._add_machine)
        self.add_operator_btn.clicked.connect(self._add_operator)
        
        buttons_layout.addWidget(self.add_project_btn)
        buttons_layout.addWidget(self.add_machine_btn)
        buttons_layout.addWidget(self.add_operator_btn)
        buttons_layout.addStretch()
        
        actions_layout.addLayout(buttons_layout)
        layout.addWidget(actions_section)
        
        # Recent activities section
        activities_section = QWidget()
        activities_layout = QVBoxLayout(activities_section)
        
        self.activities_title = QLabel(self.language_manager.translate('dashboard.activities_title'))
        self.activities_title.setObjectName("section-title")
        activities_layout.addWidget(self.activities_title)
        
        # Scrollable activities list
        activities_scroll = QScrollArea()
        activities_scroll.setWidgetResizable(True)
        activities_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.activities_container = QWidget()
        self.activities_list = QVBoxLayout(self.activities_container)
        activities_scroll.setWidget(self.activities_container)
        
        activities_layout.addWidget(activities_scroll)
        layout.addWidget(activities_section)
        
        layout.addStretch()
    
    def _load_stats(self):
        """Load and display statistics."""
        try:
            with self.db_manager.get_session() as session:
                # Projects stats
                total_projects = session.query(Project).count()
                active_projects = session.query(Project).filter_by(status='active').count()
                
                # Machines stats
                total_machines = session.query(Machine).count()
                active_machines = session.query(Machine).filter_by(status='active').count()
                
                # Operators stats - removed status filter since it doesn't exist
                total_operators = session.query(Operator).count()
                active_operators = total_operators  # All operators considered active for now
                
                # Financial stats (calculate from actual data)
                today = datetime.now()
                first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                # Get all projects in the current month
                monthly_projects = session.query(Project).filter(
                    Project.created_at >= first_day
                ).all()
                
                monthly_revenue = sum(p.contract_amount for p in monthly_projects if hasattr(p, 'contract_amount') and p.contract_amount is not None)
                monthly_costs = sum(p.total_cost for p in monthly_projects if hasattr(p, 'total_cost') and p.total_cost is not None)
                monthly_profit = monthly_revenue - monthly_costs
                
                # Update stat cards
                self.total_projects.update_text(
                    self.language_manager.translate('dashboard.total_projects'),
                    str(total_projects)
                )
                self.active_projects.update_text(
                    self.language_manager.translate('dashboard.active_projects'),
                    str(active_projects)
                )
                self.total_machines.update_text(
                    self.language_manager.translate('dashboard.total_machines'),
                    str(total_machines)
                )
                self.active_machines.update_text(
                    self.language_manager.translate('dashboard.active_machines'),
                    str(active_machines)
                )
                self.total_operators.update_text(
                    self.language_manager.translate('dashboard.total_operators'),
                    str(total_operators)
                )
                self.active_operators.update_text(
                    self.language_manager.translate('dashboard.active_operators'),
                    str(active_operators)
                )
                self.monthly_revenue.update_text(
                    self.language_manager.translate('dashboard.monthly_revenue'),
                    format_currency(monthly_revenue)
                )
                self.monthly_costs.update_text(
                    self.language_manager.translate('dashboard.monthly_costs'),
                    format_currency(monthly_costs)
                )
                self.monthly_profit.update_text(
                    self.language_manager.translate('dashboard.monthly_profit'),
                    format_currency(monthly_profit)
                )
                
                logger.info("Dashboard statistics updated successfully")
        except Exception as e:
            logger.error(f"Failed to load dashboard statistics: {str(e)}")
            QMessageBox.critical(
                self,
                self.language_manager.translate('common.error'),
                self.language_manager.translate('dashboard.load_stats_error').format(error=str(e))
            )
    
    def _load_recent_activities(self):
        """Load and display recent activities."""
        try:
            # Clear existing activities
            while self.activities_list.count():
                item = self.activities_list.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            with self.db_manager.get_session() as session:
                # Get 5 most recent projects
                recent_projects = session.query(Project).order_by(Project.created_at.desc()).limit(5).all()
                
                for project in recent_projects:
                    activity = QLabel(
                        self.language_manager.translate('dashboard.project_created').format(
                            name=project.name,
                            date=project.created_at.strftime("%Y-%m-%d")
                        )
                    )
                    activity.setObjectName("activity-item")
                    self.activities_list.addWidget(activity)
                
                logger.info(f"Loaded {len(recent_projects)} recent activities")
        except Exception as e:
            logger.error(f"Failed to load recent activities: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load activities: {str(e)}")
    
    def _add_project(self):
        """Open dialog to add a new project."""
        dialog = ProjectDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            try:
                with self.db_manager.get_session() as session:
                    project_data = dialog.get_project_data()
                    project = Project(**project_data)
                    session.add(project)
                    session.commit()
                    
                    logger.info(f"Added new project: {project.name}")
                    self._load_stats()  # Refresh dashboard stats
                    self._load_recent_activities()  # Refresh activities
                    
                    QMessageBox.information(
                        self,
                        self.language_manager.translate('common.success'),
                        self.language_manager.translate('project.add_success')
                    )
            except Exception as e:
                logger.error(f"Failed to add project: {str(e)}")
                QMessageBox.critical(
                    self,
                    self.language_manager.translate('common.error'),
                    str(e)
                )
    
    def _add_machine(self):
        """Open dialog to add a new machine."""
        dialog = MachineDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            try:
                with self.db_manager.get_session() as session:
                    machine_data = dialog.get_machine_data()
                    machine = Machine(**machine_data)
                    session.add(machine)
                    session.commit()
                    
                    logger.info(f"Added new machine: {machine.name}")
                    self._load_stats()  # Refresh dashboard stats
                    
                    QMessageBox.information(
                        self,
                        self.language_manager.translate('common.success'),
                        self.language_manager.translate('machine.add_success')
                    )
            except Exception as e:
                logger.error(f"Failed to add machine: {str(e)}")
                QMessageBox.critical(
                    self,
                    self.language_manager.translate('common.error'),
                    str(e)
                )
    
    def _add_operator(self):
        """Open dialog to add a new operator."""
        dialog = OperatorDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            try:
                with self.db_manager.get_session() as session:
                    operator_data = dialog.get_operator_data()
                    operator = Operator(**operator_data)
                    session.add(operator)
                    session.commit()
                    
                    logger.info(f"Added new operator: {operator.name}")
                    self._load_stats()  # Refresh dashboard stats
                    
                    QMessageBox.information(
                        self,
                        self.language_manager.translate('common.success'),
                        self.language_manager.translate('operator.add_success')
                    )
            except Exception as e:
                logger.error(f"Failed to add operator: {str(e)}")
                QMessageBox.critical(
                    self,
                    self.language_manager.translate('common.error'),
                    str(e)
                ) 
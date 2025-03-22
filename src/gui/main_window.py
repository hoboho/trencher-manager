from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor
from src.gui.styles import DARK_THEME, LIGHT_THEME
from src.gui.projects_widget import ProjectsWidget
from src.gui.machines_widget import MachinesWidget
from src.gui.operators_widget import OperatorsWidget
from src.gui.dashboard_widget import DashboardWidget
from src.gui.settings_widget import SettingsWidget
from src.gui.finance_widget import FinanceWidget
from src.gui.reports_widget import ReportsWidget
from src.utils.logger import setup_logger
from src.utils.language_manager import LanguageManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()
        self.language_manager.language_changed.connect(self._on_language_changed)
        self.setWindowTitle("Terencher - Project Management System")
        self.setMinimumSize(800, 600)
        self._init_ui()
    
    def _on_language_changed(self, language):
        """Handle language change event by updating all UI elements."""
        logger.info(f"Updating main window UI for language: {language}")
        
        # Update window title
        self.setWindowTitle(self.language_manager.translate('app.title'))
        
        # Update sidebar title
        self.sidebar_title.setText(self.language_manager.translate('app.name'))
        
        # Update navigation buttons
        for btn, section in self.nav_buttons:
            btn.setText(self.language_manager.translate(f'nav.{section}'))
        
        # Update content widgets
        for widget in self.content_widgets.values():
            if hasattr(widget, '_on_language_changed'):
                widget._on_language_changed(language)
        
        logger.info("Main window UI update complete")
    
    def _init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create content area
        content_area = QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content_area.setObjectName("content-area")
        
        # Create content container
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Initialize content widgets
        self._init_content_widgets(content_layout)
        
        content_area.setWidget(content_container)
        main_layout.addWidget(content_area)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Sidebar
        main_layout.setStretch(1, 4)  # Content area
    
    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(200)
        sidebar.setMaximumWidth(300)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title
        title_container = QWidget()
        title_container.setObjectName("sidebar-title")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        self.sidebar_title = QLabel(self.language_manager.translate('app.name'))
        self.sidebar_title.setObjectName("sidebar-title-text")
        title_layout.addWidget(self.sidebar_title)
        
        layout.addWidget(title_container)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_sections = [
            ("dashboard", "dashboard"),
            ("projects", "projects"),
            ("machines", "machines"),
            ("operators", "operators"),
            ("financial", "financial"),
            ("reports", "reports"),
            ("settings", "settings")
        ]
        
        for section, section_id in nav_sections:
            btn = QPushButton(self.language_manager.translate(f'nav.{section_id}'))
            btn.setObjectName("nav-button")
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, s=section: self._show_section(s))
            layout.addWidget(btn)
            self.nav_buttons.append((btn, section_id))
        
        layout.addStretch()
        
        return sidebar
    
    def _init_content_widgets(self, layout):
        # Initialize database session
        engine = create_engine('sqlite:///terencher.db')
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Initialize all content widgets
        self.content_widgets = {}
        
        # Dashboard
        self.content_widgets['dashboard'] = DashboardWidget()
        layout.addWidget(self.content_widgets['dashboard'])
        
        # Projects
        self.content_widgets['projects'] = ProjectsWidget()
        layout.addWidget(self.content_widgets['projects'])
        
        # Machines
        self.content_widgets['machines'] = MachinesWidget()
        layout.addWidget(self.content_widgets['machines'])
        
        # Operators
        self.content_widgets['operators'] = OperatorsWidget()
        layout.addWidget(self.content_widgets['operators'])
        
        # Finance
        self.content_widgets['financial'] = FinanceWidget(session)
        layout.addWidget(self.content_widgets['financial'])
        
        # Reports
        self.content_widgets['reports'] = ReportsWidget(session)
        layout.addWidget(self.content_widgets['reports'])
        
        # Settings
        self.content_widgets['settings'] = SettingsWidget()
        layout.addWidget(self.content_widgets['settings'])
        
        # Hide all widgets initially
        for widget in self.content_widgets.values():
            widget.hide()
        
        # Show dashboard by default
        self._show_section('dashboard')
    
    def _show_section(self, section):
        """Show the selected section and hide others."""
        for s, widget in self.content_widgets.items():
            widget.setVisible(s == section)
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.property("theme")
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.set_theme(new_theme)
        logger.info(f"Theme changed to: {new_theme}")
    
    def set_theme(self, theme):
        """Set the application theme."""
        self.setProperty("theme", theme)
        stylesheet = DARK_THEME if theme == 'dark' else LIGHT_THEME
        self.setStyleSheet(stylesheet)
        
        # Update palette
        palette = QPalette()
        if theme == 'dark':
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        self.setPalette(palette) 
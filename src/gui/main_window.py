from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPalette, QColor
from .styles import DARK_THEME, LIGHT_THEME
from .projects_widget import ProjectsWidget
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terencher - Trencher Management System")
        self.setMinimumSize(1200, 800)
        
        # Initialize UI components
        self._init_ui()
        
        # Set theme (default to light theme)
        self.set_theme('light')
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize the user interface components."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create main content area
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Sidebar
        main_layout.setStretch(1, 4)  # Content area
        
        # Initialize content widgets
        self._init_content_widgets()
    
    def _create_sidebar(self):
        """Create the sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo/Title area
        title_frame = QFrame()
        title_frame.setObjectName("sidebar-title")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Terencher")
        title_label.setObjectName("sidebar-title-text")
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_frame)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Projects", "projects"),
            ("Machines", "machines"),
            ("Operators", "operators"),
            ("Financial", "financial"),
            ("Reports", "reports"),
            ("Settings", "settings")
        ]
        
        for text, name in nav_items:
            btn = QPushButton(text)
            btn.setObjectName(f"nav-{name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self._handle_navigation(n))
            layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        # Add stretch to push buttons to the top
        layout.addStretch()
        
        # Theme toggle button at the bottom
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setObjectName("theme-toggle")
        theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(theme_btn)
        
        return sidebar
    
    def _init_content_widgets(self):
        """Initialize all content widgets."""
        # Create placeholder widgets for each section
        self.content_widgets = {}
        
        # Projects widget
        self.content_widgets['projects'] = ProjectsWidget()
        self.content_area.addWidget(self.content_widgets['projects'])
        
        # Placeholder widgets for other sections
        for section in ['dashboard', 'machines', 'operators', 'financial', 'reports', 'settings']:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            label = QLabel(f"{section.title()} Section - Coming Soon")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            self.content_widgets[section] = placeholder
            self.content_area.addWidget(placeholder)
    
    def _handle_navigation(self, section):
        """Handle navigation button clicks."""
        # Update button states
        for name, btn in self.nav_buttons.items():
            btn.setChecked(name == section)
        
        # Show corresponding content
        if section in self.content_widgets:
            self.content_area.setCurrentWidget(self.content_widgets[section])
            logger.info(f"Navigating to section: {section}")
    
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
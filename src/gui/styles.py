# Light theme stylesheet
LIGHT_THEME = """
QMainWindow {
    background-color: #ffffff;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #333333;
}

#sidebar {
    background-color: #f0f0f0;
    border-right: 1px solid #d0d0d0;
}

#sidebar-title {
    background-color: #e0e0e0;
    padding: 20px;
    border-bottom: 1px solid #d0d0d0;
}

#sidebar-title-text {
    font-size: 24px;
    font-weight: bold;
    color: #333333;
}

QPushButton {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #0078d4;
    color: white;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:checked {
    background-color: #106ebe;
}

#nav-dashboard, #nav-projects, #nav-machines, #nav-operators, #nav-financial, #nav-reports, #nav-settings {
    text-align: left;
    padding-left: 20px;
    margin: 2px 10px;
}

#theme-toggle {
    background-color: #e0e0e0;
    color: #333333;
    margin: 10px;
}

#theme-toggle:hover {
    background-color: #d0d0d0;
}

QTableWidget {
    border: 1px solid #d0d0d0;
    gridline-color: #f0f0f0;
    background-color: white;
    alternate-background-color: #f9f9f9;
}

QTableWidget::item {
    padding: 5px;
    color: #333333;
}

QTableWidget::item:selected {
    background-color: #0078d4;
    color: white;
}

QHeaderView::section {
    background-color: #f0f0f0;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #d0d0d0;
    font-weight: bold;
    color: #333333;
}

QLineEdit {
    padding: 5px;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
    color: #333333;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QMessageBox {
    background-color: white;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QLabel {
    color: #333333;
}
"""

# Dark theme stylesheet
DARK_THEME = """
QMainWindow {
    background-color: #2d2d2d;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #ffffff;
}

#sidebar {
    background-color: #1e1e1e;
    border-right: 1px solid #3d3d3d;
}

#sidebar-title {
    background-color: #252525;
    padding: 20px;
    border-bottom: 1px solid #3d3d3d;
}

#sidebar-title-text {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}

QPushButton {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #0078d4;
    color: white;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:checked {
    background-color: #106ebe;
}

#nav-dashboard, #nav-projects, #nav-machines, #nav-operators, #nav-financial, #nav-reports, #nav-settings {
    text-align: left;
    padding-left: 20px;
    margin: 2px 10px;
    background-color: transparent;
}

#theme-toggle {
    background-color: #3d3d3d;
    color: #ffffff;
    margin: 10px;
}

#theme-toggle:hover {
    background-color: #4d4d4d;
}

QTableWidget {
    border: 1px solid #3d3d3d;
    gridline-color: #2d2d2d;
    background-color: #2d2d2d;
    alternate-background-color: #252525;
}

QTableWidget::item {
    padding: 5px;
    color: #ffffff;
}

QTableWidget::item:selected {
    background-color: #0078d4;
    color: white;
}

QHeaderView::section {
    background-color: #1e1e1e;
    padding: 5px;
    border: none;
    border-bottom: 1px solid #3d3d3d;
    font-weight: bold;
    color: #ffffff;
}

QLineEdit {
    padding: 5px;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #2d2d2d;
    color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QMessageBox {
    background-color: #2d2d2d;
}

QMessageBox QPushButton {
    min-width: 80px;
}

QLabel {
    color: #ffffff;
}
""" 
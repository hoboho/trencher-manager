# Light theme styles
LIGHT_THEME = """
QMainWindow {
    background-color: #ffffff;
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
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    background-color: #f0f0f0;
    color: #333333;
    text-align: left;
}

QPushButton:hover {
    background-color: #e0e0e0;
}

QPushButton:checked {
    background-color: #0078d7;
    color: white;
}

#theme-toggle {
    margin: 10px;
    padding: 8px;
    border-radius: 4px;
    background-color: #e0e0e0;
    color: #333333;
}

#theme-toggle:hover {
    background-color: #d0d0d0;
}

QTableWidget {
    border: 1px solid #d0d0d0;
    gridline-color: #e0e0e0;
    background-color: white;
    alternate-background-color: #f8f8f8;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #0078d7;
    color: white;
}

QHeaderView::section {
    background-color: #f0f0f0;
    padding: 5px;
    border: 1px solid #d0d0d0;
    font-weight: bold;
}

QLineEdit {
    padding: 5px;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QLineEdit:focus {
    border: 1px solid #0078d7;
}

QLabel {
    color: #333333;
}

QComboBox {
    padding: 5px;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #333333;
}

QMessageBox QPushButton {
    padding: 5px 15px;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: #f0f0f0;
    color: #333333;
    text-align: center;
}

QMessageBox QPushButton:hover {
    background-color: #e0e0e0;
}
"""

# Dark theme styles
DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
}

#sidebar {
    background-color: #333333;
    border-right: 1px solid #404040;
}

#sidebar-title {
    background-color: #404040;
    padding: 20px;
    border-bottom: 1px solid #505050;
}

#sidebar-title-text {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
}

QPushButton {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    background-color: #333333;
    color: #ffffff;
    text-align: left;
}

QPushButton:hover {
    background-color: #404040;
}

QPushButton:checked {
    background-color: #0078d7;
    color: white;
}

#theme-toggle {
    margin: 10px;
    padding: 8px;
    border-radius: 4px;
    background-color: #404040;
    color: #ffffff;
}

#theme-toggle:hover {
    background-color: #505050;
}

QTableWidget {
    border: 1px solid #404040;
    gridline-color: #333333;
    background-color: #2b2b2b;
    alternate-background-color: #333333;
}

QTableWidget::item {
    padding: 5px;
    color: #ffffff;
}

QTableWidget::item:selected {
    background-color: #0078d7;
    color: white;
}

QHeaderView::section {
    background-color: #333333;
    padding: 5px;
    border: 1px solid #404040;
    font-weight: bold;
    color: #ffffff;
}

QLineEdit {
    padding: 5px;
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #333333;
    color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #0078d7;
}

QLabel {
    color: #ffffff;
}

QComboBox {
    padding: 5px;
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #333333;
    color: #ffffff;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QMessageBox {
    background-color: #2b2b2b;
}

QMessageBox QLabel {
    color: #ffffff;
}

QMessageBox QPushButton {
    padding: 5px 15px;
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #333333;
    color: #ffffff;
    text-align: center;
}

QMessageBox QPushButton:hover {
    background-color: #404040;
}
""" 
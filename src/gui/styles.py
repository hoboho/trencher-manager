# Light theme stylesheet
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
}

#sidebar {
    background-color: #2c3e50;
    border-right: 1px solid #34495e;
}

#sidebar-title {
    background-color: #243342;
    padding: 10px;
}

#sidebar-title-text {
    color: white;
    font-size: 20px;
    font-weight: bold;
}

#nav-button {
    background-color: transparent;
    border: none;
    color: #ecf0f1;
    text-align: left;
    padding: 10px 20px;
    font-size: 14px;
}

#nav-button:hover {
    background-color: #34495e;
}

#content-area {
    background-color: #f5f5f5;
    border: none;
}

#section-title {
    color: #2c3e50;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

#stat-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    margin: 5px;
}

#stat-title {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 5px;
}

#stat-value {
    color: #2c3e50;
    font-size: 24px;
    font-weight: bold;
}

#activities-list {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
}

#activity-item {
    color: #2c3e50;
    font-size: 14px;
    padding: 8px 0;
    border-bottom: 1px solid #ecf0f1;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #2472a4;
}

QScrollBar:vertical {
    border: none;
    background-color: #f5f5f5;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}
"""

# Dark theme stylesheet
DARK_THEME = """
QMainWindow {
    background-color: #1a1a1a;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
}

#sidebar {
    background-color: #2c3e50;
    border-right: 1px solid #34495e;
}

#sidebar-title {
    background-color: #243342;
    padding: 10px;
}

#sidebar-title-text {
    color: white;
    font-size: 20px;
    font-weight: bold;
}

#nav-button {
    background-color: transparent;
    border: none;
    color: #ecf0f1;
    text-align: left;
    padding: 10px 20px;
    font-size: 14px;
}

#nav-button:hover {
    background-color: #34495e;
}

#content-area {
    background-color: #1a1a1a;
    border: none;
}

#section-title {
    color: #ecf0f1;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

#stat-card {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 15px;
    margin: 5px;
}

#stat-title {
    color: #bdc3c7;
    font-size: 14px;
    margin-bottom: 5px;
}

#stat-value {
    color: #ecf0f1;
    font-size: 24px;
    font-weight: bold;
}

#activities-list {
    background-color: #2c3e50;
    border-radius: 8px;
    padding: 15px;
}

#activity-item {
    color: #ecf0f1;
    font-size: 14px;
    padding: 8px 0;
    border-bottom: 1px solid #34495e;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #2472a4;
}

QScrollBar:vertical {
    border: none;
    background-color: #1a1a1a;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #34495e;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #2c3e50;
}
""" 
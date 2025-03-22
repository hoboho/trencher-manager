import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.database.database import DatabaseManager

def main():
    app = QApplication(sys.argv)
    
    # Initialize database
    db = DatabaseManager()
    db.initialize()  # Initialize without password for now
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
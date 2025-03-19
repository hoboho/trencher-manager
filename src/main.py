import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from database.database import DatabaseManager
from database.models import Base
from gui.main_window import MainWindow
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main application entry point."""
    try:
        # Initialize Qt application
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize()  # TODO: Add password parameter for encryption
        
        # Create database tables
        with db_manager.get_session() as session:
            Base.metadata.create_all(db_manager.engine)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
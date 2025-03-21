from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_database():
    """Clean all data from the database tables while preserving structure."""
    # Get the absolute path to the database file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    db_path = os.path.join(project_root, "data", "terencher.db")
    
    logger.info(f"Cleaning database at: {db_path}")
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at: {db_path}")
        return
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        with engine.connect() as connection:
            # Disable foreign key checks temporarily
            connection.execute(text("PRAGMA foreign_keys = OFF;"))
            
            # Clean all tables
            tables = [
                "projects", "operators", "machines", "project_operators",
                "project_machines", "project_work_logs", "operator_work_logs",
                "machine_work_logs", "project_expenses", "operator_expenses",
                "machine_expenses", "project_payments", "operator_payments",
                "machine_payments", "project_photos", "project_documents",
                "project_notes", "operator_notes", "machine_notes",
                "project_attachments", "operator_attachments", "machine_attachments"
            ]
            
            for table in tables:
                try:
                    connection.execute(text(f"DELETE FROM {table};"))
                    logger.info(f"Cleaned table: {table}")
                except Exception as e:
                    logger.warning(f"Could not clean table {table}: {str(e)}")
            
            # Reset auto-increment counters
            connection.execute(text("DELETE FROM sqlite_sequence;"))
            
            # Re-enable foreign key checks
            connection.execute(text("PRAGMA foreign_keys = ON;"))
            
            connection.commit()
            logger.info("Successfully cleaned all tables in the database")
            
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    clean_database() 
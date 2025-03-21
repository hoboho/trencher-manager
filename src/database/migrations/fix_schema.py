from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_schema():
    """Fix the database schema to match the models."""
    # Get the absolute path to the database file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    db_path = os.path.join(project_root, "terencher.db")
    
    logger.info(f"Fixing schema for database at: {db_path}")
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at: {db_path}")
        return
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        with engine.connect() as connection:
            # Disable foreign key checks temporarily
            connection.execute(text("PRAGMA foreign_keys = OFF;"))
            
            # Fix projects table
            connection.execute(text("""
                CREATE TABLE projects_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contract_amount FLOAT NOT NULL,
                    received_amount FLOAT DEFAULT 0.0,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    status TEXT DEFAULT 'active',
                    total_length FLOAT,
                    average_depth FLOAT,
                    average_width FLOAT,
                    description TEXT,
                    client_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Copy data from old table to new table
            connection.execute(text("""
                INSERT INTO projects_new (
                    id, name, contract_amount, received_amount, start_date,
                    end_date, status, total_length, average_depth, average_width,
                    created_at
                )
                SELECT 
                    id, name, contract_amount, received_amount, start_date,
                    end_date, status, total_length, average_depth, average_width,
                    created_at
                FROM projects;
            """))
            
            # Drop old table and rename new table
            connection.execute(text("DROP TABLE projects;"))
            connection.execute(text("ALTER TABLE projects_new RENAME TO projects;"))
            
            # Fix operators table
            connection.execute(text("""
                CREATE TABLE operators_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hourly_rate FLOAT NOT NULL,
                    overtime_rate FLOAT NOT NULL,
                    overtime_threshold FLOAT DEFAULT 8.0,
                    contract_type TEXT DEFAULT 'hourly' NOT NULL,
                    rate FLOAT DEFAULT 0.0 NOT NULL,
                    status TEXT DEFAULT 'active',
                    contact TEXT,
                    skills TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Copy data from old table to new table
            connection.execute(text("""
                INSERT INTO operators_new (
                    id, name, hourly_rate, overtime_rate, overtime_threshold,
                    created_at
                )
                SELECT 
                    id, name, hourly_rate, overtime_rate, overtime_threshold,
                    created_at
                FROM operators;
            """))
            
            # Drop old table and rename new table
            connection.execute(text("DROP TABLE operators;"))
            connection.execute(text("ALTER TABLE operators_new RENAME TO operators;"))
            
            # Re-enable foreign key checks
            connection.execute(text("PRAGMA foreign_keys = ON;"))
            
            connection.commit()
            logger.info("Successfully fixed database schema")
            
    except Exception as e:
        logger.error(f"Error during schema fix: {str(e)}")
        raise

if __name__ == "__main__":
    fix_schema() 
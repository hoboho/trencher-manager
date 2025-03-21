from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add new fields to projects and operators tables."""
    # Get the absolute path to the database file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    db_path = os.path.join(project_root, "data", "terencher.db")
    
    logger.info(f"Running migration on database: {db_path}")
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at: {db_path}")
        return
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        with engine.connect() as connection:
            # Create new projects table with additional columns
            connection.execute(text("""
                CREATE TABLE projects_new (
                    id INTEGER NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    contract_amount FLOAT NOT NULL,
                    received_amount FLOAT,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME,
                    status VARCHAR(20),
                    created_at DATETIME,
                    client_name TEXT,
                    description TEXT,
                    PRIMARY KEY (id)
                );
            """))
            
            # Copy data from old table to new table
            connection.execute(text("""
                INSERT INTO projects_new (
                    id, name, contract_amount, received_amount, start_date,
                    end_date, status, created_at, client_name, description
                )
                SELECT 
                    id, name, contract_amount, received_amount, start_date,
                    end_date, status, created_at, client_name, description
                FROM projects;
            """))
            
            # Drop old table and rename new table
            connection.execute(text("DROP TABLE projects;"))
            connection.execute(text("ALTER TABLE projects_new RENAME TO projects;"))
            
            # Create new operators table with additional columns
            connection.execute(text("""
                CREATE TABLE operators_new (
                    id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    contract_type VARCHAR(20) NOT NULL,
                    rate FLOAT NOT NULL,
                    status VARCHAR(20),
                    created_at DATETIME,
                    contact TEXT,
                    skills TEXT,
                    notes TEXT,
                    PRIMARY KEY (id)
                );
            """))
            
            # Copy data from old table to new table
            connection.execute(text("""
                INSERT INTO operators_new (
                    id, name, contract_type, rate, status, created_at,
                    contact, skills, notes
                )
                SELECT 
                    id, name, contract_type, rate, status, created_at,
                    contact, skills, notes
                FROM operators;
            """))
            
            # Drop old table and rename new table
            connection.execute(text("DROP TABLE operators;"))
            connection.execute(text("ALTER TABLE operators_new RENAME TO operators;"))
            
            connection.commit()
            logger.info("Successfully added new columns to projects and operators tables")
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration() 
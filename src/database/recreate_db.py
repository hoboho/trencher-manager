from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
import os
import logging
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_database():
    """Recreate the database from scratch using SQLAlchemy models."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'terencher.db')
    
    logger.info(f"Recreating database at: {db_path}")
    
    # Create engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        # Drop all tables
        Base.metadata.drop_all(engine)
        logger.info("Dropped all existing tables")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Created all tables successfully")
        
        # Verify tables
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            logger.info(f"Available tables: {tables}")
            
    except Exception as e:
        logger.error(f"Error recreating database: {str(e)}")
        raise

if __name__ == '__main__':
    recreate_database() 
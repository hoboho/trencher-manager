import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run all database migrations."""
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files in the migrations directory
    migration_files = [f for f in os.listdir(migrations_dir) 
                      if f.endswith('.py') and f != '__init__.py' and f != 'run_migrations.py']
    
    for migration_file in migration_files:
        logger.info(f"Running migration: {migration_file}")
        try:
            # Import and run the migration
            module_name = os.path.splitext(migration_file)[0]
            module = __import__(module_name, fromlist=['run_migration'])
            module.run_migration()
        except Exception as e:
            logger.error(f"Error running migration {migration_file}: {str(e)}")
            sys.exit(1)
    
    logger.info("All migrations completed successfully")

if __name__ == "__main__":
    run_migrations() 
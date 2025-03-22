import os
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlcipher3 import dbapi2 as sqlite3
from src.utils.logger import setup_logger
from src.database.models import Base

logger = setup_logger(__name__)

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.engine = None
        self.Session = None
        # Use project root directory for database
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'terencher.db')
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure database and backup directories exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def initialize(self, password=None):
        """Initialize database connection with optional encryption."""
        try:
            if password:
                # Use SQLCipher for encrypted database
                self.engine = create_engine(
                    f'sqlite+pysqlcipher:///{self.db_path}',
                    connect_args={'key': password},
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10
                )
            else:
                # Use regular SQLite for unencrypted database
                self.engine = create_engine(
                    f'sqlite:///{self.db_path}',
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10
                )
            
            # Enable foreign key support
            with self.engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=ON"))
                conn.commit()
            
            self.Session = sessionmaker(bind=self.engine)
            
            # Create all tables
            try:
                Base.metadata.create_all(self.engine)
                logger.info("Database tables created successfully")
            except Exception as e:
                logger.error(f"Failed to create database tables: {str(e)}")
                # Try to recreate tables if creation fails
                self.recreate_tables()
            
            # Verify tables were created
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                logger.info(f"Available tables: {tables}")
            
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def recreate_tables(self):
        """Drop and recreate all tables."""
        try:
            Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            logger.info("Database tables recreated successfully")
        except Exception as e:
            logger.error(f"Failed to recreate database tables: {str(e)}")
            raise
    
    def get_session(self):
        """Get a new database session."""
        if not self.Session:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.Session()
    
    def backup_database(self):
        """Create a backup of the database."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f'terencher_backup_{timestamp}.db')
            
            # Close all connections before backup
            if self.engine:
                self.engine.dispose()
            
            # Create backup
            with open(self.db_path, 'rb') as source:
                with open(backup_path, 'wb') as target:
                    target.write(source.read())
            
            logger.info(f"Database backup created successfully at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create database backup: {str(e)}")
            raise
    
    def cleanup_old_backups(self, max_backups=5):
        """Remove old backups, keeping only the most recent ones."""
        try:
            backups = sorted([
                f for f in os.listdir(self.backup_dir)
                if f.startswith('terencher_backup_') and f.endswith('.db')
            ])
            
            while len(backups) > max_backups:
                oldest_backup = backups.pop(0)
                os.remove(os.path.join(self.backup_dir, oldest_backup))
                logger.info(f"Removed old backup: {oldest_backup}")
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            raise
    
    def verify_database(self):
        """Verify database integrity."""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            logger.info("Database integrity verified successfully")
            return True
        except Exception as e:
            logger.error(f"Database integrity check failed: {str(e)}")
            return False 
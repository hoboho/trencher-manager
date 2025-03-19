import unittest
from src.database.database import DatabaseManager
from src.database.models import Base, Project

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database."""
        self.db_manager = DatabaseManager()
        self.db_manager.initialize()
        
    def tearDown(self):
        """Clean up after tests."""
        if self.db_manager.engine:
            self.db_manager.engine.dispose()
    
    def test_database_initialization(self):
        """Test if database can be initialized."""
        self.assertIsNotNone(self.db_manager.engine)
        self.assertIsNotNone(self.db_manager.Session)
    
    def test_create_tables(self):
        """Test if tables can be created."""
        with self.db_manager.get_session() as session:
            Base.metadata.create_all(self.db_manager.engine)
            # If we get here without errors, the test passes

if __name__ == '__main__':
    unittest.main() 
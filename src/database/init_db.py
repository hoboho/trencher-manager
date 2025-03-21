import sqlite3
import os

def init_db():
    """Initialize the database with all required tables."""
    # Get the project root directory (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'terencher.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create machines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT,
                purchase_date DATE,
                purchase_price FLOAT,
                fuel_consumption_rate FLOAT,
                fuel_cost_per_liter FLOAT,
                maintenance_cost_per_hour FLOAT,
                trenching_depth FLOAT,
                trenching_width FLOAT,
                maximum_speed FLOAT,
                weight FLOAT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create operators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hourly_rate FLOAT NOT NULL,
                overtime_rate FLOAT NOT NULL,
                overtime_threshold FLOAT DEFAULT 8.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create machine_projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machine_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                machine_id INTEGER,
                start_date DATE NOT NULL,
                end_date DATE,
                hours_used FLOAT DEFAULT 0.0,
                completed_length FLOAT DEFAULT 0.0,
                average_depth FLOAT,
                average_width FLOAT,
                average_speed FLOAT,
                FOREIGN KEY (machine_id) REFERENCES machines (id),
                FOREIGN KEY (project_id) REFERENCES projects (id),
                UNIQUE (project_id, machine_id)
            );
        """)
        
        # Create operator_projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operator_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                operator_id INTEGER,
                start_date DATE NOT NULL,
                end_date DATE,
                hours_worked FLOAT DEFAULT 0.0,
                completed_length FLOAT DEFAULT 0.0,
                FOREIGN KEY (operator_id) REFERENCES operators (id),
                FOREIGN KEY (project_id) REFERENCES projects (id),
                UNIQUE (project_id, operator_id)
            );
        """)
        
        # Create machine_costs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machine_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                cost_type TEXT NOT NULL,
                amount FLOAT NOT NULL,
                date TIMESTAMP NOT NULL,
                description TEXT,
                FOREIGN KEY (machine_id) REFERENCES machines (id),
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
        """)
        
        # Create payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                recipient_type TEXT NOT NULL,
                recipient_id INTEGER NOT NULL,
                amount FLOAT NOT NULL,
                payment_date TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                description TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
        """)
        
        # Create project_expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                amount FLOAT NOT NULL,
                category TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
        """)
        
        conn.commit()
        print("Database initialized successfully!")
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db() 
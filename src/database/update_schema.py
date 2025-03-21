import sqlite3
import os

def update_schema():
    """Update the database schema to add new columns."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'terencher.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns to projects table
        cursor.execute("""
            ALTER TABLE projects 
            ADD COLUMN total_length FLOAT;
        """)
        
        cursor.execute("""
            ALTER TABLE projects 
            ADD COLUMN average_depth FLOAT;
        """)
        
        cursor.execute("""
            ALTER TABLE projects 
            ADD COLUMN average_width FLOAT;
        """)
        
        # Add new columns to machine_projects table
        cursor.execute("""
            ALTER TABLE machine_projects 
            ADD COLUMN completed_length FLOAT DEFAULT 0.0;
        """)
        
        cursor.execute("""
            ALTER TABLE machine_projects 
            ADD COLUMN average_depth FLOAT;
        """)
        
        cursor.execute("""
            ALTER TABLE machine_projects 
            ADD COLUMN average_width FLOAT;
        """)
        
        cursor.execute("""
            ALTER TABLE machine_projects 
            ADD COLUMN average_speed FLOAT;
        """)
        
        # Add new column to operator_projects table
        cursor.execute("""
            ALTER TABLE operator_projects 
            ADD COLUMN completed_length FLOAT DEFAULT 0.0;
        """)
        
        conn.commit()
        print("Database schema updated successfully!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columns already exist, skipping...")
        else:
            print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_schema() 
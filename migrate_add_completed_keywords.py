#!/usr/bin/env python3
"""Migration script to add completed_keywords column to jobs table."""
import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


def migrate_database():
    """Add completed_keywords column to jobs table if it doesn't exist."""
    # Extract database path from SQLAlchemy URL
    db_url = settings.database_url
    
    if "sqlite" not in db_url:
        print("This migration script only supports SQLite databases.")
        print(f"Database URL: {db_url}")
        return False
    
    # Extract file path from sqlite:///path/to/db
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    elif db_url.startswith("sqlite://"):
        db_path = db_url.replace("sqlite://", "")
    else:
        print(f"Could not parse database URL: {db_url}")
        return False
    
    db_file = Path(db_path)
    
    if not db_file.exists():
        print(f"Database file not found: {db_file}")
        return False
    
    print(f"Connecting to database: {db_file}")
    
    try:
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "completed_keywords" in columns:
            print("Column 'completed_keywords' already exists. Migration not needed.")
            conn.close()
            return True
        
        print("Adding 'completed_keywords' column to jobs table...")
        
        # Add the column
        cursor.execute("""
            ALTER TABLE jobs 
            ADD COLUMN completed_keywords TEXT
        """)
        
        conn.commit()
        conn.close()
        
        print("Migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)


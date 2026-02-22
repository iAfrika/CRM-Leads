#!/usr/bin/env python
"""
Script to remove UNIQUE constraint from people_person.email field in SQLite database
"""
import sqlite3
import os
import glob

def fix_database(db_path):
    """Remove UNIQUE constraint from email field in people_person table"""
    print(f"Processing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='people_person'")
        if not cursor.fetchone():
            print(f"  Table 'people_person' not found, skipping...")
            return
        
        # Get current schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='people_person'")
        result = cursor.fetchone()
        if not result:
            print(f"  Cannot get schema, skipping...")
            return
            
        current_schema = result[0]
        
        # Check if UNIQUE constraint exists
        if 'UNIQUE' not in current_schema.upper() or '"email"' not in current_schema:
            print(f"  No UNIQUE constraint on email field, skipping...")
            return
        
        print(f"  Found UNIQUE constraint, removing...")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create new table without UNIQUE constraint
        cursor.execute("""
            CREATE TABLE "people_person_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "first_name" varchar(100) NOT NULL,
                "last_name" varchar(100) NOT NULL,
                "email" varchar(254) NOT NULL,
                "phone" varchar(20) NULL,
                "telegram_username" varchar(100) NULL,
                "address" text NULL,
                "profile_picture" varchar(100) NULL,
                "date_registered" datetime NOT NULL,
                "registered_by_id" integer NULL
            )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO people_person_new 
            SELECT * FROM people_person
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE people_person")
        
        # Rename new table
        cursor.execute("ALTER TABLE people_person_new RENAME TO people_person")
        
        # Commit transaction
        conn.commit()
        print(f"  ✓ Successfully removed UNIQUE constraint from email field")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Fix main database
    if os.path.exists('db.sqlite3'):
        fix_database('db.sqlite3')
    
    # Fix all company databases
    company_db_dir = 'company_databases'
    if os.path.exists(company_db_dir):
        for db_file in glob.glob(f'{company_db_dir}/*.db'):
            fix_database(db_file)
    
    print("\nDone!")

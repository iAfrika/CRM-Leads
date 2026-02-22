#!/usr/bin/env python
"""
Script to properly remove auth_user foreign key constraints from leads tables
"""
import sqlite3
import glob
from pathlib import Path

def fix_leads_table(db_path):
    """Remove auth_user FK constraints from leads_lead table"""
    print(f"Processing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if leads_lead table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads_lead'")
        if not cursor.fetchone():
            print(f"  No leads_lead table found, skipping...")
            return
        
        # Check current schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='leads_lead'")
        current_schema = cursor.fetchone()[0]
        
        if 'REFERENCES "auth_user"' not in current_schema:
            print(f"  Already fixed, skipping...")
            return
        
        print(f"  Fixing leads_lead table...")
        
        # Begin transaction
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("BEGIN TRANSACTION")
        
        # Create new table WITHOUT auth_user FK constraints
        cursor.execute("""
            CREATE TABLE "leads_lead_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "company_name" varchar(200) NOT NULL,
                "contact_person" varchar(200) NOT NULL,
                "email" varchar(254) NOT NULL,
                "phone" varchar(20) NOT NULL,
                "website" varchar(200) NULL,
                "description" text NOT NULL,
                "requirements" text NOT NULL,
                "estimated_value" decimal NULL,
                "status" varchar(20) NOT NULL,
                "source" varchar(20) NOT NULL,
                "priority" varchar(20) NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "next_follow_up" datetime NULL,
                "tags" varchar(200) NOT NULL,
                "notes_text" text NOT NULL,
                "created_by_id" integer NULL,
                "modified_by_id" integer NULL,
                "assigned_to_id" bigint NULL REFERENCES "people_person" ("id") DEFERRABLE INITIALLY DEFERRED,
                "converted_to_client_id" bigint NULL REFERENCES "clients_client" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        """)
        
        # Copy data
        cursor.execute("""
            INSERT INTO leads_lead_new 
            SELECT id, title, company_name, contact_person, email, phone, website,
                   description, requirements, estimated_value, status, source, priority,
                   created_at, updated_at, next_follow_up, tags, notes_text,
                   created_by_id, modified_by_id, assigned_to_id, converted_to_client_id
            FROM leads_lead
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE leads_lead")
        
        # Rename new table
        cursor.execute("ALTER TABLE leads_lead_new RENAME TO leads_lead")
        
        # Recreate indexes
        cursor.execute('CREATE INDEX "leads_lead_assigned_to_id_idx" ON "leads_lead" ("assigned_to_id")')
        cursor.execute('CREATE INDEX "leads_lead_converted_to_client_id_idx" ON "leads_lead" ("converted_to_client_id")')
        
        # Commit transaction
        conn.commit()
        cursor.execute("PRAGMA foreign_keys=ON")
        print(f"  ✓ Successfully fixed")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    # Fix all company databases
    company_db_dir = Path('company_databases')
    if company_db_dir.exists():
        for db_file in company_db_dir.glob('*.db'):
            fix_leads_table(db_file)
    
    print("\nDone!")

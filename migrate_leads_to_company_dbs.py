#!/usr/bin/env python
"""
Script to apply the leads migration to all company databases using raw SQL
"""
import sqlite3
import glob
from pathlib import Path

def migrate_leads_tables(db_path):
    """Apply the leads model changes to a database"""
    print(f"Processing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if leads_lead table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads_lead'")
        if not cursor.fetchone():
            print(f"  No leads_lead table found, skipping...")
            return
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if old columns exist
        cursor.execute("PRAGMA table_info(leads_lead)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'created_by_id' in columns and 'modified_by_id' in columns:
            print(f"  Already migrated, skipping...")
            return
        
        print(f"  Applying migration...")
        
        # Create new leads_lead table
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
                "created_by_id" integer NULL,
                "modified_by_id" integer NULL,
                "tags" varchar(200) NOT NULL,
                "notes_text" text NOT NULL,
                "assigned_to_id" bigint NULL REFERENCES "people_person" ("id") DEFERRABLE INITIALLY DEFERRED,
                "converted_to_client_id" bigint NULL REFERENCES "clients_client" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        """)
        
        # Copy data from old table
        cursor.execute("""
            INSERT INTO leads_lead_new 
            SELECT id, title, company_name, contact_person, email, phone, website,
                   description, requirements, estimated_value, status, source, priority,
                   created_at, updated_at, next_follow_up,
                   created_by_id, modified_by_id,
                   tags, notes_text, assigned_to_id, converted_to_client_id
            FROM leads_lead
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE leads_lead")
        
        # Rename new table
        cursor.execute("ALTER TABLE leads_lead_new RENAME TO leads_lead")
        
        # Create indexes
        cursor.execute('CREATE INDEX "leads_lead_assigned_to_id_idx" ON "leads_lead" ("assigned_to_id")')
        cursor.execute('CREATE INDEX "leads_lead_converted_to_client_id_idx" ON "leads_lead" ("converted_to_client_id")')
        
        # Migrate LeadActivity table
        cursor.execute("PRAGMA table_info(leads_leadactivity)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'created_by_id' not in columns:
            cursor.execute("""
                CREATE TABLE "leads_leadactivity_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "activity_type" varchar(20) NOT NULL,
                    "description" text NOT NULL,
                    "created_at" datetime NOT NULL,
                    "created_by_id" integer NULL,
                    "due_date" datetime NULL,
                    "is_completed" bool NOT NULL,
                    "completed_at" datetime NULL,
                    "lead_id" bigint NOT NULL REFERENCES "leads_lead" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            
            cursor.execute("""
                INSERT INTO leads_leadactivity_new 
                SELECT id, activity_type, description, created_at, created_by_id,
                       due_date, is_completed, completed_at, lead_id
                FROM leads_leadactivity
            """)
            
            cursor.execute("DROP TABLE leads_leadactivity")
            cursor.execute("ALTER TABLE leads_leadactivity_new RENAME TO leads_leadactivity")
            cursor.execute('CREATE INDEX "leads_leadactivity_lead_id_idx" ON "leads_leadactivity" ("lead_id")')
        
        # Migrate LeadNote table
        cursor.execute("PRAGMA table_info(leads_leadnote)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'created_by_id' not in columns:
            cursor.execute("""
                CREATE TABLE "leads_leadnote_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "content" text NOT NULL,
                    "created_by_id" integer NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "lead_id" bigint NOT NULL REFERENCES "leads_lead" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            
            cursor.execute("""
                INSERT INTO leads_leadnote_new 
                SELECT id, content, created_by_id, created_at, updated_at, lead_id
                FROM leads_leadnote
            """)
            
            cursor.execute("DROP TABLE leads_leadnote")
            cursor.execute("ALTER TABLE leads_leadnote_new RENAME TO leads_leadnote")
            cursor.execute('CREATE INDEX "leads_leadnote_lead_id_idx" ON "leads_leadnote" ("lead_id")')
        
        # Migrate LeadDocument table
        cursor.execute("PRAGMA table_info(leads_leaddocument)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if 'created_by_id' not in columns:
            cursor.execute("""
                CREATE TABLE "leads_leaddocument_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "file" varchar(100) NOT NULL,
                    "description" text NULL,
                    "created_by_id" integer NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "lead_id" bigint NOT NULL REFERENCES "leads_lead" ("id") DEFERRABLE INITIALLY DEFERRED
                )
            """)
            
            cursor.execute("""
                INSERT INTO leads_leaddocument_new 
                SELECT id, file, description, created_by_id, created_at, updated_at, lead_id
                FROM leads_leaddocument
            """)
            
            cursor.execute("DROP TABLE leads_leaddocument")
            cursor.execute("ALTER TABLE leads_leaddocument_new RENAME TO leads_leaddocument")
            cursor.execute('CREATE INDEX "leads_leaddocument_lead_id_idx" ON "leads_leaddocument" ("lead_id")')
        
        # Commit transaction
        conn.commit()
        print(f"  ✓ Successfully migrated")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    # Migrate all company databases
    company_db_dir = Path('company_databases')
    if company_db_dir.exists():
        for db_file in company_db_dir.glob('*.db'):
            migrate_leads_tables(db_file)
    
    print("\nDone!")

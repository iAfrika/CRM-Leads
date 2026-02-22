#!/usr/bin/env python3
"""
Fix all User/Profile FK constraints in company databases by recreating tables
"""
import sqlite3
import glob
from pathlib import Path

def fix_table(cursor, table_name, new_schema):
    """Recreate a table with new schema"""
    try:
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"  Table {table_name} doesn't exist, skipping...")
            return False
        
        # Get current schema
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        current_schema = cursor.fetchone()[0]
        
        # Check if already fixed
        if 'REFERENCES "auth_user"' not in current_schema and 'REFERENCES "authentication_profile"' not in current_schema:
            print(f"  {table_name} already fixed")
            return False
        
        print(f"  Fixing {table_name}...")
        
        # Disable FK constraints
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("BEGIN TRANSACTION")
        
        # Create new table
        cursor.execute(new_schema)
        
        # Get column names from new schema
        cursor.execute(f"PRAGMA table_info({table_name}_new)")
        columns = [row[1] for row in cursor.fetchall()]
        cols_str = ', '.join(columns)
        
        # Copy data
        cursor.execute(f"INSERT INTO {table_name}_new SELECT {cols_str} FROM {table_name}")
        
        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}")
        
        # Rename new table
        cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        
        # Commit
        cursor.connection.commit()
        cursor.execute("PRAGMA foreign_keys=ON")
        
        print(f"  ✓ {table_name} fixed successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Error fixing {table_name}: {e}")
        cursor.connection.rollback()
        return False

def fix_database(db_path):
    """Fix all tables in a database"""
    print(f"\nProcessing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define new schemas for all affected tables
    tables_to_fix = {
        'expenses_expensecategory': '''
            CREATE TABLE "expenses_expensecategory_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(255) NOT NULL,
                "description" text,
                "created_by_id" integer,
                "profile_id" integer,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            )
        ''',
        'expenses_expense': '''
            CREATE TABLE "expenses_expense_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "amount" decimal NOT NULL,
                "date" date NOT NULL,
                "payment_method" varchar(10) NOT NULL,
                "description" text NOT NULL,
                "receipt" varchar(100),
                "created_by_id" integer,
                "profile_id" integer,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "category_id" bigint REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        ''',
        'expenses_recurringexpense': '''
            CREATE TABLE "expenses_recurringexpense_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(255) NOT NULL,
                "amount" decimal NOT NULL,
                "frequency" varchar(20) NOT NULL,
                "next_date" date NOT NULL,
                "is_active" bool NOT NULL,
                "created_by_id" integer NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "profile_id" integer,
                "category_id" bigint REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        ''',
        'purchases_purchasecategory': '''
            CREATE TABLE "purchases_purchasecategory_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(255) NOT NULL,
                "description" text,
                "created_by_id" integer,
                "profile_id" integer,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            )
        ''',
        'purchases_purchase': '''
            CREATE TABLE "purchases_purchase_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "amount" decimal NOT NULL,
                "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0),
                "unit_price" decimal NOT NULL,
                "vendor" varchar(200) NOT NULL,
                "date" date NOT NULL,
                "due_date" date,
                "status" varchar(20) NOT NULL,
                "payment_method" varchar(10) NOT NULL,
                "description" text NOT NULL,
                "invoice" varchar(100),
                "created_by_id" integer,
                "profile_id" integer,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "category_id" bigint REFERENCES "purchases_purchasecategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        ''',
        'products_supplier': '''
            CREATE TABLE "products_supplier_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(255) NOT NULL,
                "contact_person" varchar(255) NOT NULL,
                "email" varchar(254) NOT NULL,
                "phone" varchar(20) NOT NULL,
                "address" text NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "is_active" bool NOT NULL,
                "created_by_id" integer
            )
        ''',
        'products_product': '''
            CREATE TABLE "products_product_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "item_code" varchar(50) NOT NULL UNIQUE,
                "name" varchar(200) NOT NULL,
                "description" text,
                "buying_price" decimal NOT NULL,
                "selling_price" decimal NOT NULL,
                "current_stock" integer unsigned NOT NULL CHECK ("current_stock" >= 0),
                "reorder_level" integer unsigned NOT NULL CHECK ("reorder_level" >= 0),
                "status" varchar(20) NOT NULL,
                "created_by_id" integer,
                "updated_by_id" integer,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "category_id" bigint REFERENCES "products_category" ("id") DEFERRABLE INITIALLY DEFERRED
            )
        ''',
        'banking_account': '''
            CREATE TABLE "banking_account_new" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "account_number" varchar(20) NOT NULL UNIQUE,
                "account_type" varchar(20) NOT NULL,
                "owner_id" integer NOT NULL,
                "balance" decimal NOT NULL,
                "pin" varchar(4) NOT NULL,
                "is_active" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED,
                "is_main_company_account" bool NOT NULL
            )
        '''
    }
    
    fixed_count = 0
    for table_name, schema in tables_to_fix.items():
        if fix_table(cursor, table_name, schema):
            fixed_count += 1
    
    conn.close()
    print(f"  Fixed {fixed_count} tables")

if __name__ == '__main__':
    # Fix all company databases
    company_db_dir = Path('company_databases')
    if company_db_dir.exists():
        for db_file in company_db_dir.glob('*.db'):
            fix_database(db_file)
    
    print("\n✓ All databases processed!")

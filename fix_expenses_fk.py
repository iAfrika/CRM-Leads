#!/usr/bin/env python
"""
Script to remove auth_user and authentication_profile FK constraints from expenses tables
"""
import sqlite3
import glob
from pathlib import Path

def fix_expenses_tables(db_path):
    """Remove FK constraints from expenses tables"""
    print(f"Processing: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # Fix ExpenseCategory table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses_expensecategory'")
        if cursor.fetchone():
            print(f"  Fixing expenses_expensecategory table...")
            cursor.execute("BEGIN TRANSACTION")
            
            cursor.execute("""
                CREATE TABLE "expenses_expensecategory_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "name" varchar(255) NOT NULL,
                    "description" text,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "created_by_id" integer,
                    "profile_id" integer
                )
            """)
            
            cursor.execute("""
                INSERT INTO expenses_expensecategory_new 
                SELECT id, name, description, created_at, updated_at, created_by_id, profile_id
                FROM expenses_expensecategory
            """)
            
            cursor.execute("DROP TABLE expenses_expensecategory")
            cursor.execute("ALTER TABLE expenses_expensecategory_new RENAME TO expenses_expensecategory")
            
            conn.commit()
            print(f"  ✓ Fixed expenses_expensecategory")
        
        # Fix Expense table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses_expense'")
        if cursor.fetchone():
            print(f"  Fixing expenses_expense table...")
            cursor.execute("BEGIN TRANSACTION")
            
            cursor.execute("""
                CREATE TABLE "expenses_expense_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "title" varchar(200) NOT NULL,
                    "amount" decimal NOT NULL,
                    "date" date NOT NULL,
                    "payment_method" varchar(10) NOT NULL,
                    "description" text NOT NULL,
                    "receipt" varchar(100),
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "category_id" bigint REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "created_by_id" integer,
                    "profile_id" integer
                )
            """)
            
            cursor.execute("""
                INSERT INTO expenses_expense_new 
                SELECT id, title, amount, date, payment_method, description, receipt, 
                       created_at, updated_at, category_id, project_id, created_by_id, profile_id
                FROM expenses_expense
            """)
            
            cursor.execute("DROP TABLE expenses_expense")
            cursor.execute("ALTER TABLE expenses_expense_new RENAME TO expenses_expense")
            
            # Recreate indexes
            cursor.execute('CREATE INDEX "expenses_expense_category_id_idx" ON "expenses_expense" ("category_id")')
            cursor.execute('CREATE INDEX "expenses_expense_project_id_idx" ON "expenses_expense" ("project_id")')
            cursor.execute('CREATE INDEX "expenses_expense_date_idx" ON "expenses_expense" ("date")')
            
            conn.commit()
            print(f"  ✓ Fixed expenses_expense")
        
        # Fix RecurringExpense table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses_recurringexpense'")
        if cursor.fetchone():
            print(f"  Fixing expenses_recurringexpense table...")
            cursor.execute("BEGIN TRANSACTION")
            
            cursor.execute("""
                CREATE TABLE "expenses_recurringexpense_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "title" varchar(255) NOT NULL,
                    "amount" decimal NOT NULL,
                    "frequency" varchar(20) NOT NULL,
                    "next_date" date NOT NULL,
                    "is_active" bool NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL,
                    "category_id" bigint REFERENCES "expenses_expensecategory" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "project_id" bigint REFERENCES "project_management_project" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "created_by_id" integer NOT NULL,
                    "profile_id" integer
                )
            """)
            
            cursor.execute("""
                INSERT INTO expenses_recurringexpense_new 
                SELECT id, title, amount, frequency, next_date, is_active, 
                       created_at, updated_at, category_id, project_id, created_by_id, profile_id
                FROM expenses_recurringexpense
            """)
            
            cursor.execute("DROP TABLE expenses_recurringexpense")
            cursor.execute("ALTER TABLE expenses_recurringexpense_new RENAME TO expenses_recurringexpense")
            
            # Recreate indexes
            cursor.execute('CREATE INDEX "expenses_recurringexpense_category_id_idx" ON "expenses_recurringexpense" ("category_id")')
            cursor.execute('CREATE INDEX "expenses_recurringexpense_project_id_idx" ON "expenses_recurringexpense" ("project_id")')
            
            conn.commit()
            print(f"  ✓ Fixed expenses_recurringexpense")
        
        cursor.execute("PRAGMA foreign_keys=ON")
        print(f"  ✓ All expenses tables fixed successfully")
        
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
            fix_expenses_tables(db_file)
    
    print("\nDone!")

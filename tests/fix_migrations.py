import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.db import connection

def fix_migrations():
    with connection.cursor() as cursor:
        # Check if authentication.0002_initial exists
        cursor.execute(
            "SELECT * FROM django_migrations WHERE app = 'authentication' AND name = '0002_initial'"
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Add the missing migration entry
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES ('authentication', '0002_initial', CURRENT_TIMESTAMP)"
            )
            print("Added authentication.0002_initial migration entry")
        
        # Make sure the registration subscription table has the correct schema
        cursor.execute("PRAGMA table_info(registration_subscription)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        
        if 'plan' not in column_names:
            print("Column 'plan' not found in registration_subscription table")
            
            # If the table exists but is missing columns, recreate it with correct schema
            cursor.execute("ALTER TABLE registration_subscription ADD COLUMN plan VARCHAR(20)")
            print("Added 'plan' column to registration_subscription table")

if __name__ == '__main__':
    fix_migrations()
    print("Migration fixes completed.") 
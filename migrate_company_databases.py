#!/usr/bin/env python
"""
Script to apply migrations to all company databases
"""
import os
import django
import glob
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def migrate_company_databases():
    """Apply migrations to all company databases"""
    
    # Get all company database files
    company_db_dir = Path('company_databases')
    if not company_db_dir.exists():
        print("No company_databases directory found")
        return
    
    db_files = list(company_db_dir.glob('*.db'))
    
    if not db_files:
        print("No company databases found")
        return
    
    print(f"Found {len(db_files)} company database(s)")
    
    for db_file in db_files:
        db_name = db_file.stem
        print(f"\nMigrating database: {db_name}")
        
        # Temporarily add the database to settings
        settings.DATABASES[db_name] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_file,
        }
        
        # Set the company database in settings for the router
        settings.COMPANY_DATABASE = db_name
        
        try:
            # Run migrations for this database
            call_command('migrate', database=db_name, verbosity=1)
            print(f"✓ Successfully migrated {db_name}")
        except Exception as e:
            print(f"✗ Error migrating {db_name}: {e}")
        finally:
            # Clean up
            if db_name in settings.DATABASES and db_name != 'default':
                del settings.DATABASES[db_name]
            settings.COMPANY_DATABASE = None
    
    print("\nMigration complete!")

if __name__ == '__main__':
    migrate_company_databases()

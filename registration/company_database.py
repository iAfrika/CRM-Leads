"""
Utility functions for managing company-specific databases
"""
import os
from django.conf import settings
from django.db import connections
from django.core.management import call_command


def get_company_database_name(company):
    """
    Get the database name for a company
    """
    return company.database_name


def get_company_database_settings(company):
    """
    Get database configuration for a company
    """
    db_name = get_company_database_name(company)
    base_dir = settings.BASE_DIR
    
    # Get the default database settings as a template
    default_db = settings.DATABASES['default'].copy()
    
    # Override with company-specific settings
    default_db.update({
        'NAME': base_dir / 'company_databases' / f'{db_name}.db',
    })
    
    return default_db


def create_company_database(company):
    """
    Create a new database for a company and run migrations
    """
    db_name = get_company_database_name(company)
    
    # Add database configuration to settings
    db_settings = get_company_database_settings(company)
    
    # Ensure the directory exists
    db_dir = os.path.dirname(db_settings['NAME'])
    os.makedirs(db_dir, exist_ok=True)
    
    # Add to DATABASES setting
    settings.DATABASES[db_name] = db_settings
    
    # Close existing connection if any
    if db_name in connections:
        connections[db_name].close()
        del connections[db_name]
    
    # Run migrations for the company database
    print(f"Creating database for company: {company.name}")
    try:
        call_command('migrate', database=db_name, verbosity=0, interactive=False)
        print(f"✓ Database created successfully for {company.name}")
        return True
    except Exception as e:
        print(f"✗ Error creating database for {company.name}: {str(e)}")
        return False


def set_active_company_database(company):
    """
    Set the active company database in settings for the current request
    """
    if company:
        db_name = get_company_database_name(company)
        
        # Add database configuration if not already present
        if db_name not in settings.DATABASES:
            settings.DATABASES[db_name] = get_company_database_settings(company)
        
        # Set the active company database
        settings.COMPANY_DATABASE = db_name
    else:
        settings.COMPANY_DATABASE = 'default'


def get_active_company_database():
    """
    Get the currently active company database name
    """
    return getattr(settings, 'COMPANY_DATABASE', 'default')

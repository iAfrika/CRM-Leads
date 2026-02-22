import os
import sys
import re

def update_settings_file():
    """Update settings.py to use standard PostgreSQL configuration"""
    settings_path = 'core/settings.py'
    if not os.path.exists(settings_path):
        print(f"Settings file not found: {settings_path}")
        return False
    
    print(f"Updating database settings in {settings_path}")
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Update the database settings
        database_pattern = r'DATABASES\s*=\s*{[^}]*}'
        standard_database_config = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_leads',
        'USER': 'postgres',
        'PASSWORD': '',  # Set your database password here
        'HOST': 'localhost',
        'PORT': '5432',
    }
}"""
        
        if re.search(database_pattern, content):
            content = re.sub(database_pattern, standard_database_config, content)
        else:
            content += f"\n\n{standard_database_config}\n"
        
        # Remove any remaining tenant-specific settings
        content = re.sub(r'DATABASE_ROUTERS\s*=\s*\[.*?\]', '', content)
        content = re.sub(r'TENANT_.*?=.*?\n', '', content)
        
        with open(settings_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("Database settings updated successfully!")
        return True
    
    except Exception as e:
        print(f"Error updating settings file: {e}")
        return False

def create_migration_folders():
    """Create migration folders if they don't exist"""
    apps = ['leads', 'registration']
    
    for app in apps:
        migrations_dir = f"{app}/migrations"
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            print(f"Created migrations directory for {app}")
        
        init_file = f"{migrations_dir}/__init__.py"
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass
            print(f"Created __init__.py in {migrations_dir}")

def update_urls_file():
    """Update URLs file to use standard Django configuration"""
    urls_path = 'core/urls.py'
    if not os.path.exists(urls_path):
        print(f"URLs file not found: {urls_path}")
        return False
    
    print(f"Updating URLs configuration in {urls_path}")
    
    try:
        with open(urls_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Update URLs to standard Django configuration
        if "from django_tenants.urls import tenant_patterns" in content:
            content = content.replace("from django_tenants.urls import tenant_patterns", "")
        
        pattern = r'urlpatterns\s*=\s*.*?\[.*?\]'
        if not re.search(pattern, content, re.DOTALL):
            standard_url_config = """urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('leads.urls')),
    path('registration/', include('registration.urls')),
]"""
            content += f"\n\n{standard_url_config}\n"
        
        with open(urls_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("URLs configuration updated successfully!")
        return True
    
    except Exception as e:
        print(f"Error updating URLs file: {e}")
        return False

def main():
    print("=" * 60)
    print("DATABASE CONFIGURATION UPDATE TOOL")
    print("=" * 60)
    print("\nThis script will update your database settings for a standard Django project.")
    
    # Update settings.py
    update_settings_file()
    
    # Update urls.py
    update_urls_file()
    
    # Ensure migration folders exist
    create_migration_folders()
    
    print("\nDatabase configuration updated for standard Django project.")
    print("\nNext steps:")
    print("1. Update the database password in core/settings.py")
    print("2. Run 'python manage.py makemigrations' to create migrations")
    print("3. Run 'python manage.py migrate' to apply migrations")
    print("4. Run 'python manage.py createsuperuser' to create an admin user")
    print("5. Run 'python manage.py runserver' to start the development server")

if __name__ == "__main__":
    main() 
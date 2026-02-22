# Final Setup Instructions for CRM-Leads

We've made significant progress setting up your multi-tenant CRM system. Here are the final steps to complete the setup:

## 1. Install PostgreSQL (Required)

The django-tenants package requires PostgreSQL to function properly. If you haven't installed it yet:

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. During installation:
   - Remember the password you set for the 'postgres' user
   - Use the default port (5432)
   - Install all components when prompted

## 2. Set Up Your Environment

We've created a special batch file to set up your environment properly:

1. Run `.\setup_environment.bat` in PowerShell
   - This will find your PostgreSQL installation
   - Copy the necessary DLLs to your Python environment
   - Set up the PATH correctly

2. A new command window will open where you can run all Django commands

## 3. Run Migrations and Set Up Database

In the command window opened by setup_environment.bat, run:

```
python manage.py makemigrations tenants
python manage.py makemigrations leads
python manage.py makemigrations registration
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

## 4. Create a Superuser

```
python manage.py createsuperuser
```

## 5. Run the Development Server

```
python manage.py runserver
```

## 6. Access Your Multi-tenant CRM

1. Access the admin interface at: http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Create a tenant client and domain in the admin interface
4. Access your tenant site at the domain you set up

## Troubleshooting

If you still have issues with psycopg2 or PostgreSQL:

1. Make sure PostgreSQL is properly installed
2. Try running PostgreSQL commands directly to verify installation
3. Check that your PATH includes the PostgreSQL bin directory
4. Verify database connection settings in your Django settings.py file

## Next Steps

Once your basic setup is complete, you can:

1. Customize the leads management functionality
2. Add additional applications to your tenant sites
3. Set up proper authentication and permissions
4. Design a more advanced multi-tenant structure

Refer to the django-tenants documentation for more advanced configurations:
https://django-tenants.readthedocs.io/ 
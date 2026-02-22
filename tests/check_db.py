import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.db import connection

def check_db():
    """Check the database tables."""
    try:
        with connection.cursor() as cursor:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Tables in the database:")
            for table in tables:
                print(f"- {table[0]}")
            
            # Check projects_project table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_project'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(projects_project)")
                columns = cursor.fetchall()
                
                print("\nColumns in projects_project table:")
                for column in columns:
                    print(f"- {column[1]} ({column[2]})")
                
                cursor.execute("SELECT * FROM projects_project")
                projects = cursor.fetchall()
                
                print(f"\nProjects in projects_project table ({len(projects)}):")
                for project in projects:
                    print(f"- ID: {project[0]}, Name: {project[1]}")
            
            # Check banking_account table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='banking_account'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(banking_account)")
                columns = cursor.fetchall()
                
                print("\nColumns in banking_account table:")
                for column in columns:
                    print(f"- {column[1]} ({column[2]})")
                
                cursor.execute("SELECT * FROM banking_account")
                accounts = cursor.fetchall()
                
                print(f"\nAccounts in banking_account table ({len(accounts)}):")
                for account in accounts:
                    print(f"- ID: {account[0]}, Account Number: {account[1]}, Type: {account[2]}, Project ID: {account[9]}")
            
            # Check banking_projectfinancialsummary table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='banking_projectfinancialsummary'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(banking_projectfinancialsummary)")
                columns = cursor.fetchall()
                
                print("\nColumns in banking_projectfinancialsummary table:")
                for column in columns:
                    print(f"- {column[1]} ({column[2]})")
                
                cursor.execute("SELECT * FROM banking_projectfinancialsummary")
                summaries = cursor.fetchall()
                
                print(f"\nSummaries in banking_projectfinancialsummary table ({len(summaries)}):")
                for summary in summaries:
                    print(f"- ID: {summary[0]}, Project ID: {summary[1]}")
    
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_db() 
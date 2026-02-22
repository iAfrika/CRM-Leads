import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.db import connection

def fix_db():
    """Fix the banking_projectfinancialsummary table."""
    try:
        with connection.cursor() as cursor:
            # Update the project_id in banking_projectfinancialsummary to reference a valid project
            cursor.execute("UPDATE banking_projectfinancialsummary SET project_id = 1 WHERE id = 1")
            print("Updated banking_projectfinancialsummary table.")
            
            # Check if the update was successful
            cursor.execute("SELECT id, project_id FROM banking_projectfinancialsummary")
            summaries = cursor.fetchall()
            
            print(f"Summaries in banking_projectfinancialsummary table ({len(summaries)}):")
            for summary in summaries:
                print(f"- ID: {summary[0]}, Project ID: {summary[1]}")
    
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_db() 
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from django.db import connection

def fix_project_references():
    """Fix the project references in the banking app."""
    try:
        # Check if the project_management_project table exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_management_project'")
            project_management_table_exists = cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects_project'")
            projects_table_exists = cursor.fetchone() is not None
            
            print(f"project_management_project table exists: {project_management_table_exists}")
            print(f"projects_project table exists: {projects_table_exists}")
            
            if project_management_table_exists and projects_table_exists:
                # Copy data from project_management_project to projects_project
                cursor.execute("SELECT id, name, description, start_date, end_date FROM project_management_project")
                projects = cursor.fetchall()
                
                print(f"Found {len(projects)} projects in project_management_project table.")
                
                for project in projects:
                    project_id, name, description, start_date, end_date = project
                    
                    # Check if the project already exists in projects_project
                    cursor.execute("SELECT id FROM projects_project WHERE id = ?", [project_id])
                    if cursor.fetchone() is None:
                        # Insert the project into projects_project
                        cursor.execute(
                            "INSERT INTO projects_project (id, name, description, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                            [project_id, name, description, start_date, end_date]
                        )
                        print(f"Copied project {name} (ID: {project_id}) to projects_project table.")
                    else:
                        print(f"Project {name} (ID: {project_id}) already exists in projects_project table.")
            
            # Check banking_projectfinancialsummary table
            cursor.execute("SELECT id, project_id FROM banking_projectfinancialsummary")
            financial_summaries = cursor.fetchall()
            
            print(f"Found {len(financial_summaries)} financial summaries.")
            
            for summary in financial_summaries:
                summary_id, project_id = summary
                
                # Check if the project exists in projects_project
                cursor.execute("SELECT id FROM projects_project WHERE id = ?", [project_id])
                if cursor.fetchone() is None:
                    print(f"Financial summary {summary_id} references non-existent project {project_id}.")
                    
                    # Get the first project from projects_project
                    cursor.execute("SELECT id FROM projects_project LIMIT 1")
                    first_project = cursor.fetchone()
                    
                    if first_project:
                        # Update the financial summary to reference the first project
                        cursor.execute(
                            "UPDATE banking_projectfinancialsummary SET project_id = ? WHERE id = ?",
                            [first_project[0], summary_id]
                        )
                        print(f"Updated financial summary {summary_id} to reference project {first_project[0]}.")
                else:
                    print(f"Financial summary {summary_id} references valid project {project_id}.")
    
    except Exception as e:
        print(f"Error fixing project references: {e}")

if __name__ == "__main__":
    fix_project_references() 
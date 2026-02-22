import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from projects.models import Project

def test_project_model():
    """Test if the Project model is accessible."""
    try:
        # Try to get all projects
        projects = Project.objects.all()
        print(f"Successfully accessed Project model. Found {len(projects)} projects.")
        
        # List all projects
        for project in projects:
            print(f"Project: {project.name}")
        
        # If no projects exist, create a test project
        if len(projects) == 0:
            print("No projects found. Creating a test project...")
            from django.utils import timezone
            
            test_project = Project.objects.create(
                name="Test Project",
                description="This is a test project created by the test script.",
                start_date=timezone.now().date(),
                end_date=timezone.now().date()
            )
            print(f"Created test project: {test_project.name}")
            
    except Exception as e:
        print(f"Error accessing Project model: {e}")

if __name__ == "__main__":
    test_project_model() 
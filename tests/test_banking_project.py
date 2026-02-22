import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_leads.settings')
django.setup()

from projects.models import Project
from banking.models import Account
from django.contrib.auth.models import User

def test_banking_project_integration():
    """Test if the banking app can access the Project model."""
    try:
        # Get all projects
        projects = Project.objects.all()
        print(f"Found {len(projects)} projects.")
        
        # Get the first user
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        
        print(f"Using user: {user.username}")
        
        # Get the first project
        project = Project.objects.first()
        if not project:
            print("No projects found. Please create a project first.")
            return
        
        print(f"Using project: {project.name}")
        
        # Create a test account linked to the project
        account_number = '1234567890'
        pin = '1234'
        
        # Check if the account already exists
        if Account.objects.filter(account_number=account_number).exists():
            account = Account.objects.get(account_number=account_number)
            print(f"Account already exists: {account}")
        else:
            account = Account.objects.create(
                account_number=account_number,
                account_type='PROJECT',
                owner=user,
                pin=pin,
                balance=0.00,
                project=project
            )
            print(f"Created test account: {account}")
        
        # Verify the account is linked to the project
        if account.project:
            print(f"Account is linked to project: {account.project.name}")
        else:
            print("Account is not linked to a project.")
            
    except Exception as e:
        print(f"Error testing banking-project integration: {e}")

if __name__ == "__main__":
    test_banking_project_integration() 
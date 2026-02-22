import requests
import sys

def test_project_finances_url():
    """Test if the project_finances URL is working."""
    base_url = "http://127.0.0.1:8000"
    
    # First, check if the server is running
    try:
        response = requests.get(f"{base_url}/admin/", allow_redirects=False)
        if response.status_code in [200, 302]:
            print("Server is running!")
        else:
            print(f"Server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error accessing server: {e}")
        return False
    
    # Test the project_finances URL for project with ID 1
    project_id = 1
    finances_url = f"{base_url}/projects/{project_id}/finances/"
    print(f"Testing URL: {finances_url}")
    
    try:
        finances_response = requests.get(finances_url, allow_redirects=False)
        print(f"Response status code: {finances_response.status_code}")
        
        if finances_response.status_code in [200, 302]:
            print("SUCCESS: Project finances URL is accessible.")
            return True
        else:
            print(f"ERROR: Project finances URL returned status code {finances_response.status_code}")
            return False
    except Exception as e:
        print(f"Error accessing project finances URL: {e}")
        return False

if __name__ == "__main__":
    success = test_project_finances_url()
    sys.exit(0 if success else 1) 
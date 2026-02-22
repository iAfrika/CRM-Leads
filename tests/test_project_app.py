import requests
import re
import time
import sys
from bs4 import BeautifulSoup

class ProjectAppTester:
    """Class to test the project app"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username="admin", password="pass", role="administrator"):
        """Login to the application"""
        print(f"Logging in as {username} with role {role}...")
        
        # Get login page to retrieve CSRF token
        login_url = f"{self.base_url}/auth/login/"
        login_response = self.session.get(login_url)
        
        if login_response.status_code != 200:
            print(f"❌ Failed to access login page. Status code: {login_response.status_code}")
            return False
        
        # Extract CSRF token
        csrf_token = None
        try:
            csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_response.text).group(1)
            print(f"✅ CSRF token found: {csrf_token[:10]}...")
        except (AttributeError, IndexError):
            print("❌ Failed to extract CSRF token from login page")
            return False
        
        # Submit login form
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'password': password,
        }
        
        login_response = self.session.post(login_url, data=login_data, headers={
            'Referer': login_url
        })
        
        # Check if login was successful (redirected to profile selection or profile page)
        if 'profile_selection' in login_response.url or '/auth/profile/' in login_response.url:
            print(f"✅ Login successful, redirected to {login_response.url}")
            
            # If redirected to profile selection page, select the role
            if 'profile_selection' in login_response.url:
                profile_url = login_response.url
                profile_response = self.session.get(profile_url)
                
                # Extract CSRF token for profile selection
                try:
                    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', profile_response.text).group(1)
                except (AttributeError, IndexError):
                    print("❌ Failed to extract CSRF token from profile selection page")
                    return False
                
                # Parse the profile selection page to find the profile ID for the specified role
                soup = BeautifulSoup(profile_response.text, 'html.parser')
                profile_id = None
                
                for label in soup.find_all('label'):
                    if role.lower() in label.text.lower():
                        profile_input = label.find('input')
                        if profile_input:
                            profile_id = profile_input.get('value')
                            break
                
                if not profile_id:
                    print(f"❌ Could not find profile ID for role '{role}'")
                    return False
                
                # Submit profile selection form
                profile_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'profile': profile_id
                }
                
                profile_response = self.session.post(profile_url, data=profile_data, headers={
                    'Referer': profile_url
                })
                
                # Check if profile selection was successful
                if profile_response.status_code == 200 or 'dashboard' in profile_response.url:
                    print(f"✅ Successfully selected {role} profile")
                    print(f"✅ Final URL after login: {profile_response.url}")
                    return True
                else:
                    print(f"❌ Failed to select profile. Status code: {profile_response.status_code}")
                    return False
            else:
                # If directly redirected to profile page, we're already logged in
                print("✅ User already has a default profile, no need to select")
                return True
        else:
            print(f"❌ Login failed. Final URL: {login_response.url}")
            return False
    
    def test_url(self, url, expected_elements=None):
        """Test a URL and check for expected elements"""
        print(f"\nTesting URL: {url}")
        
        try:
            response = self.session.get(url, timeout=5)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for sidebar
                sidebar = soup.find('div', class_='app-sidebar')
                if sidebar:
                    print("✅ Sidebar found")
                    
                    # Check for sidebar menu
                    sidebar_menu = sidebar.find('div', class_='sidebar-menu')
                    if sidebar_menu:
                        print("✅ Sidebar menu found")
                        
                        # Count sidebar links
                        sidebar_links = sidebar_menu.find_all('a', class_='sidebar-link')
                        print(f"✅ Found {len(sidebar_links)} sidebar links")
                    else:
                        print("❌ Sidebar menu not found")
                else:
                    print("❌ Sidebar not found")
                
                # Check for header
                header = soup.find('div', class_='app-header')
                if header:
                    print("✅ Header found")
                else:
                    print("❌ Header not found")
                
                # Check for content
                content = soup.find('div', class_='app-content')
                if content:
                    print("✅ Content area found")
                else:
                    print("❌ Content area not found")
                
                # Check for footer
                footer = soup.find('div', class_='app-footer')
                if footer:
                    print("✅ Footer found")
                else:
                    print("❌ Footer not found")
                
                # Check for CSS files
                css_links = soup.find_all('link', rel='stylesheet')
                project_sidebar_css = False
                
                for link in css_links:
                    href = link.get('href', '')
                    if 'project_sidebar.css' in href:
                        project_sidebar_css = True
                        print("✅ project_sidebar.css is included")
                
                if not project_sidebar_css:
                    print("❌ project_sidebar.css is not included")
                
                # Check for specific elements if provided
                if expected_elements:
                    for selector, name in expected_elements.items():
                        element = soup.select_one(selector)
                        if element:
                            print(f"✅ Found {name}")
                        else:
                            print(f"❌ {name} not found")
                
                # Print the final URL (in case of redirects)
                print(f"Final URL: {response.url}")
                
                return True
            else:
                print(f"❌ Failed to access URL. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("Starting tests for the project app...")
        
        # Wait for server to be ready
        time.sleep(2)
        
        # Login first
        if not self.login():
            print("\n❌ Login failed. Cannot proceed with tests.")
            return False
        
        # Test project list page
        project_list_elements = {
            '.project-navigation': 'Project navigation tabs',
            '.projects-grid': 'Projects grid',
            '.project-card': 'Project card'
        }
        self.test_url(f"{self.base_url}/projects/", project_list_elements)
        
        # Test project create page
        project_create_elements = {
            '.form-group': 'Form group',
            'button[type="submit"]': 'Submit button'
        }
        self.test_url(f"{self.base_url}/projects/create/", project_create_elements)
        
        print("\nTests completed.")
        
        return True

if __name__ == "__main__":
    tester = ProjectAppTester()
    if tester.run_tests():
        sys.exit(0)
    else:
        sys.exit(1) 
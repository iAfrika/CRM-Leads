import requests
import re
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CRMTester:
    """A class to test the CRM application"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username="admin", password="pass", role="administrator"):
        """Login to the CRM application"""
        print(f"Logging in as {username} with role {role}...")
        
        # Get login page to retrieve CSRF token
        login_url = urljoin(self.base_url, "/auth/login/")
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
    
    def test_static_css(self):
        """Test if the CSS file is accessible"""
        print("\nTesting CSS file accessibility...")
        css_url = urljoin(self.base_url, "/static/css/people_styles.css")
        response = self.session.get(css_url)
        
        if response.status_code == 200:
            print(f"✅ CSS file is accessible (Status: {response.status_code})")
            return True
        else:
            print(f"❌ CSS file is not accessible (Status: {response.status_code})")
            return False
    
    def test_people_app(self):
        """Test the People app pages"""
        print("\nTesting People app pages...")
        
        # Test pages
        test_pages = [
            ("/people/", "People Directory"),
            ("/people/register/", "Register Person"),
            ("/people/contact/", "Contact People")
        ]
        
        all_ok = True
        
        for page_url, page_title in test_pages:
            print(f"\nTesting: {page_title}")
            full_url = urljoin(self.base_url, page_url)
            response = self.session.get(full_url)
            
            if response.status_code == 200:
                print(f"✅ Page accessible (Status: {response.status_code})")
                
                # Check if CSS is included in the page
                soup = BeautifulSoup(response.text, 'html.parser')
                css_links = soup.find_all('link', {'rel': 'stylesheet'})
                css_included = False
                
                for link in css_links:
                    href = link.get('href', '')
                    if 'people_styles.css' in href:
                        css_included = True
                        print("✅ people_styles.css is included in the page")
                        break
                
                if not css_included:
                    print("❌ people_styles.css is not included in the page")
                    all_ok = False
                
                # Check for specific CSS styling
                styled_elements = self.check_css_applied(response.text)
                if styled_elements:
                    print(f"✅ Found {styled_elements} styled elements - CSS appears to be applied")
                else:
                    print("⚠️ Could not confirm if CSS is properly applied to elements")
            else:
                print(f"❌ Failed to access page (Status: {response.status_code})")
                all_ok = False
        
        return all_ok
    
    def check_css_applied(self, html_content):
        """Check if CSS is applied by looking for elements with specific class names"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for elements with classes likely defined in our CSS
        styled_elements = 0
        css_classes = [
            'person-card', 'person-info', 'person-list', 'contact-form',
            'people-header', 'register-form', 'person-detail', 'custom-table'
        ]
        
        for css_class in css_classes:
            elements = soup.find_all(class_=css_class)
            styled_elements += len(elements)
        
        return styled_elements

    def run_tests(self):
        """Run all tests"""
        print("=== Starting comprehensive verification of People app ===\n")
        
        # Login first
        if not self.login():
            print("\n❌ Login failed. Cannot proceed with tests.")
            return False
        
        # Check if CSS file is accessible
        css_accessible = self.test_static_css()
        
        # Test People app pages
        people_app_ok = self.test_people_app()
        
        # Report results
        print("\n=== Test Summary ===")
        print(f"CSS File Accessible: {'✅' if css_accessible else '❌'}")
        print(f"People App Pages: {'✅' if people_app_ok else '❌'}")
        
        if css_accessible and people_app_ok:
            print("\n✅ All tests passed! The People app is working correctly with CSS styling.")
            return True
        else:
            print("\n⚠️ Some tests failed. See details above.")
            return False

if __name__ == "__main__":
    tester = CRMTester()
    if tester.run_tests():
        sys.exit(0)
    else:
        sys.exit(1) 
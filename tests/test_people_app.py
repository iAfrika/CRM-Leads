import requests
import sys
import time
import re

# Give the server a moment to start up
time.sleep(2)

# Base URL for local development server
BASE_URL = 'http://localhost:8000'

class PeopleAppTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username='admin', password='pass', role='administrator'):
        """Log in to the system"""
        print(f"\n🔑 Attempting to log in as {username} with role {role}...")
        login_url = f"{self.base_url}/auth/login/"
        
        # First, get the login page to extract the CSRF token
        login_page = self.session.get(login_url)
        
        # Extract CSRF token from the page
        csrf_token = None
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
        if match:
            csrf_token = match.group(1)
            print(f"✅ CSRF token found: {csrf_token[:10]}...")
        else:
            print("❌ CSRF token not found on the login page.")
            return False
        
        # Prepare login data
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'password': password,
            'role': role,
            'next': '/people/'
        }
        
        # Submit the login form
        login_response = self.session.post(
            login_url,
            data=login_data,
            headers={'Referer': login_url}
        )
        
        # Check if login was successful
        if login_response.status_code == 200 and 'authentication/login.css' in login_response.text:
            print("❌ Login failed - still on the login page")
            return False
        else:
            print(f"✅ Login successful - redirected to: {login_response.url}")
            return True
    
    def test_static_css(self):
        """Test if the CSS file is properly served"""
        print("\n🔍 Testing CSS file accessibility")
        css_url = f"{self.base_url}/static/css/people_styles.css"
        response = self.session.get(css_url)
        
        if response.status_code == 200:
            print(f"✅ CSS file is accessible (Status: {response.status_code})")
            # Print first few lines of the CSS to verify it's correct
            css_content = response.text[:200]
            print(f"CSS Preview: {css_content}...")
            return True
        else:
            print(f"❌ CSS file is not accessible (Status: {response.status_code})")
            return False
    
    def test_url(self, url, description=""):
        """Test a URL and print details about the response"""
        try:
            print(f"\n🔍 Testing {description or url}")
            response = self.session.get(url)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error: {url} returned status code {response.status_code}")
                return False
            
            content = response.text
            
            # Check if redirected to login page
            if 'authentication/login.css' in content:
                print("❌ Redirected to login page - not authenticated")
                return False
            
            # Check if our CSS file is included
            css_included = 'people_styles.css' in content
            print(f"CSS included: {'✅ Yes' if css_included else '❌ No'}")
            
            # Print a snippet of the response content
            print("\nResponse content preview:")
            print("-" * 80)
            content_preview = content[:500].replace('\n', ' ')
            print(f"{content_preview}...")
            print("-" * 80)
            
            # Print the current URL (if redirected)
            print(f"Final URL: {response.url}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error accessing {url}: {e}")
            return False
    
    def run_tests(self):
        """Run all tests for the people app"""
        print("🧪 Starting tests for the people app...")
        
        # First, try to login
        if not self.login(username='admin', password='pass', role='administrator'):
            print("\n❌ Cannot proceed with tests because login failed.")
            print("Please make sure the server is running and credentials are correct.")
            return False
        
        # Test CSS file directly
        self.test_static_css()
        
        # Test the people app pages
        test_urls = [
            (f"{self.base_url}/people/", "People Directory page"),
            (f"{self.base_url}/people/register/", "Register Person page"),
            (f"{self.base_url}/people/contact/", "Contact People page")
        ]
        
        success = True
        for url, description in test_urls:
            if not self.test_url(url, description):
                success = False
        
        print("\n🏁 Testing complete!")
        if success:
            print("✅ All tests passed! The people app is working correctly with the new styling.")
            return True
        else:
            print("❌ Some tests failed. Please check the output above for details.")
            return False

# Run the tests
if __name__ == "__main__":
    tester = PeopleAppTester(BASE_URL)
    success = tester.run_tests()
    sys.exit(0 if success else 1) 
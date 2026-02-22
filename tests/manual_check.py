import requests
from bs4 import BeautifulSoup
import sys

# Base URL for the server
BASE_URL = "http://127.0.0.1:8000"

def check_dashboard():
    session = requests.Session()
    
    # Try to access the dashboard directly first
    print("Accessing dashboard directly...")
    dashboard_url = f"{BASE_URL}/dashboard/"
    response = session.get(dashboard_url)
    
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    
    # Check if we were redirected to login
    if '/auth/login/' in response.url:
        print("Redirected to login page as expected")
        
        # Parse login page for CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.select_one('input[name="csrfmiddlewaretoken"]')['value']
        
        # Prepare login data
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'admin',
            'password': 'pass',
            'role': 'administrator'
        }
        
        print("Submitting login form...")
        login_response = session.post(
            response.url,
            data=login_data,
            headers={'Referer': response.url}
        )
        
        print(f"Login status: {login_response.status_code}")
        print(f"Login redirect URL: {login_response.url}")
        
        # Check if redirected to profile-selection
        if 'profile-selection' in login_response.url:
            print("Redirected to profile selection as expected")
            
            # Parse profile selection page
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Print the HTML structure of the page for debugging
            print("\nProfile selection page HTML structure:")
            print(soup.prettify()[:1000])  # Print first 1000 chars to avoid overwhelming output
            
            # Look for profile cards
            profile_links = soup.select('.profile-card')
            
            if profile_links:
                print(f"Found {len(profile_links)} profile cards")
                
                for i, link in enumerate(profile_links):
                    classes = link.get('class', [])
                    href = link.get('href', 'No href')
                    name_elem = link.select_one('.profile-name')
                    name = name_elem.text.strip() if name_elem else "No name"
                    is_add_profile = 'add-profile' in classes
                    
                    print(f"Profile {i+1}: {name}, URL: {href}, Is 'Add Profile': {is_add_profile}")
                    
                    # Select first real profile
                    if not is_add_profile:
                        print(f"Selecting profile: {name}")
                        profile_url = f"{BASE_URL}{href}"
                        profile_response = session.get(profile_url)
                        
                        print(f"Profile selection status: {profile_response.status_code}")
                        print(f"Profile selection URL: {profile_response.url}")
                        
                        # Print cookies
                        print("\nCookies after navigating to profile selection:")
                        for cookie, value in session.cookies.items():
                            print(f"  {cookie}: {value}")
                        
                        # Extract CSRF token for PIN submission
                        pin_soup = BeautifulSoup(profile_response.text, 'html.parser')
                        pin_csrf_token = pin_soup.select_one('input[name="csrfmiddlewaretoken"]')['value']
                        
                        # Print PIN form structure for debugging
                        print("\nPIN Form structure:")
                        pin_form = pin_soup.select_one('form')
                        if pin_form:
                            print(pin_form.prettify()[:500])
                        
                        # Submit PIN (using correct PIN '1122')
                        pin_data = {
                            'csrfmiddlewaretoken': pin_csrf_token,
                            'pin': '1122'  # Using the PIN provided by the user
                        }
                        
                        print(f"\nSubmitting PIN form with data: {pin_data}")
                        pin_submit_response = session.post(
                            profile_response.url,
                            data=pin_data,
                            headers={'Referer': profile_response.url}
                        )
                        
                        print(f"PIN submission status: {pin_submit_response.status_code}")
                        print(f"PIN submission URL: {pin_submit_response.url}")
                        
                        # Print cookies after PIN submission
                        print("\nCookies after PIN submission:")
                        for cookie, value in session.cookies.items():
                            print(f"  {cookie}: {value}")
                        
                        # Now try to access dashboard
                        print("Trying to access dashboard after profile selection...")
                        dashboard_response = session.get(dashboard_url)
                        
                        print(f"Dashboard status: {dashboard_response.status_code}")
                        print(f"Dashboard URL: {dashboard_response.url}")
                        
                        # If redirected to login again, try one more approach
                        if '/auth/login/' in dashboard_response.url:
                            print("Still redirected to login. Checking for authentication issues...")
                            
                            # Check if server logs show any errors
                            print("\nPlease check server logs for any errors. The test could not access the dashboard.")
                            return False
                        elif '/auth/profile-selection/' in dashboard_response.url:
                            print("Still redirected to profile selection. Check for profile selection issues.")
                            return False
                        elif '/dashboard/' in dashboard_response.url:
                            # Success! We accessed the dashboard
                            print("Success! Dashboard accessed.")
                            
                            # Check if there are any server errors
                            if dashboard_response.status_code == 500:
                                print("Server error when accessing dashboard")
                                soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                                error_divs = soup.select('.traceback')
                                if error_divs:
                                    print("Error message:")
                                    print(error_divs[0].text)
                                return False
                            
                            # Check if we got valid dashboard content
                            soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                            title = soup.title.text if soup.title else "No title"
                            print(f"Dashboard page title: {title}")
                            
                            # Try to print basic dashboard content
                            content_divs = soup.select('.card-title, .h3, h1, h2, h3')
                            if content_divs:
                                print("Dashboard content headers:")
                                for div in content_divs[:5]:  # Just show first 5
                                    print(f"  - {div.text.strip()}")
                            
                            return True
                        else:
                            print(f"Unexpected redirect to: {dashboard_response.url}")
                            return False
            else:
                print("No profile cards found on profile selection page")
                return False
        else:
            print(f"Unexpected redirect after login: {login_response.url}")
            return False
    else:
        print(f"Unexpected response when accessing dashboard: {response.url}")
        return False

if __name__ == "__main__":
    success = check_dashboard()
    if success:
        print("\nTest PASSED: Successfully accessed the dashboard")
        sys.exit(0)
    else:
        print("\nTest FAILED: Could not access the dashboard")
        sys.exit(1) 
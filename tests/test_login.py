import requests
import sys
from bs4 import BeautifulSoup
import json

def test_login_and_dashboard(username, password):
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Get the login page to retrieve the CSRF token
    login_url = 'http://localhost:8000/auth/login/'
    login_response = session.get(login_url)
    
    if login_response.status_code != 200:
        print(f"Failed to access login page: {login_response.status_code}")
        return False
    
    # Parse the HTML to extract the CSRF token
    soup = BeautifulSoup(login_response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_input:
        print("Could not find CSRF token")
        return False
    
    csrf_token = csrf_input.get('value')
    
    # Prepare login data
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': username,
        'password': password,
        'role': 'administrator'  # Explicitly set role to administrator
    }
    
    # Submit the login form
    login_post_response = session.post(
        login_url,
        data=login_data,
        headers={'Referer': login_url}
    )
    
    # Check if login was successful (should redirect)
    if login_post_response.status_code != 200 and login_post_response.status_code != 302:
        print(f"Login failed with status code: {login_post_response.status_code}")
        return False
    
    print(f"Login response URL: {login_post_response.url}")
    
    # If redirected to profile page, we need to handle that
    if 'profile' in login_post_response.url:
        print("Redirected to profile page, checking if we need to select a profile")
        
        # Get the profile page
        profile_response = session.get(login_post_response.url)
        profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Check if we're on the profile selection page
        if 'profile-selection' in profile_response.url:
            print("On profile selection page, looking for profiles")
            
            # Find all profile links
            profile_links = profile_soup.find_all('a', href=lambda href: href and 'profile-select' in href)
            
            if profile_links:
                # Get the first profile link
                profile_select_url = profile_links[0]['href']
                if not profile_select_url.startswith('http'):
                    profile_select_url = f"http://localhost:8000{profile_select_url}"
                
                print(f"Selecting profile: {profile_select_url}")
                
                # Get the profile select page to get the CSRF token
                profile_select_response = session.get(profile_select_url)
                profile_select_soup = BeautifulSoup(profile_select_response.text, 'html.parser')
                
                csrf_input = profile_select_soup.find('input', {'name': 'csrfmiddlewaretoken'})
                if not csrf_input:
                    print("Could not find CSRF token on profile select page")
                    return False
                
                csrf_token = csrf_input.get('value')
                
                # Submit the PIN form (assuming PIN is 1234 for testing)
                pin_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'pin': '1234'
                }
                
                profile_post_response = session.post(
                    profile_select_url,
                    data=pin_data,
                    headers={'Referer': profile_select_url}
                )
                
                print(f"Profile selection response URL: {profile_post_response.url}")
            else:
                print("No profile links found on profile selection page")
    
    # Try to access the dashboard
    dashboard_url = 'http://localhost:8000/'
    dashboard_response = session.get(dashboard_url, allow_redirects=True)
    
    # Print the final URL after redirects
    print(f"Final URL after redirects: {dashboard_response.url}")
    
    # Check the content of the dashboard page
    dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
    page_title = dashboard_soup.title.text if dashboard_soup.title else "No title found"
    print(f"Page title: {page_title}")
    
    # Check for dashboard elements
    dashboard_elements = dashboard_soup.find_all(string=lambda text: text and "Dashboard" in text)
    if dashboard_elements:
        print(f"Found {len(dashboard_elements)} dashboard elements on the page")
    else:
        print("No dashboard elements found on the page")
    
    # Check if we can access the dashboard
    if 'dashboard' in dashboard_response.url or dashboard_response.url == 'http://localhost:8000/':
        if "Dashboard" in dashboard_response.text:
            print("Successfully accessed the dashboard!")
            return True
        else:
            print("URL looks correct but page content doesn't appear to be the dashboard")
            return False
    else:
        print(f"Failed to access dashboard. Current URL: {dashboard_response.url}")
        print(f"Response status code: {dashboard_response.status_code}")
        print(f"Response content: {dashboard_response.text[:500]}...")  # Print first 500 chars
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_login.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    result = test_login_and_dashboard(username, password)
    
    if result:
        print("Test passed: Login and dashboard access successful")
    else:
        print("Test failed: Could not access dashboard after login") 
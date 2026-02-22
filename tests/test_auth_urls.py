import requests
import sys
import time
import json
from bs4 import BeautifulSoup
import urllib.parse

# Base URL for the server
BASE_URL = "http://127.0.0.1:8000"

# Login credentials
USERNAME = "admin"
PASSWORD = "pass"
ROLE = "administrator"  # Based on the login form fields

# List of paths to check, organized by app
PATHS = {
    "authentication": [
        "/auth/login/",
        "/auth/logout/",
        "/auth/profile/"
    ],
    "dashboard": [
        "/dashboard/",
        "/dashboard/schedule/",
        "/dashboard/calendar/",
        "/dashboard/statistics/",
        "/dashboard/api/chart-data/?type=quotes_invoices&timeline=month",
        "/dashboard/api/chart-data/?type=revenue_expenditure&timeline=month",
        "/dashboard/api/chart-data/?type=purchases_sales&timeline=month",
    ],
    "clients": [
        "/clients/",
        "/clients/create/",
    ],
    "project_management": [
        "/projects/",
        "/projects/dashboard/",
    ],
    "leads": [
        "/leads/",
        "/leads/create/",
    ],
    "products": [
        "/products/",
        "/products/create/",
    ],
    "sales": [
        "/sales/",
        "/sales/create/",
    ],
    "purchases": [
        "/purchases/",
        "/purchases/create/",
    ],
    "documents": [
        "/documents/",
        "/documents/quotes/",
        "/documents/quotes/create/",
    ],
    "expenses": [
        "/expenses/",
        "/expenses/create/",
    ],
    "banking": [
        "/banking/",
        "/banking/dashboard/",
    ],
    "reports": [
        "/reports/",
        "/reports/dashboard/",
    ],
}

results = {
    "success": [],
    "error": [],
    "not_found": [],
    "server_error": [],
    "login_required": [],
    "redirect": []
}

def login():
    """Log in to the application and return a session"""
    session = requests.Session()
    
    # Get the login page to extract CSRF token
    login_url = f"{BASE_URL}/auth/login/"
    response = session.get(login_url)
    
    if response.status_code != 200:
        print(f"Failed to get login page: {response.status_code}")
        return None
    
    # Parse the login page to extract CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_input:
        print("Failed to find CSRF token on login page")
        return None
    
    csrf_token = csrf_input.get('value', '')
    print(f"Found CSRF token: {csrf_token[:10]}...")
    
    # Prepare login data
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': USERNAME,
        'password': PASSWORD,
        'role': ROLE
    }
    
    print(f"Submitting login form with data: username={USERNAME}, role={ROLE}")
    
    # Submit login form
    login_response = session.post(
        login_url,
        data=login_data,
        headers={'Referer': login_url}
    )
    
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response URL: {login_response.url}")
    
    # Check for error messages in the response
    if login_response.status_code == 200 and 'login' in login_response.url:
        soup = BeautifulSoup(login_response.text, 'html.parser')
        error_msgs = soup.select('.alert-error')
        if error_msgs:
            for error in error_msgs:
                print(f"Login error message: {error.text.strip()}")
            return None
    
    # Check if we were redirected to profile selection page
    if "profile-selection" in login_response.url:
        print("Redirected to profile selection page. Processing profile selection...")
        
        # Parse the profile selection page
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Look for profile cards with the specific HTML structure
        profile_links = soup.select('.profile-card')
        
        if not profile_links:
            print("No profile cards found on the selection page")
            return None
        
        # Find the first profile card that is not the "New Profile" option
        profile_url = None
        for link in profile_links:
            if 'add-profile' not in link.get('class', []):
                profile_url = link.get('href')
                profile_name = link.select_one('.profile-name').text.strip() if link.select_one('.profile-name') else "Unknown"
                print(f"Found profile: {profile_name} (URL: {profile_url})")
                break
        
        if not profile_url:
            print("No existing profile found, only 'New Profile' option")
            return None
        
        # Select the profile
        profile_full_url = f"{BASE_URL}{profile_url}"
        print(f"Selecting profile at: {profile_full_url}")
        profile_response = session.get(profile_full_url)
        
        print(f"Profile selection response status: {profile_response.status_code}")
        print(f"Profile selection response URL: {profile_response.url}")
        
        # Now we need to submit the PIN
        pin_soup = BeautifulSoup(profile_response.text, 'html.parser')
        pin_csrf_token = pin_soup.select_one('input[name="csrfmiddlewaretoken"]')
        
        if not pin_csrf_token:
            print("Failed to find CSRF token on PIN page")
            return None
        
        # Submit PIN (using correct PIN '1122')
        pin_data = {
            'csrfmiddlewaretoken': pin_csrf_token['value'],
            'pin': '1122'  # Using the PIN provided by the user
        }
        
        print(f"Submitting PIN for profile")
        pin_submit_response = session.post(
            profile_response.url,
            data=pin_data,
            headers={'Referer': profile_response.url}
        )
        
        print(f"PIN submission status: {pin_submit_response.status_code}")
        print(f"PIN submission URL: {pin_submit_response.url}")
        
        # Now try accessing the dashboard
        dashboard_url = f"{BASE_URL}/dashboard/"
        print(f"Accessing dashboard at: {dashboard_url}")
        dashboard_response = session.get(dashboard_url)
        
        print(f"Dashboard access response status: {dashboard_response.status_code}")
        print(f"Dashboard access response URL: {dashboard_response.url}")
        
        if "/dashboard/" not in dashboard_response.url:
            print(f"Dashboard access failed: Redirected to {dashboard_response.url}")
            return None
    
    # Final check that we can access the dashboard
    dashboard_test_url = f"{BASE_URL}/dashboard/"
    dashboard_test_response = session.get(dashboard_test_url)
    
    if "/dashboard/" not in dashboard_test_response.url:
        print(f"Final dashboard access check failed: Redirected to {dashboard_test_response.url}")
        return None
    
    print("Login and profile selection successful. Ready to test URLs.")
    return session

def check_url(session, url):
    """Check if URL can be accessed, return status and error message if any"""
    try:
        response = session.get(url)
        
        if response.status_code == 200:
            return {"status": "success", "code": 200}
        elif response.status_code == 302:
            # Check if redirecting to login page
            location = response.headers.get('Location', '')
            if 'login' in location:
                return {"status": "login_required", "code": 302, "location": location}
            else:
                return {"status": "redirect", "code": 302, "location": location}
        elif response.status_code == 404:
            return {"status": "not_found", "code": 404}
        elif response.status_code == 500:
            # Extract error message from page if possible
            error_msg = "Unknown server error"
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                error_div = soup.select_one('.traceback')
                if error_div:
                    error_msg = error_div.text[:200] + "..."  # Truncate long error messages
            except:
                pass
            return {"status": "server_error", "code": 500, "message": error_msg}
        else:
            return {"status": "error", "code": response.status_code}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

def main():
    print(f"Testing authenticated URLs at {BASE_URL}...")
    print(f"Logging in with username: {USERNAME}")
    
    # Login first
    session = login()
    if not session:
        print("Failed to log in. Cannot proceed with tests.")
        return 0
    
    print("\nLogin successful. Proceeding with URL tests...")
    
    total_count = sum(len(paths) for paths in PATHS.values())
    success_count = 0
    
    # Check each URL
    for app, paths in PATHS.items():
        print(f"\nTesting {app} app URLs...")
        
        for path in paths:
            url = f"{BASE_URL}{path}"
            print(f"  Checking {url}... ", end="", flush=True)
            result = check_url(session, url)
            
            if result["status"] == "success":
                results["success"].append({"url": url, "app": app})
                print("OK")
                success_count += 1
            elif result["status"] == "redirect":
                # Some redirects are expected and fine
                redirect_url = result.get("location", "")
                print(f"REDIRECT -> {redirect_url}")
                results["redirect"].append({"url": url, "app": app, "redirect_to": redirect_url})
                success_count += 1  # Still count redirects as success
            else:
                category = result["status"]
                results[category].append({"url": url, "app": app, "details": result})
                print(f"FAILED ({result['status']}, code: {result.get('code', 'unknown')})")
                if result["status"] == "server_error":
                    print(f"    Error: {result.get('message', 'Unknown error')}")
            
            # Small delay to avoid overloading the server
            time.sleep(0.2)
    
    # Print summary
    print("\n--- URL Test Summary ---")
    print(f"Total URLs tested: {total_count}")
    print(f"Success: {len(results['success'])}")
    print(f"Redirects: {len(results['redirect'])}")
    print(f"Login required: {len(results['login_required'])}")
    print(f"Not found (404): {len(results['not_found'])}")
    print(f"Server errors (500): {len(results['server_error'])}")
    print(f"Other errors: {len(results['error'])}")
    
    # Detailed error reporting
    if len(results['error']) > 0 or len(results['not_found']) > 0 or len(results['server_error']) > 0:
        print("\n--- Detailed Error Report ---")
        
        if len(results['server_error']) > 0:
            print("\n500 Server Errors:")
            for item in results['server_error']:
                print(f"  {item['url']} ({item['app']})")
                if 'message' in item['details']:
                    print(f"    Error: {item['details']['message']}")
        
        if len(results['not_found']) > 0:
            print("\n404 Not Found Errors:")
            for item in results['not_found']:
                print(f"  {item['url']} ({item['app']})")
        
        if len(results['error']) > 0:
            print("\nOther Errors:")
            for item in results['error']:
                print(f"  {item['url']} ({item['app']}): {item['details'].get('message', 'Unknown error')}")

    # Save results to JSON file
    with open('auth_url_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to auth_url_test_results.json")
    
    # Return success rate
    success_rate = (success_count) / total_count
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = main()
        if success_rate >= 0.9:
            print("\nTest PASSED: Most URLs working correctly")
            sys.exit(0)
        else:
            print("\nTest FAILED: Too many URL errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        sys.exit(1) 
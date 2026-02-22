import requests
from bs4 import BeautifulSoup
import sys

# Base URL for the server
BASE_URL = "http://127.0.0.1:8000"

def debug_auth_flow():
    session = requests.Session()
    
    # Step 1: Get login page
    print("Step 1: Accessing login page")
    login_url = f"{BASE_URL}/auth/login/"
    login_response = session.get(login_url)
    
    print(f"Status: {login_response.status_code}")
    print(f"URL: {login_response.url}")
    
    # Extract CSRF token
    login_soup = BeautifulSoup(login_response.text, 'html.parser')
    csrf_token = login_soup.select_one('input[name="csrfmiddlewaretoken"]')['value']
    print(f"CSRF Token: {csrf_token[:10]}...")
    
    # Step 2: Submit login form
    print("\nStep 2: Submitting login credentials")
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': 'admin',
        'password': 'pass',
        'role': 'administrator'
    }
    
    login_submit = session.post(
        login_url,
        data=login_data,
        headers={'Referer': login_url}
    )
    
    print(f"Status: {login_submit.status_code}")
    print(f"URL: {login_submit.url}")
    
    # Display cookies
    print("\nCookies after login:")
    for cookie, value in session.cookies.items():
        print(f"  {cookie}: {value}")
    
    # Step 3: Get profile selection page
    if 'profile-selection' in login_submit.url:
        print("\nStep 3: Accessing profile selection page")
        profile_selection_url = login_submit.url
        profile_soup = BeautifulSoup(login_submit.text, 'html.parser')
        
        # Find profile cards
        profile_cards = profile_soup.select('.profile-card')
        print(f"Found {len(profile_cards)} profile cards")
        
        if profile_cards:
            for i, card in enumerate(profile_cards):
                is_add = 'add-profile' in card.get('class', [])
                if not is_add:
                    profile_url = card.get('href')
                    profile_name = card.select_one('.profile-name').text.strip() if card.select_one('.profile-name') else "Unknown"
                    print(f"Profile {i+1}: {profile_name}, URL: {profile_url}")
                    
                    # Step 4: Select the first real profile
                    print(f"\nStep 4: Selecting profile: {profile_name}")
                    profile_full_url = f"{BASE_URL}{profile_url}"
                    profile_response = session.get(profile_full_url)
                    
                    print(f"Status: {profile_response.status_code}")
                    print(f"URL: {profile_response.url}")
                    
                    # Extract form details for PIN submission
                    pin_soup = BeautifulSoup(profile_response.text, 'html.parser')
                    pin_form = pin_soup.select_one('form')
                    
                    if pin_form:
                        print("\nPIN form found:")
                        print(f"Action: {pin_form.get('action', 'Same URL')}")
                        print(f"Method: {pin_form.get('method', 'POST')}")
                        
                        # Display form fields
                        for field in pin_form.select('input'):
                            field_name = field.get('name', 'unnamed')
                            field_type = field.get('type', 'text')
                            print(f"  Field: {field_name}, Type: {field_type}")
                        
                        # Extract CSRF token
                        pin_csrf = pin_soup.select_one('input[name="csrfmiddlewaretoken"]')
                        if pin_csrf:
                            pin_csrf_token = pin_csrf['value']
                            print(f"PIN CSRF Token: {pin_csrf_token[:10]}...")
                            
                            # Step 5: Submit PIN
                            print("\nStep 5: Submitting PIN")
                            # Use the PIN provided by the user
                            pin = '1122'  # temporary pin by the user
                            print(f"Trying PIN: {pin}")
                            pin_data = {
                                'csrfmiddlewaretoken': pin_csrf_token,
                                'pin': pin
                            }
                            
                            pin_submit = session.post(
                                profile_response.url,
                                data=pin_data,
                                headers={'Referer': profile_response.url}
                            )
                            
                            print(f"Status: {pin_submit.status_code}")
                            print(f"URL: {pin_submit.url}")
                            
                            # Check if we got redirected to dashboard
                            if '/dashboard/' in pin_submit.url:
                                print(f"Success! Authenticated with PIN: {pin}")
                                
                                # Final check
                                dashboard_url = f"{BASE_URL}/dashboard/"
                                dashboard_response = session.get(dashboard_url)
                                
                                print(f"\nFinal dashboard check:")
                                print(f"Status: {dashboard_response.status_code}")
                                print(f"URL: {dashboard_response.url}")
                                
                                if '/dashboard/' in dashboard_response.url:
                                    print("SUCCESS: Authentication flow complete!")
                                    return True
                                else:
                                    print(f"Dashboard access failed, redirected to: {dashboard_response.url}")
                            else:
                                print(f"PIN '{pin}' failed")
                                
                                # Check for error message
                                error_soup = BeautifulSoup(pin_submit.text, 'html.parser')
                                error_msgs = error_soup.select('.alert-danger, .alert-error')
                                if error_msgs:
                                    for error in error_msgs:
                                        print(f"Error message: {error.text.strip()}")
                        else:
                            print("Could not find CSRF token in PIN form")
                            break
                    else:
                        print("No PIN form found on profile selection page")
                    break
    else:
        print(f"Unexpected URL after login: {login_submit.url}")
    
    # No valid profile or all PIN attempts failed, try creating a new profile
    print("\nStep 4 alternative: Creating a new profile")
    # Navigate to the profile creation page
    profile_create_url = f"{BASE_URL}/auth/profile/create/"
    profile_create_response = session.get(profile_create_url)
    
    print(f"Status: {profile_create_response.status_code}")
    print(f"URL: {profile_create_response.url}")
    
    # Extract the form details
    create_soup = BeautifulSoup(profile_create_response.text, 'html.parser')
    print("\nAuthentication flow failed")
    return False

if __name__ == "__main__":
    try:
        success = debug_auth_flow()
        if success:
            print("\nAuthentication flow PASSED")
            sys.exit(0)
        else:
            print("\nAuthentication flow FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\nScript failed with error: {str(e)}")
        sys.exit(1) 
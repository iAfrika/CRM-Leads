import requests
import sys
from bs4 import BeautifulSoup

def test_register_page(username, password):
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
    
    print(f"Login successful, redirected to: {login_post_response.url}")
    
    # Try to access the register page
    register_url = 'http://localhost:8000/people/register/'
    register_response = session.get(register_url, allow_redirects=True)
    
    # Print the final URL after redirects
    print(f"Register page URL after redirects: {register_response.url}")
    
    # Check if we can access the register page
    if register_response.status_code == 200 and 'people/register' in register_response.url:
        print("Successfully accessed the register page!")
        
        # Parse the HTML to check the content
        soup = BeautifulSoup(register_response.text, 'html.parser')
        page_title = soup.title.text if soup.title else "No title found"
        print(f"Page title: {page_title}")
        
        # Check if the form is rendered correctly
        form = soup.find('form')
        if form:
            # Check if the form has input fields
            inputs = form.find_all(['input', 'textarea', 'select'])
            if inputs:
                print(f"Found {len(inputs)} form fields")
                return True
            else:
                print("Form has no input fields")
                return False
        else:
            print("No form found on the page")
            return False
    else:
        print(f"Failed to access register page. Current URL: {register_response.url}")
        print(f"Response status code: {register_response.status_code}")
        print(f"Response content: {register_response.text[:500]}...")  # Print first 500 chars
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_register_page.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    result = test_register_page(username, password)
    
    if result:
        print("Test passed: Register page is working correctly")
    else:
        print("Test failed: Register page is not working correctly") 
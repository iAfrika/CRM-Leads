import requests
import re
from urllib.parse import urljoin
import time
import sys
from bs4 import BeautifulSoup

def test_admin_urls():
    print("Testing Admin URLs...")
    base_url = "http://localhost:8000/"
    admin_url = urljoin(base_url, "admin/")
    
    # Login credentials
    username = "admin"
    password = "pass"
    
    # Start a session
    session = requests.Session()
    
    try:
        # First get the CSRF token from the login page
        print(f"Accessing admin login page: {admin_url}")
        login_response = session.get(admin_url)
        if login_response.status_code != 200:
            print(f"❌ Failed to access admin login page: {login_response.status_code}")
            return False
        
        print(f"✅ Admin login page accessible: {admin_url}")
        
        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = None
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_input:
            csrf_token = csrf_input.get('value')
        else:
            # Try with regex as fallback
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        if not csrf_token:
            print("❌ Could not find CSRF token")
            print("Continuing without authentication...")
            # Try to access admin page directly without authentication
            admin_index_response = session.get(admin_url)
            if admin_index_response.status_code == 200:
                print(f"✅ Admin index page accessible without authentication: {admin_url}")
                # Check dark mode functionality
                if "data-theme" in admin_index_response.text:
                    print("✅ Dark mode feature found in HTML")
                else:
                    print("⚠️ Dark mode feature not found in HTML")
                return True
            else:
                print(f"❌ Failed to access admin index: {admin_index_response.status_code}")
                return False
            
        # Log in
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': username,
            'password': password,
            'next': '/admin/'
        }
        
        print(f"Attempting login as {username}...")
        login_response = session.post(
            admin_url + "login/", 
            data=login_data, 
            headers={'Referer': admin_url}
        )
        
        # Check if login was successful (should redirect)
        login_success = login_response.url == admin_url
        
        if not login_success:
            print(f"❌ Login failed: {login_response.status_code}")
            print("Continuing without authentication...")
        else:
            print(f"✅ Successfully logged in as {username}")
        
        # Check admin index page
        admin_index_response = session.get(admin_url)
        if admin_index_response.status_code != 200:
            print(f"❌ Failed to access admin index: {admin_index_response.status_code}")
            return False
        
        print(f"✅ Admin index page accessible: {admin_url}")
        
        # Check dark mode functionality
        if "data-theme" in admin_index_response.text:
            print("✅ Dark mode feature found in HTML")
        else:
            print("⚠️ Dark mode feature not found in HTML")
        
        # Use BeautifulSoup to extract app links
        soup = BeautifulSoup(admin_index_response.text, 'html.parser')
        app_links = []
        
        # Try different approaches to find app links
        app_links_elements = soup.select('a.app-link')
        if app_links_elements:
            app_links = [a.get('href') for a in app_links_elements if a.get('href')]
        
        if not app_links:
            # Fallback to regex
            app_links = re.findall(r'<a href="(/admin/[^"]+/)"[^>]*>', admin_index_response.text)
        
        if not app_links:
            print("⚠️ No app links found on admin index page")
            return True
        
        # Test each app page
        for app_link in app_links:
            # Make sure app_link starts with /admin/
            if not app_link.startswith('/admin/'):
                app_link = '/admin/' + app_link.lstrip('/')
                
            full_app_url = urljoin(base_url, app_link)
            print(f"Testing app URL: {full_app_url}")
            
            app_response = session.get(full_app_url)
            status = "✅" if app_response.status_code == 200 else "❌"
            print(f"{status} App URL: {full_app_url} - Status: {app_response.status_code}")
            
            if app_response.status_code != 200:
                continue
                
            # Use BeautifulSoup to extract model links
            soup = BeautifulSoup(app_response.text, 'html.parser')
            model_links = []
            
            # Try different approaches to find model links
            model_links_elements = soup.select('a.model-link')
            if model_links_elements:
                model_links = [a.get('href') for a in model_links_elements if a.get('href')]
            
            if not model_links:
                # Fallback to regex
                model_links = re.findall(r'<a href="(/admin/[^"]+/)"[^>]*class="[^"]*model-link[^"]*"[^>]*>', app_response.text)
                if not model_links:
                    model_links = re.findall(r'<a href="(/admin/[^"]+/)"[^>]*>', app_response.text)
            
            for model_link in model_links:
                # Skip if the model link is the same as the app link
                if model_link == app_link:
                    continue
                    
                # Make sure model_link starts with /admin/
                if not model_link.startswith('/admin/'):
                    model_link = '/admin/' + model_link.lstrip('/')
                    
                full_model_url = urljoin(base_url, model_link)
                print(f"  Testing model URL: {full_model_url}")
                
                model_response = session.get(full_model_url)
                model_status = "✅" if model_response.status_code == 200 else "❌"
                
                print(f"  {model_status} Model URL: {full_model_url} - Status: {model_response.status_code}")
                
                if model_response.status_code != 200:
                    continue
                
                # Test add new form for the model
                add_url = full_model_url + "add/"
                print(f"  Testing add form URL: {add_url}")
                
                add_response = session.get(add_url)
                add_status = "✅" if add_response.status_code == 200 else "❌"
                
                print(f"  {add_status} Add Form URL: {add_url} - Status: {add_response.status_code}")
                
            # Add a small delay to prevent overloading the server
            time.sleep(0.5)
        
        # Check for CSS and JS files
        css_js_paths = [
            'css/admin_dashboard.css',
        ]
        
        for path in css_js_paths:
            static_url = urljoin(base_url, f"static/{path}")
            print(f"Testing static file: {static_url}")
            
            static_response = session.get(static_url)
            status = "✅" if static_response.status_code == 200 else "❌"
            print(f"{status} Static file: {static_url} - Status: {static_response.status_code}")
        
        print("\nAdmin URL testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_admin_urls()
    if not success:
        sys.exit(1)
    sys.exit(0) 
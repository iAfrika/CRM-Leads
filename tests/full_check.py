import os
import re
import sys
import requests
from urllib.parse import urljoin

def check_css_exists():
    """Check if the CSS file exists in the expected locations"""
    print("\n=== Checking CSS File Existence ===")
    
    # Potential paths for the CSS file
    css_paths = [
        os.path.join('people', 'static', 'css', 'people_styles.css'),
        os.path.join('static', 'css', 'people_styles.css'),
        os.path.join('staticfiles', 'css', 'people_styles.css')
    ]
    
    css_found = False
    
    for path in css_paths:
        if os.path.exists(path):
            print(f"✅ CSS file found at: {path}")
            
            # Show a preview of the CSS file
            try:
                with open(path, 'r') as f:
                    content = f.read(500)  # Read first 500 characters
                    print("\nCSS Preview:")
                    print("-" * 40)
                    print(content)
                    print("-" * 40)
                css_found = True
            except Exception as e:
                print(f"❌ Error reading CSS file: {e}")
    
    if not css_found:
        print("❌ CSS file 'people_styles.css' not found in any of the expected locations.")
    
    return css_found

def check_template_references():
    """Check if the templates properly reference the CSS file"""
    print("\n=== Checking Template References ===")
    
    # Template files to check
    template_paths = [
        os.path.join('people', 'templates', 'people', 'base.html'),
        os.path.join('people', 'templates', 'people', 'people_list.html'),
        os.path.join('people', 'templates', 'people', 'register.html'),
        os.path.join('people', 'templates', 'people', 'person_detail.html'),
        os.path.join('people', 'templates', 'people', 'contact_form.html')
    ]
    
    all_ok = True
    
    for path in template_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    
                    # Check for CSS reference - accounting for Django template syntax
                    if 'people_styles.css' in content:
                        # Match both standard HTML links and Django template tags
                        css_pattern = r'<link\s+[^>]*href="(?:[^"]*|{% static \'css/people_styles\.css\' %})"[^>]*>'
                        django_pattern = r'<link\s+[^>]*href="{% static \'css/people_styles\.css\' %}"[^>]*>'
                        
                        if re.search(css_pattern, content) or re.search(django_pattern, content):
                            print(f"✅ Template {path} properly references people_styles.css")
                        else:
                            print(f"⚠️ Template {path} mentions people_styles.css but not in expected format")
                            all_ok = False
                    else:
                        # If it's not base.html, this might be fine as the CSS could be inherited
                        if 'base.html' in path:
                            print(f"❌ Base template {path} does not reference people_styles.css!")
                            all_ok = False
                        else:
                            print(f"ℹ️ Template {path} does not directly reference people_styles.css (may inherit from base)")
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
                all_ok = False
        else:
            print(f"❌ Template file not found: {path}")
            all_ok = False
    
    return all_ok

def check_static_url_settings():
    """Check if Django static URL settings are properly configured"""
    print("\n=== Checking Static URL Configuration ===")
    
    # Check settings.py file
    settings_file = 'crm_leads/settings.py'
    static_url_configured = False
    static_dirs_configured = False
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                content = f.read()
                
                # Check for STATIC_URL setting
                static_url_match = re.search(r"STATIC_URL\s*=\s*['\"]([^'\"]+)['\"]", content)
                if static_url_match:
                    static_url = static_url_match.group(1)
                    print(f"✅ STATIC_URL found in settings.py: {static_url}")
                    static_url_configured = True
                else:
                    print("❌ STATIC_URL setting not found in settings.py")
                
                # Check for STATICFILES_DIRS setting
                if 'STATICFILES_DIRS' in content:
                    print("✅ STATICFILES_DIRS setting found in settings.py")
                    static_dirs_configured = True
                else:
                    print("⚠️ STATICFILES_DIRS setting not found in settings.py (may use default)")
        except Exception as e:
            print(f"❌ Error reading settings.py: {e}")
    else:
        print(f"❌ Settings file not found at {settings_file}")
    
    return static_url_configured and static_dirs_configured

def check_running_server():
    """Check if the Django server is running and serving static files"""
    print("\n=== Checking Server Accessibility ===")
    
    base_url = "http://localhost:8000"
    css_url = urljoin(base_url, "/static/css/people_styles.css")
    
    try:
        response = requests.get(base_url, timeout=2)
        if response.status_code == 200:
            print(f"✅ Django server is running at {base_url} (Status: {response.status_code})")
            
            # Check if CSS is accessible
            try:
                css_response = requests.get(css_url, timeout=2)
                if css_response.status_code == 200:
                    print(f"✅ CSS file is accessible at {css_url} (Status: {css_response.status_code})")
                    return True
                else:
                    print(f"❌ CSS file is not accessible at {css_url} (Status: {css_response.status_code})")
            except Exception as e:
                print(f"❌ Error accessing CSS file: {e}")
        else:
            print(f"❌ Django server not responding correctly at {base_url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error connecting to Django server: {e}")
    
    return False

def main():
    """Run all checks and report findings"""
    print("=== People App CSS Verification ===")
    
    # Run all checks
    css_exists = check_css_exists()
    template_refs_ok = check_template_references()
    static_settings_ok = check_static_url_settings()
    server_ok = check_running_server()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"CSS File Exists: {'✅' if css_exists else '❌'}")
    print(f"Template References: {'✅' if template_refs_ok else '❌'}")
    print(f"Static Settings: {'✅' if static_settings_ok else '❌'}")
    print(f"Server Running: {'✅' if server_ok else '❌'}")
    
    # Overall status
    if css_exists and template_refs_ok and static_settings_ok and server_ok:
        print("\n✅ All checks passed! The People app CSS is properly configured and accessible.")
        return 0
    else:
        print("\n⚠️ Some issues were found. Please check the details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
import os
import sys

def check_css_files():
    """Check if all required CSS files exist in the correct locations."""
    # Base CSS in static/css
    base_css = os.path.join('static', 'css', 'base.css')
    print(f"Checking {base_css}: {'Exists' if os.path.exists(base_css) else 'Missing'}")
    
    # People CSS in people/static/people/css
    people_css = os.path.join('people', 'static', 'people', 'css', 'people.css')
    print(f"Checking {people_css}: {'Exists' if os.path.exists(people_css) else 'Missing'}")
    
    # People list CSS
    people_list_css = os.path.join('people', 'static', 'people', 'css', 'people_list.css')
    print(f"Checking {people_list_css}: {'Exists' if os.path.exists(people_list_css) else 'Missing'}")
    
    # Person detail CSS
    person_detail_css = os.path.join('people', 'static', 'people', 'css', 'person_detail.css')
    print(f"Checking {person_detail_css}: {'Exists' if os.path.exists(person_detail_css) else 'Missing'}")
    
    # Register CSS
    register_css = os.path.join('people', 'static', 'people', 'css', 'register.css')
    print(f"Checking {register_css}: {'Exists' if os.path.exists(register_css) else 'Missing'}")
    
    # Contact form CSS
    contact_form_css = os.path.join('people', 'static', 'people', 'css', 'contact_form.css')
    print(f"Checking {contact_form_css}: {'Exists' if os.path.exists(contact_form_css) else 'Missing'}")
    
    # Print current directory for reference
    print(f"Current directory: {os.getcwd()}")
    
    # List all files in the static directory
    print("\nListing files in static directory:")
    try:
        for root, dirs, files in os.walk('static'):
            print(f"Directory: {root}")
            for file in files:
                print(f"  - {file}")
    except Exception as e:
        print(f"Error listing static directory: {e}")
    
    # List all files in the people/static directory
    print("\nListing files in people/static directory:")
    try:
        for root, dirs, files in os.walk('people/static'):
            print(f"Directory: {root}")
            for file in files:
                print(f"  - {file}")
    except Exception as e:
        print(f"Error listing people/static directory: {e}")

if __name__ == "__main__":
    check_css_files() 
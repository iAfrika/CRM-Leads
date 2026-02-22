import os
import re
import sys

def check_template_references():
    """Check if the templates properly reference the CSS file"""
    print("Checking template references to people_styles.css...")
    
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

if __name__ == "__main__":
    if check_template_references():
        print("\n✅ All template references to CSS files appear to be correctly configured.")
        sys.exit(0)
    else:
        print("\n⚠️ Some issues were found with template references to CSS files.")
        sys.exit(1) 
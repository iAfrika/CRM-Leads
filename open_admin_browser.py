import webbrowser
import sys

def open_admin_pages():
    """Opens the admin dashboard in the default browser."""
    base_url = "http://localhost:8000/"
    admin_url = base_url + "admin/"
    
    print(f"Opening admin dashboard at {admin_url}")
    webbrowser.open(admin_url)
    
    print("Please manually verify the following:")
    print("1. Each app has its own card with an appropriate icon")
    print("2. The Recent Actions section has been restyled and width reduced")
    print("3. The dark mode toggle works and applies to the sidebar and top nav")
    print("4. The overall layout is visually appealing")
    
    return True

if __name__ == "__main__":
    success = open_admin_pages()
    if not success:
        sys.exit(1)
    sys.exit(0) 
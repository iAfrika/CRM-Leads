import webbrowser
import sys

def open_in_browser():
    """Open the People app in the default browser"""
    print("Opening People app in the default browser for manual verification...")
    
    # URLs to open
    urls = [
        "http://localhost:8000/people/",
        "http://localhost:8000/people/register/",
        "http://localhost:8000/people/contact/"
    ]
    
    # Open each URL in a new tab
    for url in urls:
        print(f"Opening {url}")
        webbrowser.open_new_tab(url)
    
    print("\nPlease manually verify in your browser that:")
    print("1. The People app pages load correctly")
    print("2. The CSS styling is properly applied")
    print("3. The layout and design are consistent with the rest of the application")
    
    return True

if __name__ == "__main__":
    if open_in_browser():
        sys.exit(0)
    else:
        sys.exit(1) 
import webbrowser
import sys

def open_in_browser():
    """Open the Project app in the default browser for manual verification"""
    print("Opening Project app in the default browser for manual verification...")
    
    # URLs to open
    urls = [
        "http://localhost:8000/projects/",
        "http://localhost:8000/projects/create/",
        "http://localhost:8000/projects/dashboard/"
    ]
    
    # Open each URL in a new tab
    for url in urls:
        print(f"Opening {url}")
        webbrowser.open_new_tab(url)
    
    print("\nPlease manually verify in your browser that:")
    print("1. The Project app pages load correctly with the sidebar")
    print("2. The CSS styling is properly applied")
    print("3. The layout and design are consistent with the rest of the application")
    print("4. The sidebar navigation works correctly")
    
    return True

if __name__ == "__main__":
    if open_in_browser():
        sys.exit(0)
    else:
        sys.exit(1) 
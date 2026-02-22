import os
import sys

def check_css_exists():
    """Check if the people_styles.css file exists in the correct location"""
    print("Checking if people_styles.css exists...")
    
    # Potential paths where the CSS file might be
    paths_to_check = [
        os.path.join('people', 'static', 'css', 'people_styles.css'),
        os.path.join('static', 'css', 'people_styles.css'),
        os.path.join('staticfiles', 'css', 'people_styles.css')
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            print(f"✅ Found CSS file at: {path}")
            
            # Display first few lines of the file
            try:
                with open(path, 'r') as f:
                    content = f.read(300)  # Read first 300 chars
                    print("\nCSS File Preview:")
                    print("-" * 50)
                    print(content)
                    print("-" * 50)
            except Exception as e:
                print(f"Error reading file: {e}")
                
            return True
    
    print("❌ CSS file not found in any of the standard locations")
    return False

if __name__ == "__main__":
    if check_css_exists():
        print("✅ CSS file exists and can be read. Static files configuration appears to be working.")
        sys.exit(0)
    else:
        print("❌ CSS file not found. Please check your static files configuration.")
        sys.exit(1) 
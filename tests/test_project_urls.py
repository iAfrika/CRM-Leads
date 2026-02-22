import requests
import sys
import json

def test_project_urls():
    """Test if all project management URLs are working."""
    base_url = "http://127.0.0.1:8000"
    
    # First, check if the server is running
    try:
        response = requests.get(f"{base_url}/admin/", allow_redirects=False)
        if response.status_code in [200, 302]:
            print("Server is running!")
        else:
            print(f"Server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error accessing server: {e}")
        return False
    
    # Define the URLs to test
    project_urls = [
        # Project URLs
        "/projects/",
        "/projects/create/",
        "/projects/1/",
        "/projects/1/update/",
        "/projects/1/finances/",
        
        # Dashboard URLs
        "/projects/dashboard/",
        "/projects/analytics/",
        
        # Document URLs
        "/projects/1/documents/create/",
        
        # Milestone URLs
        "/projects/1/milestones/create/",
        
        # Note URLs
        "/projects/1/notes/create/",
    ]
    
    # Test each URL
    results = {}
    success_count = 0
    
    for url in project_urls:
        full_url = f"{base_url}{url}"
        print(f"Testing URL: {full_url}")
        
        try:
            response = requests.get(full_url, allow_redirects=False)
            status_code = response.status_code
            
            if status_code in [200, 302]:
                print(f"SUCCESS: {url} is accessible (Status: {status_code})")
                results[url] = {"status": "success", "code": status_code}
                success_count += 1
            else:
                print(f"ERROR: {url} returned status code {status_code}")
                results[url] = {"status": "error", "code": status_code}
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            results[url] = {"status": "exception", "error": str(e)}
    
    # Save results to a file
    with open("project_urls_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n--- URL Test Summary ---")
    print(f"Total URLs tested: {len(project_urls)}")
    print(f"Success: {success_count}")
    print(f"Failed: {len(project_urls) - success_count}")
    print(f"Success rate: {success_count / len(project_urls) * 100:.1f}%")
    print(f"Detailed results saved to project_urls_test_results.json")
    
    return success_count == len(project_urls)

if __name__ == "__main__":
    success = test_project_urls()
    sys.exit(0 if success else 1) 
import urllib.request
import urllib.error
import sys
import time
import json

# Base URL for the server
BASE_URL = "http://127.0.0.1:8000"

# List of paths to check, organized by app
PATHS = {
    "authentication": [
        "/auth/login/",
        "/auth/logout/",
        "/auth/profile/"
    ],
    "dashboard": [
        "/dashboard/",
        "/dashboard/schedule/",
        "/dashboard/calendar/",
        "/dashboard/statistics/",
        "/dashboard/api/chart-data/?type=quotes_invoices&timeline=month",
        "/dashboard/api/chart-data/?type=revenue_expenditure&timeline=month",
        "/dashboard/api/chart-data/?type=purchases_sales&timeline=month",
    ],
    "clients": [
        "/clients/",
        "/clients/create/",
    ],
    "project_management": [
        "/projects/",
        "/projects/dashboard/",
    ],
    "leads": [
        "/leads/",
        "/leads/create/",
    ],
    "products": [
        "/products/",
        "/products/create/",
    ],
    "sales": [
        "/sales/",
        "/sales/create/",
    ],
    "purchases": [
        "/purchases/",
        "/purchases/create/",
    ],
    "documents": [
        "/documents/",
        "/documents/quotes/",
        "/documents/quotes/create/",
    ],
    "expenses": [
        "/expenses/",
        "/expenses/create/",
    ],
    "banking": [
        "/banking/",
        "/banking/dashboard/",
    ],
    "reports": [
        "/reports/",
        "/reports/dashboard/",
    ],
}

results = {
    "success": [],
    "error": [],
    "not_found": [],
    "server_error": [],
    "login_required": []
}

def check_url(url):
    """Check if URL can be accessed, return status and error message if any"""
    try:
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            return {"status": "success", "code": 200}
        else:
            return {"status": "error", "code": response.getcode()}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"status": "not_found", "code": 404}
        elif e.code == 500:
            return {"status": "server_error", "code": 500}
        elif e.code == 302:
            # Check if redirecting to login page
            if e.headers.get('Location') and 'login' in e.headers.get('Location'):
                return {"status": "login_required", "code": 302}
            else:
                return {"status": "redirect", "code": 302, "location": e.headers.get('Location')}
        else:
            return {"status": "error", "code": e.code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print(f"Testing URLs at {BASE_URL}...")
    print("This will check each URL and report any issues.")
    print()
    
    total_count = sum(len(paths) for paths in PATHS.values())
    success_count = 0
    
    # Check each URL
    for app, paths in PATHS.items():
        print(f"Testing {app} app URLs...")
        
        for path in paths:
            url = f"{BASE_URL}{path}"
            print(f"  Checking {url}... ", end="")
            result = check_url(url)
            
            if result["status"] == "success":
                results["success"].append({"url": url, "app": app})
                print("OK")
                success_count += 1
            else:
                category = result["status"]
                results[category].append({"url": url, "app": app, "details": result})
                print(f"FAILED ({result['status']}, code: {result.get('code', 'unknown')})")
            
            # Small delay to avoid overloading the server
            time.sleep(0.1)
    
    # Print summary
    print("\n--- URL Test Summary ---")
    print(f"Total URLs tested: {total_count}")
    print(f"Success: {len(results['success'])}")
    print(f"Login required: {len(results['login_required'])}")
    print(f"Not found (404): {len(results['not_found'])}")
    print(f"Server errors (500): {len(results['server_error'])}")
    print(f"Other errors: {len(results['error'])}")
    
    # Detailed error reporting
    if len(results['error']) > 0 or len(results['not_found']) > 0 or len(results['server_error']) > 0:
        print("\n--- Detailed Error Report ---")
        
        if len(results['not_found']) > 0:
            print("\n404 Not Found Errors:")
            for item in results['not_found']:
                print(f"  {item['url']} ({item['app']})")
        
        if len(results['server_error']) > 0:
            print("\n500 Server Errors:")
            for item in results['server_error']:
                print(f"  {item['url']} ({item['app']})")
        
        if len(results['error']) > 0:
            print("\nOther Errors:")
            for item in results['error']:
                print(f"  {item['url']} ({item['app']}): {item['details'].get('message', 'Unknown error')}")

    # Save results to JSON file
    with open('url_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nDetailed results saved to url_test_results.json")
    
    # Return success rate
    success_rate = (success_count + len(results['login_required'])) / total_count
    return success_rate

if __name__ == "__main__":
    success_rate = main()
    if success_rate >= 0.9:
        print("\nTest PASSED: Most URLs working correctly")
        sys.exit(0)
    else:
        print("\nTest FAILED: Too many URL errors")
        sys.exit(1) 
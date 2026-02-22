import requests
import sys

def test_server():
    """Test if the server is running."""
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", allow_redirects=False)
        print(f"Server status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("Server is running!")
            return True
        else:
            print("Server is not running properly.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1) 
"""
Test all API endpoints to find the issue
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None):
    """Test an endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        print(f"\n{'='*60}")
        print(f"Testing: {method} {path}")
        print(f"URL: {url}")
        print('='*60)
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unknown method: {method}")
            return
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                content = response.json()
                print(f"✅ Response: {json.dumps(content, indent=2)[:200]}...")
            except:
                print(f"✅ Response (text): {response.text[:200]}...")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Server not reachable at {BASE_URL}")
        print("   Make sure the server is running: python main.py")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Server took too long to respond")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("="*60)
    print("API Endpoint Tester")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    print("="*60)
    
    # Test endpoints
    endpoints = [
        ("GET", "/"),
        ("GET", "/api/health"),
        ("GET", "/docs"),
        ("GET", "/redoc"),
        ("GET", "/openapi.json"),
        ("GET", "/api/network/stats"),  # Will fail if no analysis run
        ("GET", "/api/communities"),  # Will fail if no analysis run
        ("POST", "/api/analyze", {}),
    ]
    
    for method, path, *args in endpoints:
        data = args[0] if args else None
        test_endpoint(method, path, data)
        import time
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "="*60)
    print("Testing Complete")
    print("="*60)
    print("\nIf you see connection errors:")
    print("1. Make sure server is running: python main.py")
    print("2. Check if port 8000 is available")
    print("3. Try: python start_server.py")
    print("\nIf endpoints return 404:")
    print("1. Check route registration")
    print("2. Verify api/main.py is correct")
    print("\nIf endpoints return 500:")
    print("1. Check server logs")
    print("2. Run: python test_server.py")

if __name__ == "__main__":
    main()


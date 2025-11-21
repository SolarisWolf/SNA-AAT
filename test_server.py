"""
Test script to diagnose server issues
"""
import sys
import traceback

print("="*60)
print("Testing Server Startup")
print("="*60)

try:
    print("\n1. Testing imports...")
    from config import API_HOST, API_PORT
    print(f"   ✅ Config loaded: Host={API_HOST}, Port={API_PORT}")
except Exception as e:
    print(f"   ❌ Config error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Testing API imports...")
    from api.main import app
    print("   ✅ API app imported successfully")
except Exception as e:
    print(f"   ❌ API import error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Checking routes...")
    routes = [route.path for route in app.routes]
    print(f"   ✅ Found {len(routes)} routes:")
    for route in routes[:5]:
        print(f"      - {route}")
    if len(routes) > 5:
        print(f"      ... and {len(routes) - 5} more")
except Exception as e:
    print(f"   ❌ Route check error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. Testing root endpoint handler...")
    from api.main import root
    import asyncio
    result = asyncio.run(root())
    print(f"   ✅ Root endpoint works: {result.get('message', 'OK')}")
except Exception as e:
    print(f"   ❌ Root endpoint error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ All tests passed! Server should work.")
print("="*60)
print("\nTo start the server, run:")
print("  python main.py")
print("\nOr:")
print("  uvicorn api.main:app --host 0.0.0.0 --port 8000")
print("\nThen access:")
print("  http://localhost:8000/")
print("  http://localhost:8000/docs")


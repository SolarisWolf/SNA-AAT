"""
Server startup script with better error handling
"""
import sys
import uvicorn
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import API_HOST, API_PORT, API_DEBUG
    print("="*60)
    print("Starting Multi-Layer Network Analysis API Server")
    print("="*60)
    print(f"Host: {API_HOST}")
    print(f"Port: {API_PORT}")
    print(f"Debug: {API_DEBUG}")
    print("="*60)
    print("\nServer will be available at:")
    print(f"  http://localhost:{API_PORT}/")
    print(f"  http://localhost:{API_PORT}/docs")
    print(f"  http://localhost:{API_PORT}/api/health")
    print("\nPress CTRL+C to stop the server")
    print("="*60)
    print()
    
    # Start server
    uvicorn.run(
        "api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\nServer stopped by user")
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


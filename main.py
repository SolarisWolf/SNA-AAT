"""
Main entry point for the Multi-Layer Network Analysis Backend
"""
import uvicorn
from config import API_HOST, API_PORT, API_DEBUG

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_DEBUG,
        log_level="info"
    )


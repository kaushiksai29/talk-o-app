"""
Root main.py for Railway deployment.
Runs the FastAPI backend with proper path setup.
"""
import os
import sys

# Add backend directory to Python path so imports work correctly
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

# Change working directory to backend so relative imports work
os.chdir(backend_dir)

# Now import the app from backend/main.py
from main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


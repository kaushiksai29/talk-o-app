"""
Root main.py for Railway deployment.
This file sets up the Python path and imports the FastAPI app from backend.
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

# Re-export app for uvicorn
__all__ = ["app"]

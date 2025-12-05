import os
import sys

# Add the project root to sys.path to allow importing from backend
# api/index.py -> api -> root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.main import app
except ImportError:
    from main import app

import os
import sys

# Add the project root to sys.path to allow importing from backend
# api/py/index.py -> api/py -> api -> root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.main import app

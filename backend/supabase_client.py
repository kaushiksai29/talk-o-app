import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Try loading from root .env first, then scripts/.env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../scripts/.env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found. Backend will start but DB features will fail.")
    supabase = None
else:
    try:
        supabase: Client = create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        supabase = None

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("documents").select("id", count="exact").execute()
    print(f"Total rows in 'documents': {response.count}")
except Exception as e:
    print(f"Error counting rows: {e}")

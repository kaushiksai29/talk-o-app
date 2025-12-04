import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("--- Clearing Documents Table ---")
try:
    # Delete all rows
    response = supabase.table("documents").delete().neq("id", 0).execute()
    print("Documents table cleared.")
except Exception as e:
    print(f"Error clearing table: {e}")

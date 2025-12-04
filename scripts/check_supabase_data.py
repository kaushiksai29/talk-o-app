import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase credentials.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n--- Checking Chat History ---")
response = supabase.table("chat_history").select("count", count="exact").execute()
print(f"Total Chat Messages: {response.count}")

response = supabase.table("chat_history").select("*").limit(5).execute()
print("Sample Messages:")
for row in response.data:
    print(f" - [{row.get('sender')}] {row.get('persona')}: {row.get('message')[:50]}... (User: {row.get('user_id')})")

print("\n--- Checking Profiles ---")
response = supabase.table("profiles").select("count", count="exact").execute()
print(f"Total Profiles: {response.count}")

response = supabase.table("profiles").select("*").limit(5).execute()
print("Sample Profiles:")
for row in response.data:
    print(f" - {row.get('email')} (ID: {row.get('id')})")

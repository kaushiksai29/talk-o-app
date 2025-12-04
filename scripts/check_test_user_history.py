import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env vars
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found.")
    sys.exit(1)

supabase: Client = create_client(url, key)

EMAIL = "acceptance_test@talk-o.app"

def check_history():
    print(f"Checking history for: {EMAIL}")
    
    # 1. Get User ID
    try:
        res = supabase.table("profiles").select("id").eq("email", EMAIL).single().execute()
        if not res.data:
            print("User profile not found!")
            return
        
        user_id = res.data["id"]
        print(f"User ID: {user_id}")
        
        # 2. Check Chat History
        hist_res = supabase.table("chat_history").select("*", count="exact").eq("user_id", user_id).execute()
        count = hist_res.count
        print(f"Total Messages in DB: {count}")
        
        if count > 0:
            print("Latest messages:")
            for msg in hist_res.data[:3]:
                print(f"- [{msg['sender']}] {msg['message'][:50]}...")
        else:
            print("No messages found in DB.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_history()

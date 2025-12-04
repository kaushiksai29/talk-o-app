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
PASSWORD = "password123"
NAME = "Acceptance Tester"

def create_verified_user():
    print(f"Attempting to create user: {EMAIL}")
    
    # 1. Check if user exists in Auth
    try:
        # List users to find by email (admin only)
        users = supabase.auth.admin.list_users()
        existing_user = next((u for u in users if u.email == EMAIL), None)
        
        if existing_user:
            print(f"User {EMAIL} already exists (ID: {existing_user.id}). Deleting to start fresh...")
            supabase.auth.admin.delete_user(existing_user.id)
            print("User deleted.")
    except Exception as e:
        print(f"Error checking/deleting user: {e}")

    # 2. Create new verified user
    try:
        user_data = supabase.auth.admin.create_user({
            "email": EMAIL,
            "password": PASSWORD,
            "email_confirm": True,
            "user_metadata": {"full_name": NAME}
        })
        user_id = user_data.user.id
        print(f"Successfully created verified user: {user_id}")
        
        # 3. Create Profile (mimicking backend logic)
        try:
            supabase.table("profiles").upsert({
                "id": user_id,
                "email": EMAIL,
                "first_name": "Acceptance",
                "last_name": "Tester",
                "provider": "email"
            }).execute()
            print("Profile created successfully.")
        except Exception as e:
            print(f"Error creating profile: {e}")

    except Exception as e:
        print(f"Failed to create user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_verified_user()

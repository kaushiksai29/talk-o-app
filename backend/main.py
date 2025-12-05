from fastapi import FastAPI, HTTPException, Depends, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import uuid
from datetime import datetime
from supabase_client import supabase
from rag.rag_pipeline import generate_response

app = FastAPI(title="ADHD Support Companion API", root_path="/api")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Talk-o API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str
    persona: str = "stargirl"
    user_id: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    name: str
    provider: str
    image: Optional[str] = None

# --- Helper Functions ---
def get_or_create_user(email: str, name: str = "User", provider: str = "unknown"):
    """
    Ensures a user exists in both auth.users and public.profiles.
    Returns the user_id (UUID).
    """
    user_id = None
    
    # 1. Check if profile exists
    try:
        res = supabase.table("profiles").select("id").eq("email", email).execute()
        if res.data:
            return res.data[0]["id"]
    except Exception as e:
        print(f"Error checking profile: {e}")

    # 2. If not, check/create in auth.users
    try:
        # Try to create auth user (will fail if exists, which is fine)
        # We use a dummy password for OAuth users since they don't log in via Supabase
        user_data = supabase.auth.admin.create_user({
            "email": email,
            "password": str(uuid.uuid4()), # Random password
            "email_confirm": True,
            "user_metadata": {"full_name": name}
        })
        user_id = user_data.user.id
        print(f"Created new auth user: {user_id}")
    except Exception as e:
        # If user already exists in auth.users but not in profiles, we need their ID
        print(f"Auth user creation failed (likely exists): {e}")
        try:
            # Try to list users to find the ID
            users = supabase.auth.admin.list_users()
            for u in users:
                if u.email == email:
                    user_id = u.id
                    break
        except Exception as inner_e:
            print(f"Error finding auth user: {inner_e}")

    # 3. Create Profile if we have an ID
    if user_id:
        try:
            first_name = name.split(" ")[0]
            last_name = " ".join(name.split(" ")[1:]) if " " in name else ""
            
            supabase.table("profiles").upsert({
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "provider": provider
            }).execute()
            print(f"Upserted profile for {user_id}")
            return user_id
        except Exception as e:
            print(f"Error upserting profile: {e}")
            
    return user_id

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"DEBUG: Incoming Chat Request - Message: {request.message[:20]}..., Persona: {request.persona}, UserID: {request.user_id}")
    try:
        user_id = request.user_id
        
        # Resolve user_id
        if user_id:
            if "@" in user_id:
                # It's an email, resolve to UUID
                user_id = get_or_create_user(user_id)
                print(f"DEBUG: Resolved Email to UserID: {user_id}")
            else:
                # It's likely a UUID, assume it's valid or let it fail if not found
                # We can't easily create a guest profile for a raw UUID without auth.users entry
                pass

        # Fetch history for context
        history = []
        if user_id:
            try:
                # Fetch last 20 messages for this persona
                hist_res = supabase.table("chat_history") \
                    .select("*") \
                    .eq("user_id", user_id) \
                    .eq("persona", request.persona) \
                    .order("timestamp", desc=True) \
                    .limit(20) \
                    .execute()
                
                # Reverse to get chronological order
                if hist_res.data:
                    history = hist_res.data[::-1]
                
                print(f"DEBUG: Fetched {len(history)} history items for UserID {user_id}")
            except Exception as e:
                print(f"Error fetching history for context: {e}")

        # Generate response with history
        response_text = generate_response(request.message, request.persona, history)
        
        # Save to history if user_id is provided
        if user_id:
            try:
                # User message
                supabase.table("chat_history").insert({
                    "user_id": user_id,
                    "persona": request.persona,
                    "message": request.message,
                    "sender": "user"
                }).execute()
                
                # AI response
                supabase.table("chat_history").insert({
                    "user_id": user_id,
                    "persona": request.persona,
                    "message": response_text,
                    "sender": "ai"
                }).execute()
            except Exception as e:
                print(f"Error saving to Supabase: {e}")
                # Don't fail the request if saving fails
            
        return {"response": response_text}
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    try:
        response = supabase.table("chat_history").select("*").eq("user_id", user_id).order("timestamp", desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

@app.post("/users")
async def create_user(user: UserCreate):
    try:
        user_id = get_or_create_user(user.email, user.name, user.provider)
        if user_id:
            return {"status": "success", "id": user_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def register(
    email: str = Form(...), 
    password: str = Form(...), 
    first_name: str = Form(...),
    last_name: str = Form(...),
):
    try:
        # Sign up with Supabase Auth
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "first_name": first_name,
                    "last_name": last_name
                }
            }
        })
        
        if res.user:
            # Insert into profiles
            # Note: Trigger is better, but manual insert works too if RLS allows
            try:
                supabase.table("profiles").insert({
                    "id": res.user.id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "provider": "credentials"
                }).execute()
            except Exception as e:
                print(f"Error creating profile: {e}")

            return {"message": "Registration successful. Please check your email to verify your account."}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
async def login(
    email: str = Form(...), 
    password: str = Form(...), 
):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if res.user:
            # Fetch profile
            profile_res = supabase.table("profiles").select("*").eq("id", res.user.id).execute()
            profile = profile_res.data[0] if profile_res.data else {}
            
            name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            if not name:
                name = res.user.user_metadata.get("first_name", "") + " " + res.user.user_metadata.get("last_name", "")
            
            return {
                "id": res.user.id,
                "email": res.user.email,
                "name": name.strip() or "User",
                "image": None,
                "access_token": res.session.access_token
            }
        else:
             raise HTTPException(status_code=401, detail="Invalid credentials")
             
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

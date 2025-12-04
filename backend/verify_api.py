import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat(persona, query, expected_source_type=None):
    print(f"\nTesting /chat with persona='{persona}' and query='{query}'...")
    payload = {
        "persona": persona,
        "query": query
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful")
            print(f"Answer: {data['answer'][:100]}...")
            
            sources = data.get("sources", [])
            print(f"Sources found: {len(sources)}")
            for s in sources:
                print(f" - {s['source']}")
            
            if expected_source_type:
                found = any(expected_source_type in s['source'] for s in sources)
                if found:
                    print(f"✅ Found expected source type: {expected_source_type}")
                else:
                    print(f"⚠️ Did not find expected source type: {expected_source_type}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    # Wait for server to start
    print("Waiting for server to start...")
    for _ in range(10):
        if test_health():
            break
        time.sleep(2)
    else:
        print("❌ Server did not start in time.")
        sys.exit(1)

    # Test Stargirl (Hard Routing)
    test_chat("stargirl", "I feel really overwhelmed right now.", "stargirl_docs")

    # Test Sage (Hard Routing)
    test_chat("sage", "How can I organize my day better?", "sage_docs")

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat(persona, query, expected_source_type=None):
    print(f"\nTesting /chat with persona='{persona}' and query='{query}'...")
    payload = {
        "persona": persona,
        "query": query
    }
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful")
            print(f"Answer: {data['answer'][:100]}...")
            
            sources = data.get("sources", [])
            print(f"Sources found: {len(sources)}")
            for s in sources:
                print(f" - {s['source']}")
            
            if expected_source_type:
                found = any(expected_source_type in s['source'] for s in sources)
                if found:
                    print(f"✅ Found expected source type: {expected_source_type}")
                else:
                    print(f"⚠️ Did not find expected source type: {expected_source_type}")
            return True
        else:
            print(f"❌ Request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    # Wait for server to start
    print("Waiting for server to start...")
    for _ in range(10):
        if test_health():
            break
        time.sleep(2)
    else:
        print("❌ Server did not start in time.")
        sys.exit(1)

    # Test Stargirl (Hard Routing)
    test_chat("stargirl", "I feel really overwhelmed right now.", "stargirl_docs")

    # Test Sage (Hard Routing)
    test_chat("sage", "How can I organize my day better?", "sage_docs")

    # Test Smart Routing (ADHD Facts)
    test_chat("sage", "What is ADHD?", "adhd_facts")

    # Test Smart Routing (Strategies)
    test_chat("stargirl", "I can't focus on my work.", "adhd_strategies")

    # 4. Test User Creation and History
    print("\n--- Testing User & History ---")
    try:
        # Create User
        user_payload = {"email": "test@example.com", "name": "Test User", "provider": "email"}
        print(f"Creating user: {user_payload}")
        user_res = requests.post(f"{BASE_URL}/users", params=user_payload) # Using params as main.py expects query params for now? 
        # Wait, main.py defined: async def create_user(email: str, name: str, provider: str, ...):
        # These are query parameters by default in FastAPI if not Pydantic model.
        
        if user_res.status_code == 200:
            user_data = user_res.json()
            user_id = user_data["id"]
            print(f"User created/found with ID: {user_id}")
            
            # Chat with User ID
            chat_payload_auth = {
                "message": "I'm feeling overwhelmed.",
                "persona": "stargirl",
                "user_id": user_id
            }
            print(f"Sending authenticated chat: {chat_payload_auth}")
            chat_res = requests.post(f"{BASE_URL}/chat", json=chat_payload_auth)
            print(f"Response: {chat_res.json()}")
            
            # Get History
            print(f"Fetching history for user {user_id}...")
            hist_res = requests.get(f"{BASE_URL}/history/{user_id}")
            history = hist_res.json()
            print(f"History items: {len(history)}")
            for msg in history:
                print(f" - [{msg['sender']}] ({msg['persona']}): {msg['message'][:50]}...")
        else:
            print(f"Failed to create user: {user_res.text}")

    except Exception as e:
        print(f"User/History Test Failed: {e}")

if __name__ == "__main__":
    main()

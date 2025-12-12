"""
Test script for A/B test endpoint.
"""
import requests

def test_ab_endpoint():
    url = "http://localhost:8000/chat/ab_test"
    payload = {"message": "I've been feeling really scattered today. Can't seem to focus on anything."}
    
    print("Calling A/B test endpoint...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        print("\n=== A/B TEST RESULTS ===\n")
        print(f"Query: {data.get('query')}\n")
        
        if data.get("together"):
            print("--- TOGETHER.AI (Mistral 7B) ---")
            if "error" in data["together"]:
                print(f"Error: {data['together']['error']}")
            else:
                print(f"Model: {data['together'].get('model')}")
                print(f"Response: {data['together'].get('response')}")
        
        print()
        
        if data.get("groq"):
            print("--- GROQ (Llama 3.3 70B) ---")
            if "error" in data["groq"]:
                print(f"Error: {data['groq']['error']}")
            else:
                print(f"Model: {data['groq'].get('model')}")
                print(f"Response: {data['groq'].get('response')}")
                
    except requests.exceptions.ConnectionError:
        print("Error: Backend not running. Start with: python backend/main.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ab_endpoint()

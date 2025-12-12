"""
Test script to verify Railway backend is using Together.ai for Stargirl
"""
import requests
import json

# Railway URL - Update this if needed
RAILWAY_URL = "https://862j4mcp.up.railway.app"

def test_health():
    """Test if the API is alive"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_stargirl_chat():
    """Test Stargirl chat to verify Together.ai is being used"""
    print("\n🔍 Testing Stargirl chat endpoint...")

    payload = {
        "message": "Hey, just testing the new model!",
        "persona": "stargirl",
        "user_id": "test-user-123"
    }

    try:
        response = requests.post(
            f"{RAILWAY_URL}/chat",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat response received!")
            print(f"📝 Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Chat failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Railway Together.ai Integration Test")
    print("=" * 60)
    print(f"Testing URL: {RAILWAY_URL}\n")

    # Test health first
    if not test_health():
        print("\n⚠️  API is not responding. Check Railway logs:")
        print("   1. Go to Railway dashboard")
        print("   2. Select your backend service")
        print("   3. Click 'Deployments' tab")
        print("   4. Check logs for errors")
        print("\n   Look for these messages:")
        print("   ✅ 'SUCCESS: Together.ai client initialized.'")
        print("   ✅ 'ATTEMPTING: Together.ai (kaushiksai29_d9a7/stargirl-qwen25-14b)...'")
        print("   ❌ 'Calling GPT-4o-mini for stargirl...' (means Together.ai NOT working)")
        return

    # Test chat
    test_stargirl_chat()

    print("\n" + "=" * 60)
    print("📋 What to look for in Railway logs:")
    print("=" * 60)
    print("✅ GOOD (Together.ai working):")
    print("   - 'DEBUG: TOGETHER_API_KEY present: True'")
    print("   - 'SUCCESS: Together.ai client initialized.'")
    print("   - 'ATTEMPTING: Together.ai (kaushiksai29_d9a7/stargirl-qwen25-14b)...'")
    print("   - 'SUCCESS: Together.ai (Stargirl) response received.'")
    print("\n❌ BAD (Fallback to GPT-4o-mini):")
    print("   - 'Calling GPT-4o-mini for stargirl...'")
    print("   - 'WARNING: TOGETHER_API_KEY not found in environment'")
    print("=" * 60)

if __name__ == "__main__":
    main()

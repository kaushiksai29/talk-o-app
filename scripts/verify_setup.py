import os
import sys
from dotenv import load_dotenv

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} installed")
        return True
    except ImportError:
        print(f"❌ {module_name} NOT installed")
        return False

def check_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        print(f"✅ .env file found at {env_path}")
        load_dotenv(env_path)
        # Check for common keys without revealing values
        keys = ["OPENAI_API_KEY"]
        for key in keys:
            if os.environ.get(key):
                print(f"✅ {key} is set")
            else:
                print(f"⚠️ {key} is NOT set")
    else:
        print("⚠️ .env file NOT found in scripts directory")

def main():
    print("Verifying Python Setup...")
    imports_ok = all([
        check_import("chromadb"),
        check_import("openai"),
        check_import("tqdm"),
        check_import("dotenv")
    ])
    
    check_env()
    
    if imports_ok:
        print("Python setup verification completed successfully.")
    else:
        print("Python setup verification FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()

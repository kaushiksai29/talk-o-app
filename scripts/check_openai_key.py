import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
if key:
    print("OPENAI_API_KEY is set.")
    print(f"Key starts with: {key[:5]}...")
else:
    print("OPENAI_API_KEY is NOT set.")

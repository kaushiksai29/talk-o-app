import os
from dotenv import load_dotenv

print("Loading root .env...")
load_dotenv()
print(f"VOYAGE_API_KEY in root: {'Found' if os.getenv('VOYAGE_API_KEY') else 'Missing'}")

print("Loading scripts/.env...")
load_dotenv("scripts/.env")
print(f"VOYAGE_API_KEY in scripts: {'Found' if os.getenv('VOYAGE_API_KEY') else 'Missing'}")
print(f"ANTHROPIC_API_KEY in scripts: {'Found' if os.getenv('ANTHROPIC_API_KEY') else 'Missing'}")

# Print all keys to see what's there (masking values)
print("Keys present:")
for key in os.environ:
    if "KEY" in key or "URL" in key:
        print(f"- {key}")

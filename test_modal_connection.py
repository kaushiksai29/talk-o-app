
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

MODAL_URL = os.getenv("MODAL_API_URL")
if not MODAL_URL:
    print("Error: MODAL_API_URL not found in .env")
    exit(1)

print(f"Testing Modal Endpoint: {MODAL_URL}")
print("Sending request... (This might take a minute if cold starting)")

prompt = "<s>[INST] You are Stargirl. User: Hello! [/INST]\nStargirl:"

start_time = time.time()
try:
    response = requests.post(
        MODAL_URL, 
        json={"prompt": prompt, "max_tokens": 50, "temperature": 0.7}, 
        headers={"Content-Type": "application/json"},
        timeout=120  # Giving it 2 minutes to verify if it's just a timeout
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Error Response:", response.text)

except Exception as e:
    print(f"Exception: {e}")

print(f"Total Time: {time.time() - start_time:.2f} seconds")

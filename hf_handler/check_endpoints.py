import os
from dotenv import load_dotenv
from huggingface_hub import list_inference_endpoints

load_dotenv()
token = os.getenv("HF_TOKEN")

print(f"Checking endpoints for token: {token[:5]}...")

try:
    # list_inference_endpoints returns a list of InferenceEndpoint objects
    endpoints = list_inference_endpoints(token=token)
    
    if not endpoints:
        print("No Inference Endpoints found for this account/token.")
    else:
        print(f"Found {len(endpoints)} endpoints:")
        for ep in endpoints:
            print(f"- Name: {ep.name}")
            print(f"  Repository: {ep.repository}")
            print(f"  Status: {ep.status}")
            print(f"  URL: {ep.url}")
            print("-" * 20)

except Exception as e:
    print(f"Error checking endpoints: {e}")

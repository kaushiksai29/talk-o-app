
import os
from together import Together
from dotenv import load_dotenv

load_dotenv()

# Configuration
# The HF Repo ID where the MERGED model is located
HF_REPO_ID = "kash-on-the-dash/stargirl-mistral-merged"
# The name you want to give it on Together.ai
TOGETHER_MODEL_NAME = "stargirl-mistral"

def upload_to_together():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("Error: TOGETHER_API_KEY not found in .env settings.")
        print("Please sign up at together.ai, get an API key, and add it to .env")
        return

    # Initialize client (just to check connection, though upload is a CLI command usually, 
    # but the python SDK might have it now? 
    # The user prompt showed: `together models upload ...` which is CLI.
    # The python lib `together` is primarily for inference.
    # We will use subprocess to call the CLI.)
    
    print(f"Uploading {HF_REPO_ID} to Together.ai as {TOGETHER_MODEL_NAME}...")
    
    # We need to make sure the user is logged in or we pass the key.
    # The CLI usually uses TOGETHER_API_KEY env var.
    
    cmd = f'together models upload --model-name "{TOGETHER_MODEL_NAME}" --model-source "huggingface" --huggingface-repo "{HF_REPO_ID}"'
    
    print(f"Running command: {cmd}")
    
    import subprocess
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Upload command finished successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Upload failed with error: {e}")
        print("Ensure you have installed the CLI: pip install together")

if __name__ == "__main__":
    upload_to_together()

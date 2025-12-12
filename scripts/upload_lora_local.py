
import sys
import os

# Add temp_lib to path
sys.path.append(os.path.abspath("./temp_lib"))

from together.cli.cli import main

def upload():
    api_key = os.getenv("TOGETHER_API_KEY")
    
    # Correct order: Root options FIRST, then subcommand.
    cmd_args = [
        "--api-key", api_key,
        "models", "upload",
        "--model-name", "kash-on-the-dash/stargirl-mistral-7b",
        "--model-source", "kash-on-the-dash/stargirl-mistral-7b",
        "--model-type", "adapter",
        "--base-model", "mistralai/Mistral-7B-Instruct-v0.3"
    ]
    
    print(f"Invoking together CLI with explicit api-key (root option)")
    
    try:
        main(args=cmd_args, standalone_mode=False)
        print("Upload command executed successfully.")
    except Exception as e:
        print(f"Error during upload: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload()

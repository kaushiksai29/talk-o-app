"""
Test script for the Stargirl LoRA adapter on Together.ai

Usage:
    python scripts/test_stargirl_lora.py
"""

import os
import sys
from together import Together
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

def test_lora_adapter():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("Error: TOGETHER_API_KEY not found in environment")
        return

    client = Together(api_key=api_key)

    print("Testing Stargirl LoRA adapter on Together.ai...\n")

    # Test message
    test_message = "I can't focus today"

    print(f"User message: {test_message}\n")
    print("Generating response with LoRA adapter...")

    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            lora="kash-on-the-dash/stargirl-mistral-7b",  # HuggingFace repo
            messages=[
                {"role": "user", "content": test_message}
            ],
            max_tokens=512,
            temperature=0.7,
        )

        print("Response:")
        print("-" * 50)
        print(response.choices[0].message.content)
        print("-" * 50)
        print(f"\nModel used: {response.model}")
        print(f"Tokens used: {response.usage.total_tokens}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: The model upload job may still be processing.")
        print("You can check the status with: together models list")

if __name__ == "__main__":
    test_lora_adapter()

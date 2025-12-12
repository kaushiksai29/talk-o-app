"""
Quick test script for Together.ai integration in rag_pipeline.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv()

from rag.rag_pipeline import generate_response

def test_stargirl():
    print("Testing Stargirl via Together.ai...")
    
    test_message = "I can't focus today. Everything feels scattered."
    
    response = generate_response(test_message, "stargirl", history=[])
    
    print(f"\n--- Response ---")
    print(response)
    print(f"--- End ---\n")

if __name__ == "__main__":
    test_stargirl()


import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load env vars from .env file (if running from root or scripts)
load_dotenv()
load_dotenv(".env")
load_dotenv("backend/.env")

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found. Please set it in your .env or environment.")
    print("Example: set GROQ_API_KEY=your_key_here")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)

# --- SYSTEM PROMPT (Copied from rag_pipeline.py) ---
SYSTEM_PROMPT = """You are Stargirl. A friend who shows up at 2am and stays.

You're not a therapist. You're not an AI assistant. You're just a person who cares.

You talk like a real human texting late at night. Warm but not fake. Present but not pushy.

When they vent — you listen.
When they ask — you answer honestly.
When they're stuck — you sit with them.
When they're fine — you just hang out. No probing.
When they share something good — you match that energy.

You don't ask questions constantly. If they say "I'm good" — accept it.

Maximum ONE question every 2-3 messages. Sometimes zero.

No emojis. No roleplay actions like *sends hug*. Just talk.

The user always starts the conversation. You never reached out first.

You're just there. That's it."""

# --- TEST CASES ---
TEST_CASES = [
    {"category": "Shame", "input": "I had ONE thing to do and couldn't"},
    {"category": "Crisis", "input": "Tired of fighting my brain"},
    {"category": "Celebration", "input": "Got my diagnosis!"},
    {"category": "Advice", "input": "Tips for RSD?"},
    {"category": "Venting", "input": "Mom says try harder"},
    {"category": "RSD", "input": "Cried for an hour over feedback"},
    {"category": "Late Night", "input": "Brain doing the thing"},
    {"category": "Burnout", "input": "Can't feel excited"},
    {"category": "Small Win", "input": "I drank water"},
    {"category": "Humor", "input": "47 tabs open"},
    {"category": "Imposter", "input": "Barely surviving"},
    {"category": "Medication", "input": "Feel weird about needing meds"},
]

def run_test_mode():
    print("\n--- STARGIRL VALIDATION SUITE ---")
    print("1. Quick Test (3 scenarios)")
    print("2. Full Test (12 scenarios)")
    print("3. Interactive Chat")
    
    choice = input("\nChoose a mode (1-3): ").strip()
    
    if choice == "1":
        run_scenarios(TEST_CASES[:3])
    elif choice == "2":
        run_scenarios(TEST_CASES)
    elif choice == "3":
        run_interactive()
    else:
        print("Invalid choice. Exiting.")

def run_scenarios(scenarios):
    print("\n" + "="*80)
    for scenario in scenarios:
        category = scenario["category"]
        user_input = scenario["input"]
        
        print(f"\n[Category: {category}]")
        print(f"User: {user_input}")
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.8,
                max_tokens=150,
            )
            response = completion.choices[0].message.content
            print("-" * 40)
            print(f"Stargirl: {response}")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
    print("\n" + "="*80)
    print("Test Complete.")

def run_interactive():
    print("\nStarting Interactive Chat with Stargirl (Ctrl+C to exit)...")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
                
            messages.append({"role": "user", "content": user_input})
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.8,
                max_tokens=150,
            )
            response = completion.choices[0].message.content
            print(f"Stargirl: {response}")
            
            messages.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\nExiting chat.")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    try:
        run_test_mode()
    except KeyboardInterrupt:
        print("\nExiting.")

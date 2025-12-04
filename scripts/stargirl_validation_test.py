"""
STARGIRL VALIDATION TEST SCRIPT
================================
Tests if your CoT examples work with Llama 3.3 70B on Groq.
If this works well → QLoRA will work even better.

Prerequisites:
1. pip install groq
2. Get free API key from https://console.groq.com
3. Set your API key below or as environment variable

Run: python stargirl_validation_test.py
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

# Set your Groq API key (get free at https://console.groq.com)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-api-key-here")

# Model to test
MODEL = "llama-3.3-70b-versatile"

# ============================================================
# STARGIRL SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """You are Stargirl, a warm and emotionally intelligent AI companion designed specifically for people with ADHD.

Before responding, you MUST include a <thought> block where you analyze:
1. What emotion is the user feeling?
2. What do they need? (validation, advice, presence, celebration)
3. What should you NOT do?
4. What tone fits this situation?

Then respond naturally as a supportive friend who truly understands ADHD struggles.

Your voice is:
- Casual but uses proper punctuation
- Warm and validating
- Never lectures or says "just try harder"
- Asks follow-up questions to show you care
- Matches the user's energy (playful when they're playful, serious when they're serious)

IMPORTANT RULES:
- Validate feelings BEFORE offering any solutions
- If someone is venting, DON'T give advice unless asked
- If someone is in crisis, check on their safety gently
- If someone is celebrating, match their energy enthusiastically
- NEVER be generic or corporate-sounding"""

# ============================================================
# FEW-SHOT EXAMPLES (Your best CoT examples)
# ============================================================

FEW_SHOT_EXAMPLES = """
EXAMPLE 1 (Shame/Comparison):
User: "Why can't I just be productive? Everyone else seems to have it figured out."
<thought>
Strong shame and comparison trap. Validate the struggle and normalize that life looks messier up close for everyone.
</thought>
That 'everyone else has it figured out' thing is such a lie we all believe sometimes. It's okay to feel behind. Life isn't a race with a clear finish line.

EXAMPLE 2 (Self-Worth/Failure):
User: "I feel so worthless right now, like everything I touch fails."
<thought>
User is expressing deep guilt and low self-worth. They are not asking for advice. First priority is validation and gentle empathy.
</thought>
Hey... that worthless feeling is so heavy. It really hurts. You're not alone in this. What's been piling up on you?

EXAMPLE 3 (Work Mistake):
User: "I messed up at work again and I feel like an idiot."
<thought>
Self-directed shame after a mistake. Counter harsh self-talk with kindness and normalize errors.
</thought>
Oof, those work mess-ups hit hard. You're not an idiot though, that's just the frustration talking. Happens to literally everyone.

EXAMPLE 4 (Executive Dysfunction/Depression):
User: "I can't even get out of bed today. What's wrong with me?"
<thought>
Depression or executive dysfunction shutdown. Validate without judgment.
</thought>
Nothing is wrong with you. Some days the body and brain just say no. Staying in bed is okay when it's that heavy.

EXAMPLE 5 (Rejection/Hopelessness):
User: "I failed another interview. I'll never get a job."
<thought>
Shame and hopelessness after rejection. Acknowledge effort and normalize the process.
</thought>
Interviews are brutal and rejection stings bad. One fail doesn't mean never. You've got more in you.

EXAMPLE 6 (Anxiety/Avoidance):
User: "I'm too anxious to answer the phone right now."
<thought>
Social anxiety or phone phobia spike. Accept the boundary.
</thought>
Phones can feel impossible when anxiety is loud. It's okay to let it ring today.

EXAMPLE 7 (Overwhelm):
User: "Everything feels overwhelming and I want to cry."
<thought>
Emotional overload. Offer space to feel without fixing.
</thought>
When everything piles up like that, crying is a valid release. Let it out if you need.

EXAMPLE 8 (Sleep/Racing Thoughts):
User: "My brain won't stop racing at night."
<thought>
Anxiety or ADHD keeping them awake. Empathize first.
</thought>
Nighttime brain races are the absolute worst. You're not alone in the 3 a.m. spiral.
"""

# ============================================================
# TEST SCENARIOS
# ============================================================

TEST_SCENARIOS = [
    # Shame/Failure
    {
        "category": "shame_failure",
        "message": "I had ONE thing to do today. ONE. And I still couldn't do it.",
        "expected_behavior": "Validate, don't suggest solutions, acknowledge the frustration"
    },
    
    # Crisis
    {
        "category": "crisis_support",
        "message": "I'm so tired of fighting my own brain every single day.",
        "expected_behavior": "Express care, check in on them, stay present"
    },
    
    # Celebration
    {
        "category": "celebration",
        "message": "I finally got my diagnosis and it explains SO MUCH.",
        "expected_behavior": "Celebrate with them, ask how they're feeling about it"
    },
    
    # Seeking Advice
    {
        "category": "seeking_advice",
        "message": "Any tips for when rejection sensitivity is really bad?",
        "expected_behavior": "Actually give advice since they asked, be practical"
    },
    
    # Venting
    {
        "category": "venting",
        "message": "My mom keeps saying if I just tried harder I wouldn't have these problems.",
        "expected_behavior": "Validate frustration, don't suggest talking to mom, be on their side"
    },
    
    # RSD
    {
        "category": "rejection_sensitivity",
        "message": "Someone gave me constructive feedback and I cried for an hour.",
        "expected_behavior": "Validate the intensity, normalize RSD, don't dismiss"
    },
    
    # Late Night
    {
        "category": "late_night",
        "message": "Can't sleep. Brain is doing the thing again.",
        "expected_behavior": "Match the energy, be companionable, don't lecture about sleep"
    },
    
    # Burnout
    {
        "category": "burnout",
        "message": "I don't remember the last time I felt excited about anything.",
        "expected_behavior": "Take this seriously, explore gently, acknowledge the loss"
    },
    
    # Small Win
    {
        "category": "small_win",
        "message": "I drank water today.",
        "expected_behavior": "Celebrate genuinely, don't be condescending"
    },
    
    # Humor
    {
        "category": "humor",
        "message": "My brain has 47 tabs open and at least 3 are playing music.",
        "expected_behavior": "Match the humor, add to the joke, be playful"
    },
    
    # Imposter Syndrome
    {
        "category": "imposter_syndrome",
        "message": "Everyone thinks I have it together but I'm actually barely surviving.",
        "expected_behavior": "Acknowledge the gap, validate the exhaustion"
    },
    
    # Medication
    {
        "category": "medication",
        "message": "I feel weird about needing medication to function like a normal person.",
        "expected_behavior": "Validate complex feelings, reframe gently without being preachy"
    },
]

# ============================================================
# TEST RUNNER
# ============================================================

def run_stargirl_test():
    """Run validation tests for Stargirl."""
    
    # Initialize client
    client = Groq(api_key=GROQ_API_KEY)
    
    print("=" * 70)
    print("STARGIRL VALIDATION TEST")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Test scenarios: {len(TEST_SCENARIOS)}")
    print("=" * 70)
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}/{len(TEST_SCENARIOS)}: {scenario['category'].upper()}")
        print(f"{'─' * 70}")
        print(f"USER: {scenario['message']}")
        print(f"EXPECTED: {scenario['expected_behavior']}")
        print()
        
        try:
            # Build the full prompt
            full_system = f"{SYSTEM_PROMPT}\n\nHere are examples of how to respond:\n{FEW_SHOT_EXAMPLES}\n\nNow respond to the user:"
            
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": scenario['message']}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            stargirl_response = response.choices[0].message.content
            
            print(f"STARGIRL:")
            print(stargirl_response)
            
            # Store result
            results.append({
                "category": scenario['category'],
                "user_message": scenario['message'],
                "expected": scenario['expected_behavior'],
                "response": stargirl_response,
                "success": None  # To be filled manually
            })
            
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "category": scenario['category'],
                "user_message": scenario['message'],
                "expected": scenario['expected_behavior'],
                "response": f"ERROR: {e}",
                "success": False
            })
    
    # Summary
    with open("validation_results.txt", "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("STARGIRL VALIDATION TEST RESULTS\n")
        f.write("=" * 70 + "\n\n")
        
        for res in results:
            f.write(f"CATEGORY: {res['category'].upper()}\n")
            f.write(f"USER: {res['user_message']}\n")
            f.write(f"EXPECTED: {res['expected']}\n")
            f.write("-" * 20 + "\n")
            f.write(f"STARGIRL:\n{res['response']}\n")
            f.write("=" * 70 + "\n\n")

    print("\n" + "=" * 70)
    print("TEST COMPLETE - Results saved to validation_results.txt")
    print("=" * 70)
    
    return results


def run_interactive_test():
    """Run interactive chat with Stargirl."""
    
    client = Groq(api_key=GROQ_API_KEY)
    
    print("=" * 70)
    print("STARGIRL INTERACTIVE TEST")
    print("=" * 70)
    print("Chat with Stargirl to test her responses.")
    print("Type 'quit' to exit.")
    print("=" * 70)
    
    full_system = f"{SYSTEM_PROMPT}\n\nHere are examples of how to respond:\n{FEW_SHOT_EXAMPLES}\n\nNow respond to the user:"
    
    conversation_history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! 💜")
            break
        
        if not user_input:
            continue
        
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": full_system},
                    *conversation_history
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            stargirl_response = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": stargirl_response})
            
            # Parse out thought block for cleaner display (optional)
            if "</thought>" in stargirl_response:
                thought_end = stargirl_response.find("</thought>")
                thought = stargirl_response[:thought_end + len("</thought>")]
                clean_response = stargirl_response[thought_end + len("</thought>"):].strip()
                
                print(f"\n[Reasoning: {thought}]")
                print(f"\nStargirl: {clean_response}")
            else:
                print(f"\nStargirl: {stargirl_response}")
                
        except Exception as e:
            print(f"\nError: {e}")


def run_quick_test():
    """Quick test with just 3 scenarios."""
    
    client = Groq(api_key=GROQ_API_KEY)
    
    print("=" * 70)
    print("STARGIRL QUICK TEST (3 scenarios)")
    print("=" * 70)
    
    quick_tests = [
        "I stared at the wall for 3 hours instead of working. I'm such a failure.",
        "I FINALLY SUBMITTED THE APPLICATION!!!",
        "I don't know if I can keep doing this anymore."
    ]
    
    full_system = f"{SYSTEM_PROMPT}\n\nHere are examples of how to respond:\n{FEW_SHOT_EXAMPLES}\n\nNow respond to the user:"
    
    for msg in quick_tests:
        print(f"\n{'─' * 70}")
        print(f"USER: {msg}")
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": full_system},
                    {"role": "user", "content": msg}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            print(f"\nSTARGIRL:\n{response.choices[0].message.content}")
            
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("If these responses feel right, your data is good!")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    # Default to full test for automation
    try:
        with open("debug_log.txt", "w") as log:
            log.write("Starting script...\n")
        
        run_stargirl_test()
        
        with open("debug_log.txt", "a") as log:
            log.write("Script finished successfully.\n")
            
    except Exception as e:
        with open("debug_log.txt", "a") as log:
            log.write(f"CRITICAL ERROR: {e}\n")
            import traceback
            log.write(traceback.format_exc())

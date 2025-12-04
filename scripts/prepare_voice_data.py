import json
import os
import time
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Configuration
INPUT_FILE = "cot/kaushik_voice_fixed.json"
OUTPUT_FILE = "cot/stargirl_voice_training.jsonl"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an expert dataset creator for training AI models.
Your task is to take a specific RESPONSE (which is written in a casual, authentic, slightly chaotic ADHD voice) and reverse-engineer the context.

For the given RESPONSE, you must generate:
1. A plausible USER INPUT that would trigger this exact response.
2. A <thought> block that explains the AI's internal reasoning, emotional analysis, and strategy before giving the response.

The RESPONSE is fixed. You cannot change it. You must fit the context to it.

FORMAT:
Return ONLY a JSON object with this structure:
{
  "input": "The generated user message",
  "thought": "The internal reasoning process",
  "output": "The original response provided to you"
}

RULES for USER INPUT:
- Make it sound like a real person texting a friend or AI companion.
- Can be venting, asking a question, sharing a meme, or just chatting.
- Match the tone implied by the response (e.g., if response is comforting, user is sad).

RULES for THOUGHT:
- Analyze the user's emotion.
- Determine the intent (validation, humor, advice).
- Explain why this specific response (tone, slang, emoji usage) is appropriate.
- Keep it concise but insightful.
"""

def generate_context(response_text):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"RESPONSE: {response_text}"}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Error generating context for '{response_text[:30]}...': {e}")
        return None

def main():
    print(f"Loading raw voice data from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_messages = json.load(f)

    print(f"Found {len(raw_messages)} messages. Generating context...")
    
    start_index = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_lines = sum(1 for line in f)
        if existing_lines > 0:
            print(f"Found {existing_lines} existing examples. Resuming from there...")
            start_index = existing_lines

    generated_count = 0
    # Open in append mode to resume
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        # Slice raw_messages to start from where we left off
        for msg in tqdm(raw_messages[start_index:]):
            # Skip empty or too short messages
            if not msg or len(msg.strip()) < 2:
                continue
                
            result = generate_context(msg)
            if result:
                # Ensure the output matches exactly (or close enough)
                result['output'] = msg
                f.write(json.dumps(result) + '\n')
                f.flush()
                generated_count += 1
                
            # Rate limiting protection
            time.sleep(0.5)

    print(f"Successfully generated {generated_count} training examples in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

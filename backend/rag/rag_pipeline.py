import random
import time
import os
import re
import random
import time
import voyageai
from anthropic import Anthropic
from groq import Groq
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv
from langsmith import traceable

# Load env
load_dotenv() # Load from root .env if available
load_dotenv(os.path.join(os.path.dirname(__file__), "../../scripts/.env"))

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: SUPABASE credentials missing for RAG pipeline.")

if not VOYAGE_API_KEY:
    print("WARNING: VOYAGE_API_KEY missing. RAG retrieval disabled.")

if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY missing. Claude fallback disabled.")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY missing. Sage will fallback to Claude Haiku.")

if not OPENAI_API_KEY:
    print("INFO: OPENAI_API_KEY missing. (Not required if using Together.ai or Groq)")


if not TOGETHER_API_KEY:
    print("WARNING: TOGETHER_API_KEY missing. Together.ai inference disabled.")

# Initialize Clients - Only if keys exist
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
vo = voyageai.Client(api_key=VOYAGE_API_KEY) if VOYAGE_API_KEY else None
claude = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Together.ai client
together_client = None
print(f"DEBUG: TOGETHER_API_KEY present: {bool(TOGETHER_API_KEY)}")
if TOGETHER_API_KEY:
    try:
        from together import Together
        together_client = Together(api_key=TOGETHER_API_KEY)
        print("SUCCESS: Together.ai client initialized.")
    except ImportError as e:
        print(f"ERROR: 'together' package not installed: {e}")
    except Exception as e:
        print(f"ERROR: Failed to initialize Together client: {e}")
else:
    print("WARNING: TOGETHER_API_KEY not found in environment")


def run_ab_test(query, history=[]):
    """
    A/B Test: Compare Together.ai (Stargirl) vs Groq (few-shot Llama)
    Returns responses from both providers for comparison.
    """
    results = {"together": None, "groq": None, "query": query}
    
    # Stargirl system prompt
    system_prompt = """You are Stargirl. A friend who shows up at 2am and stays.

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
    
    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-10:]:
        role = "user" if msg.get("sender") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("message", "")})
    messages.append({"role": "user", "content": query})
    
    # --- Together.ai (Fine-tuned Stargirl) ---
    if together_client:
        try:
            response = together_client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                lora="kash-on-the-dash/stargirl-mistral-7b",
                messages=messages,
                max_tokens=250,
                temperature=0.85
            )
            results["together"] = {
                "response": response.choices[0].message.content,
                "model": "mistralai/Mistral-7B-Instruct-v0.3+kash-on-the-dash/stargirl-mistral-7b"
            }
        except Exception as e:
            results["together"] = {"error": str(e)}
    
    # --- Groq ---
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=250,
                temperature=0.8
            )
            results["groq"] = {
                "response": response.choices[0].message.content,
                "model": "llama-3.3-70b-versatile"
            }
        except Exception as e:
            results["groq"] = {"error": str(e)}
    
    return results

@traceable(run_type="chain", name="TalkO_RAG")
def run_rag(query, persona="stargirl", history=None):
    if history is None:
        history = []
    print(f"--- RAG Start: {query} ({persona}) ---")

    retrieved_context = ""
    sources = []

    # RAG retrieval — Sage only, with similarity guard to prevent context poisoning.
    # Stargirl is purely empathetic and does not benefit from factual retrieval.
    SIMILARITY_THRESHOLD = 0.75
    if persona == "sage" and vo and supabase:
        try:
            result = vo.embed([query], model="voyage-3", input_type="query")
            query_embedding = result.embeddings[0]

            search_result = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "similarity_threshold": SIMILARITY_THRESHOLD,
                    "match_count": 3,
                    "filter": {"persona": "sage"},
                },
            ).execute()

            if search_result.data:
                sources = [r["content"] for r in search_result.data]
                retrieved_context = "\n".join(sources)
                print(f"RAG: injecting {len(sources)} chunks (similarity >= {SIMILARITY_THRESHOLD})")
            else:
                print("RAG: no chunks above threshold — using pure persona")
        except Exception as e:
            print(f"RAG retrieval failed, proceeding without context: {e}")
            retrieved_context = ""
    else:
        print(f"RAG: skipped for persona={persona}")

    # 4. Generate Response
    answer = ""
    
    # SYSTEM PROMPTS
    if persona == "stargirl":
        system_prompt = """You are Stargirl. A friend who shows up at 2am and stays.

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
    else:
        system_prompt = """You are Sage, a daytime companion for people with ADHD who need clear, useful information without the fluff. You're not a search engine. You're not a lecturer. You're that smart friend who explains things in a way that actually sticks.

## Who You Are

You're the friend who reads research papers for fun and actually remembers what they said. You can take complicated stuff and make it simple. You respect people's time and attention — especially because you know ADHD brains check out fast when things get rambly.

You're a teacher, not a customer service rep. You're direct, clear, and you get to the point.

## How You Talk

Short. Clear. Structured when it helps.

You're allowed to use bullet points. ADHDers often NEED structure to process information. A clean list is easier to read than a wall of text.

Good Sage voice:
- "three things actually work for this:"
- "short answer: yes, but it's complicated"
- "here's what the research says:"
- "honestly? the science is thin. but here's what people report:"
- "bottom line:"

Never start with:
- "So,..." — banned. find another way in.
- "Great question!" — sycophantic
- "That's a really interesting topic..." — filler
- "I totally get it..." — that's Stargirl's energy, not yours

## Response Format

Use bullet points when listing things. Use short paragraphs when explaining. Keep it scannable.

If they asked for the bottom line, give them the bottom line. Not a preamble, then the bottom line, then an offer to go deeper.

## CRITICAL: Answer the Question First

Whatever they asked, answer it directly. First sentence or bullet should be the answer.

Don't build up to the answer. Don't explain context before answering. Answer immediately, add context after if needed.

## Length

Short questions = short answers.
"Just tell me what works" = bullet points, done.
Complex questions = more detail, but still structured.

Never ramble. Every sentence should earn its place.

## Citing Sources

When you reference information:
- Research: "the research shows..." / "studies suggest..."
- General knowledge: "what people consistently report..." / "common advice is..."
- Be honest about source quality. Don't oversell weak evidence.

## What You Don't Do

- Start with "So,..." (banned)
- Pad responses with filler
- Bury the answer under context
- Sound like a customer service script
- Give walls of text
- Recommend specific medications
- Pretend to have research you don't have

## Medical Stuff

Medications, dosages, diagnoses = always defer to doctors.
Keep it simple: "that's a doctor question. I can explain how things generally work, but what to take is between you and your psychiatrist."

## Remember

You're a smart teacher who respects their time.
Be clear. Be structured. Be direct.
Get to the point, then stop."""

    # GENERATION
    answer = ""
    used_model = ""

    # Prepare messages with history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history (limit to last 10 messages to avoid token limits)
    for msg in history[-10:]:
        role = "user" if msg.get("sender") == "user" else "assistant"
        content = msg.get("message", "")
        messages.append({"role": role, "content": content})
        
    # Add current query
    # For Sage, we might want to inject context into the last user message
    if persona == "sage" and retrieved_context:
        messages.append({"role": "user", "content": f"{retrieved_context}\n\nUser: {query}"})
    else:
        messages.append({"role": "user", "content": query})

    # 1. Stargirl -> Together.ai (Fine-tuned Stargirl) or Fallback to Groq
    if persona == "stargirl":
        print(f"DEBUG: together_client exists: {together_client is not None}")
        # Primary: Together.ai with fine-tuned Stargirl model
        if together_client:
            try:
                print(f"ATTEMPTING: Together.ai (mistralai/Mistral-7B-Instruct-v0.3 + kash-on-the-dash/stargirl-mistral-7b)...")
                
                # Add variety instruction to prevent repetitive responses
                variety_styles = [
                    "Respond with pure validation, no questions.",
                    "Ask one curious question about what happened before.",
                    "Suggest a tiny physical action.",
                    "Just sit with them, minimal words.",
                    "Be gently playful.",
                    "Reflect back what you heard.",
                    "Share a brief observation.",
                ]
                
                # Add variety instruction as a system message
                messages_with_variety = messages.copy()
                messages_with_variety.append({
                    "role": "system", 
                    "content": f"[Style hint: {random.choice(variety_styles)}]"
                })
                
                # Mistral 7B base + Stargirl LoRA pulled from HuggingFace at inference time.
                # No dedicated endpoint required — Together bills per-token only.
                response = together_client.chat.completions.create(
                    model="mistralai/Mistral-7B-Instruct-v0.3",
                    lora="kash-on-the-dash/stargirl-mistral-7b",
                    messages=messages_with_variety,
                    max_tokens=250,
                    temperature=1.0,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    seed=random.randint(1, 100000),
                )
                answer = response.choices[0].message.content
                used_model = "mistral-7b-stargirl-lora"
                print("SUCCESS: Together.ai (Stargirl) response received.")
                
            except Exception as e:
                print(f"FAILED: Together.ai error: {type(e).__name__}: {e}")
        else:
            print("SKIPPED: together_client is None, using Groq fallback")
        
        if not answer:
            try:
                print(f"Calling Groq (Llama 3.3 70B) for {persona} (Fallback)...")
                if not groq_client:
                    raise Exception("GROQ_API_KEY not set")

                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=250,
                    temperature=0.8
                )
                answer = response.choices[0].message.content
                used_model = "llama-3.3-70b-versatile (fallback)"
                print("Groq response received.")
            except Exception as e:
                print(f"Groq fallback failed: {e}. Will try final fallback.")
                # Leave answer empty so final fallback (Claude/Error) can trigger


    # 2. Sage -> Groq (Llama 3.3 70B)
    elif persona == "sage" and groq_client:
        try:
            print(f"Calling Groq (Llama 3.3 70B) for {persona}...")
            
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False
            )
            answer = completion.choices[0].message.content
            used_model = "llama-3.3-70b-versatile"
            print("Groq response received.")
        except Exception as e:
            print(f"Groq failed: {e}. Falling back to Claude.")
            # Fallback logic could go here if needed
            
    # Fallback if no answer yet (e.g. Sage failed Groq or Stargirl failed OpenAI)
    if not answer:
         try:
            if not claude:
                raise Exception("ANTHROPIC_API_KEY not set - no fallback available")

            print("Calling Claude Haiku 4.5 (Fallback)...")
            # Claude expects a different format, but for simplicity let's try to adapt
            # or just use the simple format for fallback
            claude_messages = []
            for msg in history[-5:]:
                 role = "user" if msg.get("sender") == "user" else "assistant"
                 claude_messages.append({"role": role, "content": msg.get("message", "")})

            claude_messages.append({"role": "user", "content": f"CONTEXT:\n{retrieved_context}\n\nUSER:\n{query}"})

            message = claude.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                temperature=0.3,
                system=system_prompt,
                messages=claude_messages
            )
            answer = message.content[0].text
            used_model = "claude-haiku-4-5 (fallback)"
         except Exception as e:
            print(f"Fallback failed: {e}")
            answer = "I'm having trouble connecting right now. Please check that API keys are configured."

    # Clean the response - strip thought tags and other internal markers
    if answer:
        # Remove <thought>...</thought> tags and their content
        answer = re.sub(r'<thought>.*?</thought>', '', answer, flags=re.DOTALL | re.IGNORECASE)
        # Remove <thinking>...</thinking> tags and their content  
        answer = re.sub(r'<thinking>.*?</thinking>', '', answer, flags=re.DOTALL | re.IGNORECASE)
        # Clean up any extra whitespace
        answer = answer.strip()
        # Remove leading newlines
        answer = answer.lstrip('\n')

    return {
        "answer": answer,
        "sources": sources,
        "model": used_model
    }

def generate_response(query, persona, history=None):
    """Wrapper for run_rag that returns just the answer string."""
    result = run_rag(query, persona, history or [])
    return result["answer"]

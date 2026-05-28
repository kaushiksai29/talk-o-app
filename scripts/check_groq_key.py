import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv("scripts/.env")
load_dotenv(".env")

key = os.getenv("GROQ_API_KEY")
print(f"Key loaded: '{key}'")

if not key:
    print("Key is empty!")
    exit(1)

client = Groq(api_key=key)

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    print("Success!")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")

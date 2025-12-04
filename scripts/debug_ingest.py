import os
import voyageai
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
vo = voyageai.Client(api_key=VOYAGE_API_KEY)

text = "This is a test document."
print(f"Embedding: {text}")

try:
    result = vo.embed(texts=[text], model="voyage-3", input_type="document")
    embedding = result.embeddings[0]
    print(f"Embedding generated. Length: {len(embedding)}")
except Exception as e:
    print(f"Embedding error: {e}")
    exit(1)

row = {
    "content": text,
    "metadata": {"persona": "test", "source": "debug"},
    "embedding": embedding
}

print("Inserting into Supabase...")
try:
    data = supabase.table("documents").insert([row]).execute()
    print("Success!")
    print(data)
except Exception as e:
    print(f"Insertion error: {e}")
    # Try to print more details if available
    if hasattr(e, 'details'):
        print(f"Details: {e.details}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response}")

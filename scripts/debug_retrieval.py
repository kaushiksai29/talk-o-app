
import os
import voyageai
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# Load env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not VOYAGE_API_KEY:
    print("Missing keys.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
vo = voyageai.Client(api_key=VOYAGE_API_KEY)

query = "is body doubling actually backed by science?"

print(f"Embedding query: '{query}'...")
start = time.time()
try:
    query_embedding = vo.embed(
        texts=[query],
        model="voyage-3",
        input_type="query"
    ).embeddings[0]
    print(f"Embedding took {time.time() - start:.2f}s")
except Exception as e:
    print(f"Embedding failed: {e}")
    exit(1)

print("Calling match_documents...")
start = time.time()
try:
    response = supabase.rpc(
        'match_documents', 
        {
            'query_embedding': query_embedding,
            'match_threshold': 0.0,
            'match_count': 3
        }
    ).execute()
    print(f"Retrieval took {time.time() - start:.2f}s")
    print(f"Found {len(response.data)} documents.")
except Exception as e:
    print(f"Retrieval failed: {e}")
    if hasattr(e, 'details'):
        print(f"Details: {e.details}")
    if hasattr(e, 'message'):
        print(f"Message: {e.message}")

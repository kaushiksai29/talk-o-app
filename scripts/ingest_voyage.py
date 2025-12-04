import os
import json
import voyageai
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# Load env from scripts/.env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# --- CONFIGURATION ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not VOYAGE_API_KEY:
    print("Error: Missing environment variables. Please check scripts/.env")
    print(f"SUPABASE_URL: {'Found' if SUPABASE_URL else 'Missing'}")
    print(f"SUPABASE_KEY: {'Found' if SUPABASE_KEY else 'Missing'}")
    print(f"VOYAGE_API_KEY: {'Found' if VOYAGE_API_KEY else 'Missing'}")
    exit(1)

# Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
vo = voyageai.Client(api_key=VOYAGE_API_KEY)

DATA_FILES = [
    {"path": os.path.join(os.path.dirname(__file__), "../data/processed/sage_dataset.jsonl"), "persona": "sage"},
    {"path": os.path.join(os.path.dirname(__file__), "../data/processed/stargirl_dataset.jsonl"), "persona": "stargirl"},
]

def ingest_file(filepath, persona_type):
    print(f"--- Processing {filepath} for {persona_type} ---")
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        data = []
        for line in f:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(data)} items.")

    # Batch processing
    batch_size = 32 # Reduced from 64
    total_inserted = 0
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        
        # 1. Prepare texts to embed
        documents_to_embed = []
        batch_items = []
        
        for item in batch:
            text = item.get('context') or item.get('text') or item.get('summary') or ""
            if text and len(text.strip()) > 0:
                documents_to_embed.append(text)
                batch_items.append(item)
        
        if not documents_to_embed:
            continue
            
        # 2. Generate Embeddings via Voyage-3
        print(f"Embedding batch {i} to {i+len(batch)}...")
        try:
            result = vo.embed(
                texts=documents_to_embed, 
                model="voyage-3", 
                input_type="document"
            )
        except Exception as e:
            print(f"Error embedding batch {i}: {e}")
            continue
        
        # 3. Prepare rows for Supabase
        rows = []
        for j, embedding in enumerate(result.embeddings):
            rows.append({
                "content": documents_to_embed[j],
                "metadata": {
                    "persona": persona_type, 
                    "full_response": batch_items[j].get('response', ''),
                    "source": batch_items[j].get('source', 'unknown')
                },
                "embedding": embedding
            })
            
        # 4. Insert into Supabase
        try:
            data_response = supabase.table("documents").insert(rows).execute()
            total_inserted += len(rows)
            print(f"Inserted {len(rows)} rows. Total: {total_inserted}")
        except Exception as e:
            print(f"Error inserting batch {i} into Supabase: {e}")
            # Print first error detail if available
            if hasattr(e, 'details'):
                print(f"Details: {e.details}")
        
        print("Sleeping 1s (Standard Rate Limit)...")
        time.sleep(1)
            
    print(f"Finished processing {filepath}. Total inserted: {total_inserted}")

if __name__ == "__main__":
    for file_info in DATA_FILES:
        ingest_file(file_info["path"], file_info["persona"])

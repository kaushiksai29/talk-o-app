"""
Ingest processed JSONL datasets into a local Chroma collection.
- Uses OpenAI embeddings by default (text-embedding-3-small).
- Batches embedding calls for efficiency.
- Stores metadata: persona, source, text, text_id.
"""

import os
import json
from tqdm import tqdm
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI, RateLimitError
import math
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Config
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

CHROMA_DIRECTORY = os.path.join(os.path.dirname(__file__), "../chroma_data")
DATA_FILES = [
    os.path.join(os.path.dirname(__file__), "../data/processed/stargirl_dataset.jsonl"),
    # os.path.join(os.path.dirname(__file__), "../data/processed/sage_dataset.jsonl"),  # Uncomment when sage data is available
]

# Choose embedding model (OpenAI or switch to local sentence-transformers)
OPENAI_EMBED_MODEL = "text-embedding-3-small"  # high quality; dim=1536

# Batch size for embedding calls (OpenAI rate/latency trade-off)
BATCH_SIZE = 64

def load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            # unify fields
            text = d.get("response") or d.get("text") or d.get("summary") or ""
            context = d.get("context") or ""
            persona = d.get("persona") or "unknown"
            source = d.get("source") or "unknown"
            if not text or len(text.strip()) < 20:
                continue
            items.append({
                "id": f"{os.path.basename(path)}_{idx}",
                "text": text.strip(),
                "context": context.strip(),
                "persona": persona,
                "source": source
            })
    return items

def batch(iterable, n=1):
    l = len(iterable)
    for i in range(0, l, n):
        yield iterable[i : i + n]

def get_openai_embeddings(texts):
    """Return list of embeddings for list of texts using OpenAI embeddings API."""
    # OpenAI supports batch embedding calls
    resp = openai_client.embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
    return [r.embedding for r in resp.data]

def main():
    # create chroma client (persist to disk)
    client = chromadb.PersistentClient(path=CHROMA_DIRECTORY)
    collection_name = "adhd_support_pal"

    # Use OpenAI embedding function adapter for chroma
    ef = embedding_functions.OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name=OPENAI_EMBED_MODEL)

    # Get or create collection
    try:
        collection = client.get_or_create_collection(name=collection_name, embedding_function=ef)
        print(f"Using existing collection '{collection_name}' with {collection.count()} existing items")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        # If there's an error, try deleting and recreating
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass
        collection = client.create_collection(name=collection_name, embedding_function=ef)
        print(f"Created new collection '{collection_name}'")

    total_added = 0
    for file in DATA_FILES:
        print("Processing:", file)
        items = load_jsonl(file)
        print(f"Loaded {len(items)} items from file")

        # Check which items already exist in the collection
        existing_ids = set()
        try:
            # Get all existing IDs from the collection
            all_existing = collection.get(include=[])
            existing_ids = set(all_existing['ids']) if all_existing and 'ids' in all_existing else set()
            print(f"Found {len(existing_ids)} existing items in collection")
        except Exception as e:
            print(f"Could not check existing items: {e}")

        # Filter out items that already exist
        new_items = [it for it in items if it["id"] not in existing_ids]
        print(f"Will add {len(new_items)} new items (skipping {len(items) - len(new_items)} duplicates)")

        if len(new_items) == 0:
            print("No new items to add from this file")
            continue

        # prepare metadata and texts
        ids = [it["id"] for it in new_items]
        texts = [ (it["context"] + "\n\n" + it["text"]).strip() for it in new_items ]
        metas = [ {"persona": it["persona"], "source": it["source"], "text_id": it["id"]} for it in new_items ]

        # insert in batches
        for i, batch_idxs in enumerate(batch(list(range(len(texts))), BATCH_SIZE)):
            sub_ids = [ids[j] for j in batch_idxs]
            sub_texts = [texts[j] for j in batch_idxs]
            sub_metas = [metas[j] for j in batch_idxs]
            # Upsert into chroma (using its embedding function adapter) with retry logic
            max_retries = 5
            retry_delay = 1
            for attempt in range(max_retries):
                try:
                    collection.add(documents=sub_texts, metadatas=sub_metas, ids=sub_ids)
                    total_added += len(sub_ids)
                    print(f"Upserted batch {i+1}, count={len(sub_ids)} (total {total_added})")
                    break
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"Failed after {max_retries} retries. Error: {e}")
                        raise
    print("Done. Total vectors:", total_added)

if __name__ == "__main__":
    main()

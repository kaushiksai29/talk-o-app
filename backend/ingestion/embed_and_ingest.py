import os
import json
from tqdm import tqdm
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# Config
MODEL_NAME = "all-MiniLM-L6-v2"
# Use absolute path for DB to avoid CWD issues
DB_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data") # Pointing to project root data

# Updated Collections Mapping
COLLECTIONS = {
    "sage_docs": "processed/sage_dataset.jsonl",
    "stargirl_docs": "processed/stargirl_dataset.jsonl",
    "adhd_facts": "../backend/data/adhd_facts.jsonl",
    "adhd_strategies": "../backend/data/adhd_strategies.jsonl",
    "grounding": "../backend/data/grounding.jsonl",
    "cbt": "../backend/data/cbt.jsonl"
}

def load_jsonl(filename):
    # Handle relative paths from DATA_DIR or absolute paths
    if filename.startswith(".."):
        path = os.path.join(os.path.dirname(__file__), filename)
    else:
        path = os.path.join(DATA_DIR, filename)
        
    if not os.path.exists(path):
        print(f"Warning: {path} does not exist.")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        items = []
        for line in f:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return items

def chunk_text(text, max_chars=300):
    if not text:
        return []
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def main():
    print(f"Initializing ChromaDB Client at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    for collection_name, filename in COLLECTIONS.items():
        print(f"\nProcessing {collection_name} from {filename}...")
        
        # Delete existing collection to start fresh
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass
        
        collection = client.create_collection(name=collection_name)
        
        data = load_jsonl(filename)
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        count = 0
        for item in tqdm(data, desc="Embedding"):
            # Handle different field names from different sources
            text = item.get("text") or item.get("response") or item.get("summary") or item.get("abstract") or ""
            source = item.get("source", collection_name)
            context = item.get("context", "")
            
            if not text:
                continue
                
            # Combine context and text if available
            full_text = f"{context}\n{text}" if context else text
            
            chunks = chunk_text(full_text)
            for chunk in chunks:
                # Generate embedding
                embedding = model.encode(chunk).tolist()
                
                ids.append(f"{collection_name}_{count}")
                documents.append(chunk)
                metadatas.append({"source": source, "original_text": text[:50] + "..."})
                embeddings.append(embedding)
                count += 1
        
        if ids:
            # Batch add to avoid payload limits
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                end = min(i + batch_size, len(ids))
                collection.add(
                    ids=ids[i:end],
                    documents=documents[i:end],
                    embeddings=embeddings[i:end],
                    metadatas=metadatas[i:end]
                )
            print(f"Inserted {len(ids)} vectors into {collection_name}")
        else:
            print(f"No data found for {collection_name}")

if __name__ == "__main__":
    main()

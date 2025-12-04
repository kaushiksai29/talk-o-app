import chromadb
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)

print(f"Connected to ChromaDB at: {DB_PATH}")
print("Listing collections:")
try:
    collections = client.list_collections()
    for c in collections:
        print(f"- {c.name} (Count: {c.count()})")
except Exception as e:
    print(f"Error listing collections: {e}")

from chromadb.utils import embedding_functions
import chromadb
import os

# Use absolute path for DB
DB_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")
MODEL_NAME = "text-embedding-3-small"

class PersonaRetriever:
    def __init__(self):
        print(f"Initializing PersonaRetriever with DB: {DB_PATH}")
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found in env for PersonaRetriever")
            
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=MODEL_NAME
        )

    def _search(self, collection_name, query, limit=5):
        try:
            # Pass embedding_function so we can query by text
            collection = self.client.get_collection(
                name=collection_name, 
                embedding_function=self.embedding_function
            )
        except Exception:
            print(f"Warning: Collection {collection_name} not found.")
            return []
            
        # Query using text directly (Chroma handles embedding)
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        # Chroma returns lists of lists
        if not results['documents']:
            return []
            
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        
        hits = []
        for i in range(len(documents)):
            hits.append({
                "text": documents[i],
                "source": metadatas[i].get("source", collection_name)
            })
        return hits

    def retrieve_stargirl(self, query):
        return self._search("stargirl_docs", query)

    def retrieve_sage(self, query):
        return self._search("sage_docs", query)

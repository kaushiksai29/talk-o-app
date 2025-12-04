import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

# Load env from scripts/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../scripts/.env"))

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# DB Config for Knowledge Retrievers
from chromadb.utils import embedding_functions

# ... (existing imports)

# DB Config for Knowledge Retrievers
DB_PATH = os.path.join(os.path.dirname(__file__), "../chroma_db")
MODEL_NAME = "text-embedding-3-small"

# ... (SYSTEM_PROMPT)

class KnowledgeRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        api_key = os.environ.get("OPENAI_API_KEY")
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=MODEL_NAME
        )

    def _search(self, collection_name, query, limit=5):
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except Exception:
            return []
            
        # Query using text directly
        results = collection.query(
            query_texts=[query],
            n_results=limit
        )
        
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

    def retrieve_adhd_facts(self, query):
        return self._search("adhd_facts", query)

    def retrieve_adhd_strategies(self, query):
        return self._search("adhd_strategies", query)

    def retrieve_grounding(self, query):
        return self._search("grounding", query)

    def retrieve_cbt(self, query):
        return self._search("cbt", query)

def route_query(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Using a capable model for routing
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            temperature=0
        )
        content = response.choices[0].message.content
        # Clean up potential markdown code blocks
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Routing failed: {e}")
        return []

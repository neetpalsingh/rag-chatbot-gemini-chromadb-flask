import chromadb
from typing import List, Dict
from chromadb.config import Settings
from app.config import Config

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(Config.CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        ids = [f"doc_{i}_{metadata[0].get('filename', 'unknown')}" for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> Dict:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else []
        }
    
    def get_collection_count(self) -> int:
        return self.collection.count()
    
    def clear_collection(self):
        self.client.delete_collection("documents")
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

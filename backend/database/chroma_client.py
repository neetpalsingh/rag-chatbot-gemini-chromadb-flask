import logging
import chromadb
from chromadb.config import Settings
from config import Config

logger = logging.getLogger(__name__)

class ChromaManager:
    """
    ChromaDB manager for vector storage operations.
    Handles collection creation, document storage, and similarity search.
    """
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(
            path=str(Config.CHROMA_DB_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = "documents"
        self.collection = self._get_or_create_collection()
        logger.info(f'ChromaDB initialized at {Config.CHROMA_DB_DIR}')
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one."""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str]
    ) -> None:
        """
        Add documents with embeddings to the collection.
        
        Args:
            documents: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of unique document IDs
        """
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f'Added {len(documents)} documents to ChromaDB')
        except Exception as e:
            logger.exception(f'Failed to add documents: {e}')
            raise
    
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5
    ) -> dict:
        """
        Perform similarity search using query embedding.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            
        Returns:
            dict: Search results with documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            logger.info(f'Similarity search returned {len(results["documents"][0])} results')
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
        except Exception as e:
            logger.exception(f'Similarity search failed: {e}')
            raise
    
    def get_count(self) -> int:
        """Get total number of documents in collection."""
        return self.collection.count()
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info('Collection deleted and recreated')
        except Exception as e:
            logger.exception(f'Failed to delete collection: {e}')
            raise

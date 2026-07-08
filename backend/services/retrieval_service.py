import logging
from services.embedding_service import GeminiEmbeddingService
from database.chroma_client import ChromaManager
from config import Config

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Service for retrieving relevant document chunks.
    Handles query embedding and vector search.
    """
    
    def __init__(
        self,
        embedding_service: GeminiEmbeddingService,
        chroma_manager: ChromaManager
    ):
        """
        Initialize retrieval service with dependencies.
        
        Args:
            embedding_service: Service for generating embeddings
            chroma_manager: ChromaDB manager
        """
        self.embedding_service = embedding_service
        self.chroma_manager = chroma_manager
        logger.info('Retrieval service initialized')
    
    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = None
    ) -> dict:
        """
        Retrieve top-K relevant chunks for a query.
        
        Args:
            query: User query text
            top_k: Number of chunks to retrieve
            
        Returns:
            dict: Retrieved chunks with metadata and similarity scores
        """
        try:
            top_k = top_k or Config.TOP_K_RESULTS
            
            query_embedding = self.embedding_service.generate_query_embedding(query)
            
            search_results = self.chroma_manager.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            formatted_results = {
                'chunks': search_results['documents'],
                'sources': [
                    {
                        'text': doc,
                        'metadata': meta,
                        'similarity_score': 1 - dist
                    }
                    for doc, meta, dist in zip(
                        search_results['documents'],
                        search_results['metadatas'],
                        search_results['distances']
                    )
                ]
            }
            
            logger.info(f'Retrieved {len(formatted_results["chunks"])} chunks for query')
            return formatted_results
            
        except Exception as e:
            logger.exception(f'Retrieval failed: {e}')
            raise

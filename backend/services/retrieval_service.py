import logging
from typing import Optional, List
from services.embedding_service import GeminiEmbeddingService
from database.chroma_client import ChromaManager
from database.local_db import LocalDatabase
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
        chroma_manager: ChromaManager,
        local_db: Optional[LocalDatabase] = None
    ):
        """
        Initialize retrieval service with dependencies.

        Args:
            embedding_service: Service for generating embeddings
            chroma_manager: ChromaDB manager
            local_db: Optional local database for metadata
        """
        self.embedding_service = embedding_service
        self.chroma_manager = chroma_manager
        self.local_db = local_db or LocalDatabase()
        logger.info('Retrieval service initialized')
    
    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = None,
        category_filter: Optional[str] = None
    ) -> dict:
        """
        Retrieve top-K relevant chunks for a query with optional filtering.

        Args:
            query: User query text
            top_k: Number of chunks to retrieve
            category_filter: Optional category to filter by (hr, finance, etc.)

        Returns:
            dict: Retrieved chunks with metadata and similarity scores
        """
        try:
            top_k = top_k or Config.TOP_K_RESULTS

            collection_names = self.local_db.get_all_collection_names()

            query_embedding = self.embedding_service.generate_query_embedding(query)

            metadata_filter = None
            if category_filter:
                metadata_filter = {'category': category_filter}

            search_results = self.chroma_manager.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                collection_names=collection_names,
                metadata_filter=metadata_filter
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

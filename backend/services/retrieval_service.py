import logging
from typing import Optional, List
from services.embedding_service import GeminiEmbeddingService
from database.chroma_client import ChromaManager
from database.local_db import LocalDatabase
from config import Config

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(
        self,
        embedding_service: GeminiEmbeddingService,
        chroma_manager: ChromaManager,
        local_db: Optional[LocalDatabase] = None
    ):
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
        try:
            top_k = top_k or Config.TOP_K_RESULTS

            # Get all available collections
            collection_names = self.local_db.get_all_collection_names()

            # Convert query to embedding
            query_embedding = self.embedding_service.generate_query_embedding(query)

            metadata_filter = None
            if category_filter:
                metadata_filter = {'category': category_filter}

            # Search across all collections
            search_results = self.chroma_manager.similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                collection_names=collection_names,
                metadata_filter=metadata_filter
            )

            # Format results for chat service
            formatted_results = {
                'chunks': search_results['documents'],
                'sources': [
                    {
                        'text': doc,
                        'metadata': meta,
                        'similarity_score': 1 - dist  # Convert distance to similarity
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

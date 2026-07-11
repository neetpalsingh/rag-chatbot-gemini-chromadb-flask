import logging
import google.generativeai as genai
from config import Config

logger = logging.getLogger(__name__)

class GeminiEmbeddingService:
    """
    Service for generating embeddings using Google Gemini API.
    Handles both document and query embeddings.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini client with API key.

        Args:
            api_key: Gemini API key (defaults to config value)

        Raises:
            ValueError: If API key is not configured
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=self.api_key)
        self.embed_model = Config.GEMINI_EMBED_MODEL
        self.embedding_dimension = Config.EMBEDDING_DIMENSION
        logger.info(f'Gemini embedding service initialized with model: {self.embed_model}, dimension: {self.embedding_dimension}')
    
    def generate_document_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a document chunk.

        Args:
            text: Document text to embed

        Returns:
            list[float]: Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embed_model,
                content=text,
                task_type="retrieval_document",
                output_dimensionality=self.embedding_dimension
            )
            return result['embedding']
        except Exception as e:
            logger.exception(f'Failed to generate document embedding: {e}')
            raise
    
    def generate_query_embedding(self, query: str) -> list[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Query text to embed

        Returns:
            list[float]: Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embed_model,
                content=query,
                task_type="retrieval_query",
                output_dimensionality=self.embedding_dimension
            )
            logger.info(f'Generated query embedding for: {query[:50]}...')
            return result['embedding']
        except Exception as e:
            logger.exception(f'Failed to generate query embedding: {e}')
            raise
    
    def generate_batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple document chunks.
        
        Args:
            texts: List of text chunks
            
        Returns:
            list[list[float]]: List of embedding vectors
        """
        embeddings = []
        for idx, text in enumerate(texts):
            try:
                embedding = self.generate_document_embedding(text)
                embeddings.append(embedding)
                if (idx + 1) % 10 == 0:
                    logger.info(f'Generated {idx + 1}/{len(texts)} embeddings')
            except Exception as e:
                logger.exception(f'Failed to embed chunk {idx}: {e}')
                raise
        
        logger.info(f'Successfully generated {len(embeddings)} embeddings')
        return embeddings

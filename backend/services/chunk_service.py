import logging
from config import Config

logger = logging.getLogger(__name__)

class ChunkService:
    """
    Service for splitting documents into chunks.
    Implements word-based chunking with overlap.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize chunking parameters.
        
        Args:
            chunk_size: Number of words per chunk
            chunk_overlap: Number of overlapping words between chunks
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE_WORDS
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP_WORDS
        logger.info(
            f'Chunk service initialized: size={self.chunk_size}, '
            f'overlap={self.chunk_overlap}'
        )
    
    def create_chunks(self, text: str, filename: str) -> tuple[list[str], list[dict]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            filename: Original filename for metadata
            
        Returns:
            tuple: (list of text chunks, list of metadata dicts)
        """
        try:
            words = text.split()
            chunks = []
            metadatas = []
            
            for idx in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk_words = words[idx:idx + self.chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                if chunk_text.strip():
                    chunks.append(chunk_text)
                    metadatas.append({
                        'filename': filename,
                        'chunk_index': len(chunks) - 1,
                        'total_chunks': -1
                    })
            
            for metadata in metadatas:
                metadata['total_chunks'] = len(chunks)
            
            logger.info(f'Created {len(chunks)} chunks from {filename}')
            return chunks, metadatas
            
        except Exception as e:
            logger.exception(f'Failed to create chunks: {e}')
            raise

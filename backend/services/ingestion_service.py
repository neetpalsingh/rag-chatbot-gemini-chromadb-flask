import logging
import uuid
from pathlib import Path
from services.embedding_service import GeminiEmbeddingService
from services.chunk_service import ChunkService
from database.chroma_client import ChromaManager
from utils.pdf_reader import PDFReader
from utils.text_reader import TextReader

logger = logging.getLogger(__name__)

class DocumentIngestionService:
    def __init__(
        self,
        embedding_service: GeminiEmbeddingService,
        chunk_service: ChunkService,
        chroma_manager: ChromaManager
    ):
        self.embedding_service = embedding_service
        self.chunk_service = chunk_service
        self.chroma_manager = chroma_manager
        self.pdf_reader = PDFReader()
        self.text_reader = TextReader()
        logger.info('Document ingestion service initialized')
    
    def process_document(self, file_path: Path, category: str = 'general', collection_name: str = None) -> dict:
        try:
            # Generate unique collection name for this document
            if collection_name is None:
                collection_name = self._generate_collection_name(file_path.name)

            # Extract text from document
            text = self._read_document(file_path)

            # Split into chunks
            chunks, metadatas = self.chunk_service.create_chunks(
                text=text,
                filename=file_path.name
            )

            # Add category to all chunk metadata
            for metadata in metadatas:
                metadata['category'] = category
                metadata['collection'] = collection_name

            if not chunks:
                raise ValueError("No chunks created from document")

            # Generate embeddings for all chunks
            embeddings = self.embedding_service.generate_batch_embeddings(chunks)

            # Create unique IDs for each chunk
            ids = self._generate_chunk_ids(file_path.name, len(chunks))

            self.chroma_manager.add_documents(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
                collection_name=collection_name
            )

            logger.info(f'Successfully processed {file_path.name}: {len(chunks)} chunks in collection {collection_name}')

            return {
                'filename': file_path.name,
                'chunks_count': len(chunks),
                'collection_name': collection_name,
                'success': True
            }

        except Exception as e:
            logger.exception(f'Failed to process document {file_path.name}: {e}')
            raise
    
    def _read_document(self, file_path: Path) -> str:
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.pdf_reader.read_pdf(file_path)
        elif extension == '.txt':
            return self.text_reader.read_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def _generate_chunk_ids(self, filename: str, chunk_count: int) -> list[str]:
        unique_id = str(uuid.uuid4())[:8]
        return [f"{filename}_{unique_id}_chunk_{idx}" for idx in range(chunk_count)]

    def _generate_collection_name(self, filename: str) -> str:
        clean_name = filename.replace('.', '_').replace(' ', '_')
        unique_id = str(uuid.uuid4())[:8]
        return f"doc_{clean_name}_{unique_id}"

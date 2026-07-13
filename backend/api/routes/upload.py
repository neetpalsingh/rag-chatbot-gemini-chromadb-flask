import logging
import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from config import Config
from services import (
    GeminiEmbeddingService,
    ChunkService,
    DocumentIngestionService
)
from database import ChromaManager
from database.local_db import LocalDatabase
from utils import FileValidator
from models import (
    UploadData,
    UploadResponse,
    Document,
    DocumentsResponse,
    DeleteResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()

embedding_service = GeminiEmbeddingService()
chunk_service = ChunkService()
chroma_manager = ChromaManager()
local_db = LocalDatabase()
ingestion_service = DocumentIngestionService(
    embedding_service=embedding_service,
    chunk_service=chunk_service,
    chroma_manager=chroma_manager
)

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="general")
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        temp_file = file.file
        is_valid, error_message = FileValidator.validate_upload_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        filename = FileValidator.get_secure_filename(file.filename)
        filepath = Config.UPLOAD_FOLDER / filename
        
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        
        is_valid_size, size_error = FileValidator.validate_file_size(filepath)
        if not is_valid_size:
            filepath.unlink()
            raise HTTPException(status_code=400, detail=size_error)
        
        file_size = os.path.getsize(filepath)
        file_type = filepath.suffix.lower().replace('.', '')
        
        result = ingestion_service.process_document(filepath, category=category)
        
        doc_id = local_db.add_document(
            filename=filename,
            category=category,
            file_type=file_type,
            file_size=file_size,
            chunks_count=result['chunks_count'],
            collection_name=result['collection_name']
        )
        
        filepath.unlink()
        
        logger.info(f'Document uploaded successfully: {filename} (ID: {doc_id})')
        
        return UploadResponse(
            success=True,
            message='Document uploaded and processed successfully',
            data=UploadData(
                id=doc_id,
                filename=result['filename'],
                chunks_count=result['chunks_count'],
                category=category
            )
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        logger.error(f'Validation error: {error_msg}')
        # Return 429 for rate limit errors, 400 for others
        status_code = 429 if 'rate limit' in error_msg.lower() else 400
        raise HTTPException(status_code=status_code, detail=error_msg)
    except Exception as e:
        logger.exception(f'Upload failed: {e}')
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    try:
        documents = local_db.get_all_documents()
        doc_list = [Document(**doc) for doc in documents]
        return DocumentsResponse(success=True, data=doc_list)
    except Exception as e:
        logger.exception(f'Failed to get documents: {e}')
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    try:
        document = local_db.get_document_by_id(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        chroma_manager.delete_collection(document['collection_name'])
        local_db.delete_document(doc_id)
        
        logger.info(f'Document deleted: {doc_id}')
        return DeleteResponse(
            success=True,
            message='Document deleted successfully'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'Failed to delete document: {e}')
        raise HTTPException(status_code=500, detail="Failed to delete document")

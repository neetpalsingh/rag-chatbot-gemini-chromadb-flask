import logging
import os
from flask import Blueprint, request, jsonify
from pathlib import Path
from config import Config
from services import (
    GeminiEmbeddingService,
    ChunkService,
    DocumentIngestionService
)
from database import ChromaManager
from database.local_db import LocalDatabase
from utils import FileValidator

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

embedding_service = GeminiEmbeddingService()
chunk_service = ChunkService()
chroma_manager = ChromaManager()
local_db = LocalDatabase()
ingestion_service = DocumentIngestionService(
    embedding_service=embedding_service,
    chunk_service=chunk_service,
    chroma_manager=chroma_manager
)

@upload_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload and process document endpoint.
    Validates file, processes it, and stores embeddings.
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        category = request.form.get('category', 'general')

        is_valid, error_message = FileValidator.validate_file(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400

        filename = FileValidator.get_secure_filename(file.filename)
        filepath = Config.UPLOAD_FOLDER / filename
        file.save(str(filepath))

        is_valid_size, size_error = FileValidator.validate_file_size(filepath)
        if not is_valid_size:
            filepath.unlink()
            return jsonify({
                'success': False,
                'error': size_error
            }), 400

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
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'data': {
                'id': doc_id,
                'filename': result['filename'],
                'chunks_count': result['chunks_count'],
                'category': category
            }
        }), 200

    except ValueError as e:
        logger.error(f'Validation error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.exception(f'Upload failed: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to process document'
        }), 500

@upload_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get all documents from local database."""
    try:
        documents = local_db.get_all_documents()
        return jsonify({
            'success': True,
            'data': documents
        }), 200
    except Exception as e:
        logger.exception(f'Failed to get documents: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve documents'
        }), 500

@upload_bp.route('/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete document from both local DB and ChromaDB."""
    try:
        document = local_db.get_document_by_id(doc_id)
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404

        chroma_manager.delete_collection(document['collection_name'])
        local_db.delete_document(doc_id)

        logger.info(f'Document deleted: {doc_id}')
        return jsonify({
            'success': True,
            'message': 'Document deleted successfully'
        }), 200
    except Exception as e:
        logger.exception(f'Failed to delete document: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to delete document'
        }), 500

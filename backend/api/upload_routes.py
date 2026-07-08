import logging
from flask import Blueprint, request, jsonify
from pathlib import Path
from config import Config
from services import (
    GeminiEmbeddingService,
    ChunkService,
    DocumentIngestionService
)
from database import ChromaManager
from utils import FileValidator

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

embedding_service = GeminiEmbeddingService()
chunk_service = ChunkService()
chroma_manager = ChromaManager()
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
        
        result = ingestion_service.process_document(filepath)
        
        filepath.unlink()
        
        logger.info(f'Document uploaded successfully: {filename}')
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'data': result
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

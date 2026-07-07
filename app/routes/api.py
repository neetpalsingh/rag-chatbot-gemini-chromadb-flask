from flask import Blueprint, request, jsonify, session
from werkzeug.exceptions import BadRequest
from app.services import GeminiService, VectorStore, DocumentProcessor
from app.utils import FileHandler
from app.config import Config

bp = Blueprint('api', __name__, url_prefix='/api')

gemini_service = GeminiService()
vector_store = VectorStore()
doc_processor = DocumentProcessor()

@bp.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        filepath = FileHandler.save_upload(file)
        
        chunks, metadata = doc_processor.process_document(filepath)
        
        embeddings = [gemini_service.generate_embeddings(chunk) for chunk in chunks]
        
        vector_store.add_documents(chunks, embeddings, metadata)
        
        FileHandler.cleanup_file(filepath)
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'chunks_count': len(chunks),
            'filename': file.filename
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@bp.route('/query', methods=['POST'])
def query_documents():
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        query_embedding = gemini_service.generate_query_embedding(query)
        
        search_results = vector_store.search(query_embedding, Config.TOP_K_RESULTS)
        
        if not search_results['documents']:
            return jsonify({
                'answer': 'No relevant documents found. Please upload documents first.',
                'sources': []
            }), 200
        
        answer = gemini_service.generate_response(query, search_results['documents'])
        
        sources = [
            {
                'text': doc,
                'metadata': meta,
                'similarity': 1 - dist
            }
            for doc, meta, dist in zip(
                search_results['documents'],
                search_results['metadatas'],
                search_results['distances']
            )
        ]
        
        return jsonify({
            'answer': answer,
            'sources': sources
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        count = vector_store.get_collection_count()
        return jsonify({
            'total_chunks': count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

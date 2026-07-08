import logging
from flask import Blueprint, request, jsonify
from services import (
    GeminiEmbeddingService,
    ChatService,
    RetrievalService
)
from database import ChromaManager

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

embedding_service = GeminiEmbeddingService()
chat_service = ChatService()
chroma_manager = ChromaManager()
retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    chroma_manager=chroma_manager
)

@chat_bp.route('/query', methods=['POST'])
def query_documents():
    """
    Query endpoint for chatbot.
    Retrieves relevant chunks and generates response.
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        retrieval_results = retrieval_service.retrieve_relevant_chunks(query)
        
        if not retrieval_results['chunks']:
            return jsonify({
                'success': True,
                'data': {
                    'answer': 'No relevant documents found. Please upload documents first.',
                    'sources': []
                }
            }), 200
        
        answer = chat_service.generate_response(
            query=query,
            context_chunks=retrieval_results['chunks']
        )
        
        logger.info(f'Query processed successfully: {query[:50]}...')
        return jsonify({
            'success': True,
            'data': {
                'answer': answer,
                'sources': retrieval_results['sources']
            }
        }), 200
        
    except Exception as e:
        logger.exception(f'Query failed: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to process query'
        }), 500

import logging
from flask import Blueprint, jsonify
from database import ChromaManager

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__, url_prefix='/api')

chroma_manager = ChromaManager()

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'message': 'Service is running'
    }), 200

@health_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get database statistics.
    Returns total number of document chunks stored.
    """
    try:
        count = chroma_manager.get_count()
        return jsonify({
            'success': True,
            'data': {
                'total_chunks': count
            }
        }), 200
    except Exception as e:
        logger.exception(f'Failed to get stats: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve statistics'
        }), 500

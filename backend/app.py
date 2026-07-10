import logging
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """
    Application factory pattern.
    Creates and configures the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    Config.init_app()
    
    CORS(app)
    
    from api.upload_routes import upload_bp
    from api.chat_routes import chat_bp
    from api.health_routes import health_bp
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)

    @app.route('/')
    def index():
        """Serve the frontend HTML."""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        return send_from_directory(frontend_dir, 'chat.html')

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files (CSS, JS, etc.)."""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        return send_from_directory(frontend_dir, path)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.exception('Internal server error')
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    logger.info('Flask application initialized successfully')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

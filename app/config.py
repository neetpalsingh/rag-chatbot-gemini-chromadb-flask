import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent.parent
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    CHROMA_DB_DIR = BASE_DIR / 'chroma_db'
    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    
    CHUNK_SIZE = 200
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_EMBED_MODEL = 'models/text-embedding-004'
    GEMINI_CHAT_MODEL = 'models/gemini-1.5-flash'
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.CHROMA_DB_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class."""
    
    BASE_DIR = Path(__file__).parent
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    CHROMA_DB_DIR = BASE_DIR / 'chroma_db'
    
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    
    CHUNK_SIZE_WORDS = int(os.getenv('CHUNK_SIZE_WORDS', '200'))
    CHUNK_OVERLAP_WORDS = int(os.getenv('CHUNK_OVERLAP_WORDS', '50'))
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))

    GEMINI_EMBED_MODEL = os.getenv('GEMINI_EMBED_MODEL', 'models/text-embedding-004')
    GEMINI_CHAT_MODEL = os.getenv('GEMINI_CHAT_MODEL', 'models/gemini-1.5-flash')

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app():
        """Initialize application folders."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.CHROMA_DB_DIR, exist_ok=True)

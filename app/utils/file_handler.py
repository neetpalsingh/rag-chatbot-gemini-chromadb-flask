import os
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.config import Config

class FileHandler:
    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_upload(file: FileStorage) -> Path:
        if not file or file.filename == '':
            raise ValueError("No file selected")
        
        if not FileHandler.allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {Config.ALLOWED_EXTENSIONS}")
        
        filename = secure_filename(file.filename)
        filepath = Config.UPLOAD_FOLDER / filename
        
        file.save(str(filepath))
        
        if filepath.stat().st_size > Config.MAX_FILE_SIZE:
            filepath.unlink()
            raise ValueError(f"File size exceeds {Config.MAX_FILE_SIZE / (1024*1024)}MB limit")
        
        return filepath
    
    @staticmethod
    def cleanup_file(filepath: Path):
        if filepath.exists():
            filepath.unlink()

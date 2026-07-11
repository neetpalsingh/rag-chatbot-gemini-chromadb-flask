import logging
import re
from pathlib import Path
from config import Config

try:
    from werkzeug.utils import secure_filename as werkzeug_secure_filename
    from werkzeug.datastructures import FileStorage
    HAS_WERKZEUG = True
except ImportError:
    HAS_WERKZEUG = False

try:
    from fastapi import UploadFile
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

logger = logging.getLogger(__name__)

class FileValidator:
    """
    File upload validation.
    Validates file type, size, and security.
    """

    @staticmethod
    def validate_file(file) -> tuple[bool, str]:
        """
        Validate uploaded file (Flask).

        Args:
            file: Uploaded file object

        Returns:
            tuple: (is_valid, error_message)
        """
        if not file or file.filename == '':
            return False, "No file selected"

        if not FileValidator._is_allowed_extension(file.filename):
            allowed = ', '.join(Config.ALLOWED_EXTENSIONS)
            return False, f"File type not allowed. Allowed: {allowed}"

        return True, ""

    @staticmethod
    def validate_upload_file(file) -> tuple[bool, str]:
        """
        Validate uploaded file (FastAPI).

        Args:
            file: FastAPI UploadFile object

        Returns:
            tuple: (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No file selected"

        if not FileValidator._is_allowed_extension(file.filename):
            allowed = ', '.join(Config.ALLOWED_EXTENSIONS)
            return False, f"File type not allowed. Allowed: {allowed}"

        return True, ""
    
    @staticmethod
    def _is_allowed_extension(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_secure_filename(filename: str) -> str:
        """
        Get secure version of filename.

        Args:
            filename: Original filename

        Returns:
            str: Secure filename
        """
        if HAS_WERKZEUG:
            return werkzeug_secure_filename(filename)

        filename = str(filename).strip().replace(' ', '_')
        filename = re.sub(r'(?u)[^-\w.]', '', filename)
        return filename
    
    @staticmethod
    def validate_file_size(file_path: Path) -> tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_path: Path to file
            
        Returns:
            tuple: (is_valid, error_message)
        """
        file_size = file_path.stat().st_size
        
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            return False, f"File size exceeds {Config.MAX_FILE_SIZE_MB}MB limit"
        
        return True, ""

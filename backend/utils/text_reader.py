import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TextReader:
    """
    Plain text document reader.
    Reads .txt files.
    """
    
    def read_text(self, file_path: Path) -> str:
        """
        Read text from .txt file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            str: File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                logger.info(f'Successfully read {file_path.name}')
                return text.strip()
        except Exception as e:
            logger.exception(f'Failed to read text file {file_path.name}: {e}')
            raise

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TextReader:
    def read_text(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                logger.info(f'Successfully read {file_path.name}')
                return text.strip()
        except Exception as e:
            logger.exception(f'Failed to read text file {file_path.name}: {e}')
            raise

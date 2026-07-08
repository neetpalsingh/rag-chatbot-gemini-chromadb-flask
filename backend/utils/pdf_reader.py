import logging
import PyPDF2
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFReader:
    """
    PDF document reader.
    Extracts text from PDF files.
    """
    
    def read_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    
                    if (page_num + 1) % 10 == 0:
                        logger.info(f'Extracted {page_num + 1}/{page_count} pages')
                
                logger.info(f'Successfully extracted text from {file_path.name}')
                return text.strip()
                
        except Exception as e:
            logger.exception(f'Failed to read PDF {file_path.name}: {e}')
            raise

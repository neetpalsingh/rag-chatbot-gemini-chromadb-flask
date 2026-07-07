import PyPDF2
from typing import List, Dict
from pathlib import Path
from app.config import Config

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def read_file(self, file_path: Path) -> str:
        if file_path.suffix.lower() == '.pdf':
            return self._read_pdf(file_path)
        elif file_path.suffix.lower() == '.txt':
            return self._read_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    def _read_pdf(self, file_path: Path) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _read_txt(self, file_path: Path) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str, filename: str) -> tuple[List[str], List[Dict]]:
        words = text.split()
        chunks = []
        metadata = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)
                metadata.append({
                    'filename': filename,
                    'chunk_index': len(chunks) - 1,
                    'total_chunks': -1
                })
        
        for meta in metadata:
            meta['total_chunks'] = len(chunks)
        
        return chunks, metadata
    
    def process_document(self, file_path: Path) -> tuple[List[str], List[Dict]]:
        text = self.read_file(file_path)
        chunks, metadata = self.chunk_text(text, file_path.name)
        return chunks, metadata

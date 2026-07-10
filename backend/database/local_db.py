import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os
import uuid

logger = logging.getLogger(__name__)

class LocalDatabase:
    def __init__(self, db_path: str = 'data/documents.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                category TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                chunks_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                collection_name TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Local database initialized")
    
    def add_document(self, filename: str, category: str, file_type: str, 
                    file_size: int, chunks_count: int, collection_name: str) -> str:
        doc_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents 
            (id, filename, category, file_type, file_size, chunks_count, status, collection_name, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (doc_id, filename, category, file_type, file_size, chunks_count, 'processed', 
              collection_name, datetime.utcnow().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Document added: {filename} (ID: {doc_id})")
        return doc_id
    
    def get_all_documents(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents ORDER BY uploaded_at DESC')
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                'id': row['id'],
                'filename': row['filename'],
                'category': row['category'],
                'file_type': row['file_type'],
                'file_size': row['file_size'],
                'chunks_count': row['chunks_count'],
                'status': row['status'],
                'collection_name': row['collection_name'],
                'uploaded_at': row['uploaded_at']
            })
        
        conn.close()
        return documents
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'filename': row['filename'],
                'category': row['category'],
                'file_type': row['file_type'],
                'file_size': row['file_size'],
                'chunks_count': row['chunks_count'],
                'status': row['status'],
                'collection_name': row['collection_name'],
                'uploaded_at': row['uploaded_at']
            }
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"Document deleted: {doc_id}")
        return deleted
    
    def get_total_chunks(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(chunks_count) FROM documents')
        result = cursor.fetchone()[0]
        
        conn.close()
        return result or 0
    
    def get_all_collection_names(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT collection_name FROM documents')
        collections = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return collections

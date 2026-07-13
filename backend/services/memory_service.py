import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ChatMemoryService:
    """
    Service for managing chat session memory.
    Stores conversation history in JSON file per session.
    """
    
    def __init__(self, memory_dir: str = "memory"):
        """
        Initialize memory service.

        Args:
            memory_dir: Directory to store session files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Memory service initialized at: {self.memory_dir}')
    
    def create_session(self) -> str:
        """
        Create a new chat session.
        
        Returns:
            str: New session ID
        """
        session_id = str(uuid.uuid4())
        session_file = self._get_session_file(session_id)
        
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f'Created new session: {session_id}')
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to session history.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
        """
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            logger.warning(f'Session {session_id} not found, creating new one')
            self.create_session_with_id(session_id)
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session_data["messages"].append(message)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f'Added {role} message to session {session_id}')
    
    def get_history(self, session_id: str, last_n: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history for session.
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages to retrieve
            
        Returns:
            List of messages with role and content
        """
        session_file = self._get_session_file(session_id)
        
        if not session_file.exists():
            logger.warning(f'Session {session_id} not found')
            return []
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        messages = session_data.get("messages", [])
        recent_messages = messages[-last_n:] if len(messages) > last_n else messages
        
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent_messages
        ]
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear session history.
        
        Args:
            session_id: Session identifier
        """
        session_file = self._get_session_file(session_id)
        
        if session_file.exists():
            session_file.unlink()
            logger.info(f'Cleared session: {session_id}')
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if session exists.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session exists
        """
        return self._get_session_file(session_id).exists()
    
    def create_session_with_id(self, session_id: str) -> None:
        """
        Create session with specific ID.
        
        Args:
            session_id: Session identifier
        """
        session_file = self._get_session_file(session_id)
        
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f'Created session with ID: {session_id}')
    
    def _get_session_file(self, session_id: str) -> Path:
        """Get path to session file."""
        return self.memory_dir / f"{session_id}.json"

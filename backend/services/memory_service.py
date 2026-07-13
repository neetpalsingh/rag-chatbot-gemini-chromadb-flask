import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ChatMemoryService:
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'Memory service initialized at: {self.memory_dir}')
    
    def create_session(self, clear_old: bool = False) -> str:
        # Only clear old sessions when user clicks "New Chat"
        if clear_old:
            self._clear_all_sessions()
            logger.info('Cleared all old sessions for new chat')

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
        session_file = self._get_session_file(session_id)

        # Create session if it doesn't exist
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
        # Only return last N messages to keep context window small
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            logger.warning(f'Session {session_id} not found')
            return []

        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        messages = session_data.get("messages", [])
        recent_messages = messages[-last_n:] if len(messages) > last_n else messages

        logger.info(f'Retrieved {len(recent_messages)} messages from session {session_id} (last {last_n})')

        # Strip timestamps for cleaner LLM input
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent_messages
        ]
    
    def clear_session(self, session_id: str) -> None:
        session_file = self._get_session_file(session_id)
        
        if session_file.exists():
            session_file.unlink()
            logger.info(f'Cleared session: {session_id}')
    
    def session_exists(self, session_id: str) -> bool:
        return self._get_session_file(session_id).exists()
    
    def create_session_with_id(self, session_id: str) -> None:
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
        return self.memory_dir / f"{session_id}.json"

    def _clear_all_sessions(self) -> None:
        try:
            for session_file in self.memory_dir.glob("*.json"):
                session_file.unlink()
                logger.info(f'Deleted old session file: {session_file.name}')
        except Exception as e:
            logger.warning(f'Failed to clear old sessions: {e}')

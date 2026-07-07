from typing import List, Dict
from datetime import datetime
import uuid

class ChatSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str, sources: List[Dict] = None):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'sources': sources or []
        }
        self.messages.append(message)
    
    def get_history(self, limit: int = None) -> List[Dict]:
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear_history(self):
        self.messages = []

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(self) -> str:
        session = ChatSession()
        self.sessions[session.session_id] = session
        return session.session_id
    
    def get_session(self, session_id: str) -> ChatSession:
        if session_id not in self.sessions:
            session = ChatSession(session_id)
            self.sessions[session_id] = session
        return self.sessions[session_id]
    
    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

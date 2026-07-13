import json
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMemoryService:
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / "chat_history.json"
        self._initialize_memory_file()
        logger.info(f'Memory service initialized with single file: {self.memory_file}')

    def _initialize_memory_file(self):
        if not self.memory_file.exists():
            self._write_memory({
                "created_at": datetime.now().isoformat(),
                "messages": []
            })

    def _read_memory(self) -> Dict:
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"created_at": datetime.now().isoformat(), "messages": []}

    def _write_memory(self, data: Dict):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        memory_data = self._read_memory()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        memory_data["messages"].append(message)
        self._write_memory(memory_data)

        logger.info(f'Added {role} message (total: {len(memory_data["messages"])})')

    def get_history(self, session_id: str, last_n: int = 10) -> List[Dict[str, str]]:
        memory_data = self._read_memory()
        messages = memory_data.get("messages", [])

        recent_messages = messages[-last_n:] if len(messages) > last_n else messages

        logger.info(f'Retrieved {len(recent_messages)} messages (last {last_n} from {len(messages)} total)')

        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in recent_messages
        ]

    def clear_session(self, session_id: str = None) -> None:
        self._write_memory({
            "created_at": datetime.now().isoformat(),
            "messages": []
        })
        logger.info('Cleared chat history')

"""In-memory session history with swappable interface."""
from collections import defaultdict
from app.models.schemas import ChatMessage


class SessionMemoryStore:
    def __init__(self, max_messages: int = 10) -> None:
        self._data: dict[str, list[ChatMessage]] = defaultdict(list)
        self.max_messages = max_messages

    def append(self, session_id: str, message: ChatMessage) -> None:
        self._data[session_id].append(message)
        self._data[session_id] = self._data[session_id][-self.max_messages :]

    def get(self, session_id: str) -> list[ChatMessage]:
        return list(self._data.get(session_id, []))

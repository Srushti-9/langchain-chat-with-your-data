import asyncio
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.config import get_settings
from app.core.vectorstore import count_documents, delete_collection


@dataclass
class Session:
    session_id: str
    created_at: datetime
    strategy: str = "similarity"
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self) -> Session:
        session_id = uuid.uuid4().hex
        session = Session(session_id=session_id, created_at=datetime.now(timezone.utc))
        self._sessions[session_id] = session
        self._upload_dir(session_id).mkdir(parents=True, exist_ok=True)
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def list(self) -> list[dict]:
        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat(),
                "doc_count": count_documents(s.session_id),
            }
            for s in self._sessions.values()
        ]

    def delete(self, session_id: str) -> bool:
        session = self._sessions.pop(session_id, None)
        if session is None:
            return False
        delete_collection(session_id)
        shutil.rmtree(self._upload_dir(session_id), ignore_errors=True)
        return True

    def _upload_dir(self, session_id: str):
        return get_settings().upload_dir / session_id


_manager = SessionManager()


def get_session_manager() -> SessionManager:
    return _manager

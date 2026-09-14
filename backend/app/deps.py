from fastapi import HTTPException, Path

from app.services.session_manager import Session, get_session_manager


def resolve_session(session_id: str = Path(...)) -> Session:
    session = get_session_manager().get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

from fastapi import APIRouter, Depends, HTTPException

from app.deps import resolve_session
from app.schemas.session import SessionCreated, SessionInfo
from app.services.session_manager import Session, SessionManager, get_session_manager

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreated)
def create_session(manager: SessionManager = Depends(get_session_manager)) -> SessionCreated:
    session = manager.create()
    return SessionCreated(
        session_id=session.session_id,
        created_at=session.created_at.isoformat(),
    )


@router.get("", response_model=list[SessionInfo])
def list_sessions(manager: SessionManager = Depends(get_session_manager)) -> list[SessionInfo]:
    return [SessionInfo(**s) for s in manager.list()]


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    manager: SessionManager = Depends(get_session_manager),
) -> dict[str, str]:
    if not manager.delete(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}

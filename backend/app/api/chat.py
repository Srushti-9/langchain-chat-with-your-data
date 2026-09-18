from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.deps import resolve_session
from app.schemas.chat import ChatRequest
from app.services.session_manager import Session
from app.services.streaming import stream_chat

router = APIRouter(prefix="/sessions/{session_id}/chat", tags=["chat"])


@router.post("")
async def chat(
    request: ChatRequest,
    session: Session = Depends(resolve_session),
) -> StreamingResponse:
    return StreamingResponse(
        stream_chat(session.session_id, request.message),
        media_type="text/event-stream",
    )

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, HumanMessage

from app.core.agent import build_agent, get_checkpointer, get_chat_model
from app.deps import resolve_session
from app.schemas.memory import (
    CondenseRequest,
    CondenseResult,
    MemoryState,
    MemoryTurn,
)
from app.services.session_manager import Session

router = APIRouter(prefix="/sessions/{session_id}/memory", tags=["memory"])

_CONDENSE_PROMPT = (
    "Given the conversation so far and a follow-up question, rewrite the follow-up "
    "as a standalone question that can be understood without the prior context. "
    "Return only the rewritten question.\n\n"
    "Conversation:\n{history}\n\nFollow-up: {followup}\n\nStandalone question:"
)


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


async def _read_turns(session: Session) -> list[MemoryTurn]:
    agent = build_agent(session.session_id, session.strategy)
    state = await agent.aget_state(_config(session.session_id))
    messages = state.values.get("messages", []) if state.values else []
    turns: list[MemoryTurn] = []
    for m in messages:
        content = (getattr(m, "content", "") or "").strip()
        if not content:
            continue
        if isinstance(m, HumanMessage):
            turns.append(MemoryTurn(role="user", content=content))
        elif isinstance(m, AIMessage):
            turns.append(MemoryTurn(role="assistant", content=content))
    return turns


@router.get("", response_model=MemoryState)
async def get_memory(session: Session = Depends(resolve_session)) -> MemoryState:
    return MemoryState(turns=await _read_turns(session))


@router.post("/reset", response_model=MemoryState)
async def reset_memory(session: Session = Depends(resolve_session)) -> MemoryState:
    checkpointer = get_checkpointer()
    if checkpointer is not None:
        await checkpointer.adelete_thread(session.session_id)
    return MemoryState(turns=[])


@router.post("/preview-condensed", response_model=CondenseResult)
async def preview_condensed(
    body: CondenseRequest, session: Session = Depends(resolve_session)
) -> CondenseResult:
    turns = await _read_turns(session)
    history = "\n".join(f"{t.role}: {t.content}" for t in turns) or "(no prior turns)"
    prompt = _CONDENSE_PROMPT.format(history=history, followup=body.followup)
    result = await get_chat_model().ainvoke(prompt)
    return CondenseResult(standalone_question=(result.content or "").strip())

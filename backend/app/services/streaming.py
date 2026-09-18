import json
from collections.abc import AsyncIterator

from langchain_core.documents import Document

from app.core.agent import build_agent


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _sources_from_artifact(artifact) -> list[dict]:
    if not artifact:
        return []
    docs = artifact if isinstance(artifact, list) else [artifact]
    sources = []
    for d in docs:
        if not isinstance(d, Document):
            continue
        meta = d.metadata or {}
        sources.append(
            {
                "source": meta.get("source"),
                "page": meta.get("page"),
                "chunk_index": meta.get("chunk_index"),
                "snippet": d.page_content[:300],
            }
        )
    return sources


async def stream_chat(session_id: str, message: str) -> AsyncIterator[str]:
    agent = build_agent(session_id)
    config = {"configurable": {"thread_id": session_id}}

    try:
        async for ev in agent.astream_events(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            version="v2",
        ):
            et = ev["event"]
            if et == "on_chat_model_stream":
                chunk = ev["data"].get("chunk")
                text = getattr(chunk, "content", None)
                if text:
                    yield _sse({"type": "token", "text": text})
            elif et == "on_tool_start":
                query = (ev.get("data") or {}).get("input", {}).get("query")
                yield _sse({"type": "tool_call", "query": query})
            elif et == "on_tool_end":
                output = (ev.get("data") or {}).get("output")
                artifact = getattr(output, "artifact", None)
                yield _sse({"type": "sources", "sources": _sources_from_artifact(artifact)})
        yield _sse({"type": "done"})
    except Exception as exc:  # surface the failure to the client instead of a dead stream
        yield _sse({"type": "error", "detail": str(exc)})

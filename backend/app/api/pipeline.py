from fastapi import APIRouter, Depends

from app.config import get_settings
from app.core.agent import get_chat_model
from app.core.embeddings import get_embeddings
from app.core.prompts import RAG_SYSTEM_PROMPT
from app.core.retrievers import get_retriever
from app.deps import resolve_session
from app.schemas.pipeline import EmbeddingStage, PipelineTrace, TraceChunk, TraceRequest
from app.services.session_manager import Session

router = APIRouter(prefix="/sessions/{session_id}/pipeline", tags=["pipeline"])


@router.post("/trace", response_model=PipelineTrace)
async def trace_pipeline(
    body: TraceRequest, session: Session = Depends(resolve_session)
) -> PipelineTrace:
    settings = get_settings()
    k = body.k or 4

    query_vector = await get_embeddings().aembed_query(body.query)

    retriever = get_retriever(session.session_id, session.strategy, k)
    docs = await retriever.ainvoke(body.query)
    retrieved = [
        TraceChunk(
            source=(d.metadata or {}).get("source"),
            chunk_index=(d.metadata or {}).get("chunk_index"),
            snippet=d.page_content[:300],
        )
        for d in docs
    ]

    context = "\n\n".join(d.page_content for d in docs) or "(no documents retrieved)"
    prompt = f"{RAG_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {body.query}\n\nAnswer:"
    result = await get_chat_model().ainvoke(prompt)

    return PipelineTrace(
        query=body.query,
        strategy=session.strategy,
        embedding=EmbeddingStage(
            model=settings.embed_model,
            dimensions=len(query_vector),
            preview=[round(v, 4) for v in query_vector[:8]],
        ),
        retrieved=retrieved,
        answer=(result.content or "").strip(),
    )

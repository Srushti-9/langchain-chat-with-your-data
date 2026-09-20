import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException

from app.core.retrievers import STRATEGIES, get_retriever
from app.deps import resolve_session
from app.schemas.retrieval import (
    CompareRequest,
    CompareResult,
    RetrievedChunk,
    RetrieverState,
    SetRetriever,
    StrategyResult,
)
from app.services.session_manager import Session

router = APIRouter(prefix="/sessions/{session_id}", tags=["retrieval"])


@router.put("/retriever", response_model=RetrieverState)
def set_retriever(body: SetRetriever, session: Session = Depends(resolve_session)) -> RetrieverState:
    if body.strategy not in STRATEGIES:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {body.strategy}")
    session.strategy = body.strategy
    return RetrieverState(strategy=session.strategy)


@router.get("/retriever", response_model=RetrieverState)
def get_active_retriever(session: Session = Depends(resolve_session)) -> RetrieverState:
    return RetrieverState(strategy=session.strategy)


async def _run_strategy(session_id: str, strategy: str, query: str, k: int) -> StrategyResult:
    start = time.perf_counter()
    try:
        retriever = get_retriever(session_id, strategy, k)
        docs = await retriever.ainvoke(query)
    except Exception as exc:
        return StrategyResult(chunks=[], latency_ms=0.0, error=str(exc))
    latency_ms = (time.perf_counter() - start) * 1000
    chunks = [
        RetrievedChunk(
            source=(d.metadata or {}).get("source"),
            chunk_index=(d.metadata or {}).get("chunk_index"),
            snippet=d.page_content[:300],
        )
        for d in docs
    ]
    return StrategyResult(chunks=chunks, latency_ms=round(latency_ms, 1))


@router.post("/retrieval/compare", response_model=CompareResult)
async def compare_retrieval(
    body: CompareRequest, session: Session = Depends(resolve_session)
) -> CompareResult:
    strategies = body.strategies or list(STRATEGIES)
    unknown = [s for s in strategies if s not in STRATEGIES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown strategies: {unknown}")

    k = body.k or 4
    results = await asyncio.gather(
        *(_run_strategy(session.session_id, s, body.query, k) for s in strategies)
    )
    return CompareResult(results=dict(zip(strategies, results)))

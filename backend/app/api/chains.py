import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException

from app.core.chains_classic import CHAIN_TYPES, run_qa_chain
from app.core.retrievers import get_retriever
from app.deps import resolve_session
from app.schemas.chains import ChainCompareRequest, ChainCompareResult, ChainResult
from app.services.session_manager import Session

router = APIRouter(prefix="/sessions/{session_id}/chains", tags=["chains"])


async def _run_chain(chain_type: str, docs, question: str) -> ChainResult:
    start = time.perf_counter()
    try:
        answer = await run_qa_chain(chain_type, docs, question)
    except Exception as exc:
        return ChainResult(answer="", latency_ms=0.0, n_docs=len(docs), error=str(exc))
    latency_ms = (time.perf_counter() - start) * 1000
    return ChainResult(answer=answer, latency_ms=round(latency_ms, 1), n_docs=len(docs))


@router.post("/compare", response_model=ChainCompareResult)
async def compare_chains(
    body: ChainCompareRequest, session: Session = Depends(resolve_session)
) -> ChainCompareResult:
    chain_types = body.chain_types or list(CHAIN_TYPES)
    unknown = [c for c in chain_types if c not in CHAIN_TYPES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown chain types: {unknown}")

    k = body.k or 4
    retriever = get_retriever(session.session_id, session.strategy, k)
    docs = await retriever.ainvoke(body.query)

    results = await asyncio.gather(
        *(_run_chain(ct, docs, body.query) for ct in chain_types)
    )
    return ChainCompareResult(results=dict(zip(chain_types, results)))

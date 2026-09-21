from pydantic import BaseModel


class ChainCompareRequest(BaseModel):
    query: str
    chain_types: list[str] | None = None
    k: int | None = None


class ChainResult(BaseModel):
    answer: str
    latency_ms: float
    n_docs: int
    error: str | None = None


class ChainCompareResult(BaseModel):
    results: dict[str, ChainResult]

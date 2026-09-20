from pydantic import BaseModel


class SetRetriever(BaseModel):
    strategy: str


class RetrieverState(BaseModel):
    strategy: str


class CompareRequest(BaseModel):
    query: str
    strategies: list[str] | None = None
    k: int | None = None


class RetrievedChunk(BaseModel):
    source: str | None = None
    chunk_index: int | None = None
    snippet: str


class StrategyResult(BaseModel):
    chunks: list[RetrievedChunk]
    latency_ms: float
    error: str | None = None


class CompareResult(BaseModel):
    results: dict[str, StrategyResult]

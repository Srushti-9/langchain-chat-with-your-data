from pydantic import BaseModel


class TraceRequest(BaseModel):
    query: str
    k: int | None = None


class TraceChunk(BaseModel):
    source: str | None = None
    chunk_index: int | None = None
    snippet: str


class EmbeddingStage(BaseModel):
    model: str
    dimensions: int
    preview: list[float]


class PipelineTrace(BaseModel):
    query: str
    strategy: str
    embedding: EmbeddingStage
    retrieved: list[TraceChunk]
    answer: str

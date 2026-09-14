from pydantic import BaseModel


class SessionCreated(BaseModel):
    session_id: str
    created_at: str


class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    doc_count: int


class IngestedSource(BaseModel):
    source: str
    n_chunks: int


class IngestResult(BaseModel):
    ingested: list[IngestedSource]
    total_chunks: int


class DocumentInfo(BaseModel):
    total_chunks: int

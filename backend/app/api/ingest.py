from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.config import get_settings
from app.core.loaders import SUPPORTED_EXTENSIONS, load_file, load_url
from app.core.splitting import split_documents
from app.core.vectorstore import add_documents, count_documents
from app.deps import resolve_session
from app.schemas.session import DocumentInfo, IngestedSource, IngestResult
from app.services.session_manager import Session

router = APIRouter(prefix="/sessions/{session_id}/documents", tags=["ingestion"])


def _ingest_file(session_id: str, path, source_name: str, chunk_size, chunk_overlap) -> int:
    docs = load_file(path)
    for d in docs:
        d.metadata["source"] = source_name
    chunks = split_documents(docs, chunk_size, chunk_overlap)
    return add_documents(session_id, chunks)


def _ingest_url(session_id: str, url: str, chunk_size, chunk_overlap) -> int:
    docs = load_url(url)
    chunks = split_documents(docs, chunk_size, chunk_overlap)
    return add_documents(session_id, chunks)


@router.post("", response_model=IngestResult)
async def ingest_documents(
    files: list[UploadFile] | None = None,
    urls: list[str] | None = Form(default=None),
    chunk_size: int | None = Form(default=None),
    chunk_overlap: int | None = Form(default=None),
    session: Session = Depends(resolve_session),
) -> IngestResult:
    if not files and not urls:
        raise HTTPException(status_code=400, detail="Provide at least one file or url")

    settings = get_settings()
    upload_dir = settings.upload_dir / session.session_id
    ingested: list[IngestedSource] = []

    async with session.lock:
        for file in files or []:
            suffix = f".{file.filename.rsplit('.', 1)[-1].lower()}" if "." in file.filename else ""
            if suffix not in SUPPORTED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
            dest = upload_dir / file.filename
            content = await file.read()
            dest.write_bytes(content)
            n = await run_in_threadpool(
                _ingest_file, session.session_id, dest, file.filename, chunk_size, chunk_overlap
            )
            ingested.append(IngestedSource(source=file.filename, n_chunks=n))

        for url in urls or []:
            n = await run_in_threadpool(
                _ingest_url, session.session_id, url, chunk_size, chunk_overlap
            )
            ingested.append(IngestedSource(source=url, n_chunks=n))

    return IngestResult(ingested=ingested, total_chunks=sum(i.n_chunks for i in ingested))


@router.get("", response_model=DocumentInfo)
def list_documents(session: Session = Depends(resolve_session)) -> DocumentInfo:
    return DocumentInfo(total_chunks=count_documents(session.session_id))

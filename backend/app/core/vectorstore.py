import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import get_settings
from app.core.embeddings import get_embeddings


def _collection_dir(session_id: str) -> str:
    settings = get_settings()
    return str(settings.chroma_dir / session_id)


def get_vectorstore(session_id: str) -> Chroma:
    return Chroma(
        collection_name=f"s_{session_id}",
        embedding_function=get_embeddings(),
        persist_directory=_collection_dir(session_id),
    )


def add_documents(session_id: str, chunks: list[Document]) -> int:
    store = get_vectorstore(session_id)
    store.add_documents(chunks)
    return len(chunks)


def count_documents(session_id: str) -> int:
    # langchain-chroma exposes no public count; _collection is the underlying
    # chromadb collection and count() is O(1) vs get() which materializes all ids.
    return get_vectorstore(session_id)._collection.count()


def delete_collection(session_id: str) -> None:
    settings = get_settings()
    path = settings.chroma_dir / session_id
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)

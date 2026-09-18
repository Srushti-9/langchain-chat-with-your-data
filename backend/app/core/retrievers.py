from langchain_core.vectorstores import VectorStoreRetriever

from app.core.vectorstore import get_vectorstore

DEFAULT_K = 4


def get_retriever(session_id: str, k: int = DEFAULT_K) -> VectorStoreRetriever:
    store = get_vectorstore(session_id)
    return store.as_retriever(search_kwargs={"k": k})

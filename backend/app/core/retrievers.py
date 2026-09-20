from langchain_classic.chains.query_constructor.schema import AttributeInfo
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.retrievers import BaseRetriever

from app.core.vectorstore import get_vectorstore

DEFAULT_K = 4
STRATEGIES = ("similarity", "mmr", "self_query", "compression")

_DOCUMENT_CONTENTS = "Chunks of the user's uploaded documents"
_METADATA_FIELDS = [
    AttributeInfo(name="source", description="The document the chunk came from", type="string"),
    AttributeInfo(name="chunk_index", description="Position of the chunk within its document", type="integer"),
]


def get_retriever(session_id: str, strategy: str = "similarity", k: int = DEFAULT_K) -> BaseRetriever:
    store = get_vectorstore(session_id)

    if strategy == "mmr":
        return store.as_retriever(search_type="mmr", search_kwargs={"k": k})

    if strategy == "self_query":
        from langchain_community.query_constructors.chroma import ChromaTranslator

        from app.core.agent import get_chat_model

        return SelfQueryRetriever.from_llm(
            llm=get_chat_model(),
            vectorstore=store,
            document_contents=_DOCUMENT_CONTENTS,
            metadata_field_info=_METADATA_FIELDS,
            structured_query_translator=ChromaTranslator(),
        )

    if strategy == "compression":
        from app.core.agent import get_chat_model

        base = store.as_retriever(search_kwargs={"k": k})
        return ContextualCompressionRetriever(
            base_compressor=LLMChainExtractor.from_llm(get_chat_model()),
            base_retriever=base,
        )

    return store.as_retriever(search_kwargs={"k": k})

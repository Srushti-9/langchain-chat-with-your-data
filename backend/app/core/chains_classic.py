from langchain_classic.chains.question_answering import load_qa_chain
from langchain_core.documents import Document

from app.core.agent import get_chat_model

CHAIN_TYPES = ("stuff", "map_reduce", "refine")


async def run_qa_chain(chain_type: str, docs: list[Document], question: str) -> str:
    chain = load_qa_chain(get_chat_model(), chain_type=chain_type)
    result = await chain.ainvoke({"input_documents": docs, "question": question})
    return (result.get("output_text") or "").strip()

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import create_retriever_tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.config import get_settings
from app.core.prompts import RAG_SYSTEM_PROMPT
from app.core.retrievers import get_retriever

_checkpointer: BaseCheckpointSaver | None = None


def set_checkpointer(checkpointer: BaseCheckpointSaver) -> None:
    global _checkpointer
    _checkpointer = checkpointer


def get_chat_model() -> BaseChatModel:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
        streaming=True,
    )


def build_agent(session_id: str):
    retriever = get_retriever(session_id)
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_documents",
        description="Search the user's uploaded documents for passages relevant to the question.",
        response_format="content_and_artifact",
    )
    return create_agent(
        model=get_chat_model(),
        tools=[retriever_tool],
        system_prompt=RAG_SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )

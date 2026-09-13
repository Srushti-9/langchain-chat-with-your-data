from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_file(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path)).load()
    if suffix in {".txt", ".md"}:
        return TextLoader(str(path), encoding="utf-8").load()
    raise ValueError(f"Unsupported file type: {suffix}")


def load_url(url: str) -> list[Document]:
    return WebBaseLoader(url).load()

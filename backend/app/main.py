import os
import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

# langchain-community loaders emit a sunset warning; keep logs clean until a
# standalone loader package replaces PyPDFLoader/WebBaseLoader.
warnings.filterwarnings("ignore", message=".*langchain-community.*")
os.environ.setdefault("USER_AGENT", "chat-with-your-data/0.1.0")

for directory in (settings.chroma_dir, settings.checkpoint_dir, settings.upload_dir):
    directory.mkdir(parents=True, exist_ok=True)

from app.api import ingest, sessions  # noqa: E402  (import after env setup)

app = FastAPI(title="Chat With Your Data", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(ingest.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

import os
import warnings
from contextlib import AsyncExitStack, asynccontextmanager

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

from app.api import chains, chat, ingest, memory, pipeline, retrieval, sessions  # noqa: E402  (import after env setup)
from app.core.agent import set_checkpointer  # noqa: E402

CHECKPOINT_DB = str(settings.checkpoint_dir / "graph.sqlite")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    async with AsyncExitStack() as stack:
        checkpointer = await stack.enter_async_context(
            AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB)
        )
        await checkpointer.setup()
        set_checkpointer(checkpointer)
        yield


app = FastAPI(title="Chat With Your Data", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(retrieval.router)
app.include_router(memory.router)
app.include_router(pipeline.router)
app.include_router(chains.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

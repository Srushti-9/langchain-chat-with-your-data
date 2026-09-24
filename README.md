# Chat With Your Data

A conversational RAG (Retrieval-Augmented Generation) chatbot that answers questions about **your own documents** — with streamed answers, source citations, and conversation memory.

Built on the current LangChain 1.4 + LangGraph stack, it doubles as an interactive showcase: four views let you watch the retrieval machine think.

## What it does

Upload a PDF / webpage / text file → it gets chunked, embedded, and stored in a vector database → ask questions and get answers grounded in the actual source text, with citations and multi-turn memory.

### Four showcase views

| View | What it shows |
|---|---|
| **Retrieval comparison** | Four search strategies (similarity / MMR / self-query / compression) side by side on your own docs |
| **Memory inspector** | The live conversation memory — inspect and reset it |
| **Pipeline visualizer** | One question tracing the full load → split → embed → retrieve → answer path |
| **Chain-type comparison** | `stuff` / `map_reduce` / `refine` answer strategies raced for quality and latency |

## Stack

- **Backend**: FastAPI (SSE streaming)
- **Frontend**: React + Vite
- **LLM orchestration**: LangChain 1.4 — `create_agent` (LangGraph-backed) with a retriever tool + memory checkpointer
- **Provider**: OpenAI (`gpt-4o-mini`, `text-embedding-3-small`)
- **Vector store**: Chroma (persisted to disk)

## Project layout

| Area | Module |
|---|---|
| Document loading | `backend/app/core/loaders.py` |
| Document splitting | `backend/app/core/splitting.py` |
| Embeddings + vector store | `backend/app/core/embeddings.py`, `vectorstore.py` |
| Retrieval strategies | `backend/app/core/retrievers.py` |
| Question answering / chat | `backend/app/core/agent.py` |
| Conversation memory | `backend/app/core/memory.py` |
| Answer-combining chains | `backend/app/core/chains_classic.py` |
| Evaluation | `backend/app/evals/` (later phase) |

## Running it locally

```bash
# backend
cd backend && pip install -e . && uvicorn app.main:app --reload   # :8000

# frontend
cd frontend && npm install && npm run dev                          # :5173
```

Set `OPENAI_API_KEY` in `backend/.env` (see `.env.example` for all keys). The frontend talks to the backend through Vite's dev proxy, so no CORS setup is needed in development.

## Scope

Single-user, local-first by design. Chroma and the SQLite checkpointer aren't built for concurrent writers, so ingestion is serialized per session and chat turns are serialized per conversation thread. Sessions live in memory (lost on restart), while the vector store and conversation checkpoints persist to disk.

## Status

Built in phases: skeleton → ingestion → chat → showcase views → **polish** (done) → evals (deferred). The four showcase views, streaming chat with citations and memory, and visible loading/error states are all in place.

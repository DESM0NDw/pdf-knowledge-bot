# PDF Knowledge Bot

AI-powered document Q&A demo. Upload a PDF, ask questions, get answers with source references.

**Live:** https://pdf-demo.autonomika.de

## How it works

1. User uploads a PDF
2. Document is chunked and embedded via `nomic-embed-text` (Ollama)
3. Embeddings are stored in [Qdrant](https://qdrant.tech/) vector database
4. User asks a question → relevant chunks are retrieved (RAG)
5. [Groq](https://groq.com/) (llama-3.1-8b-instant) generates an answer with source references

## Stack

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit + adapter-static + Nginx |
| Backend | FastAPI + Python |
| Embeddings | Ollama (`nomic-embed-text`) |
| Vector DB | Qdrant |
| LLM | Groq API (`llama-3.1-8b-instant`) |
| Deploy | Docker Compose on Hetzner Cloud |

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Requires a running Qdrant instance and Ollama with `nomic-embed-text` pulled.

## Deploy

```bash
docker compose build --no-cache
docker compose up -d
```

Requires the `1panel-network` Docker network and a running Ollama + Qdrant instance.

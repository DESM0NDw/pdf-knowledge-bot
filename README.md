# PDF Knowledge Bot

AI-powered document Q&A demo. Select a demo document, ask questions, get answers with source references.

**Live:** https://pdf-demo.autonomika.de

## How it works

1. User selects one of the pre-loaded demo documents (click or drag into viewer)
2. Documents are chunked and embedded via `nomic-embed-text` (Ollama) at startup
3. Embeddings are stored in [Qdrant](https://qdrant.tech/) vector database
4. User asks a question → relevant chunks are retrieved (RAG)
5. [Groq](https://groq.com/) (llama-3.1-8b-instant) generates an answer with source references
6. Source page badges are clickable — jumps the PDF viewer to the referenced page

## Stack

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit + adapter-static + Nginx |
| Backend | FastAPI + Python |
| Embeddings | Ollama (`nomic-embed-text`) |
| Vector DB | Qdrant |
| LLM | Groq API (`llama-3.1-8b-instant`) |
| Deploy | Docker Compose on Hetzner Cloud |

## Demo Documents

Three fictional company documents are included under `docs/`:

- `autonomika_mitarbeiterhandbuch_demo.pdf` — tech company employee handbook
- `bellavista_betriebshandbuch_demo.pdf` — restaurant operations manual
- `hausmann_handbuch_demo.pdf` — real estate agency handbook

Generated via `docs/gen_*.py` scripts using the `reportlab` library.

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

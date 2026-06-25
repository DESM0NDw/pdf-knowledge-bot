# Wissens-Assistent (pdf-knowledge-bot)

AI-powered document Q&A demo with semantic question analytics. Pick a use case, ask questions, get answers with source references — and the system learns which questions get asked most.

**Live:** https://pdf-demo.autonomika.de

## How it works

1. User picks one of the demo documents — each represents a different use case (click or drag into viewer)
2. On selection, the document is chunked and embedded via `nomic-embed-text` (Ollama)
3. Embeddings are stored in [Qdrant](https://qdrant.tech/) vector database
4. User asks a question → relevant chunks are retrieved (RAG)
5. [Groq](https://groq.com/) (llama-3.1-8b-instant) generates an answer with source references
6. Source page badges are clickable — jumps the PDF viewer to the referenced page
7. Each question is embedded and **semantically clustered** in Qdrant: similar questions
   (similarity ≥ 0.65) increment a shared counter instead of creating duplicates. The most
   frequent questions surface in a "what others ask" panel — revealing where the real
   information demand is.

## Use cases

The demo ships with four fictional documents under `docs/`, each showing a different
application of the same engine:

| Use case | Document | What the analytics add |
|----------|----------|------------------------|
| Mitarbeiter-Self-Service | `autonomika_mitarbeiterhandbuch_demo.pdf` | HR sees which policies are looked up most |
| Kundensupport | `helio_hilfecenter_demo.pdf` | Top clusters become FAQ/help-article candidates |
| Onboarding | `nordlicht_onboarding_demo.pdf` | Shows where new hires get stuck → improve the guide |
| Sales-Enablement | `voltedge_datenblatt_demo.pdf` | Reveals what prospects ask about most |

Per use case, the UI adapts the "how it works" flow steps, the hint text and the
processing label — all driven by metadata from the backend (`/api/docs`).

PDFs are generated via the `docs/gen_*.py` scripts using the `fpdf2` library. With no
local Python/pip, generate them in a throwaway container:

```bash
docker run --rm -v "$(pwd)/docs:/out" -w /out python:3.12-slim \
  sh -c "pip install fpdf2 -q && python gen_handbook.py && python gen_helio.py \
         && python gen_nordlicht.py && python gen_voltedge.py"
```

## Stack

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit + adapter-static + Nginx |
| Backend | FastAPI + Python |
| Embeddings | Ollama (`nomic-embed-text`) |
| Vector DB | Qdrant (documents + question clusters) |
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

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from groq import Groq
import rag

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "1Panel-ollama-1RR8")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PDF_PATH = "/docs/autonomika_mitarbeiterhandbuch_demo.pdf"

qdrant: QdrantClient | None = None
groq_client: Groq | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant, groq_client
    qdrant = QdrantClient(host=QDRANT_HOST, port=6333)
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("Indexing PDF...", flush=True)
    count = rag.index_pdf(PDF_PATH, qdrant, OLLAMA_HOST)
    print(f"Indexed {count} chunks.", flush=True)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[int]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Frage darf nicht leer sein.")

    chunks = rag.search(req.question, qdrant, OLLAMA_HOST)
    context = "\n\n".join(f"[Seite {c['page']}]: {c['text']}" for c in chunks)

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "Du bist ein hilfreicher Assistent fuer das Mitarbeiterhandbuch der Autonomika GmbH. "
                    "Beantworte Fragen ausschliesslich basierend auf dem bereitgestellten Kontext. "
                    "Gib immer die Seitenzahl an (z.B. 'Laut Seite 3...'). "
                    "Wenn die Antwort nicht im Kontext steht, sage das klar und knapp."
                ),
            },
            {
                "role": "user",
                "content": f"Kontext:\n{context}\n\nFrage: {req.question}",
            },
        ],
        max_tokens=512,
        temperature=0.1,
    )

    answer = completion.choices[0].message.content
    sources = sorted(set(c["page"] for c in chunks))
    return ChatResponse(answer=answer, sources=sources)

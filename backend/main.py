import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from qdrant_client import QdrantClient
from groq import Groq
import rag

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "1Panel-ollama-1RR8")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DOCS_DIR = "/docs"

DOCS = [
    {
        "id": "autonomika",
        "name": "Autonomika GmbH",
        "industry": "Technologie",
        "description": "Mitarbeiterhandbuch",
        "pdf_file": "autonomika_mitarbeiterhandbuch_demo.pdf",
        "suggestions": [
            "Wie viele Urlaubstage habe ich?",
            "Was ist die Kernarbeitszeit?",
            "Wie viele Homeoffice-Tage sind erlaubt?",
            "Wie reiche ich Spesen ein?",
            "Wie lange dauert das Onboarding?",
            "Was ist mein Equipment-Budget?",
            "Welche Tools nutzen wir im Team?",
            "Wann finden Leistungsbeurteilungen statt?",
        ],
    },
    {
        "id": "bellavista",
        "name": "Bella Vista Restaurants",
        "industry": "Gastronomie",
        "description": "Betriebshandbuch",
        "pdf_file": "bellavista_betriebshandbuch_demo.pdf",
        "suggestions": [
            "Welche Allergene hat das Tiramisu?",
            "Wie lange dauert eine Abendschicht?",
            "Was kostet die Pizza Margherita?",
            "Wie wird das Trinkgeld aufgeteilt?",
            "Was sind die Oeffnungszeiten am Wochenende?",
            "Wer ist der Fischlieferant?",
            "Wie oft wird die HACCP-Kontrolle durchgefuehrt?",
            "Was darf ich als Mitarbeiterverpflegung essen?",
        ],
    },
    {
        "id": "hausmann",
        "name": "Hausmann & Partner Immobilien",
        "industry": "Immobilien",
        "description": "Mitarbeiterhandbuch",
        "pdf_file": "hausmann_handbuch_demo.pdf",
        "suggestions": [
            "Wie hoch ist die Maklerprovision beim Kauf?",
            "Welche Unterlagen brauche ich fuer den Verkauf?",
            "Wie lange dauert eine Besichtigung?",
            "Wie schnell antworten wir auf Anfragen?",
            "Was kostet eine Immobilienbewertung?",
            "Welche Provision zahlt der Mieter?",
            "Welches CRM-System nutzen wir?",
            "Wie lange dauert ein typischer Verkaufsprozess?",
        ],
    },
]

qdrant: QdrantClient | None = None
groq_client: Groq | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant, groq_client
    qdrant = QdrantClient(host=QDRANT_HOST, port=6333)
    groq_client = Groq(api_key=GROQ_API_KEY)
    for doc in DOCS:
        pdf_path = f"{DOCS_DIR}/{doc['pdf_file']}"
        print(f"Indexing {doc['id']}...", flush=True)
        count = rag.index_pdf(pdf_path, doc["id"], qdrant, OLLAMA_HOST)
        print(f"  -> {count} chunks", flush=True)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/pdfs", StaticFiles(directory=DOCS_DIR), name="pdfs")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/docs")
def list_docs():
    return [
        {
            "id": d["id"],
            "name": d["name"],
            "industry": d["industry"],
            "description": d["description"],
            "pdf_url": f"/pdfs/{d['pdf_file']}",
            "suggestions": d["suggestions"],
        }
        for d in DOCS
    ]


class ChatRequest(BaseModel):
    question: str
    doc_id: str = "autonomika"


class ChatResponse(BaseModel):
    answer: str
    sources: list[int]


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Frage darf nicht leer sein.")

    doc = next((d for d in DOCS if d["id"] == req.doc_id), None)
    if not doc:
        raise HTTPException(404, f"Dokument '{req.doc_id}' nicht gefunden.")

    chunks = rag.search(req.question, req.doc_id, qdrant, OLLAMA_HOST)
    context = "\n\n".join(f"[Seite {c['page']}]: {c['text']}" for c in chunks)

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Du bist ein hilfreicher Assistent fuer das Dokument '{doc['name']} - {doc['description']}'. "
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

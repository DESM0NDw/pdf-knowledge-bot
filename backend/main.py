import os
import time
import tempfile
import hashlib
from collections import defaultdict
from contextlib import asynccontextmanager
import sentry_sdk
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from qdrant_client import QdrantClient
from groq import Groq
import rag

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")

if dsn := os.getenv("SENTRY_DSN", ""):
    sentry_sdk.init(dsn=dsn, traces_sample_rate=0.2)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "1Panel-ollama-1RR8")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DOCS_DIR = "/docs"

DOCS = [
    {
        "id": "autonomika",
        "name": "Autonomika GmbH",
        "use_case": "Mitarbeiter-Self-Service",
        "description": "Mitarbeiterhandbuch",
        "pdf_file": "autonomika_mitarbeiterhandbuch_demo.pdf",
        "flow_steps": ["Handbuch laden", "Wissensbasis aufbauen", "Mitarbeiter fragt", "Antwort + Bedarf erkannt"],
        "flow_hint": "Mitarbeiter finden Antworten selbst, ohne in HR oder bei Kollegen nachzufragen — und HR sieht, welche Themen am häufigsten gesucht werden.",
        "processing_text": "Handbuch wird zur durchsuchbaren Wissensbasis verarbeitet",
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
        "id": "helio",
        "name": "Helio (SaaS)",
        "use_case": "Kundensupport",
        "description": "Hilfe-Center",
        "pdf_file": "helio_hilfecenter_demo.pdf",
        "flow_steps": ["Hilfe-Doku laden", "Wissensbasis aufbauen", "Kunde fragt", "Antwort + häufige Fragen"],
        "flow_hint": "Kunden bekommen sofort Antworten aus der Produktdoku, statt ein Ticket zu öffnen — und die häufigsten Fragen werden zur Vorlage für eure Hilfe-Artikel.",
        "processing_text": "Hilfe-Doku wird zur durchsuchbaren Wissensbasis verarbeitet",
        "suggestions": [
            "Wie setze ich mein Passwort zurück?",
            "Wie lade ich Teammitglieder ein?",
            "Welche Pläne gibt es und was kosten sie?",
            "Wie exportiere ich meine Projektdaten?",
            "Unterstützt Helio Zwei-Faktor-Authentifizierung?",
            "Wie kündige ich mein Abo?",
            "Gibt es eine API oder Integrationen?",
            "Wie erreiche ich den Support?",
        ],
    },
    {
        "id": "nordlicht",
        "name": "Nordlicht Studios",
        "use_case": "Onboarding",
        "description": "Onboarding-Guide",
        "pdf_file": "nordlicht_onboarding_demo.pdf",
        "flow_steps": ["Guide laden", "Wissensbasis aufbauen", "Neue:r MA fragt", "Antwort + offene Punkte"],
        "flow_hint": "Neue Mitarbeiter klären Fragen selbst in den ersten Tagen — und das Team sieht, wo der Onboarding-Guide unklar ist und nachgebessert werden sollte.",
        "processing_text": "Onboarding-Guide wird zur durchsuchbaren Wissensbasis verarbeitet",
        "suggestions": [
            "Wo finde ich meine Zugangsdaten?",
            "Wer ist mein Buddy und Ansprechpartner?",
            "Wie richte ich den VPN-Zugang ein?",
            "Welche Tools brauche ich am ersten Tag?",
            "Wann ist mein erstes Feedbackgespräch?",
            "Wie funktioniert die Zeiterfassung?",
            "An wen wende ich mich bei IT-Problemen?",
            "Was passiert in meiner ersten Woche?",
        ],
    },
    {
        "id": "voltedge",
        "name": "VoltEdge Solar",
        "use_case": "Sales-Enablement",
        "description": "Produkt- & Preisübersicht",
        "pdf_file": "voltedge_datenblatt_demo.pdf",
        "flow_steps": ["Datenblatt laden", "Wissensbasis aufbauen", "Vertrieb fragt", "Antwort + Top-Fragen"],
        "flow_hint": "Das Vertriebsteam bekommt belastbare Antworten zu Preisen und Specs in Sekunden — und sieht, was Interessenten am häufigsten fragen.",
        "processing_text": "Datenblatt wird zur durchsuchbaren Wissensbasis verarbeitet",
        "suggestions": [
            "Welche Rabatte gibt es bei Jahreszahlung?",
            "Wie hoch ist die Leistungsgarantie?",
            "Lässt sich ein Speicher nachrüsten?",
            "Was kostet die jährliche Wartung?",
            "Wie lang ist die Lieferzeit?",
            "Gibt es Mengenrabatte für Großprojekte?",
            "Wie lange dauert die Installation?",
            "Welche Förderungen sind möglich?",
        ],
    },
]

qdrant: QdrantClient | None = None
groq_client: Groq | None = None
_indexed: set[str] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant, groq_client
    qdrant = QdrantClient(host=QDRANT_HOST, port=6333)
    groq_client = Groq(api_key=GROQ_API_KEY)
    yield


RATE_LIMIT = 20
RATE_WINDOW = 3600
_requests: dict = defaultdict(list)


def get_ip(request: Request) -> str:
    fwd = request.headers.get("X-Forwarded-For")
    return fwd.split(",")[0].strip() if fwd else request.client.host


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pdf-demo.autonomika.de"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "POST":
        ip = get_ip(request)
        now = time.time()
        _requests[ip] = [t for t in _requests[ip] if now - t < RATE_WINDOW]
        if len(_requests[ip]) >= RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "Zu viele Anfragen. Bitte später erneut versuchen."})
        _requests[ip].append(now)
    return await call_next(request)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/pdfs/{filename}")
def serve_pdf(filename: str):
    safe = filename.replace("/", "").replace("..", "")
    path = f"{DOCS_DIR}/{safe}"
    return FileResponse(
        path,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={safe}"},
    )


@app.get("/api/docs")
def list_docs():
    return [
        {
            "id": d["id"],
            "name": d["name"],
            "use_case": d["use_case"],
            "description": d["description"],
            "pdf_url": f"/pdfs/{d['pdf_file']}",
            "flow_steps": d["flow_steps"],
            "flow_hint": d["flow_hint"],
            "processing_text": d["processing_text"],
            "suggestions": d["suggestions"],
        }
        for d in DOCS
    ]


@app.post("/api/index/{doc_id}")
def index_demo(doc_id: str):
    doc = next((d for d in DOCS if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(404, "Dokument nicht gefunden")
    if doc_id in _indexed:
        return {"doc_id": doc_id, "chunks": 0, "cached": True}
    pdf_path = f"{DOCS_DIR}/{doc['pdf_file']}"
    count = rag.index_pdf(pdf_path, doc_id, qdrant, OLLAMA_HOST)
    _indexed.add(doc_id)
    return {"doc_id": doc_id, "chunks": count, "cached": False}


MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Datei zu groß (max. 20 MB)")
    doc_id = "up_" + hashlib.md5(contents).hexdigest()[:12]
    if doc_id in _indexed:
        return {"doc_id": doc_id, "chunks": 0, "name": file.filename, "cached": True}
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    try:
        count = rag.index_pdf(tmp_path, doc_id, qdrant, OLLAMA_HOST)
    finally:
        os.unlink(tmp_path)
    _indexed.add(doc_id)
    return {"doc_id": doc_id, "chunks": count, "name": file.filename, "cached": False}


class ChatRequest(BaseModel):
    question: str
    doc_id: str
    doc_name: str = "Dokument"


class ChatResponse(BaseModel):
    answer: str
    sources: list[int]
    question_count: int
    is_new_question: bool


@app.get("/api/questions/{doc_id}")
def get_questions(doc_id: str):
    return rag.top_questions(doc_id, qdrant)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Frage darf nicht leer sein.")

    q_vector = rag.get_embedding(req.question, OLLAMA_HOST)
    chunks = rag.search(req.question, req.doc_id, qdrant, OLLAMA_HOST, vector=q_vector)
    context = "\n\n".join(f"[Seite {c['page']}]: {c['text']}" for c in chunks)

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Du bist ein hilfreicher Assistent fuer das Dokument '{req.doc_name}'. "
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

    question = req.question.strip()
    if len(question) >= 10:
        count, is_new = rag.track_question(question, req.doc_id, qdrant, q_vector)
    else:
        count, is_new = 0, False

    return ChatResponse(answer=answer, sources=sources, question_count=count, is_new_question=is_new)

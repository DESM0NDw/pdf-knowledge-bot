import uuid
import httpx
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

VECTOR_SIZE = 768  # nomic-embed-text
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
# Kalibriert an nomic-embed-text: gleiche Frage umformuliert ~0.70-0.77,
# verschiedene Themen ~0.55. 0.65 trennt beide sauber.
QUESTION_THRESHOLD = 0.65


def _collection(doc_id: str) -> str:
    return f"doc_{doc_id}"


def _questions_collection(doc_id: str) -> str:
    return f"questions_{doc_id}"


def get_embedding(text: str, ollama_host: str) -> list[float]:
    resp = httpx.post(
        f"http://{ollama_host}:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def chunk_text(text: str, page: int) -> list[dict]:
    chunks = []
    start = 0
    while start < len(text):
        piece = text[start : start + CHUNK_SIZE]
        if piece.strip():
            chunks.append({"text": piece, "page": page})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def index_pdf(pdf_path: str, doc_id: str, client: QdrantClient, ollama_host: str) -> int:
    collection = _collection(doc_id)
    reader = PdfReader(pdf_path)

    try:
        client.delete_collection(collection)
    except Exception:
        pass

    client.create_collection(
        collection,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    points = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for chunk in chunk_text(text, page_num):
            vector = get_embedding(chunk["text"], ollama_host)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": chunk["text"], "page": chunk["page"]},
            ))

    if points:
        client.upsert(collection_name=collection, points=points)

    return len(points)


def search(question: str, doc_id: str, client: QdrantClient, ollama_host: str, top_k: int = 5, vector: list[float] | None = None) -> list[dict]:
    collection = _collection(doc_id)
    if vector is None:
        vector = get_embedding(question, ollama_host)
    hits = client.search(collection_name=collection, query_vector=vector, limit=top_k)
    return [{"text": h.payload["text"], "page": h.payload["page"], "score": h.score} for h in hits]


def track_question(question: str, doc_id: str, client: QdrantClient, vector: list[float]) -> tuple[int, bool]:
    """Speichert die Frage semantisch geclustert. Gibt (count, is_new) zurück."""
    collection = _questions_collection(doc_id)
    if not client.collection_exists(collection):
        client.create_collection(
            collection,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    hits = client.search(collection_name=collection, query_vector=vector, limit=1)
    if hits and hits[0].score >= QUESTION_THRESHOLD:
        point = hits[0]
        new_count = point.payload["count"] + 1
        client.set_payload(collection_name=collection, payload={"count": new_count}, points=[point.id])
        return new_count, False

    client.upsert(collection_name=collection, points=[PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={"text": question, "count": 1},
    )])
    return 1, True


def top_questions(doc_id: str, client: QdrantClient, limit: int = 8) -> list[dict]:
    collection = _questions_collection(doc_id)
    if not client.collection_exists(collection):
        return []
    points, _ = client.scroll(collection_name=collection, limit=500, with_payload=True)
    items = [{"text": p.payload["text"], "count": p.payload["count"]} for p in points]
    items.sort(key=lambda x: x["count"], reverse=True)
    return items[:limit]
